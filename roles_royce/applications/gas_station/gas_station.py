from web3 import Web3
from defabipedia.types import Chains
from roles_royce.toolshed.alerting.utils import get_tx_receipt_message_with_transfers
from roles_royce.toolshed.alerting import SlackMessenger, TelegramMessenger, Messenger, LoggingLevel, web3_connection_check
from prometheus_client import start_http_server as prometheus_start_http_server
import logging
from utils import ENV, log_initial_data
import time
import sys
from decimal import Decimal

# Importing the environment variables from the .env file
ENV = ENV()

test_mode = ENV.TEST_MODE
if test_mode:
    from tests.utils import top_up_address
    w3_eth = Web3(Web3.HTTPProvider(f'http://{ENV.LOCAL_FORK_HOST_ETHEREUM}:{ENV.LOCAL_FORK_PORT_ETHEREUM}'))
    w3_gnosis = Web3(Web3.HTTPProvider(f'http://{ENV.LOCAL_FORK_HOST_GNOSIS}:{ENV.LOCAL_FORK_PORT_GNOSIS}'))

    top_up_address(w3_eth, ENV.BOT_ADDRESS, 1)
    top_up_address(w3_gnosis, ENV.BOT_ADDRESS, 1)



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

# Exception and RPC endpoint failure counters
exception_counter = 0
rpc_endpoint_failure_counter = 0

log_initial_data(ENV, messenger)



def bot_do(w3_eth, w3_gnosis):
    1+1

# -----------------------------MAIN LOOP-----------------------------------------

while True:

    try:
        if not test_mode:
            w3_eth, connection_check_eth = web3_connection_check(ENV.RPC_ENDPOINT_ETHEREUM, messenger, rpc_endpoint_failure_counter,
                                                         ENV.RPC_ENDPOINT_FALLBACK_ETHEREUM)
            if not connection_check_eth:
                continue
        else:
            w3 = Web3(Web3.HTTPProvider(f'http://localhost:{ENV.LOCAL_FORK_PORT}'))

        bot_do(w3_eth, w3_gnosis)

    except Exception as e:
        messenger.log_and_alert(LoggingLevel.Error, title='Exception', message='  ' + str(e.args[0]))
        exception_counter += 1
        if exception_counter == 5:  # TODO: this can be added as an environment variable
            messenger.log_and_alert(LoggingLevel.Error, title='Too many exceptions, exiting...', message='')
            time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
            sys.exit(1)
    time.sleep(ENV.COOLDOWN_MINUTES * 60)
