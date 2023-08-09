import sys
import requests
import json
from enum import Enum
from threading import Thread
import logging
import time
from queue import Queue
from web3 import Web3

logger = logging.getLogger(__name__)


class SlackMessageIcon(Enum):
    Loudspeaker = (':loudspeaker: ', '#00FF00')
    WarningSign = ('Warning :warning: ', '#FFF000')
    ErrorRotatingLight = ('Error :rotating_light: ', '#FF0000')

class SlackMessenger(Thread):
    def __init__(self, webhook):
        super().__init__()
        self.webhook = webhook
        self.out_queue = Queue()
        self.daemon = True

    def run(self):
        while True:
            icon, title, msg = self.out_queue.get()
            try:
                send_slack_msg(self.webhook, icon, title, msg)
            except Exception:
                logger.exception("Error sending slack message.")

    def send_msg(self, icon: SlackMessageIcon, title: str, msg: str):
        self.out_queue.put((icon, title, msg))

class TelegramMessenger(Thread):
    def __init__(self, bot_token: str, chat_id: int):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.out_queue = Queue()
        self.daemon = True

    def run(self):
        while True:
            msg = self.out_queue.get()
            try:
                send_telegram_msg(self.bot_token, self.chat_id, msg)
            except Exception:
                logger.exception("Error sending Telegram message.")

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
    data = json.dumps(slack_data)
    headers = {'Content-Type': 'application/json', 'Content-Length': len(data)}
    response = requests.post(url, data=data, headers=headers)

    if response.status_code != 200:
       logger.error("Error sending Slack message; status: %d, message %s", response.status_code, response.text)

    return response


def send_telegram_msg(bot_access_token: str, chat_id: int, message: str) -> requests.Response:
    URL_TELEGRAM = 'https://api.telegram.org/bot%s/sendMessage?chat_id=-%d&text=%s' % (
        bot_access_token, chat_id, message)
    response = requests.post(URL_TELEGRAM)

    if response.status_code != 200:
        logger.error("Error sending Telegram message; status: %d, message %s", response.status_code, response.text)

    return response
