from web3 import Web3
from defabipedia.types import Chain
from defabipedia.tokens import erc20_contract
from roles_royce.toolshed.alerting.utils import get_tx_receipt_message_with_transfers
from roles_royce.toolshed.alerting import SlackMessenger, TelegramMessenger, Messenger, LoggingLevel, web3_connection_check
from prometheus_client import start_http_server as prometheus_start_http_server
import logging
from utils import ENV, log_initial_data, Gauges
from swaps import SwapsDataManager, Swapper, AddressesAndAbis, decimalsWXDAI, decimalsEURe
import time
import sys
from decimal import Decimal

# Importing the environment variables from the .env file
ENV = ENV()

test_mode = ENV.TEST_MODE
if test_mode:
    from tests.utils import top_up_address
    w3 = Web3(Web3.HTTPProvider(f'http://localhost:{ENV.LOCAL_FORK_PORT}'))
    top_up_address(w3, ENV.BOT_ADDRESS, 1)


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
rpc_endpoint_failure_counter = 0

log_initial_data(ENV, messenger)

# -----------------------------------------------------------------------------------------------------------------------

amount_WXDAI = ENV.AMOUNT
amount_EURe = ENV.AMOUNT

gauges.drift_threshold.set(ENV.DRIFT_THRESHOLD)

lack_of_gas_warning_flag = False  # flag to stop alerting when the bot's xDAI balance is below 0.1
lack_of_WXDAI_flag = False  # flag to stop alerting when the WXDAI balance is below 1
lack_of_EURe_flag = False  # flag to stop alerting when the EURe balance is below 1


def bot_do(w3):
    global amount_WXDAI
    global amount_EURe
    global gauges
    global lack_of_gas_warning_flag
    global lack_of_WXDAI_flag
    global lack_of_EURe_flag

    # -----------------------------------------------------------------------------------------------------------------------

    WXDAI_contract = erc20_contract(w3, AddressesAndAbis[Chain.GNOSIS].WXDAI.address)
    balance_WXDAI = WXDAI_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
    if 10 * amount_WXDAI * (10 ** decimalsWXDAI) < balance_WXDAI and amount_WXDAI < ENV.AMOUNT:
        while 10 * amount_WXDAI * (10 ** decimalsWXDAI) < balance_WXDAI and 10 * amount_WXDAI <= ENV.AMOUNT:
            amount_WXDAI = amount_WXDAI * 10
    elif amount_WXDAI * (10 ** decimalsWXDAI) < balance_WXDAI < 10 * amount_WXDAI * (10 ** decimalsWXDAI):
        pass
    elif balance_WXDAI < amount_WXDAI * (10 ** decimalsWXDAI):
        if lack_of_WXDAI_flag is False:
            title = "Lack of WXDAI in the avatar safe"
            message = f"  Im running outta WXDAI! Only {balance_WXDAI / (10 ** decimalsWXDAI):.5f} left."
            messenger.log_and_alert(LoggingLevel.Warning, title, message,
                                    alert_flag=lack_of_WXDAI_flag)

        while balance_WXDAI < amount_WXDAI * (10 ** decimalsWXDAI) and amount_WXDAI > 1:
            amount_WXDAI = amount_WXDAI / 10
        if amount_WXDAI <= 1:
            lack_of_WXDAI_flag = True

    # -----------------------------------------------------------------------------------------------------------------------

    EURe_contract = w3.eth.contract(address=AddressesAndAbis[Chain.GNOSIS].EURe.address,
                                    abi=AddressesAndAbis[Chain.GNOSIS].ERC20.abi)
    balance_EURe = EURe_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
    if 10 * amount_EURe * (10 ** decimalsEURe) < balance_EURe and amount_EURe < ENV.AMOUNT:
        while 10 * amount_EURe * (10 ** decimalsEURe) < balance_EURe and 10 * amount_EURe <= ENV.AMOUNT:
            amount_EURe = amount_EURe * 10
    elif amount_EURe * (10 ** decimalsEURe) < balance_EURe < 10 * amount_EURe * (10 ** decimalsEURe):
        pass
    elif balance_EURe < amount_EURe * (10 ** decimalsEURe):
        if lack_of_EURe_flag is False:
            title = "Lack of EURe in the avatar safe"
            message = f"  Im running outta EURe! Only {balance_EURe / (10 ** decimalsEURe):.5f} left."
            messenger.log_and_alert(LoggingLevel.Warning, title, message,
                                    alert_flag=lack_of_EURe_flag)
        while balance_EURe < amount_EURe * (10 ** decimalsEURe) and amount_EURe > 1:
            amount_EURe = amount_EURe / 10
        if amount_EURe <= 1:
            lack_of_EURe_flag = True

    # -----------------------------------------------------------------------------------------------------------------------

    bot_xDAI_balance = w3.eth.get_balance(ENV.BOT_ADDRESS)

    if bot_xDAI_balance < 0.1:
        title = 'Lack of xDAI for gas'
        message = f'  Im running outta xDAI for gas! Only {bot_xDAI_balance / (10 ** 18):,5f}%.5f xDAI left.'
        messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=lack_of_gas_warning_flag)
        lack_of_gas_warning_flag = True

    if bot_xDAI_balance >= 0.1 and lack_of_gas_warning_flag:
        lack_of_gas_warning_flag = False

    # -----------------------------------------------------------------------------------------------------------------------

    tx_executed_flag = False

    swapper = Swapper(w3=w3, private_keys=ENV.PRIVATE_KEY, role=ENV.ROLE, roles_mod_address=ENV.ROLES_MOD_ADDRESS,
                      avatar_safe_address=ENV.AVATAR_SAFE_ADDRESS, max_slippage=ENV.MAX_SLIPPAGE)

    swaps_data_manager = SwapsDataManager(w3, ENV.FIXER_API_ACCESS_KEY)
    data = swaps_data_manager.get_data(amount_WXDAI, amount_EURe)

    drift_EURe_to_WXDAI = data.drift_EURe_to_WXDAI
    drift_WXDAI_to_EURe = data.drift_WXDAI_to_EURe

    logger.info(
        f'Status update:\n'
        f'  EUR to USD oracle: {data.amount_EURe:.3f} EURe ---> {data.amount_EURe * data.EUR_price:.3f} USD.\n'
        f'  EURe to WXDAI Curve: {data.amount_EURe:.3f} EURe ---> {data.EURe_to_WXDAI:.3f} WXDAI.\n'
        f'  EURe to WXDAI drift: {drift_EURe_to_WXDAI:.5f}.\n'
        f'\n'
        f'  USD to EUR oracle: {data.amount_WXDAI:.3f} USD ---> {data.amount_WXDAI / data.EUR_price:.3f} EURe.\n'
        f'  WXDAI to EURe Curve: {data.amount_WXDAI:.3f} WXDAI ---> {data.WXDAI_to_EURe:.3f} EURe.\n'
        f'  WXDAI to EURe drift: {drift_WXDAI_to_EURe:.5f}.\n'
        f'\n'
        f'  Drift threshold: {ENV.DRIFT_THRESHOLD:.5f}.\n'
        f'\n'
        f'  Avatar safe"s WXDAI balance: {balance_WXDAI / (10 ** decimalsWXDAI):.5f}.\n'
        f'  Avatar safe"s EURe balance: {balance_EURe / (10 ** decimalsEURe):.5f}.\n'
        f'  Bot"s xDAI balance: {bot_xDAI_balance / (10 ** 18):.5f}.\n'
    )

    # -----------------------------------------------------------------------------------------------------------------------

    gauges.update(EUR_price_feed=data.EUR_price, EURe_price_curve=data.EURe_to_WXDAI / data.amount_EURe,
                  bot_xDAI_balance=bot_xDAI_balance, safe_WXDAI_balance=balance_WXDAI,
                  safe_EURe_balance=balance_EURe, amount_WXDAI=amount_WXDAI, amount_EURe=amount_EURe,
                  drift_threshold=ENV.DRIFT_THRESHOLD, drift_EURe_to_WXDAI=drift_EURe_to_WXDAI,
                  drift_WXDAI_to_EURe=drift_WXDAI_to_EURe)

    # -----------------------------------------------------------------------------------------------------------------------

    if drift_EURe_to_WXDAI > ENV.DRIFT_THRESHOLD and balance_EURe >= amount_EURe * (10 ** decimalsEURe):
        logger.info(f'Swapping {amount_EURe:.3f} EURe for WDAI...')
        tx_receipt_EURe_to_WXDAI = swapper.swap_EURe_for_WXDAI(data)

        message, message_slack = get_tx_receipt_message_with_transfers(tx_receipt_EURe_to_WXDAI,
                                                                       ENV.AVATAR_SAFE_ADDRESS, w3)
        messenger.log_and_alert(LoggingLevel.Info, f'{amount_EURe:.3f} EURe swapped for WXDAI', message,
                                slack_msg=message_slack)

        tx_executed_flag = True

    elif drift_WXDAI_to_EURe > ENV.DRIFT_THRESHOLD and balance_WXDAI >= amount_WXDAI * (10 ** decimalsWXDAI):
        logger.info(f'Swapping {amount_WXDAI:.3f} WXDAI for EURe...')
        tx_receipt_WXDAI_to_EURe = swapper.swap_WXDAI_for_EURe(data)

        message, message_slack = get_tx_receipt_message_with_transfers(tx_receipt_WXDAI_to_EURe,
                                                                       ENV.AVATAR_SAFE_ADDRESS, w3)
        messenger.log_and_alert(LoggingLevel.Info, f'{amount_WXDAI:.3f} WXDAI swapped for EURe', message,
                                slack_msg=message_slack)

        tx_executed_flag = True

    if tx_executed_flag:
        data = swaps_data_manager.get_data(amount_WXDAI, amount_EURe)

        balance_EURe = EURe_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
        balance_WXDAI = WXDAI_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
        bot_xDAI_balance = w3.eth.get_balance(ENV.BOT_ADDRESS)
        drift_EURe_to_WXDAI = data.drift_EURe_to_WXDAI
        drift_WXDAI_to_EURe = data.drift_WXDAI_to_EURe

        gauges.last_updated.set_to_current_time()
        gauges.update(EUR_price_feed=data.EUR_price, EURe_price_curve=data.EURe_to_WXDAI / data.amount_EURe,
                      bot_xDAI_balance=bot_xDAI_balance, safe_WXDAI_balance=balance_WXDAI,
                      safe_EURe_balance=balance_EURe, amount_WXDAI=amount_WXDAI, amount_EURe=amount_EURe,
                      drift_threshold=ENV.DRIFT_THRESHOLD, drift_EURe_to_WXDAI=drift_EURe_to_WXDAI,
                      drift_WXDAI_to_EURe=drift_WXDAI_to_EURe)

        logger.info(
            f'Status update after swap:\n'
            f'  New EUR to USD oracle: {data.amount_EURe:.3f} EURe ---> {data.amount_EURe * data.EUR_price:.3f} USD.\n'
            f'  New EURe to WXDAI Curve: {data.amount_EURe:.3f} EURe ---> {data.EURe_to_WXDAI:.3f} WXDAI.\n'
            f'  New EURe to WXDAI drift: {drift_EURe_to_WXDAI:.5f}.\n'
            f'\n'
            f'  New USD to EURe oracle: {data.amount_WXDAI:.3f} USD ---> {data.amount_WXDAI / data.EUR_price:.3f} EURe.\n'
            f'  New WXDAI to EURe Curve: {data.amount_WXDAI:.3f} WXDAI ---> {data.WXDAI_to_EURe:.3f} EURe.\n'
            f'  New WXDAI to EURe drift: {drift_WXDAI_to_EURe:.5f}.\n'
            f'\n'
            f'  Drift threshold: {ENV.DRIFT_THRESHOLD:.5f}.\n'
            f'\n'
            f'  Avatar safe"s WXDAI balance: {balance_WXDAI / (10 ** decimalsWXDAI):.5f}.\n'
            f'  Avatar safe"s EURe balance: {balance_EURe / (10 ** decimalsEURe):.5f}.\n'
            f'  Bot"s xDAI balance: {bot_xDAI_balance / (10 ** 18):.5f}.\n'
        )


# -----------------------------MAIN LOOP-----------------------------------------

while True:

    try:
        if not test_mode:
            w3, connection_check = web3_connection_check(ENV.RPC_ENDPOINT, messenger, rpc_endpoint_failure_counter,
                                                         ENV.FALLBACK_RPC_ENDPOINT)
            if not connection_check:
                continue
        else:
            w3 = Web3(Web3.HTTPProvider(f'http://localhost:{ENV.LOCAL_FORK_PORT}'))

        bot_do(w3)

    except Exception as e:
        messenger.log_and_alert(LoggingLevel.Error, title='Exception', message='  ' + str(e.args[0]))
        exception_counter += 1
        if exception_counter == 5:  # TODO: this can be added as an environment variable
            messenger.log_and_alert(LoggingLevel.Error, title='Too many exceptions, exiting...', message='')
            time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
            sys.exit(1)
    time.sleep(ENV.COOLDOWN_MINUTES * 60)
