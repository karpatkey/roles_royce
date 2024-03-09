import json
from dataclasses import dataclass, field, fields
from roles_royce.applications.utils import custom_config, config
from web3.types import Address, ChecksumAddress, TxReceipt
from web3 import Web3
from defabipedia.tokens import erc20_contract
from roles_royce import roles
from roles_royce.protocols.uniswap_v3.types_and_enums import FeeAmount
from roles_royce.protocols.uniswap_v3.methods_general import mint_nft, decrease_liquidity_nft
from roles_royce.protocols.uniswap_v3.utils import NFTPosition
from roles_royce.applications.utils import to_dict


@dataclass
class ENV:
    RPC_ENDPOINT: str = config("RPC_ENDPOINT", default="")
    RPC_ENDPOINT_FALLBACK: str = config("RPC_ENDPOINT_FALLBACK", default="")
    RPC_ENDPOINT_MEV: str = config("RPC_ENDPOINT_MEV", default="")
    PRIVATE_KEY: str = config("PRIVATE_KEY", default="")
    AVATAR_SAFE_ADDRESS: Address | ChecksumAddress | str = config("AVATAR_SAFE_ADDRESS", default="")
    ROLES_MOD_ADDRESS: Address | ChecksumAddress | str = config("ROLES_MOD_ADDRESS", default="")
    ROLE: int = config("ROLE", cast=int)
    COOLDOWN_MINUTES: float = custom_config("COOLDOWN_MINUTES", default=5, cast=float)
    SLACK_WEBHOOK_URL: str = config("SLACK_WEBHOOK_URL", default="")
    TELEGRAM_BOT_TOKEN: str = config("TELEGRAM_BOT_TOKEN", default="")
    TELEGRAM_CHAT_ID: int = custom_config("TELEGRAM_CHAT_ID", default="", cast=int)
    PROMETHEUS_PORT: int = custom_config("PROMETHEUS_PORT", default=8000, cast=int)
    TEST_MODE: bool = config("TEST_MODE", default=True, cast=bool)
    LOCAL_FORK_HOST: int = custom_config("LOCAL_FORK_HOST", default='localhost', cast=str)
    LOCAL_FORK_PORT: int = custom_config("LOCAL_FORK_PORT", default=8545, cast=int)
    TOKEN0_ADDRESS: Address | ChecksumAddress | str = config("TOKEN0_ADDRESS", default="", cast=str)
    TOKEN1_ADDRESS: Address | ChecksumAddress | str = config("TOKEN1_ADDRESS", default="", cast=str)
    FEE: FeeAmount = config("FEE", default=3000, cast=int)
    INITIAL_MIN_PRICE: float = custom_config("INITIAL_MIN_PRICE", default=None, cast=float)
    INITIAL_MAX_PRICE: float = custom_config("INITIAL_MAX_PRICE", default=None, cast=float)
    INITIAL_AMOUNT0: float | None = custom_config("INITIAL_AMOUNT0", default=None, cast=float)
    INITIAL_AMOUNT1: float | None = custom_config("INITIAL_AMOUNT1", default=None, cast=float)
    PRICE_RANGE_THRESHOLD: float = config("PRICE_RANGE_THRESHOLD", default=10, cast=float)
    PRICE_DELTA_MULTIPLIER: float = config("PRICE_DELTA_MULTIPLIER", default=5, cast=float)
    MINIMUM_MIN_PRICE: float = config("MINIMUM_MIN_PRICE", cast=float)
    MINTING_SLIPPAGE_PERCENTAGE: float = custom_config("MINTING_SLIPPAGE_PERCENTAGE", default=0.5, cast=float)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    def __post_init__(self):
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


@dataclass
class StaticData:
    env: ENV
    token0_decimals: int = field(init=False)
    token1_decimals: int = field(init=False)

    def __post_init__(self):
        if self.env.TEST_MODE:
            w3 = Web3(Web3.HTTPProvider(f"http://{self.env.LOCAL_FORK_HOST}:{self.env.LOCAL_FORK_PORT}"))
        else:
            w3 = Web3(Web3.HTTPProvider(self.env.RPC_ENDPOINT))
        self.token0_decimals = erc20_contract(w3, self.env.TOKEN0_ADDRESS).functions.decimals().call()
        self.token1_decimals = erc20_contract(w3, self.env.TOKEN1_ADDRESS).functions.decimals().call()

    def __str__(self):
        return json.dumps(to_dict(self, exclude_key="PRIVATE_KEY"), indent=4)


@dataclass
class DynamicData:
    nft_id: int
    bot_ETH_balance: int
    safe_token0_balance: int
    safe_token1_balance: int
    token0_balance: int
    token1_balance: int
    price_min: float
    price_max: float
    price: float

    def check_triggering_condition(self, static_data: StaticData) -> bool:
        if (self.price - self.price_min) / (
                self.price_max - self.price_min) < static_data.env.PRICE_RANGE_THRESHOLD / 100:
            return True
        elif (self.price_max - self.price) / (
                self.price_max - self.price_min) < static_data.env.PRICE_RANGE_THRESHOLD / 100:
            return True
        else:
            return False

    def __str__(self):
        return json.dumps(to_dict(self), indent=4)


def update_dynamic_data(w3: Web3, nft_id: int, static_data: StaticData) -> DynamicData:
    nft_position = NFTPosition(w3, nft_id)
    balances = nft_position.get_balances()
    return DynamicData(
        nft_id=nft_id,
        bot_ETH_balance=w3.eth.get_balance(static_data.env.BOT_ADDRESS),
        safe_token0_balance=erc20_contract(w3, static_data.env.TOKEN0_ADDRESS)
        .functions.balanceOf(static_data.env.AVATAR_SAFE_ADDRESS).call(),
        safe_token1_balance=erc20_contract(w3, static_data.env.TOKEN1_ADDRESS)
        .functions.balanceOf(static_data.env.AVATAR_SAFE_ADDRESS).call(),
        token0_balance=balances[0],
        token1_balance=balances[1],
        price_min=float(nft_position.price_min),
        price_max=float(nft_position.price_max),
        price=float(nft_position.pool.price)
    )


@dataclass
class TransactionsManager:
    avatar: Address | ChecksumAddress | str
    roles_mod: Address | ChecksumAddress | str
    role: int
    private_key: str

    def collect_fees_and_disassemble_position(self, w3: Web3, nft_id: int) -> TxReceipt:
        decrease_liquidity_transactables = decrease_liquidity_nft(
            w3=w3,
            recipient=self.avatar,
            nft_id=nft_id,
            removed_liquidity_percentage=100,
            amount0_min_slippage=10,
            amount1_min_slippage=10,
            withdraw_eth=False
        )

        return roles.send(
            decrease_liquidity_transactables,
            role=self.role,
            private_key=self.private_key,
            roles_mod_address=self.roles_mod,
            web3=w3
        )

    def mint_nft(self, w3: Web3, amount0: int | None, amount1: int | None,
                 price_min: float, price_max: float, static_data: StaticData) -> TxReceipt:
        mint_transactables = mint_nft(
            w3=w3,
            avatar=self.avatar,
            token0=static_data.env.TOKEN0_ADDRESS,
            token1=static_data.env.TOKEN1_ADDRESS,
            fee=static_data.env.FEE,
            token0_min_price=price_min,
            token0_max_price=price_max,
            amount0_desired=amount0,
            amount1_desired=amount1,
            amount0_min_slippage=static_data.env.MINTING_SLIPPAGE_PERCENTAGE,
            amount1_min_slippage=static_data.env.MINTING_SLIPPAGE_PERCENTAGE,
        )

        return roles.send(
            mint_transactables,
            role=self.role,
            private_key=self.private_key,
            roles_mod_address=self.roles_mod,
            web3=w3,
        )
