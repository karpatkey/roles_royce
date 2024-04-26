import logging
import sys
import time
from datetime import datetime
from decimal import Decimal

from defabipedia.types import Chain
from defabipedia.xdai_bridge import ContractSpecs
from prometheus_client import start_http_server as prometheus_start_http_server

from roles_royce.applications.bridge_keeper.core import (
    StaticData,
    invest_DAI,
    pay_interest,
    refill_bridge,
    update_dynamic_data,
)
from roles_royce.applications.bridge_keeper.env import ENV
from roles_royce.applications.bridge_keeper.logs import log_initial_data, log_status_update
from roles_royce.applications.bridge_keeper.prometheus import Gauges
from roles_royce.applications.bridge_keeper.utils import Flags
from roles_royce.applications.utils import web3_connection_check
from roles_royce.toolshed.alerting import LoggingLevel, Messenger, SlackMessenger, TelegramMessenger
from roles_royce.toolshed.alerting.utils import get_tx_receipt_message_with_transfers

# Importing the environment variables from the .env file
env = ENV()

# -----------------------------------------------------------------------------------------------------------------------

# Alert flags
flags = Flags()

# Messenger system
slack_messenger = SlackMessenger(webhook=env.SLACK_WEBHOOK_URL)
slack_messenger.start()
telegram_messenger = TelegramMessenger(bot_token=env.TELEGRAM_BOT_TOKEN, chat_id=env.TELEGRAM_CHAT_ID)
telegram_messenger.start()

# Configure logging settings
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create a logger instance
logger = logging.getLogger(__name__)
messenger = Messenger(slack_messenger, telegram_messenger)

# Prometheus metrics from prometheus_client import Info
prometheus_start_http_server(env.PROMETHEUS_PORT)
gauges = Gauges()

# Exception and RPC endpoint failure counters
exception_counter = 0
rpc_endpoint_failure_counter_eth = 0
rpc_endpoint_failure_counter_gnosis = 0

# -----------------------------------------------------------------------------------------------------------------------

static_data = StaticData(env)
log_initial_data(static_data, messenger)


# -----------------------------------------------------------------------------------------------------------------------


def bot_do(w3_eth, w3_gnosis, static_data: StaticData) -> int:
    global gauges
    global flags

    dynamic_data = update_dynamic_data(w3_eth, w3_gnosis, static_data)
    log_status_update(static_data=static_data, dynamic_data=dynamic_data, flags=flags)
    gauges.update(static_data=static_data, dynamic_data=dynamic_data, flags=flags)

    # -----------------------------------------------------------------------------------------------------------------------

    if dynamic_data.bot_ETH_balance < static_data.env.GAS_ETH_THRESHOLD * (10**18):
        title = "Lack of ETH for gas"
        message = f"  Im running outta ETH for gas! Only {dynamic_data.bot_ETH_balance / (10 ** 18):,5f}%.5f ETH left."
        messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=flags.lack_of_gas_warning.is_set())
        flags.lack_of_gas_warning.set()

    if dynamic_data.bot_ETH_balance >= static_data.env.GAS_ETH_THRESHOLD and flags.lack_of_gas_warning.is_set():
        flags.lack_of_gas_warning.clear()

    # -----------------------------------------------------------------------------------------------------------------------

    # see claimable in https://etherscan.io/address/0x166124b75c798cedf1b43655e9b5284ebd5203db#code#F7#L142
    if (
        dynamic_data.next_claim_epoch - 60 * static_data.env.MINUTES_BEFORE_CLAIM_EPOCH
        < time.time()
        < dynamic_data.next_claim_epoch
        and dynamic_data.min_interest_paid
        <= min(static_data.env.AMOUNT_OF_INTEREST_TO_PAY * (10**static_data.decimals_DAI), dynamic_data.claimable)
        and not flags.interest_payed.is_set()
    ):
        title = "Paying interest to interest receiver contract on Gnosis Chain..."
        message = f"  The next claim epoch {datetime.utcfromtimestamp(dynamic_data.next_claim_epoch)} UTC is in less than {static_data.env.MINUTES_BEFORE_CLAIM_EPOCH} minutes."
        logger.info(title + "\n" + message)
        tx_receipt = pay_interest(w3_eth, static_data, dynamic_data)
        flags.tx_executed.set()
        message, message_slack = get_tx_receipt_message_with_transfers(
            tx_receipt, ContractSpecs[Chain.ETHEREUM].xDaiBridge.address, w3_eth
        )
        messenger.log_and_alert(
            LoggingLevel.Info,
            f"Interest payed. Amount: {min(int(Decimal(static_data.env.AMOUNT_OF_INTEREST_TO_PAY) * Decimal(10 ** static_data.decimals_DAI)), dynamic_data.claimable) / (10 ** static_data.decimals_DAI):,.2f} DAI",
            message,
            slack_msg=message_slack,
        )
        flags.interest_payed.set()
    elif dynamic_data.next_claim_epoch - time.time() > 60 * 60 * 24:
        flags.interest_payed.clear()

    if flags.tx_executed.is_set():
        # Update data
        dynamic_data = update_dynamic_data(w3_eth, w3_gnosis, static_data)
        log_status_update(static_data=static_data, dynamic_data=dynamic_data, flags=flags)
        gauges.update(static_data=static_data, dynamic_data=dynamic_data, flags=flags)

    # -----------------------------------------------------------------------------------------------------------------------

    # see minCashThreshold in https://etherscan.io/address/0x166124b75c798cedf1b43655e9b5284ebd5203db#code#F1#L47
    if dynamic_data.bridge_DAI_balance < min(
        static_data.env.REFILL_THRESHOLD * (10**static_data.decimals_DAI), dynamic_data.min_cash_threshold
    ):
        title = "Refilling the bridge..."
        message = (
            f'  The bridge"s DAI balance {dynamic_data.bridge_DAI_balance / (10 ** static_data.decimals_DAI):,.2f}'
            f" dropped below the refill threshold {min(static_data.env.REFILL_THRESHOLD * (10 ** static_data.decimals_DAI), dynamic_data.min_cash_threshold):,.2f}."
        )
        logger.info(title + "\n" + message)
        tx_receipt = refill_bridge(w3_eth, static_data)
        flags.tx_executed.set()

        message, message_slack = get_tx_receipt_message_with_transfers(
            tx_receipt, ContractSpecs[Chain.ETHEREUM].xDaiBridge.address, w3_eth
        )
        messenger.log_and_alert(LoggingLevel.Info, f"Bridge refilled", message, slack_msg=message_slack)

    # see minCashThreshold in https://etherscan.io/address/0x166124b75c798cedf1b43655e9b5284ebd5203db#code#F7#L168
    elif (
        dynamic_data.bridge_DAI_balance
        > static_data.env.INVEST_THRESHOLD * (10**static_data.decimals_DAI) + dynamic_data.min_cash_threshold
    ):
        title = "Investing DAI..."
        message = (
            f'  The bridge"s DAI balance {dynamic_data.bridge_DAI_balance / (10 ** static_data.decimals_DAI):,.2f}'
            f" surpassed Invest threshold + Minimum cash threshold = "
            f"{static_data.env.INVEST_THRESHOLD + dynamic_data.min_cash_threshold / (10 ** static_data.decimals_DAI):,.2f}."
        )
        logger.info(title + "\n" + message)
        tx_receipt = invest_DAI(w3_eth, static_data)
        flags.tx_executed.set()
        message, message_slack = get_tx_receipt_message_with_transfers(
            tx_receipt, ContractSpecs[Chain.ETHEREUM].xDaiBridge.address, w3_eth
        )
        messenger.log_and_alert(LoggingLevel.Info, f"DAI invested", message, slack_msg=message_slack)

    if flags.tx_executed.is_set():
        # Update data
        dynamic_data = update_dynamic_data(w3_eth, w3_gnosis, static_data)
        log_status_update(static_data=static_data, dynamic_data=dynamic_data, flags=flags)
        gauges.update(static_data=static_data, dynamic_data=dynamic_data, flags=flags)

    # -----------------------------------------------------------------------------------------------------------------------

    flags.tx_executed.clear()

    return 0


# -----------------------------MAIN LOOP-----------------------------------------


while True:
    try:
        w3_eth, w3_eth_execution, rpc_endpoint_failure_counter_eth = web3_connection_check(
            static_data.env.RPC_ENDPOINT_ETHEREUM,
            messenger,
            rpc_endpoint_failure_counter_eth,
            static_data.env.RPC_ENDPOINT_ETHEREUM_FALLBACK,
        )

        w3_gnosis, w3_gnosis_execution, rpc_endpoint_failure_counter_gnosis = web3_connection_check(
            static_data.env.RPC_ENDPOINT_GNOSIS,
            messenger,
            rpc_endpoint_failure_counter_eth,
            static_data.env.RPC_ENDPOINT_GNOSIS,
        )

        if rpc_endpoint_failure_counter_eth != 0 or rpc_endpoint_failure_counter_gnosis != 0:
            continue

        try:
            exception_counter = bot_do(w3_eth, w3_gnosis, static_data)  # If successful, resets the counter
        except:
            time.sleep(5)
            exception_counter = bot_do(w3_eth, w3_gnosis, static_data)  # Second attempt

    except Exception as e:
        messenger.log_and_alert(LoggingLevel.Warning, title="Exception", message="  " + str(e.args[0]))
        exception_counter += 1
        if exception_counter == 5:
            messenger.log_and_alert(LoggingLevel.Error, title="Too many exceptions, exiting...", message="")
            time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
            sys.exit(1)
        time.sleep(30)  # Time to breathe
        continue
    time.sleep(static_data.env.COOLDOWN_MINUTES * 60)
