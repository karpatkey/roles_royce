from web3 import Web3
from roles_royce.toolshed.alerting import SlackMessenger, TelegramMessenger, Messenger, LoggingLevel, \
    web3_connection_check
from roles_royce.toolshed.alerting.utils import get_tx_receipt_message_with_transfers
from prometheus_client import start_http_server as prometheus_start_http_server
import logging
from utils import ENV, Gauges, refill_bridge, invest_DAI, pay_interest, decimals_DAI, Flags, \
    log_initial_data, log_status_update
import time
import sys
from datetime import datetime
from defabipedia.xdai_bridge import ContractSpecs
from defabipedia.tokens import EthereumContractSpecs as Tokens
from defabipedia.types import Chain
from decimal import Decimal

# Importing the environment variables from the .env file
ENV = ENV()

# -----------------------------------------------------------------------------------------------------------------------

test_mode = ENV.TEST_MODE
if test_mode:
    from tests.utils import top_up_address

    w3_eth = Web3(Web3.HTTPProvider(f'http://localhost:{ENV.LOCAL_FORK_PORT_ETHEREUM}'))
    top_up_address(w3_eth, ENV.BOT_ADDRESS, 1)
    w3_gnosis = Web3(Web3.HTTPProvider(f'http://localhost:{ENV.LOCAL_FORK_PORT_GNOSIS}'))
    top_up_address(w3_gnosis, ENV.BOT_ADDRESS, 1)

# -----------------------------------------------------------------------------------------------------------------------

# Alert flags
flags = Flags()

# Messenger system
slack_messenger = SlackMessenger(webhook=ENV.SLACK_WEBHOOK_URL)
slack_messenger.start()
telegram_messenger = TelegramMessenger(bot_token=ENV.TELEGRAM_BOT_TOKEN, chat_id=ENV.TELEGRAM_CHAT_ID)
telegram_messenger.start()

# Configure logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger instance
logger = logging.getLogger(__name__)
messenger = Messenger(slack_messenger, telegram_messenger)

# Prometheus metrics from prometheus_client import Info
prometheus_start_http_server(ENV.PROMETHEUS_PORT)
gauges = Gauges()

# Exception and RPC endpoint failure counters
exception_counter = 0
rpc_endpoint_failure_counter_eth = 0
rpc_endpoint_failure_counter_gnosis = 0

# -----------------------------------------------------------------------------------------------------------------------

log_initial_data(ENV, messenger)


# -----------------------------------------------------------------------------------------------------------------------


def bot_do(w3_eth, w3_gnosis) -> int:
    global gauges
    global flags

    # Contracts
    DAI_contract = Tokens.DAI.contract(w3_eth)
    bridge_contract = ContractSpecs[Chain.ETHEREUM].xDaiBridge.contract(w3_eth)
    interest_receiver_contract = ContractSpecs[Chain.GNOSIS].BridgeInterestReceiver.contract(w3_gnosis)

    # Data
    bridge_DAI_balance = DAI_contract.functions.balanceOf(ContractSpecs[Chain.ETHEREUM].xDaiBridge.address).call()
    min_cash_threshold = bridge_contract.functions.minCashThreshold(Tokens.DAI.address).call()
    next_claim_epoch = interest_receiver_contract.functions.nextClaimEpoch().call()
    bot_ETH_balance = w3_eth.eth.get_balance(ENV.BOT_ADDRESS)

    log_status_update(ENV, bridge_DAI_balance, bot_ETH_balance, next_claim_epoch, min_cash_threshold)
    gauges.update(bridge_DAI_balance, bot_ETH_balance, next_claim_epoch, min_cash_threshold)

    # -----------------------------------------------------------------------------------------------------------------------

    if bot_ETH_balance < ENV.GAS_ETH_THRESHOLD * (10 ** 18):
        title = 'Lack of ETH for gas'
        message = f'  Im running outta ETH for gas! Only {bot_ETH_balance / (10 ** 18):,5f}%.5f ETH left.'
        messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=flags.lack_of_gas_warning.is_set())
        flags.lack_of_gas_warning.set()

    if bot_ETH_balance >= ENV.GAS_ETH_THRESHOLD and flags.lack_of_gas_warning.is_set():
        flags.lack_of_gas_warning.clear()

    # -----------------------------------------------------------------------------------------------------------------------

    # see minCashThreshold in https://etherscan.io/address/0x166124b75c798cedf1b43655e9b5284ebd5203db#code#F1#L47
    if bridge_DAI_balance < ENV.REFILL_THRESHOLD * (10 ** decimals_DAI) and bridge_DAI_balance < min_cash_threshold:
        title = 'Refilling the bridge...'
        message = f'  The bridge"s DAI balance {bridge_DAI_balance / (10 ** decimals_DAI):.2f} dropped below the refill threshold {ENV.REFILL_THRESHOLD}.'
        logger.info(title + '\n' + message)
        tx_receipt = refill_bridge(w3_eth, ENV)
        flags.tx_executed.set()

        message, message_slack = get_tx_receipt_message_with_transfers(tx_receipt, ContractSpecs[
            Chain.ETHEREUM].xDaiBridge.address, w3_eth)
        messenger.log_and_alert(LoggingLevel.Info, f'Bridge refilled', message,
                                slack_msg=message_slack)

    # see minCashThreshold in https://etherscan.io/address/0x166124b75c798cedf1b43655e9b5284ebd5203db#code#F7#L168
    elif bridge_DAI_balance > ENV.INVEST_THRESHOLD * (10 ** decimals_DAI) and bridge_DAI_balance > min_cash_threshold:
        title = 'Investing DAI...'
        message = f'  The bridge"s DAI balance {bridge_DAI_balance / (10 ** decimals_DAI):.2f} surpassed the invest threshold {ENV.INVEST_THRESHOLD}.'
        logger.info(title + '\n' + message)
        tx_receipt = invest_DAI(w3_eth, ENV)
        flags.tx_executed.set()
        message, message_slack = get_tx_receipt_message_with_transfers(tx_receipt, ContractSpecs[
            Chain.ETHEREUM].xDaiBridge.address, w3_eth)
        messenger.log_and_alert(LoggingLevel.Info, f'DAI invested', message,
                                slack_msg=message_slack)

    # -----------------------------------------------------------------------------------------------------------------------

    if next_claim_epoch - 60 * ENV.MINUTES_BEFORE_CLAIM_EPOCH < time.time() < next_claim_epoch and not flags.interest_payed.is_set():
        title = 'Paying interest to interest receiver contract on Gnosis Chain...'
        message = f'  The next claim epoch {datetime.utcfromtimestamp(next_claim_epoch)} is in less than {ENV.MINUTES_BEFORE_CLAIM_EPOCH} minutes.'
        logger.info(title + '\n' + message)
        tx_receipt = pay_interest(w3_eth, ENV,
                                  int(Decimal(ENV.AMOUNT_OF_INTEREST_TO_PAY) * Decimal(10 ** decimals_DAI)))
        flags.tx_executed.set()
        message, message_slack = get_tx_receipt_message_with_transfers(tx_receipt, ContractSpecs[
            Chain.ETHEREUM].xDaiBridge.address, w3_eth)
        messenger.log_and_alert(LoggingLevel.Info, f'Interest payed', message,
                                slack_msg=message_slack)
        flags.interest_payed.set()
    elif time.time() > next_claim_epoch:
        flags.interest_payed.clear()

    if flags.tx_executed.is_set():
        # Update data
        bridge_DAI_balance = DAI_contract.functions.balanceOf(ContractSpecs[Chain.ETHEREUM].xDaiBridge.address).call()
        min_cash_threshold = bridge_contract.functions.minCashThreshold(Tokens.DAI.address).call()
        next_claim_epoch = interest_receiver_contract.functions.nextClaimEpoch().call()
        bot_ETH_balance = w3_eth.eth.get_balance(ENV.BOT_ADDRESS)

        log_status_update(ENV, bridge_DAI_balance, bot_ETH_balance, next_claim_epoch, min_cash_threshold)
        gauges.update(bridge_DAI_balance, bot_ETH_balance, next_claim_epoch, min_cash_threshold)

        flags.tx_executed.clear()

    return 0


# -----------------------------MAIN LOOP-----------------------------------------


while True:

    try:
        if not test_mode:
            w3_eth, rpc_endpoint_failure_counter_eth = web3_connection_check(ENV.RPC_ENDPOINT_ETHEREUM, messenger,
                                                                             rpc_endpoint_failure_counter_eth,
                                                                             ENV.RPC_ENDPOINT_ETHEREUM_FALLBACK)
            w3_gnosis, rpc_endpoint_failure_counter_gnosis = web3_connection_check(ENV.RPC_ENDPOINT_GNOSIS, messenger,
                                                                                   rpc_endpoint_failure_counter_gnosis,
                                                                                   ENV.RPC_ENDPOINT_GNOSIS_FALLBACK)
            if rpc_endpoint_failure_counter_eth != 0 or rpc_endpoint_failure_counter_gnosis != 0:
                continue
        else:
            w3_eth = Web3(Web3.HTTPProvider(f'http://localhost:{ENV.LOCAL_FORK_PORT_ETHEREUM}'))
            w3_gnosis = Web3(Web3.HTTPProvider(f'http://localhost:{ENV.LOCAL_FORK_PORT_GNOSIS}'))

        try:
            exception_counter = bot_do(w3_eth, w3_gnosis) # If successful, resets the counter
        except:
            time.sleep(5)
            exception_counter = bot_do(w3_eth, w3_gnosis)  # Second attempt

    except Exception as e:
        messenger.log_and_alert(LoggingLevel.Error, title='Exception', message='  ' + str(e.args[0]))
        exception_counter += 1
        if exception_counter == 5:  # TODO: this can be added as an environment variable
            messenger.log_and_alert(LoggingLevel.Error, title='Too many exceptions, exiting...', message='')
            time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
            sys.exit(1)
        time.sleep(30)  # Time to breathe
        continue
    time.sleep(ENV.COOLDOWN_MINUTES * 60)
