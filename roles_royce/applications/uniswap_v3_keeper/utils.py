from dataclasses import dataclass, field
import threading
from prometheus_client import Gauge
from decouple import config
from web3.types import Address, ChecksumAddress, TxReceipt
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
import logging
from defabipedia.uniswap_v3 import ContractSpecs
from defabipedia.types import Chain
from defabipedia.tokens import erc20_contract
from datetime import datetime
from roles_royce import roles
from roles_royce.toolshed.alerting.utils import Event, EventLogDecoder
from roles_royce.protocols.uniswap_v3.methods_general import mint_nft, decrease_liquidity_nft, collect_all_fees
from roles_royce.protocols.uniswap_v3.utils import NFTPosition

logger = logging.getLogger(__name__)


# The next helper function allows to leave variables unfilled in the .env file
def custom_config(variable, default, cast):
    value = config(variable, default=default)
    return default if value == '' else config(variable, default=default, cast=cast)


@dataclass
class ENV:
    RPC_ENDPOINT: str = config('RPC_ENDPOINT', default='')
    RPC_ENDPOINT_FALLBACK: str = config('RPC_ENDPOINT_FALLBACK', default='')
    RPC_ENDPOINT_MEV: str = config('RPC_ENDPOINT_MEV', default='')
    PRIVATE_KEY: str = config('PRIVATE_KEY', default='')
    AVATAR_SAFE_ADDRESS: Address | ChecksumAddress | str = config('AVATAR_SAFE_ADDRESS', default='')
    ROLES_MOD_ADDRESS: Address | ChecksumAddress | str = config('ROLES_MOD_ADDRESS', default='')
    ROLE: int = custom_config('ROLE', default='', cast=int)
    COOLDOWN_MINUTES: float = custom_config('COOLDOWN_MINUTES', default=5, cast=float)
    SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
    TELEGRAM_BOT_TOKEN: str = config('TELEGRAM_BOT_TOKEN', default='')
    TELEGRAM_CHAT_ID: int = custom_config('TELEGRAM_CHAT_ID', default='', cast=int)
    PROMETHEUS_PORT: int = custom_config('PROMETHEUS_PORT', default=8000, cast=int)
    TEST_MODE: bool = config('TEST_MODE', default=False, cast=bool)
    LOCAL_FORK_PORT: int = custom_config('LOCAL_FORK_PORT', default=8545, cast=int)
    TOKEN0_ADDRESS: Address | ChecksumAddress | str = config('TOKEN0_ADDRESS', default='', cast=str)
    TOKEN1_ADDRESS: Address | ChecksumAddress | str = config('TOKEN1_ADDRESS', default='', cast=str)
    MIN_PRICE_THRESHOLD: float = custom_config('MIN_PRICE_THRESHOLD', default=10, cast=float)
    MAX_PRICE_THRESHOLD: float = custom_config('MAX_PRICE_THRESHOLD', default=10, cast=float)
    PRICE_RANGE_MULTIPLICATOR_SEED: float = custom_config('NEW_PRICE_RANGE_DELTA_PERCENTAGE_SEED', default=5,
                                                          cast=float)
    PRICE_RANGE_MULTIPLICATOR_PERCENTUAL_DECREMENT: float = custom_config('NEW_PRICE_RANGE_DELTA_PERCENTAGE_DECREMENT',
                                                                          default=0.5, cast=float)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)
    TOKEN0_DECIMALS: int = field(init=False)
    TOKEN1_DECIMALS: int = field(init=False)

    def __post_init__(self):
        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).is_connected():
            raise ValueError(f"RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT}.")
        if self.RPC_ENDPOINT_FALLBACK != '':
            if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_FALLBACK)).is_connected():
                raise ValueError(
                    f"FALLBACK_RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT_FALLBACK}.")
        if self.RPC_ENDPOINT_MEV != '':
            if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_MEV)).is_connected():
                self.RPC_ENDPOINT_MEV = self.RPC_ENDPOINT
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        self.TOKEN0_ADDRESS = Web3.to_checksum_address(self.TOKEN0_ADDRESS)
        self.TOKEN1_ADDRESS = Web3.to_checksum_address(self.TOKEN1_ADDRESS)
        if not 0 <= self.MIN_PRICE_THRESHOLD <= 100:
            raise ValueError(
                f"MIN_PRICE_THRESHOLD must be between 0 and 100. MIN_PRICE_THRESHOLD inputted: {self.MIN_PRICE_THRESHOLD}.")
        if not 0 <= self.MAX_PRICE_THRESHOLD <= 100:
            raise ValueError(
                f"MAX_PRICE_THRESHOLD must be between 0 and 100. MAX_PRICE_THRESHOLD inputted: {self.MAX_PRICE_THRESHOLD}.")
        if self.PRICE_RANGE_MULTIPLICATOR_SEED <= 1:
            raise ValueError(
                f"PRICE_RANGE_MULTIPLICATOR_SEED must be greater than 1. PRICE_RANGE_MULTIPLICATOR_SEED inputted: {self.PRICE_RANGE_MULTIPLICATOR_SEED}.")
        if not 0 < self.PRICE_RANGE_MULTIPLICATOR_PERCENTUAL_DECREMENT < 100:
            raise ValueError(
                f"PRICE_RANGE_MULTIPLICATOR_PERCENTUAL_DECREMENT must be between 0 and 100. PRICE_RANGE_MULTIPLICATOR_PERCENTUAL_DECREMENT inputted: {self.PRICE_RANGE_MULTIPLICATOR_PERCENTUAL_DECREMENT}.")

        self.BOT_ADDRESS = Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).eth.account.from_key(
            self.PRIVATE_KEY).address

    def __repr__(self):
        return 'Environment variables'


@dataclass
class SystemData:
    nft_id: int
    bot_ETH_balance: float
    safe_token0_balance: float
    safe_token1_balance: float
    token0_balance: float
    token1_balance: float
    price_min: float
    price_max: float
    price: float
    min_price_threshold: float
    max_price_threshold: float

    def check_triggering_condition(self) -> (bool, float | None):
        if (self.price - self.price_min) / (self.price_max - self.price_min) < self.min_price_threshold:
            return (True, self.price- self.price_min)
        elif (self.price_max - self.price) / (self.price_max - self.price_min) < self.max_price_threshold:
            return (True, self.price_max - self.price)
        else:
            return (False, None)


def update_system_data(w3: Web3, nft_id: int, env: ENV) -> SystemData:
    nft_position = NFTPosition(w3, nft_id)
    balances = nft_position.get_balances()
    return SystemData(nft_id=nft_id,
                      bot_ETH_balance=w3.eth.get_balance(env.BOT_ADDRESS) / (10 ** 18),
                      safe_token0_balance=erc20_contract(w3, env.TOKEN0_ADDRESS).functions.balanceOf(
                          env.AVATAR_SAFE_ADDRESS).call() / (10 ** erc20_contract(w3,
                                                                                  env.TOKEN0_ADDRESS).functions.decimals().call()),
                      safe_token1_balance=erc20_contract(w3, env.TOKEN1_ADDRESS).functions.balanceOf(
                          env.AVATAR_SAFE_ADDRESS).call() / (10 ** erc20_contract(w3,
                                                                                  env.TOKEN1_ADDRESS).functions.decimals().call()),
                      token0_balance=balances[0],
                      token1_balance=balances[1],
                      price_min=nft_position.price_min,
                      price_max=nft_position.price_max,
                      price=nft_position.pool.price,
                      min_price_threshold=env.MIN_PRICE_THRESHOLD,
                      max_price_threshold=env.MAX_PRICE_THRESHOLD)


@dataclass
class Gauges:
    nft_id = Gauge('nft_id', 'NFT Id')
    bot_ETH_balance = Gauge('bot_ETH_balance', 'ETH balance of the bot')
    safe_token0_balance = Gauge('safe_token0_balance', 'Safe token0 balance')
    safe_token1_balance = Gauge('safe_token1_balance', 'Safe token1 balance')
    token0_balance = Gauge('token0_balance', 'Position token0 balance')
    token1_balance = Gauge('token1_balance', 'Position token1 balance')
    price_min = Gauge('price_min', 'Minimum range range price of token1 vs token0')
    price_max = Gauge('price_max', 'Maximum range range price of token1 vs token0')
    price = Gauge('price', 'Current price of token1 vs token0')
    min_threshold = Gauge('min_threshold', 'Minimum price threshold')
    max_threshold = Gauge('max_threshold', 'Maximum price threshold')

    def update(self, system_data: SystemData):
        self.nft_id.set(system_data.nft_id)
        self.bot_ETH_balance.set(system_data.bot_ETH_balance)
        self.safe_token0_balance.set(system_data.safe_token0_balance)
        self.safe_token1_balance.set(system_data.safe_token1_balance)
        self.token0_balance.set(system_data.token0_balance)
        self.token1_balance.set(system_data.token1_balance)
        self.price_min.set(system_data.price_min)
        self.price_max.set(system_data.price_max)
        self.price.set(system_data.price)
        self.min_threshold.set(system_data.min_price_threshold * (self.price_max - self.price_min) + self.price_min)
        self.max_threshold.set(self.price_max - system_data.max_price_threshold * (self.price_max - self.price_min))


@dataclass
class Flags:
    lack_of_gas_warning: threading.Event = field(default_factory=threading.Event)
    tx_executed: threading.Event = field(default_factory=threading.Event)


def get_nft_id_from_mint_tx(w3: Web3, tx_receipt: TxReceipt, recipient: Address) -> int | None:
    """Returns the NFT Id of the minted NFT in the transaction.

    Args:
        w3 (Web3): Web3 instance.
        tx_receipt (TxReceipt): Transaction receipt.

    Returns:
        int | None: NFT Id of the minted NFT in the transaction. Returns None if no NFT was minted to the recipient
            in that transaction.

    """
    event_log_decoder = EventLogDecoder(
        Web3().eth.contract(abi=ContractSpecs[Chain.get_blockchain_from_web3(w3)].PositionsNFT.abi))
    for element in tx_receipt.logs:
        if element['address'] == ContractSpecs[Chain.get_blockchain_from_web3(w3)].PositionsNFT.address:
            event = event_log_decoder.decode_log(element)
            if not event:
                continue
            if event.name == "Transfer" and event.values['to'] == recipient:
                return event.values['tokenId']
    return None


def get_all_active_nfts(w3: Web3, wallet: str) -> list:
    """Returns all NFT Ids owned by a wallet.

    Args:
        w3 (Web3): Web3 instance.
        wallet (str): Wallet address.

    Returns:
        a list where each element is the nft id that is owned by the wallet (open and closed nfts)
    """

    nftids = []

    nft_contract = ContractSpecs[Chain.get_blockchain_from_web3(w3)].PositionsNFT.contract(w3)
    nfts = nft_contract.functions.balanceOf(wallet).call()
    for nft_index in range(nfts):
        nft_id = nft_contract.functions.tokenOfOwnerByIndex(wallet, nft_index).call()
        nft_position = NFTPosition(w3=w3, nft_id=nft_id)
        if nft_position.liquidity > 0:
            nftids.append(nft_id)
    return nftids


@dataclass
class TransactionsManager:
    avatar: Address | ChecksumAddress | str
    roles_mod: Address | ChecksumAddress | str
    role: int
    private_key: str

    def disassemble_position(self, w3: Web3, nft_id: int) -> TxReceipt:
        decrease_liquidity_transactables = decrease_liquidity_nft(w3=w3,
                                                                  recipient=self.avatar,
                                                                  nft_id=nft_id,
                                                                  removed_liquidity_percentage=100,
                                                                  amount0_min_slippage=10,
                                                                  amount1_min_slippage=10,
                                                                  withdraw_eth=False)
        return roles.send(decrease_liquidity_transactables,
                          role=self.role,
                          private_key=self.private_key,
                          roles_mod_address=self.roles_mod,
                          web3=w3)

    def collect_all_fees(self, w3: Web3, nft_id: int) -> TxReceipt:
        collect_all_fees_transactables = collect_all_fees(w3=w3, avatar=self.avatar, nft_id=nft_id)
        return roles.send(collect_all_fees_transactables,
                          role=self.role,
                          private_key=self.private_key,
                          roles_mod_address=self.roles_mod,
                          web3=w3)


def log_initial_data(env: ENV, messenger: Messenger):
    title = "Bridge Keeper started"
    message = (f"  xDAI bridge address: {ContractSpecs[Chain.ETHEREUM].xDaiBridge.address}\n"
               f"  Bot address: {env.BOT_ADDRESS}\n"
               f"  Refill threshold: {env.REFILL_THRESHOLD} DAI\n"
               f"  Invest threshold: {env.INVEST_THRESHOLD} DAI\n"
               f"  Amount of interest to pay: {env.AMOUNT_OF_INTEREST_TO_PAY} DAI\n"
               f"  Minutes before claim epoch to pay interest: {env.MINUTES_BEFORE_CLAIM_EPOCH}\n"
               f"  ETH gas alerting threshold: {env.GAS_ETH_THRESHOLD} ETH\n")
    messenger.log_and_alert(LoggingLevel.Info, title, message)


def log_status_update(env: ENV, bridge_DAI_balance: int, bot_ETH_balance: int, next_claim_epoch: int,
                      min_cash_threshold: int):
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
