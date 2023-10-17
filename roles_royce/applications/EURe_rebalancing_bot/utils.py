from dataclasses import dataclass, field
from decouple import config
from web3.types import Address, ChecksumAddress
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
import logging
from roles_royce.protocols.base import ContractMethod, InvalidArgument, AvatarAddress, Address
import threading
import schedule
import time
from prometheus_client import start_http_server as prometheus_start_http_server, Gauge


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
    FIXER_API_ACCESS_KEY: str = config('FIXER_API_ACCESS_KEY', cast=str)
    MAX_SLIPPAGE: float = custom_config('MAX_SLIPPAGE', default=0.01, cast=float)
    DRIFT_THRESHOLD: float = config('DRIFT_THRESHOLD', cast=float)
    AMOUNT: float = config('AMOUNT', cast=float)
    COOLDOWN_MINUTES: int = custom_config('COOLDOWN_MINUTES', default=5, cast=int)
    SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
    TELEGRAM_BOT_TOKEN: str = config('TELEGRAM_BOT_TOKEN', default='')
    TELEGRAM_CHAT_ID: int = custom_config('TELEGRAM_CHAT_ID', default='', cast=int)
    PROMETHEUS_PORT: int = custom_config('PROMETHEUS_PORT', default=8000, cast=int)
    TEST_MODE: bool = config('TEST_MODE', default=False, cast=bool)
    LOCAL_FORK_PORT: int = custom_config('LOCAL_FORK_PORT', default=8545, cast=int)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    def __post_init__(self):
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).is_connected():
            raise ValueError(f"RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT}.")
        self.BOT_ADDRESS = Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).eth.account.from_key(self.PRIVATE_KEY).address

    def __repr__(self):
        return 'Environment variables'


logger = logging.getLogger(__name__)


def log_initial_data(env: ENV, messenger: Messenger):
    title = "EURe rebalancing bot started"
    message = (f"  Avatar safe address: {env.AVATAR_SAFE_ADDRESS}\n"
               f"  Roles mod address: {env.ROLES_MOD_ADDRESS}\n"
               f"  Bot address: {env.BOT_ADDRESS}\n"
               f"  Drift threshold: {env.DRIFT_THRESHOLD * 100}%\n"
               f"  Initial amount to swap: {env.AMOUNT}\n"
               f"  Cooldown Minutes: {env.COOLDOWN_MINUTES}\n")

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
    EUR_price_feed = Gauge('EUR_price_feed', 'EUR price from feed')
    EURe_price_curve = Gauge('EURe_price_curve', 'EURe price from Curve')
    bot_ETH_balance = Gauge('bot_ETH_balance', 'ETH balance of the bot')
    safe_WXDAI_balance = Gauge('safe_WXDAI_balance', 'WXDAI balance of the avatar safe')
    safe_EURe_balance = Gauge('safe_EURe_balance', 'EURe balance of the avatar safe')
    amount_WXDAI = Gauge('amount_WXDAI', 'Amount of WXDAI to swap')
    amount_EURe= Gauge('amount_EURe', 'Amount of EURe to swap')
    drift_threshold = Gauge('drift_threshold', 'Drift threshold')
    drift_EURe_to_WXDAI = Gauge('EURe_to_WXDAI_drift', 'EURe to WXDAI drift')
    drift_WXDAI_to_EURe = Gauge('WXDAI_to_EURe_drift', 'WXDAI to EURe drift')
    last_updated = Gauge('last_updated', 'Last updated time and date')