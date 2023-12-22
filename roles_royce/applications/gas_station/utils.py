from dataclasses import dataclass, field
from decouple import config
from web3.types import Address, ChecksumAddress
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
import logging
from roles_royce.protocols.base import ContractMethod, InvalidArgument, AvatarAddress, Address
from prometheus_client import start_http_server as prometheus_start_http_server, Gauge
import os
import json


# The next helper function allows to leave variables unfilled in the .env file
def custom_config(variable, default, cast):
    value = config(variable, default=default)
    return default if value == '' else config(variable, default=default, cast=cast)


@dataclass
class ENV:
    RPC_ENDPOINT_ETHEREUM: str = config('RPC_ENDPOINT_ETHEREUM')
    RPC_ENDPOINT_FALLBACK_ETHEREUM: str = config('RPC_ENDPOINT_FALLBACK_ETHEREUM', default='')
    RPC_ENDPOINT_GNOSIS: str = config('RPC_ENDPOINT_GNOSIS')
    RPC_ENDPOINT_FALLBACK_GNOSIS: str = config('RPC_ENDPOINT_FALLBACK_GNOSIS', default='')

    AVATAR_SAFE_ADDRESS: Address | ChecksumAddress | str = config('AVATAR_SAFE_ADDRESS')
    ROLES_MOD_ADDRESS: Address | ChecksumAddress | str = config('ROLES_MOD_ADDRESS')
    ROLE: int = config('ROLE', cast=int)
    PRIVATE_KEY: str = config('PRIVATE_KEY')

    COOLDOWN_MINUTES: int = custom_config('COOLDOWN_MINUTES', default=5, cast=int)
    SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
    TELEGRAM_BOT_TOKEN: str = config('TELEGRAM_BOT_TOKEN', default='')
    TELEGRAM_CHAT_ID: int = custom_config('TELEGRAM_CHAT_ID', default='', cast=int)
    PROMETHEUS_PORT: int = custom_config('PROMETHEUS_PORT', default=8000, cast=int)

    TEST_MODE: bool = config('TEST_MODE', default=False, cast=bool)
    LOCAL_FORK_HOST_ETHEREUM: int = custom_config('LOCAL_FORK_HOST_ETHEREUM', default='localhost', cast=str)
    LOCAL_FORK_PORT_ETHEREUM: int = custom_config('LOCAL_FORK_PORT_ETHEREUM', default=8545, cast=int)
    LOCAL_FORK_HOST_GNOSIS: int = custom_config('LOCAL_FORK_HOST_GNOSIS', default='localhost', cast=str)
    LOCAL_FORK_PORT_GNOSIS: int = custom_config('LOCAL_FORK_PORT_GNOSIS', default=8546, cast=int)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    def __post_init__(self):
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_ETHEREUM)).is_connected():
            raise ValueError(f"Ethereum RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT_ETHEREUM}.")
        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_GNOSIS)).is_connected():
            raise ValueError(f"Gnosis RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT_GNOSIS}.")
        self.BOT_ADDRESS = Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_ETHEREUM)).eth.account.from_key(
            self.PRIVATE_KEY).address

    def __repr__(self):
        return 'Environment variables'


logger = logging.getLogger(__name__)


def log_initial_data(env: ENV, messenger: Messenger):
    title = "Gas station bot started"
    message = (f"  Avatar safe address: {env.AVATAR_SAFE_ADDRESS}\n"
               f"  Roles mod address: {env.ROLES_MOD_ADDRESS}\n"
               f"  Bot address: {env.BOT_ADDRESS}\n"
               f"  Cooldown Minutes: {env.COOLDOWN_MINUTES}\n")

    messenger.log_and_alert(LoggingLevel.Info, title, message)


def get_config_data() -> (dict,list):
    with open("config.json", "r") as f:
        config_data = json.load(f)

    gauges = []
    for element in config_data:
        if element['blockchain'] == 'ethereum':
            native_token = 'ETH'
        elif element['blockchain'] == 'gnosis':
            native_token = 'xDAI'
        else:
            raise ValueError(f"Blockchain is not valid: {element['blockchain']}")
        gauges.append(Gauge(name=element['name'], documentation=f'{native_token} balance of {element["name"]}'))
    return config_data, gauges
