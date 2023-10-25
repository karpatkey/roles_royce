from dataclasses import dataclass, field

from decouple import config
from web3 import Web3
from web3.types import Address, ChecksumAddress


# The next helper function allows to leave variables unfilled in the .env file
def custom_config(variable, default, cast):
    value = config(variable, default=default)
    return default if value == '' else config(variable, default=default, cast=cast)


@dataclass
class ENV:
    RPC_ENDPOINT: str = config('RPC_ENDPOINT')
    FALLBACK_RPC_ENDPOINT: str = config('FALLBACK_RPC_ENDPOINT', default='')

    THRESHOLD_HEALTH_FACTOR: float = config('THRESHOLD_HEALTH_FACTOR', cast=float)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    # Path to bigquery credentials file (json) to get the list of addresses to monitor
    BIGQUERY_CREDENTIALS_PATH: str = config('BIGQUERY_CREDENTIALS_PATH')

    # I left all of these down below in case you need them for the actual bot. 
    AVATAR_SAFE_ADDRESS: Address | ChecksumAddress | str = config('AVATAR_SAFE_ADDRESS')
    ROLES_MOD_ADDRESS: Address | ChecksumAddress | str = config('ROLES_MOD_ADDRESS')
    ROLE: int = config('ROLE', cast=int)
    PRIVATE_KEY: str = config('PRIVATE_KEY')
    
    TOLERANCE: float = custom_config('TOLERANCE', default=0.01, cast=float)
    COOLDOWN_MINUTES: int = custom_config('COOLDOWN_MINUTES', default=5, cast=int)
    ADDRESS_UPDATE_INTERVAL: int = custom_config('ADDRESS_UPDATE_INTERVAL', default=5, cast=int)
    SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
    TELEGRAM_BOT_TOKEN: str = config('TELEGRAM_BOT_TOKEN', default='')
    TELEGRAM_CHAT_ID: int = custom_config('TELEGRAM_CHAT_ID', default='', cast=int)
    PROMETHEUS_PORT: int = custom_config('PROMETHEUS_PORT', default=8000, cast=int)
  

    def __post_init__(self):
        # self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        # self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).is_connected():
            raise ValueError(f"RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT}.")
        if self.FALLBACK_RPC_ENDPOINT != '':
            if not Web3(Web3.HTTPProvider(self.FALLBACK_RPC_ENDPOINT)).is_connected():
                raise ValueError(f"FALLBACK_RPC_ENDPOINT is not valid or not active: {self.FALLBACK_RPC_ENDPOINT}.")
        self.BOT_ADDRESS = Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).eth.account.from_key(self.PRIVATE_KEY).address

    def __repr__(self):
        return 'Environment variables'
    

