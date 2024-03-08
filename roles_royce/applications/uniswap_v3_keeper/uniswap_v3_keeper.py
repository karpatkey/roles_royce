from web3 import Web3
from roles_royce.toolshed.alerting import (
    SlackMessenger,
    TelegramMessenger,
    Messenger,
    LoggingLevel,
    web3_connection_check,
)
from roles_royce.protocols.uniswap_v3 import Pool
from roles_royce.toolshed.alerting.utils import get_tx_receipt_message_with_transfers
from prometheus_client import start_http_server as prometheus_start_http_server
import logging
import time
import sys
from decimal import Decimal
from utils import (
    ENV,
    Gauges,
    Flags,
    log_initial_data,
    log_status_update,
    get_all_nfts,
    get_nft_id_from_mint_tx,
    StaticData,
    TransactionsManager,
    update_dynamic_data,
    get_amounts_quotient_from_price_delta,
    NFTPosition,
    MinimumPriceError,
    check_initial_data
)

# Importing the environment variables from the .env file
env = ENV()
check_initial_data(env)
static_data = StaticData(env=env)

# -----------------------------------------------------------------------------------------------------------------------

# Alert flags
flags = Flags()

# Messenger system
slack_messenger = SlackMessenger(webhook=ENV.SLACK_WEBHOOK_URL)
slack_messenger.start()
telegram_messenger = TelegramMessenger(
    bot_token=ENV.TELEGRAM_BOT_TOKEN, chat_id=ENV.TELEGRAM_CHAT_ID
)
telegram_messenger.start()

# Configure logging settings
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

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

log_initial_data(static_data.env, messenger)

# -----------------------------------------------------------------------------------------------------------------------

test_mode = static_data.env.TEST_MODE
if test_mode:
    from tests.utils import top_up_address

    w3 = Web3(Web3.HTTPProvider(f"http://{static_data.env.LOCAL_FORK_HOST}:{static_data.env.LOCAL_FORK_PORT}"))
    top_up_address(w3, static_data.env.BOT_ADDRESS, 1)
else:
    w3, rpc_endpoint_failure_counter = web3_connection_check(
        static_data.env.RPC_ENDPOINT,
        messenger,
        rpc_endpoint_failure_counter,
        static_data.env.RPC_ENDPOINT_FALLBACK,
    )

# -----------------------------------------------------------------------------------------------------------------------


transactions_manager = TransactionsManager(
    avatar=static_data.env.AVATAR_SAFE_ADDRESS,
    roles_mod=static_data.env.ROLES_MOD_ADDRESS,
    role=static_data.env.ROLE,
    private_key=static_data.env.PRIVATE_KEY,
)

all_nft_ids = get_all_nfts(
    w3,
    static_data.env.AVATAR_SAFE_ADDRESS,
    active=False,
    token0=static_data.env.TOKEN0_ADDRESS,
    token1=static_data.env.TOKEN1_ADDRESS,
    fee=static_data.env.FEE,
)
active_nfts = get_all_nfts(
    w3,
    static_data.env.AVATAR_SAFE_ADDRESS,
    token0=static_data.env.TOKEN0_ADDRESS,
    token1=static_data.env.TOKEN1_ADDRESS,
    fee=static_data.env.FEE,
)
discarded_nfts = list(set(all_nft_ids) - set(active_nfts))
if not active_nfts:
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

# -----------------------------------------------------------------------------------------------------------------------


def bot_do(w3: Web3, static_data: StaticData) -> int:
    global gauges
    global flags
    global exception_counter

    nft_ids = get_all_nfts(
        w3,
        static_data.env.AVATAR_SAFE_ADDRESS,
        discarded_nfts=discarded_nfts,
        token0=static_data.env.TOKEN0_ADDRESS,
        token1=static_data.env.TOKEN1_ADDRESS,
        fee=static_data.env.FEE,
    )
    # TODO: Check that it's the correct NFT Id
    nft_id = nft_ids[-1]
    dynamic_data = update_dynamic_data(w3=w3, nft_id=nft_id, static_data=static_data)
    if dynamic_data.price < static_data.env.MINIMUM_MIN_PRICE:
        raise MinimumPriceError(
            f"The current price is below the minimum min price ${static_data.env.MINIMUM_MIN_PRICE}")
    gauges.update(dynamic_data, static_data)
    triggering_condition = dynamic_data.check_triggering_condition(static_data)
    if triggering_condition:
        nft_position = NFTPosition(w3, dynamic_data.nft_id)
        # TODO: Improve the choice of delta
        a = Decimal(static_data.env.PRICE_RANGE_THRESHOLD / 100) * (nft_position.price_max - nft_position.price_min)
        b = nft_position.pool.price - nft_position.price_min
        c = nft_position.price_max - nft_position.pool.price

        delta = (Decimal(static_data.env.PRICE_DELTA_MULTIPLIER) * Decimal(static_data.env.PRICE_RANGE_THRESHOLD / 100)
                 * (nft_position.price_max - nft_position.price_min))
        transactions_manager.collect_fees_and_disassemble_position(w3=w3, nft_id=dynamic_data.nft_id)
        # TODO: Add logs...
        dynamic_data = update_dynamic_data(w3=w3, nft_id=nft_id, static_data=static_data)
        gauges.update(dynamic_data, static_data)
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
        discarded_nfts.append(nft_id)
        nft_id = get_nft_id_from_mint_tx(w3=w3,
                                         tx_receipt=mint_receipt,
                                         recipient=static_data.env.AVATAR_SAFE_ADDRESS)
        dynamic_data = update_dynamic_data(w3=w3, nft_id=nft_id, static_data=static_data)
        gauges.update(dynamic_data, static_data)

    return 0


# -----------------------------MAIN LOOP-----------------------------------------


while True:

    try:
        if not test_mode:
            w3, rpc_endpoint_failure_counter = web3_connection_check(
                static_data.env.RPC_ENDPOINT,
                messenger,
                rpc_endpoint_failure_counter,
                static_data.env.RPC_ENDPOINT_FALLBACK,
            )
            if rpc_endpoint_failure_counter != 0:
                continue
        else:
            w3 = Web3(Web3.HTTPProvider(f"http://{static_data.env.LOCAL_FORK_HOST}:{static_data.env.LOCAL_FORK_PORT}"))

        try:
            exception_counter = bot_do(w3, static_data)  # If successful, resets the counter
        except:
            time.sleep(5)
            exception_counter = bot_do(w3, static_data)  # Second attempt

    except MinimumPriceError:
        messenger.log_and_alert(
            LoggingLevel.Warning, title="Minimum Price Error",
            message="The current price is below the minimum min price"
        )
        time.sleep(5)
        continue

    except Exception as e:
        messenger.log_and_alert(
            LoggingLevel.Error, title="Exception", message="  " + str(e.args[0])
        )
        exception_counter += 1
        if exception_counter == 5:  # TODO: this can be added as an environment variable
            messenger.log_and_alert(
                LoggingLevel.Error, title="Too many exceptions, exiting...", message=""
            )
            time.sleep(
                5
            )  # Cooldown time for the messenger system to send messages in queue
            sys.exit(1)
        time.sleep(30)  # Time to breathe
        continue
    time.sleep(static_data.env.COOLDOWN_MINUTES * 60)
