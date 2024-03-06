from decimal import Decimal
from dataclasses import dataclass, field
import threading
from datetime import datetime
from prometheus_client import Gauge
from decouple import config
from web3.types import Address, ChecksumAddress, TxReceipt
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
import logging
from defabipedia.uniswap_v3 import ContractSpecs
from defabipedia.types import Chain
from defabipedia.tokens import erc20_contract

from roles_royce import roles
from roles_royce.toolshed.alerting.utils import Event, EventLogDecoder
from roles_royce.protocols.uniswap_v3.methods_general import (
    mint_nft,
    decrease_liquidity_nft,
)
from roles_royce.protocols.uniswap_v3.utils import NFTPosition

logger = logging.getLogger(__name__)


# The next helper function allows to leave variables unfilled in the .env file
def custom_config(variable, default, cast):
    value = config(variable, default=default)
    return default if value == "" else config(variable, default=default, cast=cast)


@dataclass
class ENV:
    RPC_ENDPOINT: str = config("RPC_ENDPOINT", default="")
    RPC_ENDPOINT_FALLBACK: str = config("RPC_ENDPOINT_FALLBACK", default="")
    RPC_ENDPOINT_MEV: str = config("RPC_ENDPOINT_MEV", default="")
    PRIVATE_KEY: str = config("PRIVATE_KEY", default="")
    AVATAR_SAFE_ADDRESS: Address | ChecksumAddress | str = config(
        "AVATAR_SAFE_ADDRESS", default=""
    )
    ROLES_MOD_ADDRESS: Address | ChecksumAddress | str = config(
        "ROLES_MOD_ADDRESS", default=""
    )
    ROLE: int = custom_config("ROLE", default="", cast=int)
    COOLDOWN_MINUTES: float = custom_config("COOLDOWN_MINUTES", default=5, cast=float)
    SLACK_WEBHOOK_URL: str = config("SLACK_WEBHOOK_URL", default="")
    TELEGRAM_BOT_TOKEN: str = config("TELEGRAM_BOT_TOKEN", default="")
    TELEGRAM_CHAT_ID: int = custom_config("TELEGRAM_CHAT_ID", default="", cast=int)
    PROMETHEUS_PORT: int = custom_config("PROMETHEUS_PORT", default=8000, cast=int)
    TEST_MODE: bool = config("TEST_MODE", default=True, cast=bool)
    LOCAL_FORK_PORT: int = custom_config("LOCAL_FORK_PORT", default=8545, cast=int)
    TOKEN0_ADDRESS: Address | ChecksumAddress | str = config(
        "TOKEN0_ADDRESS", default="", cast=str
    )
    TOKEN1_ADDRESS: Address | ChecksumAddress | str = config(
        "TOKEN1_ADDRESS", default="", cast=str
    )
    FEE: int = custom_config("FEE", default=3000, cast=int)
    MIN_PRICE_THRESHOLD: float = custom_config(
        "MIN_PRICE_THRESHOLD", default=10, cast=float
    )
    MAX_PRICE_THRESHOLD: float = custom_config(
        "MAX_PRICE_THRESHOLD", default=10, cast=float
    )
    PRICE_RANGE_MULTIPLICATOR_SEED: float = custom_config(
        "NEW_PRICE_RANGE_DELTA_PERCENTAGE_SEED", default=5, cast=float
    )
    PRICE_RANGE_MULTIPLICATOR_PERCENTUAL_DECREMENT: float = custom_config(
        "NEW_PRICE_RANGE_DELTA_PERCENTAGE_DECREMENT", default=0.5, cast=float
    )

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)
    TOKEN0_DECIMALS: int = field(init=False)
    TOKEN1_DECIMALS: int = field(init=False)

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
        # TODO: add check for correct FEES
        if not 0 <= self.MIN_PRICE_THRESHOLD <= 100:
            raise ValueError(
                f"MIN_PRICE_THRESHOLD must be between 0 and 100. MIN_PRICE_THRESHOLD inputted: {self.MIN_PRICE_THRESHOLD}."
            )
        if not 0 <= self.MAX_PRICE_THRESHOLD <= 100:
            raise ValueError(
                f"MAX_PRICE_THRESHOLD must be between 0 and 100. MAX_PRICE_THRESHOLD inputted: {self.MAX_PRICE_THRESHOLD}."
            )
        if self.PRICE_RANGE_MULTIPLICATOR_SEED <= 1:
            raise ValueError(
                f"PRICE_RANGE_MULTIPLICATOR_SEED must be greater than 1. PRICE_RANGE_MULTIPLICATOR_SEED inputted: {self.PRICE_RANGE_MULTIPLICATOR_SEED}."
            )
        if not 0 < self.PRICE_RANGE_MULTIPLICATOR_PERCENTUAL_DECREMENT < 100:
            raise ValueError(
                f"PRICE_RANGE_MULTIPLICATOR_PERCENTUAL_DECREMENT must be between 0 and 100. PRICE_RANGE_MULTIPLICATOR_PERCENTUAL_DECREMENT inputted: {self.PRICE_RANGE_MULTIPLICATOR_PERCENTUAL_DECREMENT}."
            )

        self.BOT_ADDRESS = (
            Web3(Web3.HTTPProvider(self.RPC_ENDPOINT))
            .eth.account.from_key(self.PRIVATE_KEY)
            .address
        )

    def __repr__(self):
        return "Environment variables"


@dataclass
class SystemData:
    nft_id: int
    bot_ETH_balance: float
    safe_token0_balance: float
    safe_token1_balance: float
    token0_balance: float
    token1_balance: float
    price_min: float
    price_max: float
    price: float
    min_price_threshold: float
    max_price_threshold: float

    def check_triggering_condition(self) -> (bool, float | None):
        if (self.price - self.price_min) / (
            self.price_max - self.price_min
        ) < self.min_price_threshold:
            return (True, self.price - self.price_min)
        elif (self.price_max - self.price) / (
            self.price_max - self.price_min
        ) < self.max_price_threshold:
            return (True, self.price_max - self.price)
        else:
            return (False, None)


def update_system_data(w3: Web3, nft_id: int, env: ENV) -> SystemData:
    nft_position = NFTPosition(w3, nft_id)
    balances = nft_position.get_balances()
    return SystemData(
        nft_id=nft_id,
        bot_ETH_balance=w3.eth.get_balance(env.BOT_ADDRESS) / (10**18),
        safe_token0_balance=erc20_contract(w3, env.TOKEN0_ADDRESS)
        .functions.balanceOf(env.AVATAR_SAFE_ADDRESS)
        .call()
        / (10 ** erc20_contract(w3, env.TOKEN0_ADDRESS).functions.decimals().call()),
        safe_token1_balance=erc20_contract(w3, env.TOKEN1_ADDRESS)
        .functions.balanceOf(env.AVATAR_SAFE_ADDRESS)
        .call()
        / (10 ** erc20_contract(w3, env.TOKEN1_ADDRESS).functions.decimals().call()),
        token0_balance=float(balances[0]),
        token1_balance=float(balances[1]),
        price_min=float(nft_position.price_min),
        price_max=float(nft_position.price_max),
        price=float(nft_position.pool.price),
        min_price_threshold=env.MIN_PRICE_THRESHOLD,
        max_price_threshold=env.MAX_PRICE_THRESHOLD,
    )


@dataclass
class Gauges:
    nft_id = Gauge("nft_id", "NFT Id")
    bot_ETH_balance = Gauge("bot_ETH_balance", "ETH balance of the bot")
    safe_token0_balance = Gauge("safe_token0_balance", "Safe token0 balance")
    safe_token1_balance = Gauge("safe_token1_balance", "Safe token1 balance")
    token0_balance = Gauge("token0_balance", "Position token0 balance")
    token1_balance = Gauge("token1_balance", "Position token1 balance")
    price_min = Gauge("price_min", "Minimum range range price of token1 vs token0")
    price_max = Gauge("price_max", "Maximum range range price of token1 vs token0")
    price = Gauge("price", "Current price of token1 vs token0")
    min_threshold = Gauge("min_threshold", "Minimum price threshold")
    max_threshold = Gauge("max_threshold", "Maximum price threshold")

    def update(self, system_data: SystemData):
        self.nft_id.set(system_data.nft_id)
        self.bot_ETH_balance.set(system_data.bot_ETH_balance)
        self.safe_token0_balance.set(system_data.safe_token0_balance)
        self.safe_token1_balance.set(system_data.safe_token1_balance)
        self.token0_balance.set(system_data.token0_balance)
        self.token1_balance.set(system_data.token1_balance)
        self.price_min.set(system_data.price_min)
        self.price_max.set(system_data.price_max)
        self.price.set(system_data.price)
        self.min_threshold.set(
            float(
                system_data.min_price_threshold
                * (system_data.price_max - system_data.price_min)
                + system_data.price_min
            )
        )
        self.max_threshold.set(
            float(
                system_data.price_max
                - system_data.max_price_threshold
                * (system_data.price_max - system_data.price_min)
            )
        )


@dataclass
class Flags:
    lack_of_gas_warning: threading.Event = field(default_factory=threading.Event)
    tx_executed: threading.Event = field(default_factory=threading.Event)


def get_nft_id_from_mint_tx(
    w3: Web3, tx_receipt: TxReceipt, recipient: Address
) -> int | None:
    """Returns the NFT Id of the minted NFT in the transaction.

    Args:
        w3 (Web3): Web3 instance.
        tx_receipt (TxReceipt): Transaction receipt.

    Returns:
        int | None: NFT Id of the minted NFT in the transaction. Returns None if no NFT was minted to the recipient
            in that transaction.

    """
    event_log_decoder = EventLogDecoder(
        Web3().eth.contract(
            abi=ContractSpecs[Chain.get_blockchain_from_web3(w3)].PositionsNFT.abi
        )
    )
    for element in tx_receipt.logs:
        if (
            element["address"]
            == ContractSpecs[Chain.get_blockchain_from_web3(w3)].PositionsNFT.address
        ):
            event = event_log_decoder.decode_log(element)
            if not event:
                continue
            if event.name == "Transfer" and event.values["to"] == recipient:
                return event.values["tokenId"]
    return None


def get_all_nfts(
    w3: Web3,
    owner: str,
    discarded_nfts: list[int] = [],
    active: bool = True,
    token0: Address | None = None,
    token1: Address | None = None,
    fee: int | None = None,
) -> list[int]:
    """Returns all NFT Ids owned by a wallet with liquidity>0. It a priori filters any NFT Ids that are passed in the
    discarded_nfts list (this allows for faster performance). If active=True, it will discard those with liquidity=0.
    It also filters by token0, token1 and fee if these are specified.

    Args:
        w3 (Web3): Web3 instance.
        owner (str): Owner address.
        discarded_nfts (list[int], optional): List of NFT Ids to be discarded. Defaults to [].
        active (bool, optional): If True, it will only return NFT Ids with liquidity>0. Defaults to True.
        token0 (Address | None, optional): Token0 address. Defaults to None. If specified it will only return NFT Ids
            having liquidity in a pool with token0 as token0.
        token1 (Address | None, optional): Token1 address. Defaults to None. If specified it will only return NFT Ids
            having liquidity in a pool with token1 as token1.
        fee (int | None, optional): Fee. Defaults to None. If specified it will only return NFT Ids having liquidity in
            a pool with the specified fee.

    Returns:
        a list where each element is the nft id with liquidity>0 that is owned by the wallet (open and closed nfts)
    """

    result = []

    nft_contract = ContractSpecs[
        Chain.get_blockchain_from_web3(w3)
    ].PositionsNFT.contract(w3)
    nfts = nft_contract.functions.balanceOf(owner).call()
    for nft_index in range(nfts):
        nft_id = nft_contract.functions.tokenOfOwnerByIndex(owner, nft_index).call()
        if nft_id in discarded_nfts:
            continue
        nft_position = NFTPosition(w3=w3, nft_id=nft_id)
        if active:
            if nft_position.liquidity == 0:
                continue
        if token0 is not None:
            if nft_position.pool.token0 != token0:
                continue
        if token1 is not None:
            if nft_position.pool.token1 != token1:
                continue
        if fee is not None:
            if nft_position.pool.fee != fee:
                continue
        result.append(nft_id)
    return result


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
            withdraw_eth=False,
        )

        return roles.send(
            decrease_liquidity_transactables,
            role=self.role,
            private_key=self.private_key,
            roles_mod_address=self.roles_mod,
            web3=w3,
        )


def log_initial_data(env: ENV, messenger: Messenger):
    title = "Bridge Keeper started"
    message = f"  Something"
    messenger.log_and_alert(LoggingLevel.Info, title, message)


def log_status_update(
    env: ENV,
    bridge_DAI_balance: int,
    bot_ETH_balance: int,
    next_claim_epoch: int,
    min_cash_threshold: int,
):
    title = "Status update"
    message = f"  Something"
    logger.info(title + ".\n" + message)
