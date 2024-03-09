from web3 import Web3
from roles_royce.toolshed.alerting import (
    SlackMessenger,
    TelegramMessenger,
    Messenger,
    LoggingLevel,
    web3_connection_check,
)
from roles_royce.toolshed.alerting.utils import get_tx_receipt_message_with_transfers
from prometheus_client import start_http_server as prometheus_start_http_server
import logging
import time
import sys
from decimal import Decimal
from prometheus import Gauges
from logs import log_initial_data, log_status_update
from core import ENV, StaticData, TransactionsManager, update_dynamic_data
from utils import (
    Flags,
    get_active_nft, store_active_nft,
    get_nft_id_from_mint_tx,
    get_amounts_quotient_from_price_delta,
    NFTPosition,
    MinimumPriceError,
    check_initial_data
)
from web3.middleware import geth_poa_middleware

# -----------------------------------------------------------------------------------------------------------------------

env = ENV()
nft_id_initial = get_active_nft()
# Importing the environment variables from the .env file
check_initial_data(env, nft_id_initial)
static_data = StaticData(env=env)

# -----------------------------------------------------------------------------------------------------------------------

# Alert flags
flags = Flags()

# Messenger system
slack_messenger = SlackMessenger(webhook=env.SLACK_WEBHOOK_URL)
slack_messenger.start()
telegram_messenger = TelegramMessenger(
    bot_token=env.TELEGRAM_BOT_TOKEN, chat_id=env.TELEGRAM_CHAT_ID
)
telegram_messenger.start()

# Configure logging settings
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create a logger instance
logger = logging.getLogger(__name__)
messenger = Messenger(slack_messenger, telegram_messenger)

# Prometheus metrics from prometheus_client import Info
prometheus_start_http_server(static_data.env.PROMETHEUS_PORT)
gauges = Gauges()

# Exception and RPC endpoint failure counters
exception_counter = 0
rpc_endpoint_failure_counter = 0

# -----------------------------------------------------------------------------------------------------------------------

log_initial_data(static_data, messenger)

transactions_manager = TransactionsManager(
    avatar=static_data.env.AVATAR_SAFE_ADDRESS,
    roles_mod=static_data.env.ROLES_MOD_ADDRESS,
    role=static_data.env.ROLE,
    private_key=static_data.env.PRIVATE_KEY,
)

w3, rpc_endpoint_failure_counter = web3_connection_check(
    static_data.env.RPC_ENDPOINT,
    messenger,
    rpc_endpoint_failure_counter,
    static_data.env.RPC_ENDPOINT_FALLBACK)

if not nft_id_initial:
    mint_receipt = transactions_manager.mint_nft(w3=w3,
                                                 amount0=static_data.env.INITIAL_AMOUNT0,
                                                 amount1=static_data.env.INITIAL_AMOUNT1,
                                                 price_min=static_data.env.INITIAL_MIN_PRICE,
                                                 price_max=static_data.env.INITIAL_MAX_PRICE,
                                                 static_data=static_data)
    nft_id = get_nft_id_from_mint_tx(w3=w3,
                                     tx_receipt=mint_receipt,
                                     recipient=static_data.env.AVATAR_SAFE_ADDRESS)
    dynamic_data = update_dynamic_data(w3=w3, nft_id=nft_id, static_data=static_data)
    gauges.update(dynamic_data, static_data)
    store_active_nft(nft_id)


# -----------------------------------------------------------------------------------------------------------------------


def bot_do(w3: Web3, static_data: StaticData) -> int:
    global gauges
    global flags
    global exception_counter

    nft_id = get_active_nft()
    dynamic_data = update_dynamic_data(w3=w3, nft_id=nft_id, static_data=static_data)
    if dynamic_data.price < static_data.env.MINIMUM_MIN_PRICE:
        raise MinimumPriceError(
            f"The current price is below the minimum min price ${static_data.env.MINIMUM_MIN_PRICE}")

    log_status_update(static_data, dynamic_data)
    gauges.update(dynamic_data, static_data)

    triggering_condition = dynamic_data.check_triggering_condition(static_data)
    if triggering_condition:
        nft_position = NFTPosition(w3, dynamic_data.nft_id)

        delta = (Decimal(static_data.env.PRICE_DELTA_MULTIPLIER) * Decimal(static_data.env.PRICE_RANGE_THRESHOLD / 100)
                 * (nft_position.price_max - nft_position.price_min))
        tx_receipt = transactions_manager.collect_fees_and_disassemble_position(w3=w3, nft_id=dynamic_data.nft_id)
        message, message_slack = get_tx_receipt_message_with_transfers(tx_receipt,
                                                                       target_address=static_data.env.AVATAR_SAFE_ADDRESS,
                                                                       w3=w3)
        messenger.log_and_alert(LoggingLevel.Info, f'Fees collected and position disassembled', message,
                                slack_msg=message_slack)
        dynamic_data = update_dynamic_data(w3=w3, nft_id=nft_id, static_data=static_data)
        gauges.update(dynamic_data, static_data)
        log_status_update(static_data, dynamic_data)

        pool = NFTPosition(w3, dynamic_data.nft_id).pool
        desired_quotient = get_amounts_quotient_from_price_delta(pool, delta)
        current_quotient = Decimal(dynamic_data.safe_token1_balance) / Decimal(dynamic_data.safe_token0_balance)
        if current_quotient < desired_quotient:
            amount0_desired = None
            amount1_desired = dynamic_data.safe_token1_balance
        else:
            amount0_desired = dynamic_data.safe_token0_balance
            amount1_desired = None
        price_min = max(float(Decimal(dynamic_data.price) - delta), static_data.env.MINIMUM_MIN_PRICE)
        price_max = float(Decimal(dynamic_data.price) + delta)
        mint_receipt = transactions_manager.mint_nft(w3=w3,
                                                     amount0=amount0_desired,
                                                     amount1=amount1_desired,
                                                     price_min=price_min,
                                                     price_max=price_max,
                                                     static_data=static_data)
        nft_id = get_nft_id_from_mint_tx(w3=w3,
                                         tx_receipt=mint_receipt,
                                         recipient=static_data.env.AVATAR_SAFE_ADDRESS)
        dynamic_data = update_dynamic_data(w3=w3, nft_id=nft_id, static_data=static_data)
        gauges.update(dynamic_data, static_data)
        log_status_update(static_data, dynamic_data)
        store_active_nft(nft_id)

    return 0


# -----------------------------MAIN LOOP-----------------------------------------


while True:

    try:
        w3, rpc_endpoint_failure_counter = web3_connection_check(
            static_data.env.RPC_ENDPOINT,
            messenger,
            rpc_endpoint_failure_counter,
            static_data.env.RPC_ENDPOINT_FALLBACK)

        if rpc_endpoint_failure_counter != 0:
            continue

        try:
            exception_counter = bot_do(w3, static_data)  # If successful, resets the counter
        except:
            time.sleep(5)
            exception_counter = bot_do(w3, static_data)  # Second attempt

    except MinimumPriceError:
        messenger.log_and_alert(LoggingLevel.Warning, title="Minimum Price Error",
                                message="The current price is below the minimum min price")
        time.sleep(5)
        continue

    except Exception as e:
        messenger.log_and_alert(LoggingLevel.Error, title="Exception", message="  " + str(e.args[0]))
        exception_counter += 1
        if exception_counter == 5:  # TODO: this can be added as an environment variable
            messenger.log_and_alert(LoggingLevel.Error, title="Too many exceptions, exiting...", message="")
            time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
            sys.exit(1)
        time.sleep(30)  # Time to breathe
        continue
    time.sleep(static_data.env.COOLDOWN_MINUTES * 60)
