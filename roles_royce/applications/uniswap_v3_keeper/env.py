import json
from dataclasses import dataclass, field
from roles_royce.applications.utils import custom_config, config
from web3.types import Address, ChecksumAddress
from web3 import Web3
from roles_royce.protocols.uniswap_v3.types_and_enums import FeeAmount
from roles_royce.applications.utils import to_dict


@dataclass
class ENV:
    RPC_ENDPOINT: str = field(init=False)
    RPC_ENDPOINT_FALLBACK: str = field(init=False)
    RPC_ENDPOINT_MEV: str = field(init=False)
    PRIVATE_KEY: str = field(init=False)
    AVATAR_SAFE_ADDRESS: Address | ChecksumAddress | str = field(init=False)
    ROLES_MOD_ADDRESS: Address | ChecksumAddress | str = field(init=False)
    ROLE: int = field(init=False)
    COOLDOWN_MINUTES: float = field(init=False)
    SLACK_WEBHOOK_URL: str = field(init=False)
    TELEGRAM_BOT_TOKEN: str = field(init=False)
    TELEGRAM_CHAT_ID: int = field(init=False)
    PROMETHEUS_PORT: int = field(init=False)
    TEST_MODE: bool = field(init=False)
    LOCAL_FORK_HOST: int = field(init=False)
    LOCAL_FORK_PORT: int = field(init=False)
    TOKEN0_ADDRESS: Address | ChecksumAddress | str = field(init=False)
    TOKEN1_ADDRESS: Address | ChecksumAddress | str = field(init=False)
    FEE: FeeAmount = field(init=False)
    INITIAL_MIN_PRICE: float = field(init=False)
    INITIAL_MAX_PRICE: float = field(init=False)
    INITIAL_AMOUNT0: float | None = field(init=False)
    INITIAL_AMOUNT1: float | None = field(init=False)
    PRICE_RANGE_THRESHOLD: float = field(init=False)
    PRICE_DELTA_MULTIPLIER: float = field(init=False)
    MINIMUM_MIN_PRICE: float = field(init=False)
    MINTING_SLIPPAGE_PERCENTAGE: float = field(init=False)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    def __post_init__(self):
        self.TEST_MODE = config("TEST_MODE", default=True, cast=bool)
        self.LOCAL_FORK_HOST = custom_config("LOCAL_FORK_HOST", default='localhost', cast=str)
        self.LOCAL_FORK_PORT = custom_config("LOCAL_FORK_PORT", default=8545, cast=int)
        if self.TEST_MODE:
            self.RPC_ENDPOINT = f"http://{self.LOCAL_FORK_HOST}:{self.LOCAL_FORK_PORT}"
            self.RPC_ENDPOINT_FALLBACK = f"http://{self.LOCAL_FORK_HOST}:{self.LOCAL_FORK_PORT}"
            self.RPC_ENDPOINT_MEV = f"http://{self.LOCAL_FORK_HOST}:{self.LOCAL_FORK_PORT}"
        else:
            self.RPC_ENDPOINT = config("RPC_ENDPOINT", default="", cast=str)
            self.RPC_ENDPOINT_FALLBACK = custom_config("RPC_ENDPOINT_FALLBACK", default="", cast=str)
            self.RPC_ENDPOINT_MEV = custom_config("RPC_ENDPOINT_MEV", default="", cast=str)
        self.PRIVATE_KEY = custom_config("PRIVATE_KEY", default="", cast=str)
        self.AVATAR_SAFE_ADDRESS = config("AVATAR_SAFE_ADDRESS", default="")
        self.ROLES_MOD_ADDRESS = config("ROLES_MOD_ADDRESS", default="")
        self.ROLE = config("ROLE", cast=int)
        self.COOLDOWN_MINUTES = custom_config("COOLDOWN_MINUTES", default=5, cast=float)
        self.SLACK_WEBHOOK_URL = custom_config("SLACK_WEBHOOK_URL", default="", cast=str)
        self.TELEGRAM_BOT_TOKEN = custom_config("TELEGRAM_BOT_TOKEN", default="", cast=str)
        self.TELEGRAM_CHAT_ID = custom_config("TELEGRAM_CHAT_ID", default="", cast=int)
        self.PROMETHEUS_PORT = custom_config("PROMETHEUS_PORT", default=8000, cast=int)
        self.TOKEN0_ADDRESS = config("TOKEN0_ADDRESS", default="", cast=str)
        self.TOKEN1_ADDRESS = config("TOKEN1_ADDRESS", default="", cast=str)
        self.FEE = config("FEE", default=3000, cast=int)
        self.INITIAL_MIN_PRICE = custom_config("INITIAL_MIN_PRICE", default=None, cast=float)
        self.INITIAL_MAX_PRICE = custom_config("INITIAL_MAX_PRICE", default=None, cast=float)
        self.INITIAL_AMOUNT0 = custom_config("INITIAL_AMOUNT0", default=None, cast=float)
        self.INITIAL_AMOUNT1 = custom_config("INITIAL_AMOUNT1", default=None, cast=float)
        self.PRICE_RANGE_THRESHOLD = config("PRICE_RANGE_THRESHOLD", default=10, cast=float)
        self.PRICE_DELTA_MULTIPLIER = config("PRICE_DELTA_MULTIPLIER", default=5, cast=float)
        self.MINIMUM_MIN_PRICE = config("MINIMUM_MIN_PRICE", cast=float)
        self.MINTING_SLIPPAGE_PERCENTAGE = custom_config("MINTING_SLIPPAGE_PERCENTAGE", default=0.5, cast=float)

        if not self.TEST_MODE:
            if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).is_connected():
                raise ValueError(
                    f"RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT}."
                )
            if self.RPC_ENDPOINT_FALLBACK != "":
                if not Web3(
                        Web3.HTTPProvider(self.RPC_ENDPOINT_FALLBACK)
                ).is_connected():
                    raise ValueError(
                        f"FALLBACK_RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT_FALLBACK}."
                    )
            if self.RPC_ENDPOINT_MEV != "":
                if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_MEV)).is_connected():
                    self.RPC_ENDPOINT_MEV = self.RPC_ENDPOINT
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        self.TOKEN0_ADDRESS = Web3.to_checksum_address(self.TOKEN0_ADDRESS)
        self.TOKEN1_ADDRESS = Web3.to_checksum_address(self.TOKEN1_ADDRESS)

        if self.FEE not in [FeeAmount.LOWEST, FeeAmount.LOW, FeeAmount.MEDIUM, FeeAmount.HIGH]:
            raise ValueError(
                f"FEE must be one of the following: {FeeAmount.LOWEST}, {FeeAmount.LOW}, {FeeAmount.MEDIUM}, {FeeAmount.HIGH}. FEE inputted: {self.FEE}."
            )

        if not 0 <= self.PRICE_RANGE_THRESHOLD <= 100:
            raise ValueError(
                f"PRICE_RANGE_THRESHOLD must be between 0 and 100. MAX_PRICE_THRESHOLD inputted: {self.PRICE_RANGE_THRESHOLD}."
            )
        if self.PRICE_DELTA_MULTIPLIER <= 1:
            raise ValueError(
                f"PRICE_DELTA_MULTIPLIER must be greater than 1. PRICE_DELTA_MULTIPLIER inputted: {self.PRICE_DELTA_MULTIPLIER}."
            )

        if self.MINTING_SLIPPAGE_PERCENTAGE <= 0:
            raise ValueError(
                f"MINTING_SLIPPAGE_PERCENTAGE must be greater than 0. MINTING_SLIPPAGE_PERCENTAGE inputted: {self.MINTING_SLIPPAGE_PERCENTAGE}."
            )
        if not 0 < self.MINTING_SLIPPAGE_PERCENTAGE < 100:
            raise ValueError(
                f"MINTING_SLIPPAGE_PERCENTAGE must be between 0 and 100. MINTING_SLIPPAGE_PERCENTAGE inputted: {self.MINTING_SLIPPAGE_PERCENTAGE}."
            )

        if self.PRIVATE_KEY != "":
            self.BOT_ADDRESS = Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).eth.account.from_key(self.PRIVATE_KEY).address
        else:
            self.BOT_ADDRESS = config("BOT_ADDRESS", default="")
            if self.BOT_ADDRESS == "":
                raise ValueError("Either PRIVATE_KEY or BOT_ADDRESS must be provided.")

    def __str__(self):
        return json.dumps(to_dict(self, exclude_key="PRIVATE_KEY"), indent=4)