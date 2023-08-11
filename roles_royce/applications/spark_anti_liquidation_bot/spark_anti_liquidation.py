from roles_royce.toolshed.anti_liquidation.spark.cdp import SparkCDPManager
from web3 import Web3
from roles_royce.protocols.eth import spark
from roles_royce.constants import ETHAddr
from roles_royce.toolshed.protocol_utils.spark.utils import SparkUtils
from roles_royce.toolshed.alerting.utils import get_token_amounts_from_transfer_event
from decimal import Decimal
from roles_royce import send
from roles_royce.evm_utils import erc20_abi
from roles_royce.toolshed.alerting.alerting import SlackMessenger, TelegramMessenger, Messenger, LoggingLevel
from prometheus_client import start_http_server as prometheus_start_http_server
import logging
from utils import ENV

#Importing the environment variables from the .env file
ENV = ENV()

w3 = Web3(Web3.HTTPProvider(ENV.RPC_ENDPOINT))

slack_messenger = SlackMessenger(webhook=ENV.SLACK_WEBHOOK_URL)
slack_messenger.start()
telegram_messenger = TelegramMessenger(bot_token=ENV.TELEGRAM_BOT_TOKEN, chat_id=ENV.TELEGRAM_CHAT_ID)
telegram_messenger.start()

prometheus_start_http_server(ENV.PROMETHEUS_PORT)

# Configure logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger instance
logger = logging.getLogger(__name__)
messenger = Messenger(slack_messenger, telegram_messenger)

lack_of_gas_warning = False

# -----------------------------------------------------------------------------------------------------------------------

def bot_do(w3: Web3, test_mode: bool = False):
    global lack_of_gas_warning

    logger.info(
        f"Target health factor: {ENV.TARGET_HEALTH_FACTOR}, Alerting health factor: {ENV.ALERTING_HEALTH_FACTOR}, Health factor threshold: {ENV.THRESHOLD_HEALTH_FACTOR}")

    cdp_manager = SparkCDPManager(w3, ENV.AVATAR_SAFE_ADDRESS)
    cdp = cdp_manager.get_cdp_data()
    logger.info("SparK CDP data retrieved:\n"
                f"{cdp}")
    if ENV.THRESHOLD_HEALTH_FACTOR < cdp.health_factor <= ENV.ALERTING_HEALTH_FACTOR:
        logger.info()
    elif cdp.health_factor <= ENV.ALERTING_HEALTH_FACTOR:
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

        if sDAI_balance < amount_of_sDAI_to_redeem:
            amount_of_sDAI_to_redeem = sDAI_balance

            title = 'Not enough sDAI to redeem'
            message = (f'Current health factor: {cdp.health_factor}.\n'
                       f'Target health factor: {ENV.TARGET_HEALTH_FACTOR}.\n'
                       f'Amount of DAI to repay: {amount_of_DAI_to_repay / 1e18:.5f}.\n'
                       f'Amount of sDAI needed to redeem: {amount_of_sDAI_to_redeem / 1e18:.5f}.\n'
                       f'Current sDAI balance: {sDAI_balance / 1e18:.5f}.')
            messenger.log_and_alert(LoggingLevel.Warning, title, message)

        logger.info(f'Redeeming {amount_of_sDAI_to_redeem} sDAI for DAI...')
        tx_receipt_sDAI_redeemed = send(
            [spark.RedeemSDAIforDAI(amount=amount_of_sDAI_to_redeem, avatar=ENV.AVATAR_SAFE_ADDRESS)], role=ENV.ROLE,
            private_key=ENV.PRIVATE_KEY, roles_mod_address=ENV.ROLES_MOD_ADDRESS, web3=w3)


        transfers_sDAI = get_token_amounts_from_transfer_event(tx_receipt=tx_receipt_sDAI_redeemed,
                                                               token_address=ETHAddr.sDAI,
                                                               target_address=ENV.AVATAR_SAFE_ADDRESS, w3=w3)
        for element in transfers_sDAI:
            if element['from'] == ENV.AVATAR_SAFE_ADDRESS:
                amount_of_sDAI_redeemed = element['amount']
                break
        transfers_DAI = get_token_amounts_from_transfer_event(tx_receipt=tx_receipt_sDAI_redeemed,
                                                              token_address=ETHAddr.DAI,
                                                              target_address=ENV.AVATAR_SAFE_ADDRESS, w3=w3)
        for element in transfers_DAI:
            if element['from'] == ENV.AVATAR_SAFE_ADDRESS:
                amount_of_DAI_received = element['amount']
                break

        DAI_contract = w3.eth.contract(address=ETHAddr.DAI, abi=erc20_abi)
        DAI_balance = DAI_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
        if DAI_balance < amount_of_DAI_to_repay:
            amount_of_DAI_to_repay = DAI_balance
            title = 'Not enough DAI to repay'
            message = (f'Current health factor: {cdp.health_factor}.\n'
                       f'Target health factor: {ENV.TARGET_HEALTH_FACTOR}.\n'
                       f'Amount of DAI to repay: {amount_of_DAI_to_repay / 1e18:.5f}.\n'
                       f'Current DAI balance: {DAI_balance / 1e18:.5f}.')
            messenger.log_and_alert(LoggingLevel.Warning, title, message)

        tx_receipt_debt_repayed = cdp_manager.repay_single_token_debt(spark_cdp=cdp, token_in_address=ETHAddr.DAI,
                                                                      token_in_amount=amount_of_DAI_to_repay,
                                                                      rate_model=spark.RateModel.VARIABLE,
                                                                      private_key=ENV.PRIVATE_KEY,
                                                                      role=ENV.ROLE,
                                                                      roles_mod_address=ENV.ROLES_MOD_ADDRESS)

        transfers_DAI = get_token_amounts_from_transfer_event(tx_receipt=tx_receipt_debt_repayed,
                                                              token_address=ETHAddr.DAI,
                                                              target_address=ENV.AVATAR_SAFE_ADDRESS, w3=w3)
        for element in transfers_DAI:
            if element['from'] == ENV.AVATAR_SAFE_ADDRESS:
                amount_of_DAI_received = element['amount']
                break

        bot_ETH_balance = w3.eth.get_balance(ENV.BOT_ADDRESS)
        if bot_ETH_balance < 0.1 and lack_of_gas_warning is False:
            title = 'Lack of ETH for gas'
            message = 'Im running outta ETH for gas! Only %.5f ETH left.' % (bot_ETH_balance / (10 ** 18))
            messenger.log_and_alert(LoggingLevel.Warning, title, message)
            lack_of_gas_warning = True


while False:

    try:
        bot_do(w3=w3, test_mode=ENV.TEST_MODE)

    except Exception:
        logger.exception("Error")
    time.sleep(ENV.COOLDOWN_MINUTES)
