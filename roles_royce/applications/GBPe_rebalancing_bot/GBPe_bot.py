import logging
import sys
import time

from core import DynamicDataManager, StaticData, Swapper
from prometheus_client import start_http_server as prometheus_start_http_server

from roles_royce.applications.GBPe_rebalancing_bot.env import ENV
from roles_royce.applications.GBPe_rebalancing_bot.logs import log_initial_data, log_status_update
from roles_royce.applications.GBPe_rebalancing_bot.prometheus import Gauges
from roles_royce.applications.GBPe_rebalancing_bot.utils import Flags
from roles_royce.applications.utils import web3_connection_check
from roles_royce.toolshed.alerting import LoggingLevel, Messenger, SlackMessenger, TelegramMessenger
from roles_royce.toolshed.alerting.utils import get_tx_receipt_message_with_transfers

# Importing the environment variables from the .env file
env = ENV()

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
static_data = StaticData(env=env)
log_initial_data(static_data, messenger)

decimals_x3CRV = static_data.decimals_x3CRV
decimals_GBPe = static_data.decimals_GBPe
amount_x3CRV = env.AMOUNT
amount_GBPe = env.AMOUNT


def bot_do(w3_eth, w3_gnosis, static_data: StaticData) -> int:
    global amount_x3CRV
    global amount_GBPe
    global gauges
    global flags
    # -----------------------------------------------------------------------------------------------------------------------
    dynamic_data_manager = DynamicDataManager(w3_gnosis, w3_eth, static_data)

    dynamic_data = dynamic_data_manager.get_data(amount_x3CRV, amount_GBPe)

    # -----------------------------------------------------------------------------------------------------------------------

    balance_x3CRV = dynamic_data.x3CRV_balance
    if 10 * amount_x3CRV * (10**decimals_x3CRV) < balance_x3CRV and amount_x3CRV < env.AMOUNT:
        while 10 * amount_x3CRV * (10**decimals_x3CRV) < balance_x3CRV and 10 * amount_x3CRV <= env.AMOUNT:
            amount_x3CRV = amount_x3CRV * 10
    elif amount_x3CRV * (10**decimals_x3CRV) < balance_x3CRV < 10 * amount_x3CRV * (10**decimals_x3CRV):
        pass
    elif balance_x3CRV < amount_x3CRV * (10**decimals_x3CRV):
        if flags.lack_of_x3CRV.is_set() is False:
            title = "Lack of x3CRV in the avatar safe"
            message = f"  Im running outta x3CRV! Only {balance_x3CRV / (10 ** decimals_x3CRV):,.5f} left."
            messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=flags.lack_of_x3CRV.is_set())

        while balance_x3CRV < amount_x3CRV * (10**decimals_x3CRV) and amount_x3CRV > 1:
            amount_x3CRV = amount_x3CRV / 10
        if amount_x3CRV <= 1:
            flags.lack_of_x3CRV.set()

    # -----------------------------------------------------------------------------------------------------------------------

    balance_GBPe = dynamic_data.GBPe_balance
    if 10 * amount_GBPe * (10**decimals_GBPe) < balance_GBPe and amount_GBPe < env.AMOUNT:
        while 10 * amount_GBPe * (10**decimals_GBPe) < balance_GBPe and 10 * amount_GBPe <= env.AMOUNT:
            amount_GBPe = amount_GBPe * 10
    elif amount_GBPe * (10**decimals_GBPe) < balance_GBPe < 10 * amount_GBPe * (10**decimals_GBPe):
        pass
    elif balance_GBPe < amount_GBPe * (10**decimals_GBPe):
        if flags.lack_of_GBPe.is_set() is False:
            title = "Lack of GBPe in the avatar safe"
            message = f"  Im running outta GBPe! Only {balance_GBPe / (10 ** decimals_GBPe):,.5f} left."
            messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=flags.lack_of_GBPe.is_set())
        while balance_GBPe < amount_GBPe * (10**decimals_GBPe) and amount_GBPe > 1:
            amount_GBPe = amount_GBPe / 10
        if amount_GBPe <= 1:
            flags.lack_of_GBPe.set()

    # -----------------------------------------------------------------------------------------------------------------------

    bot_xDAI_balance = dynamic_data.bot_xDAI_balance

    if bot_xDAI_balance < 0.1:
        title = "Lack of xDAI for gas"
        message = f"  Im running outta xDAI for gas! Only {bot_xDAI_balance / (10 ** 18):,.5f} xDAI left."
        messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=flags.lack_of_gas_warning.is_set())
        flags.lack_of_gas_warning.set()

    if bot_xDAI_balance >= 0.1 and flags.lack_of_gas_warning.is_set():
        flags.lack_of_gas_warning.clear()

    # -----------------------------------------------------------------------------------------------------------------------

    flags.tx_executed.clear()

    swapper = Swapper(
        w3=w3_gnosis,
        private_keys=env.PRIVATE_KEY,
        role=env.ROLE,
        roles_mod_address=env.ROLES_MOD_ADDRESS,
        avatar_safe_address=env.AVATAR_SAFE_ADDRESS,
        max_slippage=env.MAX_SLIPPAGE,
    )

    dynamic_data = dynamic_data_manager.get_data(amount_x3CRV, amount_GBPe)
    gauges.update(static_data, dynamic_data)
    log_status_update(static_data=static_data, dynamic_data=dynamic_data)

    # -----------------------------------------------------------------------------------------------------------------------

    if dynamic_data.drift_GBPe_to_x3CRV > env.DRIFT_THRESHOLD and balance_GBPe >= amount_GBPe * (10**decimals_GBPe):
        logger.info(f"Swapping {amount_GBPe:,.3f} GBPe for x3CRV...")
        tx_receipt_GBPe_to_x3CRV = swapper.swap_GBPe_for_x3CRV(static_data, dynamic_data)

        message, message_slack = get_tx_receipt_message_with_transfers(
            tx_receipt_GBPe_to_x3CRV, env.AVATAR_SAFE_ADDRESS, w3_gnosis
        )
        messenger.log_and_alert(
            LoggingLevel.Info, f"{amount_GBPe:,.3f} GBPe swapped for x3CRV", message, slack_msg=message_slack
        )

        flags.tx_executed.set()

    elif dynamic_data.drift_x3CRV_to_GBPe > env.DRIFT_THRESHOLD and balance_x3CRV >= amount_x3CRV * (
        10**decimals_x3CRV
    ):
        logger.info(f"Swapping {amount_x3CRV:,.3f} x3CRV for GBPe...")
        tx_receipt_x3CRV_to_GBPe = swapper.swap_x3CRV_for_GBPe(static_data, dynamic_data)

        message, message_slack = get_tx_receipt_message_with_transfers(
            tx_receipt_x3CRV_to_GBPe, env.AVATAR_SAFE_ADDRESS, w3_gnosis
        )
        messenger.log_and_alert(
            LoggingLevel.Info, f"{amount_x3CRV:,.3f} x3CRV swapped for GBPe", message, slack_msg=message_slack
        )

        flags.tx_executed.set()

    if flags.tx_executed.is_set():
        dynamic_data = dynamic_data_manager.get_data(amount_x3CRV, amount_GBPe)
        log_status_update(static_data=static_data, dynamic_data=dynamic_data)
        gauges.update(static_data=static_data, dynamic_data=dynamic_data)

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
            static_data.env.RPC_ENDPOINT_GNOSIS_FALLBACK,
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
    time.sleep(env.COOLDOWN_MINUTES * 60)
