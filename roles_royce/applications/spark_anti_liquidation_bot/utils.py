from dataclasses import dataclass, field
import threading

import schedule
import time
from decouple import config
from web3.types import Address, ChecksumAddress
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
from roles_royce.toolshed.anti_liquidation.spark.cdp import SparkCDP
import logging

logger = logging.getLogger(__name__)

# The next helper function allows to leave variables unfilled in the .env file
def custom_config(variable, default, cast):
    value = config(variable, default=default)
    return default if value == '' else config(variable, default=default, cast=cast)


@dataclass
class ENV:
    RPC_ENDPOINT: str = config('RPC_ENDPOINT')
    AVATAR_SAFE_ADDRESS: Address | ChecksumAddress | str = config('AVATAR_SAFE_ADDRESS')
    ROLES_MOD_ADDRESS: Address | ChecksumAddress | str = config('ROLES_MOD_ADDRESS')
    ROLE: int = config('ROLE', cast=int)
    PRIVATE_KEY: str = config('PRIVATE_KEY')
    TARGET_HEALTH_FACTOR: float = config('TARGET_HEALTH_FACTOR', cast=float)
    THRESHOLD_HEALTH_FACTOR: float = config('THRESHOLD_HEALTH_FACTOR', cast=float)
    ALERTING_HEALTH_FACTOR: float | None = custom_config('ALERTING_HEALTH_FACTOR', default=None, cast=float)
    TOLERANCE: float = custom_config('TOLERANCE', default=0.01, cast=float)
    COOLDOWN_MINUTES: int = custom_config('COOLDOWN_MINUTES', default=5, cast=int)
    SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
    TELEGRAM_BOT_TOKEN: str = config('TELEGRAM_BOT_TOKEN', default='')
    TELEGRAM_CHAT_ID: int = custom_config('TELEGRAM_CHAT_ID', default='', cast=int)
    PROMETHEUS_PORT: int = custom_config('PROMETHEUS_PORT', default=8000, cast=int)
    TEST_MODE: bool = config('TEST_MODE', default=False, cast=bool)
    LOCAL_FORK_PORT: int = custom_config('LOCAL_FORK_PORT', default=8545, cast=int)
    STATUS_NOTIFICATION_HOUR: int = custom_config('STATUS_NOTIFICATION_HOUR', default=12, cast=int)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    MANDATORY_ATTRIBUTES = ['RPC_ENDPOINT', 'AVATAR_SAFE_ADDRESS', 'ROLES_MOD_ADDRESS', 'ROLE', 'PRIVATE_KEY',
                            'TARGET_HEALTH_FACTOR', 'THRESHOLD_HEALTH_FACTOR']

    def __post_init__(self):
        for attr_name in self.MANDATORY_ATTRIBUTES:
            attr_value = getattr(self, attr_name)
            if not attr_value:
                raise ValueError(f"{attr_name} is cannot be empty in .env file.")
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).is_connected():
            raise ValueError(f"RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT}.")
        self.BOT_ADDRESS = Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).eth.account.from_key(self.PRIVATE_KEY).address
        if not self.ALERTING_HEALTH_FACTOR:
            self.ALERTING_HEALTH_FACTOR = (self.TARGET_HEALTH_FACTOR + self.THRESHOLD_HEALTH_FACTOR) / 2

    def __repr__(self):
        return 'Environment variables'


def log_initial_data(env: ENV, messenger: Messenger):
    title = "Spark Anti-Liquidation Bot started"
    message = (f"  Avatar safe address: {env.AVATAR_SAFE_ADDRESS}\n"
               f"  Roles mod address: {env.ROLES_MOD_ADDRESS}\n"
               f"  Bot address: {env.BOT_ADDRESS}\n"
               f"  Target health factor: {env.TARGET_HEALTH_FACTOR}\n")
    if messenger.slack_messenger.webhook != '' or (
            messenger.telegram_messenger.bot_token != '' and messenger.telegram_messenger.chat_id != ''):
        message = message + f"  Alerting health factor: {env.ALERTING_HEALTH_FACTOR}\n"
    message = message + (f"  Health Factor threshold: {env.THRESHOLD_HEALTH_FACTOR}\n"
                         f"  Tolerance: {env.TOLERANCE}\n"
                         f"  Cooldown Minutes: {env.COOLDOWN_MINUTES}\n")
    messenger.log_and_alert(LoggingLevel.Info, title, message)

def send_status(env: ENV, messenger: Messenger, cdp: SparkCDP, bot_ETH_balance: float):
    title = "Spark CDP status update"
    message = (f"  Current health factor: {cdp.health_factor}\n"
               f"{cdp}\n"
               f"Bot ETH balance: {bot_ETH_balance:.5f}")
    messenger.log_and_alert(LoggingLevel.Info, title, message)


class SchedulerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True

    def run(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.running = False
