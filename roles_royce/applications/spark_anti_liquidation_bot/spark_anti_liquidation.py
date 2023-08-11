from decouple import config
from roles_royce.toolshed.anti_liquidation.spark.cdp import SparkCDPManager
from web3 import Web3
from roles_royce.protocols.eth import spark
from roles_royce.constants import ETHAddr
from roles_royce.toolshed.protocol_utils.spark.utils import SparkUtils
from roles_royce.evm_utils import get_token_amounts_from_transfer_event
from decimal import Decimal
from roles_royce import send
from roles_royce.evm_utils import erc20_abi
from roles_royce.toolshed.alerting import SlackMessenger, SlackMessageIcon, TelegramMessenger
from prometheus_client import start_http_server as prometheus_start_http_server
import logging
import time

bot_address = config('BOT_ADDRESS')
roles_mod_address = config('ROLES_MOD_ADDRESS')
role = config('ROLE')
private_key = config('PRIVATE_KEY')
avatar_safe_address = config('AVATAR_SAFE_ADDRESS')
RPC_endpoint = config('RPC_ENDPOINT')

target_health_factor = config('TARGET_HEALTH_FACTOR')
alerting_health_factor = config('ALERTING_HEALTH_FACTOR')
threshold_health_factor = config('THRESHOLD_HEALTH_FACTOR')
tolerance = int(config('TOLERANCE', default=0.01))

slack_webhook_url = config('SLACK_WEBHOOK_URL', default='')
telegram_bot_token = config('TELEGRAM_BOT_TOKEN', default='')
telegram_chat_id = config('TELEGRAM_CHAT_ID', default='')
prometheus_port = int(config('PROMETHEUS_PORT', default=8000))

cooldown_minutes = int(config('COOLDOWN_MINUTES', default=5))

test_mode = config('TEST_MODE')

slack_messenger = SlackMessenger(webhook=slack_webhook_url)
slack_messenger.start()
telegram_messenger = TelegramMessenger(bot_token=telegram_bot_token, chat_id=telegram_chat_id)
telegram_messenger.start()

prometheus_start_http_server(prometheus_port)
# Configure logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger instance
logger = logging.getLogger(__name__)



def bot_do(w3: Web3, test_mode: bool = False):
    logger.info(f"Target health factor: {target_health_factor}, Alerting health factor: {alerting_health_factor}, Health factor threshold: {threshold_health_factor}")
    cdp_manager = SparkCDPManager(w3, avatar_safe_address)
    cdp = cdp_manager.get_cdp_data()
    logger.info("SparK CDP data retrieved:\n"
        f"{cdp}")
    if threshold_health_factor < cdp.health_factor <= alerting_health_factor:
        logger.info()
    elif cdp.health_factor <= target_health_factor:
        logger.info('Attempting to repay debt...')
        amount_of_DAI_to_repay = cdp_manager.get_delta_of_token_to_repay(spark_cdp=cdp,
                                                                         target_health_factor=target_health_factor,
                                                                         token_in_address=ETHAddr.DAI,
                                                                         rate_model=spark.RateModel.VARIABLE,
                                                                         tolerance=tolerance)
        chi = SparkUtils.get_chi(w3)
        amount_of_sDAI_to_redeem = int(Decimal(amount_of_DAI_to_repay) / (Decimal(chi) / Decimal(1e27)))

        sDAI_contract = w3.eth.contract(address=ETHAddr.sDAI, abi=erc20_abi)
        sDAI_balance = sDAI_contract.functions.balanceOf(avatar_safe_address).call()

        if sDAI_balance < amount_of_sDAI_to_redeem:
            amount_of_sDAI_to_redeem = sDAI_balance
            title = 'Not enough sDAI to redeem'
            message = (f'Current health factor: {cdp.health_factor}.\n'
                       f'Target health factor: {target_health_factor}.\n'
                       f'Amount of DAI to repay: {amount_of_DAI_to_repay/1e18:.5f}.\n'
                       f'Amount of sDAI needed to redeem: {amount_of_sDAI_to_redeem}.\n'
                       f'Current sDAI balance: {sDAI_balance}.')

            logger.warning('Warning: not enough sDAI to redeem. '
                           f'Current health factor: {cdp.health_factor}. '
                           f'Target health factor: {target_health_factor}. '
                           f'Amount of DAI to repay: {amount_of_DAI_to_repay}. '
                           f'Amount of sDAI needed to redeem: {amount_of_sDAI_to_redeem}. '
                           f'Current sDAI balance: {sDAI_balance}.')


            slack_messenger.send_msg(SlackMessageIcon.WarningSign, title, message) if slack_messenger_thread else None
            telegram_messenger.send_msg('Warning: not enough sDAI to redeem.\n' + message) if telegram_messenger_thread else None

        logger.info(f'Redeeming {amount_of_sDAI_to_redeem} sDAI for DAI...')
        tx_receipt_sDAI_redeemed = send(
            [spark.RedeemSDAIforDAI(amount=amount_of_sDAI_to_redeem, avatar=avatar_safe_address)], role=role,
            private_key=private_key, roles_mod_address=roles_mod_address, web3=w3)

        transfers_sDAI = get_token_amounts_from_transfer_event(tx_receipt=tx_receipt_sDAI_redeemed,
                                                               token_address=ETHAddr.sDAI,
                                                               target_address=avatar_safe_address, w3=w3)
        for element in transfers_sDAI:
            if element['from'] == avatar_safe_address:
                amount_of_sDAI_redeemed = element['amount']
                break
        transfers_DAI = get_token_amounts_from_transfer_event(tx_receipt=tx_receipt_sDAI_redeemed,
                                                              token_address=ETHAddr.DAI,
                                                              target_address=avatar_safe_address, w3=w3)
        for element in transfers_DAI:
            if element['from'] == avatar_safe_address:
                amount_of_DAI_received = element['amount']
                break

        DAI_contract = w3.eth.contract(address=ETHAddr.DAI, abi=erc20_abi)
        DAI_balance = DAI_contract.functions.balanceOf(avatar_safe_address).call()
        if DAI_balance < amount_of_DAI_to_repay:
            amount_of_DAI_to_repay = DAI_balance
            title = 'Not enough DAI to repay'
            message = (f'Current health factor: {cdp.health_factor}.\n'
                       f'Target health factor: {target_health_factor}.\n'
                       f'Amount of DAI to repay: {amount_of_DAI_to_repay}.\n'
                       f'Current DAI balance: {DAI_balance}.')
            logger.warning('Warning: not enough DAI to repay. '
                           f'Current health factor: {cdp.health_factor}. '
                           f'Target health factor: {target_health_factor}. '
                           f'Amount of DAI to repay: {amount_of_DAI_to_repay}. '
                           f'Current DAI balance: {DAI_balance}.')
            if slack_messenger_thread:
                slack_messenger.send_msg(SlackMessageIcon.WarningSign, title=title, msg=message)
            if telegram_messenger_thread:
                telegram_messenger.send_msg('Warning: not enough DAI to repay.\n' + message)

        tx_receipt_debt_repayed = cdp_manager.repay_single_token_debt(spark_cdp=cdp, token_in_address=ETHAddr.DAI,
                                                         token_in_amount=amount_of_DAI_to_repay,
                                                         rate_model=spark.RateModel.VARIABLE, private_key=private_key,
                                                         role=role, roles_mod_address=roles_mod_address)

        transfers_DAI = get_token_amounts_from_transfer_event(tx_receipt=tx_receipt_debt_repayed,
                                                              token_address=ETHAddr.DAI,
                                                              target_address=avatar_safe_address, w3=w3)
        for element in transfers_DAI:
            if element['from'] == avatar_safe_address:
                amount_of_DAI_received = element['amount']
                break

        bot_ETH_balance = w3.eth.get_balance(bot_address)
        if bot_ETH_balance < 0.1:
            title = 'Lack of ETH for gas'
            message = 'Im running outta ETH for gas! Only %.5f left.' % (bot_ETH_balance / (10 ** 18))
            slack_messenger.send_msg(SlackMessageIcon.WarningSign, title=title, msg=message) if slack_messenger_thread else None
            telegram_messenger.send_msg('Warning: lack of ETH for gas. ' + message) if telegram_messenger_thread else None
            logger.warning('Warning: lack of ETH for gas. ' + message)



while True:
    w3 = Web3(Web3.HTTPProvider(RPC_endpoint))
    try:
        bot_do(w3=w3, test_mode=test_mode)

    except Exception:
        logger.exception("Error")
    time.sleep(cooldown_minutes)
