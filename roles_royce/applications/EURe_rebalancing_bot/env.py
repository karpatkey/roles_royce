import json
from dataclasses import dataclass, field

from decouple import config
from web3 import Web3
from web3.types import ChecksumAddress

from roles_royce.applications.utils import check_env_endpoints, custom_config, to_dict
from roles_royce.protocols.base import Address


@dataclass
class ENV:
    TEST_MODE: bool = field(init=False)
    LOCAL_FORK_HOST: str = field(init=False)
    LOCAL_FORK_PORT: int = field(init=False)
    RPC_ENDPOINT: str = field(init=False)
    RPC_ENDPOINT_FALLBACK: str = field(init=False)
    RPC_ENDPOINT_EXECUTION: str = field(init=False)
    AVATAR_SAFE_ADDRESS: Address | ChecksumAddress | str = field(init=False)
    ROLES_MOD_ADDRESS: Address | ChecksumAddress | str = field(init=False)
    ROLE: int = field(init=False)
    PRIVATE_KEY: str = field(init=False)
    FIXER_API_ACCESS_KEY: str = field(init=False)
    MAX_SLIPPAGE: float = field(init=False)
    DRIFT_THRESHOLD: float = field(init=False)
    AMOUNT: float = field(init=False)
    COOLDOWN_MINUTES: int = field(init=False)
    SLACK_WEBHOOK_URL: str = field(init=False)
    TELEGRAM_BOT_TOKEN: str = field(init=False)
    TELEGRAM_CHAT_ID: int = field(init=False)
    PROMETHEUS_PORT: int = field(init=False)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    def __post_init__(self):
        self.TEST_MODE = config("TEST_MODE", default=True, cast=bool)
        self.LOCAL_FORK_HOST = custom_config("LOCAL_FORK_HOST", default="localhost", cast=str)
        self.LOCAL_FORK_PORT = custom_config("LOCAL_FORK_PORT", default=8545, cast=int)
        if self.TEST_MODE:
            self.RPC_ENDPOINT = f"http://{self.LOCAL_FORK_HOST}:{self.LOCAL_FORK_PORT}"
            self.RPC_ENDPOINT_FALLBACK = f"http://{self.LOCAL_FORK_HOST}:{self.LOCAL_FORK_PORT}"
            self.RPC_ENDPOINT_EXECUTION = f"http://{self.LOCAL_FORK_HOST}:{self.LOCAL_FORK_PORT}"
        else:
            self.RPC_ENDPOINT = config("RPC_ENDPOINT", default="", cast=str)
            self.RPC_ENDPOINT_FALLBACK = custom_config("RPC_ENDPOINT_FALLBACK", default="", cast=str)
            self.RPC_ENDPOINT_EXECUTION = custom_config("RPC_ENDPOINT_MEV", default="", cast=str)

        check_env_endpoints([(self.RPC_ENDPOINT, self.RPC_ENDPOINT_FALLBACK)])

        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(config("AVATAR_SAFE_ADDRESS", cast=str))
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(config("ROLES_MOD_ADDRESS", cast=str))
        self.ROLE = config("ROLE", cast=int)
        self.PRIVATE_KEY = custom_config("PRIVATE_KEY", default="", cast=str)
        self.FIXER_API_ACCESS_KEY = custom_config("FIXER_API_ACCESS_KEY", default="", cast=str)
        self.MAX_SLIPPAGE = custom_config("MAX_SLIPPAGE", default=0.01, cast=float)
        self.DRIFT_THRESHOLD = config("DRIFT_THRESHOLD", cast=float)
        self.AMOUNT = config("AMOUNT", cast=float)
        self.COOLDOWN_MINUTES = custom_config("COOLDOWN_MINUTES", default=5, cast=int)
        self.SLACK_WEBHOOK_URL = custom_config("SLACK_WEBHOOK_URL", default="", cast=str)
        self.TELEGRAM_BOT_TOKEN = custom_config("TELEGRAM_BOT_TOKEN", default="", cast=str)
        self.TELEGRAM_CHAT_ID = custom_config("TELEGRAM_CHAT_ID", default="", cast=int)
        self.PROMETHEUS_PORT = custom_config("PROMETHEUS_PORT", default=8000, cast=int)
        self.LOCAL_FORK_PORT = custom_config("LOCAL_FORK_PORT", default=8545, cast=int)

        if self.PRIVATE_KEY != "":
            self.BOT_ADDRESS = Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).eth.account.from_key(self.PRIVATE_KEY).address
        else:
            self.BOT_ADDRESS = config("BOT_ADDRESS", default="")
            if self.BOT_ADDRESS == "":
                raise ValueError("Either PRIVATE_KEY or BOT_ADDRESS must be provided.")

    def __str__(self):
        return json.dumps(to_dict(self, exclude_key="PRIVATE_KEY"), indent=4)
