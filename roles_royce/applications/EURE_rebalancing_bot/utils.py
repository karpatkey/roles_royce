from dataclasses import dataclass, field
from decouple import config
from web3.types import Address, ChecksumAddress
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
import logging


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
    FIXER_API_ACCESS_KEY: float = config('FIXER_API_ACCESS_KEY', cast=str)
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
    STATUS_NOTIFICATION_HOUR: int = custom_config('STATUS_NOTIFICATION_HOUR', default=12, cast=int)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    ATTRIBUTE_NAMES = {
        'RPC_ENDPOINT': 'RPC_ENDPOINT',
        'AVATAR_SAFE_ADDRESS': 'AVATAR_SAFE_ADDRESS',
        'ROLES_MOD_ADDRESS': 'ROLES_MOD_ADDRESS',
        'ROLE': 'ROLE',
        'PRIVATE_KEY': 'PRIVATE_KEY',
        'FIXER_API_ACCESS_KEY': 'FIXER_API_ACCESS_KEY',
        'MAX_SLIPPAGE': 'MAX_SLIPPAGE',
        'DRIFT_THRESHOLD': 'DRIFT_THRESHOLD',
        'AMOUNT': 'AMOUNT',
        'COOLDOWN_MINUTES': 'COOLDOWN_MINUTES',
        'SLACK_WEBHOOK_URL': 'SLACK_WEBHOOK_URL',
        'TELEGRAM_BOT_TOKEN': 'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID': 'TELEGRAM_CHAT_ID',
        'PROMETHEUS_PORT': 'PROMETHEUS_PORT',
        'TEST_MODE': 'TEST_MODE',
        'LOCAL_FORK_PORT': 'LOCAL_FORK_PORT',
        'STATUS_NOTIFICATION_HOUR': 'STATUS_NOTIFICATION_HOUR'
    }

    MANDATORY_ATTRIBUTES = ['RPC_ENDPOINT', 'AVATAR_SAFE_ADDRESS', 'ROLES_MOD_ADDRESS', 'ROLE', 'PRIVATE_KEY',
                            'DRIFT_THRESHOLD', 'AMOUNT']

    @classmethod
    def get_attribute_name(cls, attribute):
        return cls.ATTRIBUTE_NAMES.get(attribute, 'Unknown')

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

    def __repr__(self):
        return 'Environment variables'


logger = logging.getLogger(__name__)
