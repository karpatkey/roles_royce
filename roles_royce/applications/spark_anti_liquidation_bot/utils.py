from dataclasses import dataclass, field
from decouple import config
from web3.types import Address, ChecksumAddress
from web3 import Web3


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
    TELEGRAM_CHAT_ID = config('TELEGRAM_CHAT_ID', default='')
    PROMETHEUS_PORT: int = custom_config('PROMETHEUS_PORT', default=8000, cast=int)
    TEST_MODE: bool = config('TEST_MODE', default=False, cast=bool)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    ATTRIBUTE_NAMES = {
        'RPC_ENDPOINT': 'RPC_ENDPOINT',
        'AVATAR_SAFE_ADDRESS': 'AVATAR_SAFE_ADDRESS',
        'ROLES_MOD_ADDRESS': 'ROLES_MOD_ADDRESS',
        'ROLE': 'ROLE',
        'PRIVATE_KEY': 'PRIVATE_KEY',
        'TARGET_HEALTH_FACTOR': 'TARGET_HEALTH_FACTOR',
        'ALERTING_HEALTH_FACTOR': 'ALERTING_HEALTH_FACTOR',
        'THRESHOLD_HEALTH_FACTOR': 'THRESHOLD_HEALTH_FACTOR',
        'TOLERANCE': 'TOLERANCE',
        'COOLDOWN_MINUTES': 'COOLDOWN_MINUTES',
        'SLACK_WEBHOOK_URL': 'SLACK_WEBHOOK_URL',
        'TELEGRAM_BOT_TOKEN': 'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID': 'TELEGRAM_CHAT_ID',
        'PROMETHEUS_PORT': 'PROMETHEUS_PORT',
        'TEST_MODE': 'TEST_MODE'
    }

    MANDATORY_ATTRIBUTES = ['RPC_ENDPOINT', 'AVATAR_SAFE_ADDRESS', 'ROLES_MOD_ADDRESS', 'ROLE', 'PRIVATE_KEY',
                            'TARGET_HEALTH_FACTOR', 'THRESHOLD_HEALTH_FACTOR']

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