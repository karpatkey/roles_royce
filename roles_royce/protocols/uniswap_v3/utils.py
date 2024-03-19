from decimal import Decimal

from defabipedia.tokens import Abis as TokenAbis
from defabipedia.tokens import EthereumTokenAddr as ETHAddr
from defabipedia.types import Chain
from defabipedia.uniswap_v3 import Abis, ContractSpecs
from karpatkit.constants import Address as GenAddr
from web3 import Web3

from roles_royce.protocols.base import Address
from roles_royce.protocols.uniswap_v3.types_and_enums import FeeAmount


def validate_tokens(token0: Address, token1: Address):
    if token0 == token1:
        raise ValueError("token0 and token1 must be different")


def validate_amounts(amount0_desired: float, amount1_desired: float) -> tuple:
    if not amount0_desired and not amount1_desired:
        raise ValueError("One of amount0_desired or amount1_desired must be provided")

    if amount0_desired:
        if amount0_desired <= 0:
            raise ValueError("amount0_desired must be greater than 0")
        else:
            if amount1_desired:
                raise ValueError("Only one amount can be provided")
            else:
                amount1_desired = 0
    else:
        if amount1_desired <= 0:
            raise ValueError("amount1_desired must be greater than 0")
        else:
            if amount0_desired:
                raise ValueError("Only one amount can be provided")
            else:
                amount0_desired = 0

    return amount0_desired, amount1_desired


def validate_price_percentage_deviation(token0_min_price_perc_dev: float, token0_max_price_perc_dev: float):
    if not 0 <= token0_min_price_perc_dev <= 100:
        raise ValueError("token0_min_percentage_deviation must be between 0 and 100")

    if not 0 <= token0_max_price_perc_dev <= 100:
        raise ValueError("token0_max_percentage_deviation must be between 0 and 100")


def validate_slippage(amount0_min_slippage: float, amount1_min_slippage: float):
    if not 0 <= amount0_min_slippage <= 100:
        raise ValueError("amount0_min_slippage must be between 0 and 100")

    if not 0 <= amount1_min_slippage <= 100:
        raise ValueError("amount1_min_slippage must be between 0 and 100")


def validate_removed_liquidity_percentage(removed_liquidity_percentage: float):
    if not 0 <= removed_liquidity_percentage <= 100:
        raise ValueError("removed_liquidity_percentage must be between 0 and 100")


def check_allowance(w3: Web3, owner: Address, spender: Address, token: Address, amount: Decimal) -> bool:
    allowance = w3.eth.contract(address=token, abi=TokenAbis.ERC20.abi).functions.allowance(owner, spender).call()
    return allowance >= amount


class Pool:
    def __init__(self, w3: Web3, token0: Address, token1: Address, fee: FeeAmount):
        self.fee = fee
        blockchain = Chain.get_blockchain_from_web3(w3)
        factory = ContractSpecs[blockchain].Factory.contract(w3)

        if token0 == GenAddr.E or token0 == GenAddr.ZERO:
            token0 = ETHAddr.WETH
            if token1 < token0:
                token0, token1 = token1, token0

        if token1 == GenAddr.E or token1 == GenAddr.ZERO:
            token1 = ETHAddr.WETH
            if token1 < token0:
                token0, token1 = token1, token0

        self.addr = factory.functions.getPool(token0, token1, self.fee).call()
        if self.addr == GenAddr.ZERO:
            raise ValueError("Pool does not exist")
        self.pool_contract = w3.eth.contract(address=self.addr, abi=Abis[blockchain].Pool.abi)
        self.sqrt_price_x96, self.ic = self.pool_contract.functions.slot0().call()[0:2]
        self.sqrt_price = Decimal(self.sqrt_price_x96) / Decimal(2**96)
        self.token0 = self.pool_contract.functions.token0().call()
        self.token0_decimals = w3.eth.contract(address=self.token0, abi=TokenAbis.ERC20.abi).functions.decimals().call()
        self.token1 = self.pool_contract.functions.token1().call()
        self.token1_decimals = w3.eth.contract(address=self.token1, abi=TokenAbis.ERC20.abi).functions.decimals().call()
        self.price = (self.sqrt_price**2) / 10 ** (self.token1_decimals - self.token0_decimals)
        self.tick_spacing = self.pool_contract.functions.tickSpacing().call()


class NFTPosition:
    def __init__(self, w3: Web3, nft_id: int):
        blockchain = Chain.get_blockchain_from_web3(w3)
        try:
            position_data = (
                w3.eth.contract(
                    address=ContractSpecs[blockchain].PositionsNFT.address,
                    abi=ContractSpecs[blockchain].PositionsNFT.abi,
                )
                .functions.positions(nft_id)
                .call()
            )
        except Exception as e:
            raise ValueError(e.args[0]) from e

        token0 = position_data[2]
        token1 = position_data[3]
        fee = position_data[4]
        self.pool = Pool(w3, token0, token1, fee)
        self.tick_lower = position_data[5]
        self.tick_upper = position_data[6]
        self.liquidity = position_data[7]
        self.fr0 = position_data[8]
        self.fr1 = position_data[9]

    def get_balances(self, ic: int, sqrt_price: Decimal) -> list:
        balances = []

        if self.liquidity != 0:
            sa = Decimal(1.0001) ** Decimal(int(self.tick_lower) / 2)
            sb = Decimal(1.0001) ** Decimal(int(self.tick_upper) / 2)

            if self.tick_upper <= ic:
                amount0 = 0
                amount1 = self.liquidity * (sb - sa)
            elif self.tick_lower < ic < self.tick_upper:
                amount0 = self.liquidity * (sb - sqrt_price) / (sqrt_price * sb)
                amount1 = self.liquidity * (sqrt_price - sa)
            else:
                amount0 = self.liquidity * (sb - sa) / (sa * sb)
                amount1 = 0

            balances.append(Decimal(amount0))
            balances.append(Decimal(amount1))

        else:
            balances.append(Decimal(0))
            balances.append(Decimal(0))

        return balances


def set_and_check_desired_amounts(
    w3: Web3,
    owner: Address,
    amount0_desired: float,
    amount1_desired: float,
    pool: Pool,
    tick_lower: int,
    tick_upper: int,
    send_eth: bool,
):
    if amount0_desired:
        amount1_desired = Decimal(
            amount0_desired
            * Decimal(
                pool.sqrt_price_x96
                * 1.0001 ** (tick_upper / 2)
                * (pool.sqrt_price_x96 - 1.0001 ** (tick_lower / 2) * (2**96))
            )
        ) / Decimal((2**96) * (1.0001 ** (tick_upper / 2) * (2**96) - pool.sqrt_price_x96))
    elif amount1_desired:
        amount0_desired = Decimal(
            amount1_desired * Decimal((2**96) * (1.0001 ** (tick_upper / 2) * (2**96) - pool.sqrt_price_x96))
        ) / (
            Decimal(
                pool.sqrt_price_x96
                * 1.0001 ** (tick_upper / 2)
                * (pool.sqrt_price_x96 - 1.0001 ** (tick_lower / 2) * (2**96))
            )
        )

    if send_eth:
        if pool.token0 != ETHAddr.WETH and pool.token1 != ETHAddr.WETH:
            raise ValueError("ETH can only be sent if one of the tokens is WETH")
        if pool.token0 == ETHAddr.WETH:
            if amount0_desired > w3.eth.get_balance(owner):
                raise ValueError("Not enough ETH balance")
        else:
            if amount1_desired > w3.eth.get_balance(owner):
                raise ValueError("Not enough ETH balance")
    else:
        token0_balance = w3.eth.contract(address=pool.token0, abi=TokenAbis.ERC20.abi).functions.balanceOf(owner).call()
        if amount0_desired > token0_balance:
            raise ValueError("Not enough token0 balance")

        token1_balance = w3.eth.contract(address=pool.token1, abi=TokenAbis.ERC20.abi).functions.balanceOf(owner).call()
        if amount1_desired > token1_balance:
            raise ValueError("Not enough token1 balance")

    return Decimal(amount0_desired), Decimal(amount1_desired)
