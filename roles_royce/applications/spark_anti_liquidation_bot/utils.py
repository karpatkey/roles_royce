from dataclasses import dataclass, field
import threading
from prometheus_client import Gauge, Info
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
    FALLBACK_RPC_ENDPOINT: str = config('FALLBACK_RPC_ENDPOINT', default='')
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
    STATUS_NOTIFICATION_HOUR: int = custom_config('STATUS_NOTIFICATION_HOUR', default='', cast=int)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    def __post_init__(self):
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).is_connected():
            raise ValueError(f"RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT}.")
        if self.FALLBACK_RPC_ENDPOINT != '':
            if not Web3(Web3.HTTPProvider(self.FALLBACK_RPC_ENDPOINT)).is_connected():
                raise ValueError(f"FALLBACK_RPC_ENDPOINT is not valid or not active: {self.FALLBACK_RPC_ENDPOINT}.")
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


def send_status(messenger: Messenger, cdp: SparkCDP, bot_ETH_balance: float):
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

@dataclass
class Gauges:
    health_factor = Gauge('health_factor', 'Spark CDP health factor')
    # TODO: This should be generalized for any Spark CDP with any tokens
    wstETH_deposited = Gauge('wstETH_balance', 'wstETH deposited balance of the Spark CDP')
    DAI_borrowed = Gauge('DAI_borrowed', 'DAI borrowed balance of the Spark CDP')
    wstETH_price = Gauge('wstETH_price', 'wstETH price')
    DAI_price = Gauge('DAI_price', 'DAI price')
    bot_ETH_balance = Gauge('bot_ETH_balance', 'ETH balance of the bot')
    alerting_health_factor = Gauge('alerting_health_factor', 'Alerting health factor')
    health_factor_threshold = Gauge('health_factor_threshold', 'Health factor threshold')
    sDAI_balance = Gauge('sDAI_balance', 'sDAI balance of the avatar safe')
    last_updated = Gauge('last_updated', 'Last updated time and date')
    DAI_equivalent = Gauge('DAI_equivalent', 'DAI that would be obtained by redeeming the total of the sDAI')
    DAI_balance = Gauge('DAI_balance', 'DAI balance of the avatar safe')