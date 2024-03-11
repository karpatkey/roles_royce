from dataclasses import dataclass, field
from decouple import config
from web3.types import ChecksumAddress
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
import logging
from roles_royce.protocols.base import Address
import json
from roles_royce.applications.utils import custom_config, to_dict
import threading
import schedule
import time
from prometheus_client import Gauge
from swaps import decimalsWXDAI, decimalsEURe



@dataclass
class ENV:
    TEST_MODE: bool = field(init=False)
    RPC_ENDPOINT: str = field(init=False)
    RPC_ENDPOINT_FALLBACK: str = field(init=False)
    RPC_ENDPOINT_EXECUTION: str = field(init=False)
    AVATAR_SAFE_ADDRESS: Address | ChecksumAddress | str = config('AVATAR_SAFE_ADDRESS')
    ROLES_MOD_ADDRESS: Address | ChecksumAddress | str = config('ROLES_MOD_ADDRESS')
    ROLE: int = config('ROLE', cast=int)
    PRIVATE_KEY: str = config('PRIVATE_KEY')
    FIXER_API_ACCESS_KEY: str = config('FIXER_API_ACCESS_KEY', cast=str)
    MAX_SLIPPAGE: float = custom_config('MAX_SLIPPAGE', default=0.01, cast=float)
    DRIFT_THRESHOLD: float = config('DRIFT_THRESHOLD', cast=float)
    AMOUNT: float = config('AMOUNT', cast=float)
    COOLDOWN_MINUTES: int = custom_config('COOLDOWN_MINUTES', default=5, cast=int)
    SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
    TELEGRAM_BOT_TOKEN: str = config('TELEGRAM_BOT_TOKEN', default='')
    TELEGRAM_CHAT_ID: int = custom_config('TELEGRAM_CHAT_ID', default='', cast=int)
    PROMETHEUS_PORT: int = custom_config('PROMETHEUS_PORT', default=8000, cast=int)
    LOCAL_FORK_PORT: int = custom_config('LOCAL_FORK_PORT', default=8545, cast=int)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    def __post_init__(self):
        self.TEST_MODE = custom_config('TEST_MODE', default=True, cast=bool)
        if self.TEST_MODE is False:
            self.RPC_ENDPOINT = config('RPC_ENDPOINT', cast=str)
            self.RPC_ENDPOINT_FALLBACK = custom_config('RPC_ENDPOINT_FALLBACK', default='', cast=str)
            self.RPC_ENDPOINT_EXECUTION = custom_config('RPC_ENDPOINT_MEV', default='', cast=str)
        self.AVATAR_SAFE_ADDRESS = config('AVATAR_SAFE_ADDRESS', cast=str)
        self.ROLES_MOD_ADDRESS = config('ROLES_MOD_ADDRESS', cast=str)
        self.ROLE = config('ROLE', cast=int)
        self.PRIVATE_KEY = config('PRIVATE_KEY', cast=str)
        self.FIXER_API_ACCESS_KEY = custom_config('FIXER_API_ACCESS_KEY', cast=str)
        self.MAX_SLIPPAGE = custom_config('MAX_SLIPPAGE', default=0.01, cast=float)
        self.DRIFT_THRESHOLD = config('DRIFT_THRESHOLD', cast=float)
        self.AMOUNT = config('AMOUNT', cast=float)
        self.COOLDOWN_MINUTES = custom_config('COOLDOWN_MINUTES', default=5, cast=int)
        self.SLACK_WEBHOOK_URL = custom_config('SLACK_WEBHOOK_URL', default='', cast=str)
        self.TELEGRAM_BOT_TOKEN = custom_config('TELEGRAM_BOT_TOKEN', default='', cast=str)
        self.TELEGRAM_CHAT_ID = custom_config('TELEGRAM_CHAT_ID', default='', cast=int)
        self.PROMETHEUS_PORT = custom_config('PROMETHEUS_PORT', default=8000, cast=int)
        self.LOCAL_FORK_PORT = custom_config('LOCAL_FORK_PORT', default=8545, cast=int)
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).is_connected():
            raise ValueError(f"RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT}.")
        self.BOT_ADDRESS = Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).eth.account.from_key(self.PRIVATE_KEY).address

    def __str__(self):
        return json.dumps(to_dict(self, exclude_key="PRIVATE_KEY"), indent=4)