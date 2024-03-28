import json
from dataclasses import dataclass, field

from decouple import config
from web3 import Web3
from web3.types import Address, ChecksumAddress

from roles_royce.applications.utils import check_env_endpoints, custom_config, to_dict
from tests.utils import fork_unlock_account


@dataclass
class ENV:
    TEST_MODE: bool = field(init=False)
    LOCAL_FORK_HOST_ETHEREUM: str = field(init=False)
    LOCAL_FORK_PORT_ETHEREUM: int = field(init=False)
    LOCAL_FORK_HOST_GNOSIS: str = field(init=False)
    LOCAL_FORK_PORT_GNOSIS: int = field(init=False)

    RPC_ENDPOINT_ETHEREUM: str = field(init=False)
    RPC_ENDPOINT_ETHEREUM_FALLBACK: str = field(init=False)
    RPC_ENDPOINT_ETHEREUM_EXECUTION: str = field(init=False)
    RPC_ENDPOINT_GNOSIS: str = field(init=False)
    RPC_ENDPOINT_GNOSIS_FALLBACK: str = field(init=False)
    RPC_ENDPOINT_GNOSIS_EXECUTION: str = field(init=False)

    PRIVATE_KEY: str = field(init=False)
    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    COOLDOWN_MINUTES: float = field(init=False)
    SLACK_WEBHOOK_URL: str = field(init=False)
    TELEGRAM_BOT_TOKEN: str = field(init=False)
    TELEGRAM_CHAT_ID: int = field(init=False)
    PROMETHEUS_PORT: int = field(init=False)

    REFILL_THRESHOLD: float = field(init=False)
    INVEST_THRESHOLD: float = field(init=False)
    GAS_ETH_THRESHOLD: float = field(init=False)
    MINUTES_BEFORE_CLAIM_EPOCH: int = field(init=False)
    AMOUNT_OF_INTEREST_TO_PAY: float = field(init=False)

    def __post_init__(self):
        self.TEST_MODE = config("TEST_MODE", default=True, cast=bool)
        self.LOCAL_FORK_HOST_ETHEREUM = custom_config("LOCAL_FORK_HOST_ETHEREUM", default="localhost", cast=str)
        self.LOCAL_FORK_PORT_ETHEREUM = custom_config("LOCAL_FORK_PORT_ETHEREUM", default=8545, cast=int)
        self.LOCAL_FORK_HOST_GNOSIS = custom_config("LOCAL_FORK_HOST_GNOSIS", default="localhost", cast=str)
        self.LOCAL_FORK_PORT_GNOSIS = custom_config("LOCAL_FORK_PORT_GNOSIS", default=8546, cast=int)
        if self.TEST_MODE:
            self.RPC_ENDPOINT_ETHEREUM = f"http://{self.LOCAL_FORK_HOST_ETHEREUM}:{self.LOCAL_FORK_PORT_ETHEREUM}"
            self.RPC_ENDPOINT_ETHEREUM_FALLBACK = (
                f"http://{self.LOCAL_FORK_HOST_ETHEREUM}:{self.LOCAL_FORK_PORT_ETHEREUM}"
            )
            self.RPC_ENDPOINT_ETHEREUM_EXECUTION = (
                f"http://{self.LOCAL_FORK_HOST_ETHEREUM}:{self.LOCAL_FORK_PORT_ETHEREUM}"
            )
            self.RPC_ENDPOINT_GNOSIS = f"http://{self.LOCAL_FORK_HOST_GNOSIS}:{self.LOCAL_FORK_PORT_GNOSIS}"
            self.RPC_ENDPOINT_GNOSIS_FALLBACK = f"http://{self.LOCAL_FORK_HOST_GNOSIS}:{self.LOCAL_FORK_PORT_GNOSIS}"
            self.RPC_ENDPOINT_GNOSIS_EXECUTION = f"http://{self.LOCAL_FORK_HOST_GNOSIS}:{self.LOCAL_FORK_PORT_GNOSIS}"
        else:
            self.RPC_ENDPOINT_ETHEREUM = config("RPC_ENDPOINT_ETHEREUM", default="", cast=str)
            self.RPC_ENDPOINT_ETHEREUM_FALLBACK = custom_config("RPC_ENDPOINT_ETHEREUM_FALLBACK", default="", cast=str)
            self.RPC_ENDPOINT_ETHEREUM_EXECUTION = custom_config(
                "RPC_ENDPOINT_ETHEREUM_EXECUTION", default="", cast=str
            )
            self.RPC_ENDPOINT_GNOSIS = config("RPC_ENDPOINT_GNOSIS", default="", cast=str)
            self.RPC_ENDPOINT_GNOSIS_FALLBACK = custom_config("RPC_ENDPOINT_GNOSIS_FALLBACK", default="", cast=str)
            self.RPC_ENDPOINT_GNOSIS_EXECUTION = custom_config("RPC_ENDPOINT_GNOSIS_EXECUTION", default="", cast=str)

        check_env_endpoints(
            [
                (self.RPC_ENDPOINT_ETHEREUM, self.RPC_ENDPOINT_ETHEREUM_FALLBACK),
                (self.RPC_ENDPOINT_GNOSIS, self.RPC_ENDPOINT_GNOSIS_FALLBACK),
            ]
        )

        self.PRIVATE_KEY = custom_config("PRIVATE_KEY", default="", cast=str)

        if self.TEST_MODE is False and self.PRIVATE_KEY == "":
            raise ValueError("PRIVATE_KEY must be provided in production mode (TEST_MODE=False).")

        if self.PRIVATE_KEY != "":
            self.BOT_ADDRESS = (
                Web3(Web3.HTTPProvider(self.RPC_ENDPOINT_ETHEREUM)).eth.account.from_key(self.PRIVATE_KEY).address
            )
        else:
            self.BOT_ADDRESS = config("BOT_ADDRESS", default="")
            if self.BOT_ADDRESS == "":
                raise ValueError("Either PRIVATE_KEY or BOT_ADDRESS must be provided.")
            fork_unlock_account(
                w3=Web3(
                    Web3.HTTPProvider(f"http://{self.LOCAL_FORK_HOST_ETHEREUM}:" f"{self.LOCAL_FORK_PORT_ETHEREUM}")
                ),
                address=self.BOT_ADDRESS,
            )

        self.COOLDOWN_MINUTES = custom_config("COOLDOWN_MINUTES", default=5, cast=float)
        self.SLACK_WEBHOOK_URL = custom_config("SLACK_WEBHOOK_URL", default="", cast=str)
        self.TELEGRAM_BOT_TOKEN = custom_config("TELEGRAM_BOT_TOKEN", default="", cast=str)
        self.TELEGRAM_CHAT_ID = custom_config("TELEGRAM_CHAT_ID", default="", cast=int)
        self.PROMETHEUS_PORT = custom_config("PROMETHEUS_PORT", default=8000, cast=int)

        self.REFILL_THRESHOLD = config("REFILL_THRESHOLD", cast=float)
        self.INVEST_THRESHOLD = config("INVEST_THRESHOLD", cast=float)
        self.GAS_ETH_THRESHOLD = custom_config("GAS_ETH_THRESHOLD", default=0.5, cast=float)
        self.MINUTES_BEFORE_CLAIM_EPOCH = custom_config("MINUTES_BEFORE_CLAIM_EPOCH", default=90, cast=int)
        self.AMOUNT_OF_INTEREST_TO_PAY = config("AMOUNT_OF_INTEREST_TO_PAY", cast=float)

    def __str__(self):
        return json.dumps(to_dict(self, exclude_key="PRIVATE_KEY"), separators=(",", ":"))
