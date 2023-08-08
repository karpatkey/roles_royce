import sys
import requests
import json
from enum import Enum


class SlackMessageIcon(Enum):
    Loudspeaker = (':loudspeaker: ', '#00FF00')
    WarningExclamationMark = ('Warning :warning: ', '#FFF000')
    ErrorExclamationMark = ('Error :rotating_light: ', '#FF0000')



def send_slack_message(slack_webhook: str, spark_icon: SlackMessageIcon, title: str, message: str) -> requests.Response:
    url = slack_webhook
    title = spark_icon.value[0] + title
    color = spark_icon.value[1]

    # if __name__ == '__main__':
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

    # if response.status_code != 200:
    #    raise Exception(response.status_code, response.text)

    return response


def send_telegram_message(bot_access_token: str, chat_id: str, message: str) -> requests.Response:
    URL_TELEGRAM = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s' % (
        bot_access_token, chat_id, message)
    response = requests.get(URL_TELEGRAM)

    # if response.status_code != 200:
    #    raise Exception(response.status_code, response.text)

    return response
