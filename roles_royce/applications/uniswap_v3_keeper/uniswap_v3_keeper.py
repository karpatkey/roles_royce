from web3 import Web3
from roles_royce.toolshed.alerting import SlackMessenger, TelegramMessenger, Messenger, LoggingLevel, \
    web3_connection_check
from roles_royce.toolshed.alerting.utils import get_tx_receipt_message_with_transfers
from prometheus_client import start_http_server as prometheus_start_http_server
import logging
from utils import ENV, Gauges, Flags, log_initial_data, log_status_update
import time
import sys
from datetime import datetime
from defabipedia.xdai_bridge import ContractSpecs
from defabipedia.tokens import EthereumContractSpecs as Tokens
from defabipedia.types import Chain
from decimal import Decimal
from roles_royce.protocols.uniswap_v3.methods_general import mint_nft, decrease_liquidity_nft
from roles_royce.protocols.uniswap_v3.utils import NFTPosition

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
rpc_endpoint_failure_counter = 0

# -----------------------------------------------------------------------------------------------------------------------

log_initial_data(ENV, messenger)


# -----------------------------------------------------------------------------------------------------------------------


def bot_do(w3):
    global gauges
    global flags


# -----------------------------MAIN LOOP-----------------------------------------


while True:

    try:
        if not test_mode:
            w3, rpc_endpoint_failure_counter = web3_connection_check(ENV.RPC_ENDPOINT, messenger,
                                                                     rpc_endpoint_failure_counter,
                                                                     ENV.RPC_ENDPOINT_ETHEREUM_FALLBACK)
            if rpc_endpoint_failure_counter != 0:
                continue
        else:
            w3 = Web3(Web3.HTTPProvider(f'http://localhost:{ENV.LOCAL_FORK_PORT_ETHEREUM}'))

        try:
            bot_do(w3)
        except:
            time.sleep(5)
            bot_do(w3)

    except Exception as e:
        messenger.log_and_alert(LoggingLevel.Error, title='Exception', message='  ' + str(e.args[0]))
        exception_counter += 1
        if exception_counter == 5:  # TODO: this can be added as an environment variable
            messenger.log_and_alert(LoggingLevel.Error, title='Too many exceptions, exiting...', message='')
            time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
            sys.exit(1)
    time.sleep(ENV.COOLDOWN_MINUTES * 60)
