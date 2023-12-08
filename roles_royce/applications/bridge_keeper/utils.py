from dataclasses import dataclass, field
import threading
from prometheus_client import Gauge
import schedule
import time
from decouple import config
from web3.types import Address, ChecksumAddress, TxReceipt
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
from roles_royce.toolshed.anti_liquidation.spark import SparkCDP
import logging
from defabipedia.xDAI_bridge import ContractSpecs
from defabipedia.types import Chain
from defabipedia.tokens import EthereumContractSpecs as Tokens
from datetime import datetime

logger = logging.getLogger(__name__)


# The next helper function allows to leave variables unfilled in the .env file
def custom_config(variable, default, cast):
    value = config(variable, default=default)
    return default if value == '' else config(variable, default=default, cast=cast)


@dataclass
class ENV:
    RPC_ENDPOINT_ETHEREUM: str = config('RPC_ENDPOINT_ETHEREUM')
    RPC_ENDPOINT_GNOSIS: str = config('RPC_ENDPOINT_GNOSIS')
    RPC_ENDPOINT_ETHEREUM_FALLBACK: str = config('RPC_ENDPOINT_ETHEREUM_FALLBACK', default='')
    RPC_ENDPOINT_GNOSIS_FALLBACK: str = config('RPC_ENDPOINT_GNOSIS_FALLBACK', default='')
    PRIVATE_KEY: str = config('PRIVATE_KEY')
    COOLDOWN_MINUTES: float = custom_config('COOLDOWN_MINUTES', default=5, cast=float)
    SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
    TELEGRAM_BOT_TOKEN: str = config('TELEGRAM_BOT_TOKEN', default='')
    TELEGRAM_CHAT_ID: int = custom_config('TELEGRAM_CHAT_ID', default='', cast=int)
    PROMETHEUS_PORT: int = custom_config('PROMETHEUS_PORT', default=8000, cast=int)
    TEST_MODE: bool = config('TEST_MODE', default=False, cast=bool)
    LOCAL_FORK_PORT_ETHEREUM: int = custom_config('LOCAL_FORK_PORT_ETHEREUM', default=8545, cast=int)
    LOCAL_FORK_PORT_GNOSIS: int = custom_config('LOCAL_FORK_PORT_GNOSIS', default=8546, cast=int)
    STATUS_NOTIFICATION_HOUR: int = custom_config('STATUS_NOTIFICATION_HOUR', default='', cast=int)
    REFILL_THRESHOLD: float = config('REFILL_THRESHOLD', cast=int)
    INVEST_THRESHOLD: float = config('INVEST_THRESHOLD', cast=int)
    GAS_ETH_THRESHOLD: float = custom_config('GAS_ETH_THRESHOLD', default=0.5, cast=float)
    MINUTES_BEFORE_CLAIM_EPOCH: int = custom_config('MINUTES_BEFORE_CLAIM_EPOCH', default=90, cast=int)
    AMOUNT_OF_INTEREST_TO_PAY: float = config('AMOUNT_OF_INTEREST_TO_PAY', cast=float)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    def __post_init__(self):
        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_ETHEREUM)).is_connected():
            raise ValueError(f"RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT_ETHEREUM}.")
        if self.RPC_ENDPOINT_ETHEREUM_FALLBACK != '':
            if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_ETHEREUM_FALLBACK)).is_connected():
                raise ValueError(
                    f"FALLBACK_RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT_ETHEREUM_FALLBACK}.")

        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_GNOSIS)).is_connected():
            raise ValueError(f"RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT_GNOSIS}.")
        if self.RPC_ENDPOINT_ETHEREUM_FALLBACK != '':
            if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_GNOSIS_FALLBACK)).is_connected():
                raise ValueError(
                    f"FALLBACK_RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT_GNOSIS_FALLBACK}.")

        self.BOT_ADDRESS = Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_ETHEREUM)).eth.account.from_key(
            self.PRIVATE_KEY).address

    def __repr__(self):
        return 'Environment variables'


@dataclass
class Gauges:
    bridge_DAI_balance = Gauge('bridge_DAI_balance', 'Bridge"s DAI balance')
    bot_ETH_balance = Gauge('bot_ETH_balance', 'ETH balance of the bot')
    next_claim_epoch = Gauge('next_claim_epoch', 'Next claim epoch')
    refill_threshold = Gauge('refill_threshold', 'Refill threshold')
    invest_threshold = Gauge('invest_threshold', 'Invest threshold')
    min_cash_threshold = Gauge('min_cash_threshold', 'Minimum cash threshold')

    def update(self, bridge_DAI_balance: int, bot_ETH_balance: int, next_claim_epoch: int, min_cash_threshold: int):
        self.bot_ETH_balance.set(bot_ETH_balance / (10 ** 18))
        self.bridge_DAI_balance.set(bridge_DAI_balance / (10 ** decimals_DAI))
        self.next_claim_epoch.set(next_claim_epoch)
        self.invest_threshold.set(ENV.INVEST_THRESHOLD)
        self.refill_threshold.set(ENV.REFILL_THRESHOLD)
        self.min_cash_threshold.set(min_cash_threshold / (10 ** decimals_DAI))


@dataclass
class Flags:
    lack_of_gas_warning: threading.Event = field(default_factory=threading.Event)
    interest_payed: threading.Event = field(default_factory=threading.Event)
    tx_executed: threading.Event = field(default_factory=threading.Event)


def refill_bridge(w3: Web3, env: ENV) -> TxReceipt:
    bridge_contract = ContractSpecs[Chain.Ethereum].xDaiBridge.contract(w3)
    unsigned_tx = bridge_contract.functions.refillBridge().build_transaction({
        "from": env.BOT_ADDRESS,
        "nonce": w3.eth.get_transaction_count(env.BOT_ADDRESS),
    })
    signed_tx = w3.eth.account.sign_transaction(unsigned_tx, private_key=env.PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def invest_DAI(w3: Web3, env: ENV) -> TxReceipt:
    bridge_contract = ContractSpecs[Chain.Ethereum].xDaiBridge.contract(w3)
    unsigned_tx = bridge_contract.functions.investDai().build_transaction({
        "from": env.BOT_ADDRESS,
        "nonce": w3.eth.get_transaction_count(env.BOT_ADDRESS),
    })
    signed_tx = w3.eth.account.sign_transaction(unsigned_tx, private_key=env.PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def pay_interest(w3: Web3, env: ENV, amount: int) -> TxReceipt:
    bridge_contract = ContractSpecs[Chain.Ethereum].xDaiBridge.contract(w3)
    unsigned_tx = bridge_contract.functions.payInterest(Tokens.DAI.address, amount).build_transaction({
        "from": env.BOT_ADDRESS,
        "nonce": w3.eth.get_transaction_count(env.BOT_ADDRESS),
    })
    signed_tx = w3.eth.account.sign_transaction(unsigned_tx, private_key=env.PRIVATE_KEY)

    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


decimals_DAI = 18


def log_initial_data(env: ENV, messenger: Messenger):
    title = "Bridge Keeper started"
    message = (f"  xDAI bridge address: {ContractSpecs[Chain.Ethereum].xDaiBridge.address}\n"
               f"  Bot address: {env.BOT_ADDRESS}\n"
               f"  Refill threshold: {env.REFILL_THRESHOLD} DAI\n"
               f"  Invest threshold: {env.INVEST_THRESHOLD} DAI\n"
               f"  Amount of interest to pay: {env.AMOUNT_OF_INTEREST_TO_PAY} DAI\n"
               f"  Minutes before claim epoch to pay interest: {env.MINUTES_BEFORE_CLAIM_EPOCH}\n"
               f"  ETH gas alerting threshold: {env.GAS_ETH_THRESHOLD} ETH\n")
    messenger.log_and_alert(LoggingLevel.Info, title, message)


def log_status_update(env: ENV, bridge_DAI_balance: int, bot_ETH_balance: int, next_claim_epoch: int, min_cash_threshold: int):
    title = 'Status update'
    message = (f'  Bridge"s DAI balance: {bridge_DAI_balance / (10 ** decimals_DAI):.2f} DAI.\n'
               f'  Bot"s ETH balance: {bot_ETH_balance / (10 ** 18):.5f} ETH.\n'
               f'  Next claim epoch: {datetime.utcfromtimestamp(next_claim_epoch)} UTC.\n'
               f'  Minimum cash threshold: {min_cash_threshold / (10 ** decimals_DAI):.2f} DAI.\n'
               f'  Refill threshold: {ENV.REFILL_THRESHOLD:.2f} DAI.\n'
               f'  Invest threshold: {ENV.INVEST_THRESHOLD:.2f} DAI.\n'
               f"  Invest threshold: {env.INVEST_THRESHOLD} DAI\n"
               f"  Amount of interest to pay: {env.AMOUNT_OF_INTEREST_TO_PAY} DAI\n"
               f"  Minutes before claim epoch to pay interest: {env.MINUTES_BEFORE_CLAIM_EPOCH}\n"
               f"  ETH gas alerting threshold: {env.GAS_ETH_THRESHOLD} ETH\n")
    logger.info(title + '.\n' + message)
