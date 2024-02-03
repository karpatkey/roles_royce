import sys
import requests
import json
from enum import Enum
from threading import Thread
import logging
import time
from queue import Queue
from web3 import Web3


class LoggingLevel(Enum):
    Info = 1
    Warning = 2
    Error = 3


logger = logging.getLogger(__name__)


class SlackMessageIcon(Enum):
    Loudspeaker = (':loudspeaker: ', '#00FF00')
    WarningSign = ('Warning :warning: ', '#FFF000')
    ErrorRotatingLight = ('Error :rotating_light: ', '#FF0000')


class SlackMessenger(Thread):
    def __init__(self, webhook: str):
        super().__init__()
        self.webhook = webhook
        self.out_queue = Queue()
        self.daemon = True
        self.running = True  # Add a flag to control the thread's execution

    def run(self):
        while self.webhook != '' and self.running:
            icon, title, msg = self.out_queue.get()
            try:
                send_slack_msg(self.webhook, icon, title, msg)
            except Exception:
                logger.exception("Error sending Slack message.")

    def stop(self):
        self.running = False  # Set the flag to stop the thread

    def send_msg(self, icon: SlackMessageIcon, title: str, msg: str):
        self.out_queue.put((icon, title, msg))


class TelegramMessenger(Thread):
    def __init__(self, bot_token: str, chat_id: int):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.out_queue = Queue()
        self.daemon = True
        self.running = True  # Add a flag to control the thread's execution

    def run(self):
        while self.bot_token != '' and self.chat_id != '' and self.running:
            msg = self.out_queue.get()
            try:
                send_telegram_msg(self.bot_token, self.chat_id, msg)
            except Exception:
                logger.exception("Error sending Telegram message.")

    def stop(self):
        self.running = False  # Set the flag to stop the thread

    def send_msg(self, msg: str):
        self.out_queue.put(msg)


def send_slack_msg(slack_webhook: str, icon: SlackMessageIcon, title: str, message: str) -> requests.Response:
    url = slack_webhook
    title = icon.value[0] + title
    color = icon.value[1]

    slack_data = {
        # 'username': 'NotificationBot',
        # 'icon_emoji': ':satellite:',
        # 'channel' : '#somerandomcahnnel',
        'attachments': [
            {
                'mrkdwn_in': ['text'],
                'color': color,
                'title': title,
                'text': message
                # 'image_url': image_url,
                # 'fields': [
                #     {
                #         'title': title,
                #         'value': txns_message,
                #         #'short': 'false',
                #     }
                # ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': 'application/json', 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)

    if response.status_code != 200:
        logger.error("Error sending Slack message; status: %d, message %s", response.status_code, response.text)

    return response


def send_telegram_msg(bot_access_token: str, chat_id: int, message: str) -> requests.Response:
    URL_TELEGRAM = f'https://api.telegram.org/bot{bot_access_token}/sendMessage?chat_id=-{chat_id}&text={message}'
    response = requests.post(URL_TELEGRAM)

    if response.status_code != 200:
        logger.error("Error sending Telegram message; status: %d, message %s", response.status_code, response.text)

    return response


class Messenger:
    def __init__(self, slack_messenger: SlackMessenger, telegram_messenger: TelegramMessenger):
        self.slack_messenger = slack_messenger
        self.telegram_messenger = telegram_messenger

    def log_and_alert(self, logging_level: LoggingLevel, title: str, message: str, slack_msg: str | None = None,
                      alert_flag: bool = False):
        if logging_level == LoggingLevel.Info:
            logger.info(title + '.\n' + message)
            if not alert_flag:
                if slack_msg is not None:
                    self.slack_messenger.send_msg(SlackMessageIcon.Loudspeaker, title, slack_msg)
                else:
                    self.slack_messenger.send_msg(SlackMessageIcon.Loudspeaker, title, message)
                self.telegram_messenger.send_msg('Info: ' + title + '\n' + message)
        if logging_level == LoggingLevel.Warning:
            logger.warning(title + '.\n' + message)
            if not alert_flag:
                if slack_msg is not None:
                    self.slack_messenger.send_msg(SlackMessageIcon.WarningSign, title, slack_msg)
                else:
                    self.slack_messenger.send_msg(SlackMessageIcon.WarningSign, title, message)
                self.telegram_messenger.send_msg('Warning: ' + title + '\n' + message)
        if logging_level == LoggingLevel.Error:
            logger.exception(title + '.\n' + message)
            if not alert_flag:
                if slack_msg is not None:
                    self.slack_messenger.send_msg(SlackMessageIcon.ErrorRotatingLight, title, slack_msg)
                else:
                    self.slack_messenger.send_msg(SlackMessageIcon.ErrorRotatingLight, title, message)
                self.telegram_messenger.send_msg('Error: ' + title + '\n' + message)


def web3_connection_check(rpc_endpoint_url: str, messenger: Messenger, rpc_endpoint_failure_counter: int,
                          fallback_rpc_endpoint_url: str = '', max_rpc_endpoint_failures: int = 5) -> (object, int):
    """Checks if the RPC endpoint is working, and if not, tries to connect to a fallback RPC endpoint.

    Args:
        rpc_endpoint_url: RPC endpoint URL to check.
        messenger: Messenger object.
        rpc_endpoint_failure_counter: Counter of RPC endpoint failures.
        fallback_rpc_endpoint_url: Fallback RPC endpoint URL to check.
        max_rpc_endpoint_failures: Maximum number of RPC endpoint failures before exiting.

    Returns:
        w3: Web3 object.
        rpc_endpoint_failure_counter: Updated counter of RPC endpoint failures.
    """
    w3 = Web3(Web3.HTTPProvider(rpc_endpoint_url))
    if not w3.is_connected(show_traceback=True):
        time.sleep(5)
        # Second attempt
        if not w3.is_connected(show_traceback=True):
            # Case where a fallback RPC endpoint is provided
            if fallback_rpc_endpoint_url != '':
                messenger.log_and_alert(LoggingLevel.Warning, title='Warning',
                                        message=f'  RPC endpoint {rpc_endpoint_url} is not working.')
                w3 = Web3(Web3.HTTPProvider(fallback_rpc_endpoint_url))
                if not w3.is_connected(show_traceback=True):
                    time.sleep(5)
                    # Second attempt with fallback RPC endpoint
                    if not w3.is_connected(show_traceback=True):
                        messenger.log_and_alert(LoggingLevel.Error, title='Error',
                                                message=f'  RPC endpoint {rpc_endpoint_url} and fallback RPC '
                                                        f'endpoint {fallback_rpc_endpoint_url} are both not '
                                                        f'working.')
                        rpc_endpoint_failure_counter += 1
                    else:
                        rpc_endpoint_failure_counter = 0
                else:
                    rpc_endpoint_failure_counter = 0
            # Case where no fallback RPC endpoint is provided
            else:
                messenger.log_and_alert(LoggingLevel.Error, title='Error',
                                        message=f'  RPC endpoint {rpc_endpoint_url} is not working.')
                rpc_endpoint_failure_counter += 1
        else:
            rpc_endpoint_failure_counter = 0
    else:
        rpc_endpoint_failure_counter = 0

    if rpc_endpoint_failure_counter == max_rpc_endpoint_failures:
        messenger.log_and_alert(LoggingLevel.Error, title='Too many RPC endpoint failures, exiting...',
                                message='')
        time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
        sys.exit(1)

    else:
        return w3, rpc_endpoint_failure_counter
