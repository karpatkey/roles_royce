from roles_royce.toolshed.anti_liquidation.spark.cdp import SparkCDPManager, CDPData
from web3 import Web3
from roles_royce.protocols.eth import spark
from roles_royce.constants import ETHAddr
from roles_royce.toolshed.protocol_utils.spark.utils import SparkUtils
from roles_royce.toolshed.alerting.utils import get_tx_receipt_message_with_transfers
from decimal import Decimal
from roles_royce import roles
from roles_royce.evm_utils import erc20_abi
from roles_royce.toolshed.alerting import SlackMessenger, TelegramMessenger, Messenger, LoggingLevel
from prometheus_client import start_http_server as prometheus_start_http_server
import logging
from utils import ENV, log_initial_data, send_status, SchedulerThread, Gauges
import time
from threading import Event
import sys
import datetime
import schedule

# Importing the environment variables from the .env file
ENV = ENV()

test_mode = ENV.TEST_MODE
if test_mode:
    from tests.utils import top_up_address

    w3 = Web3(Web3.HTTPProvider(f'http://localhost:{ENV.LOCAL_FORK_PORT}'))
    top_up_address(w3, ENV.BOT_ADDRESS, 1)
else:
    w3 = Web3(Web3.HTTPProvider(ENV.RPC_ENDPOINT))

# Alert flags
send_status_flag = Event()
lack_of_gas_warning_flag = Event()
alerting_health_factor_flag = Event()
threshold_health_factor_flag = Event()

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

# Prometheus metricsfrom prometheus_client import Info
prometheus_start_http_server(ENV.PROMETHEUS_PORT)
gauges = Gauges()

# FIXME: there's already an event for this
lack_of_gas_warning = False

# Exception and RPC endpoint failure counters
exception_counter = 0
rpc_endpoint_failure_counter = 0

log_initial_data(ENV, messenger)
gauges.alerting_health_factor.set(ENV.ALERTING_HEALTH_FACTOR)
gauges.health_factor_threshold.set(ENV.THRESHOLD_HEALTH_FACTOR)

# -----------------------------------------------------------------------------------------------------------------------

def bot_do():
    global w3
    global lack_of_gas_warning
    global gauges

    bot_ETH_balance = w3.eth.get_balance(ENV.BOT_ADDRESS)
    cdp_manager = SparkCDPManager(w3, ENV.AVATAR_SAFE_ADDRESS)
    cdp = cdp_manager.get_cdp_data()

    if send_status_flag.is_set():
        send_status_flag.clear()
        send_status(messenger, cdp, bot_ETH_balance / 1e18)

    gauges.bot_ETH_balance.set(bot_ETH_balance / 1e18)
    gauges.health_factor.set(float(cdp.health_factor))
    for element in cdp.balances_data:
        if element[CDPData.UnderlyingAddress] == ETHAddr.GNO:
            gauges.GNO_deposited.set(element[CDPData.InterestBearingBalance])
            gauges.GNO_price.set(element[CDPData.UnderlyingPriceUSD])
        if element[CDPData.UnderlyingAddress] == ETHAddr.DAI:
            gauges.DAI_borrowed.set(element[CDPData.VariableDebtBalance])
            gauges.DAI_price.set(element[CDPData.UnderlyingPriceUSD])

    # DAI_balances_data.info(cdp.balances_data[0])
    # GNO_balances_data.info(cdp.balances_data[1])

    logger.info(
        f"Target health factor: {ENV.TARGET_HEALTH_FACTOR}, Alerting health factor: {ENV.ALERTING_HEALTH_FACTOR}, "
        f"Health factor threshold: {ENV.THRESHOLD_HEALTH_FACTOR}, Bot ETH balance: {bot_ETH_balance / 1e18}")

    logger.info("SparK CDP data retrieved:\n"
                f"{cdp}")
    if ENV.THRESHOLD_HEALTH_FACTOR < cdp.health_factor <= ENV.ALERTING_HEALTH_FACTOR:
        title = "Health factor dropped below the alerting threshold"
        message = (f"  Current health factor: ({cdp.health_factor}).\n"
                   f"  Alerting health factor: ({ENV.ALERTING_HEALTH_FACTOR})\n."
                   f"{cdp}")
        messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=alerting_health_factor_flag.is_set())
        alerting_health_factor_flag.set()

    elif cdp.health_factor <= ENV.THRESHOLD_HEALTH_FACTOR:
        title = "Health factor dropped below the critical threshold"
        message = (f"  Current health factor: ({cdp.health_factor}).\n"
                   f"  Health factor threshold: ({ENV.ALERTING_HEALTH_FACTOR}).\n"
                   f"{cdp}")
        messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=threshold_health_factor_flag.is_set())

        logger.info('Attempting to repay debt...')
        amount_of_DAI_to_repay = cdp_manager.get_delta_of_token_to_repay(spark_cdp=cdp,
                                                                         target_health_factor=ENV.TARGET_HEALTH_FACTOR,
                                                                         token_in_address=ETHAddr.DAI,
                                                                         rate_model=spark.RateModel.VARIABLE,
                                                                         tolerance=ENV.TOLERANCE)
        chi = SparkUtils.get_chi(w3)
        amount_of_sDAI_to_redeem = int(Decimal(amount_of_DAI_to_repay) / (Decimal(chi) / Decimal(1e27)))

        sDAI_contract = w3.eth.contract(address=ETHAddr.sDAI, abi=erc20_abi)
        sDAI_balance = sDAI_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()

        if sDAI_balance == 0:
            title = 'No sDAI to redeem'
            message = (f'  Current health factor: {cdp.health_factor}.\n'
                       f'  Target health factor: {ENV.TARGET_HEALTH_FACTOR}.\n'
                       f'  Amount of sDAI needed to redeem: {amount_of_sDAI_to_redeem / 1e18:.5f}.\n'
                       f'  Current sDAI balance: {sDAI_balance / 1e18:.5f}.')
            messenger.log_and_alert(LoggingLevel.Warning, title, message)
            return None

        if sDAI_balance < amount_of_sDAI_to_redeem:
            title = 'Not enough sDAI to redeem'
            message = (f'  Current health factor: {cdp.health_factor}.\n'
                       f'  Target health factor: {ENV.TARGET_HEALTH_FACTOR}.\n'
                       f'  Amount of DAI to repay: {amount_of_DAI_to_repay / 1e18:.5f}.\n'
                       f'  Amount of sDAI needed to redeem: {amount_of_sDAI_to_redeem / 1e18:.5f}.\n'
                       f'  Current sDAI balance: {sDAI_balance / 1e18:.5f}.')
            messenger.log_and_alert(LoggingLevel.Warning, title, message)

            amount_of_sDAI_to_redeem = sDAI_balance

        logger.info(f'Redeeming {amount_of_sDAI_to_redeem} sDAI for DAI...')
        tx_receipt_sDAI_redeemed = roles.send(
            [spark.RedeemSDAIforDAI(amount=amount_of_sDAI_to_redeem, avatar=ENV.AVATAR_SAFE_ADDRESS)],
            role=ENV.ROLE, private_key=ENV.PRIVATE_KEY, roles_mod_address=ENV.ROLES_MOD_ADDRESS, web3=w3)

        message, message_slack = get_tx_receipt_message_with_transfers(tx_receipt_sDAI_redeemed,
                                                                       ENV.AVATAR_SAFE_ADDRESS, w3)
        messenger.log_and_alert(LoggingLevel.Info, 'sDAI redeemed for DAI', message, slack_msg=message_slack)

        DAI_contract = w3.eth.contract(address=ETHAddr.DAI, abi=erc20_abi)
        DAI_balance = DAI_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
        if DAI_balance < amount_of_DAI_to_repay:
            title = 'Not enough DAI to repay'
            message = (f'  Current health factor: {cdp.health_factor}.\n'
                       f'  Target health factor: {ENV.TARGET_HEALTH_FACTOR}.\n'
                       f'  Amount of DAI to repay: {amount_of_DAI_to_repay / 1e18:.5f}.\n'
                       f'  Current DAI balance: {DAI_balance / 1e18:.5f}.')
            messenger.log_and_alert(LoggingLevel.Warning, title, message)

            amount_of_DAI_to_repay = DAI_balance

        tx_receipt_debt_repayed = cdp_manager.repay_single_token_debt(spark_cdp=cdp, token_in_address=ETHAddr.DAI,
                                                                      token_in_amount=amount_of_DAI_to_repay,
                                                                      rate_model=spark.RateModel.VARIABLE,
                                                                      private_key=ENV.PRIVATE_KEY,
                                                                      role=ENV.ROLE,
                                                                      roles_mod_address=ENV.ROLES_MOD_ADDRESS)

        message, message_slack = get_tx_receipt_message_with_transfers(tx_receipt_debt_repayed, ENV.AVATAR_SAFE_ADDRESS,
                                                                       w3)
        cdp = cdp_manager.get_cdp_data()
        extra_message = (f'New health factor: {cdp.health_factor}.\n'
                         f'{cdp}')
        messenger.log_and_alert(LoggingLevel.Info, 'DAI debt repayed', message + '\n' + extra_message,
                                slack_msg=message_slack + '\n' + extra_message)

        gauges.bot_ETH_balance.set(bot_ETH_balance / 1e18)
        gauges.health_factor.set(float(cdp.health_factor))

        if bot_ETH_balance < 0.1:
            title = 'Lack of ETH for gas'
            message = 'Im running outta ETH for gas! Only %.5f ETH left.' % (bot_ETH_balance / (10 ** 18))
            messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=lack_of_gas_warning)
            lack_of_gas_warning = True

        if bot_ETH_balance >= 0.1 and lack_of_gas_warning_flag:
            lack_of_gas_warning = False


# -----------------------------MAIN LOOP-----------------------------------------

# Status notification scheduling
if ENV.STATUS_NOTIFICATION_HOUR != '':
    # FIXME: make sure the scheduling job is set at UTC time
    status_run_time = datetime.time(hour=ENV.STATUS_NOTIFICATION_HOUR, minute=0, second=0)
    schedule.every().day.at(str(status_run_time)).do(lambda: send_status_flag.set())
    scheduler_thread = SchedulerThread()
    scheduler_thread.start()

while True:

    try:
        if not test_mode:
            w3 = Web3(Web3.HTTPProvider(ENV.RPC_ENDPOINT))
            if not w3.is_connected(show_traceback=True):
                time.sleep(5)
                if not w3.is_connected(show_traceback=True):
                    if ENV.FALLBACK_RPC_ENDPOINT != '':
                        messenger.log_and_alert(LoggingLevel.Warning, title='Warning',
                                                message=f'  RPC endpoint {ENV.RPC_ENDPOINT} is not working.')
                        w3 = Web3(Web3.HTTPProvider(ENV.FALLBACK_RPC_ENDPOINT))
                        if not w3.is_connected(show_traceback=True):
                            time.sleep(5)
                            if not w3.is_connected(show_traceback=True):
                                messenger.log_and_alert(LoggingLevel.Error, title='Error',
                                                        message=f'  RPC endpoint {ENV.RPC_ENDPOINT} and fallback RPC '
                                                                f'endpoint {ENV.FALLBACK_RPC_ENDPOINT} are both not '
                                                                f'working.')
                                rpc_endpoint_failure_counter += 1
                                continue
                    else:
                        messenger.log_and_alert(LoggingLevel.Error, title='Error',
                                                message=f'  RPC endpoint {ENV.RPC_ENDPOINT} is not working.')
                        rpc_endpoint_failure_counter += 1
                        continue

            if rpc_endpoint_failure_counter == 5:  # TODO: this can be added as an environment variable
                messenger.log_and_alert(LoggingLevel.Error, title='Too many RPC endpoint failures, exiting...',
                                        message='')
                time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
                sys.exit(1)

        bot_do()

    except Exception as e:
        messenger.log_and_alert(LoggingLevel.Error, title='Exception', message='  ' + str(e.args[0]))
        exception_counter += 1
        if exception_counter == 5:  # TODO: this can be added as an environment variable
            messenger.log_and_alert(LoggingLevel.Error, title='Too many exceptions, exiting...', message='')
            time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
            sys.exit(1)
    time.sleep(ENV.COOLDOWN_MINUTES * 60)
