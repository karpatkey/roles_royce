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
from roles_royce.applications.uniswap_v3_keeper.env import ENV


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
