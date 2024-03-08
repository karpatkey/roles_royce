from decimal import Decimal
from web3 import Web3
from karpatkit.constants import Address as GenAddr
from roles_royce.protocols.base import Address
from roles_royce.protocols.uniswap_v3.types_and_enums import FeeAmount
from defabipedia.uniswap_v3 import ContractSpecs, Abis
from defabipedia.tokens import Abis as TokenAbis
from defabipedia.types import Chain
from defabipedia.tokens import EthereumTokenAddr as ETHAddr


def validate_tokens(token0: Address, token1: Address) -> bool:
    if token0 == token1:
        raise ValueError("token0 and token1 must be different")
    else:
        return True


def validate_amounts(amount0_desired: int | None, amount1_desired: int | None) -> bool:
    if not amount0_desired and not amount1_desired:
        raise ValueError("Either amount0_desired or amount1_desired must be provided")

    if amount0_desired and amount1_desired:
        raise ValueError("Only one amount can be provided")
    if amount0_desired:
        if amount0_desired <= 0:
            raise ValueError("amount0_desired must be greater than 0")
    elif amount1_desired:
        if amount1_desired <= 0:
            raise ValueError("amount1_desired must be greater than 0")

    return True


def validate_price_range(token0_min_price: float, token0_max_price: float, pool_price: float) -> bool:
    if not token0_min_price > 0:
        raise ValueError("token0_min_price must be greater than 0")

    if not token0_max_price > 0:
        raise ValueError("token0_max_price must be greater than 0")

    if not (token0_min_price < pool_price < token0_max_price):
        raise ValueError("pool_price out of range")

    return True


def validate_slippage(amount0_min_slippage: float, amount1_min_slippage: float) -> bool:
    if not 0 <= amount0_min_slippage <= 100:
        raise ValueError("amount0_min_slippage must be between 0 and 100")

    if not 0 <= amount1_min_slippage <= 100:
        raise ValueError("amount1_min_slippage must be between 0 and 100")

    return True


def validate_removed_liquidity_percentage(removed_liquidity_percentage: float) -> bool:
    if not 0 <= removed_liquidity_percentage <= 100:
        raise ValueError("removed_liquidity_percentage must be between 0 and 100")
    return True


def check_allowance(w3: Web3, owner: Address, spender: Address, token: Address, amount: int) -> bool:
    """Check if the owner has enough allowance for the spender to spend the amount of tokens.

    Args:
        w3: Web3 instance
        owner: Address of the owner
        spender: Address of the spender
        token: Address of the token
        amount: Amount of tokens to spend

    Returns:
        bool: True if the owner has enough allowance, False otherwise
    """
    allowance = w3.eth.contract(address=token, abi=TokenAbis.ERC20.abi).functions.allowance(owner, spender).call()
    return allowance >= amount


class Pool:
    """Class to represent a Uniswap V3 pool. It contains the pool's data.

    Args:
        w3: Web3 instance
        token0: Address of the token0
        token1: Address of the token1
        fee: FeeAmount of the pool, should be one of 100, 500, 3000, 10000.

    """

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
        self.pool_contract = w3.eth.contract(
            address=self.addr, abi=Abis[blockchain].Pool.abi
        )
        self.sqrt_price_x96, self.ic = self.pool_contract.functions.slot0().call()[0:2]
        self.sqrt_price = Decimal(self.sqrt_price_x96) / Decimal(2 ** 96)
        self.token0 = self.pool_contract.functions.token0().call()
        self.token0_decimals = (
            w3.eth.contract(address=self.token0, abi=TokenAbis.ERC20.abi)
            .functions.decimals()
            .call()
        )
        self.token1 = self.pool_contract.functions.token1().call()
        self.token1_decimals = (
            w3.eth.contract(address=self.token1, abi=TokenAbis.ERC20.abi)
            .functions.decimals()
            .call()
        )

        self.price = (self.sqrt_price ** 2) / Decimal(
            10 ** (self.token1_decimals - self.token0_decimals)
        )
        self.tick_spacing = self.pool_contract.functions.tickSpacing().call()


def get_tick_from_price(pool: Pool, price: float) -> int:
    """Get the approximate corresponding tick to a price in a pool.

    Args:
        pool: Pool instance
        price: Price to get the tick for

    Returns:
        int: Approximate tick corresponding to the price
    """
    price = Decimal(price)
    return int(((price.log10() + pool.token0_decimals - pool.token1_decimals)
                / (Decimal(1.0001).log10())).to_integral_value())


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

        self.pool = Pool(
            w3, token0=position_data[2], token1=position_data[3], fee=position_data[4]
        )
        self.tick_lower = position_data[5]
        self.tick_upper = position_data[6]
        self.liquidity = position_data[7]
        self.fr0 = position_data[8]
        self.fr1 = position_data[9]
        self.price_min = Decimal(1.0001) ** Decimal(self.tick_lower) / Decimal(
            10 ** (self.pool.token1_decimals - self.pool.token0_decimals)
        )
        self.price_max = Decimal(1.0001) ** Decimal(self.tick_upper) / Decimal(
            10 ** (self.pool.token1_decimals - self.pool.token0_decimals)
        )

    def get_balances(self) -> list[int]:
        balances = []

        if self.liquidity != 0:
            sa = Decimal(1.0001) ** Decimal(int(self.tick_lower) / 2)
            sb = Decimal(1.0001) ** Decimal(int(self.tick_upper) / 2)

            if self.tick_upper <= self.pool.ic:
                amount0 = 0
                amount1 = self.liquidity * (sb - sa)
            elif self.tick_lower < self.pool.ic < self.tick_upper:
                amount0 = (
                        self.liquidity
                        * (sb - self.pool.sqrt_price)
                        / (self.pool.sqrt_price * sb)
                )
                amount1 = self.liquidity * (self.pool.sqrt_price - sa)
            else:
                amount0 = self.liquidity * (sb - sa) / (sa * sb)
                amount1 = 0

            balances.append(int(amount0))
            balances.append(int(amount1))

        else:
            balances.append(0)
            balances.append(0)

        return balances


def set_and_check_desired_amounts(
        w3: Web3,
        owner: Address,
        amount0_desired: int | None,
        amount1_desired: int | None,
        pool: Pool,
        tick_lower: int,
        tick_upper: int,
        send_eth: bool,
) -> (int, int):
    """
    Returns the amounts of tokens desired to deposit, calculating one amount from the other. If amount_0_desired is
    provided, amount_1_desired is calculated and vice versa. It also checks if there is enough balance of the
    tokens, and if send_eth is True it checks if there is enough ETH balance.

    Args:
        w3: Web3 instance
        owner: Address of the owner
        amount0_desired: Desired amount of token0 to deposit. If None, amount1_desired must be provided
        amount1_desired: Desired amount of token1 to deposit. If None, amount0_desired must be provided
        pool: Pool instance
        tick_lower: Lower tick
        tick_upper: Upper tick
        send_eth: If True, it checks one of the tokens is either ETH or WETH and if there is enough ETH balance

    Returns:
        amount0_desired: Desired amount of token0
        amount1_desired: Desired amount of token1

    Raises:
        ValueError: If there is not enough balance of either token
    """
    sqrt_price_x96_decimal = Decimal(pool.sqrt_price_x96)
    price_min = Decimal(1.0001) ** Decimal(tick_lower / 2)
    price_max = Decimal(1.0001) ** Decimal(tick_upper / 2)
    if not amount0_desired and not amount1_desired:
        raise ValueError("Either amount0_desired or amount1_desired must be provided")
    elif amount0_desired and amount1_desired:
        raise ValueError("Only one amount can be provided")
    elif amount0_desired and (not amount1_desired):
        if amount0_desired <= 0:
            raise ValueError("amount0_desired must be greater than 0")
        amount1_desired = (
                Decimal(amount0_desired) * sqrt_price_x96_decimal * price_max
                * (sqrt_price_x96_decimal - price_min * Decimal(2 ** 96))
                / Decimal(2 ** 96) / (price_max * Decimal(2 ** 96) - sqrt_price_x96_decimal)
        )
    else:
        if amount1_desired <= 0:
            raise ValueError("amount1_desired must be greater than 0")
        amount0_desired = (
                Decimal(amount1_desired) * (Decimal(2 ** 96) * (price_max * Decimal(2 ** 96) - sqrt_price_x96_decimal))
                / (sqrt_price_x96_decimal * price_max * (sqrt_price_x96_decimal - price_min * Decimal(2 ** 96)))
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
        token0_balance = (
            w3.eth.contract(address=pool.token0, abi=TokenAbis.ERC20.abi).functions.balanceOf(owner).call())
        if amount0_desired > token0_balance:
            raise ValueError("Not enough token0 balance")

        token1_balance = (
            w3.eth.contract(address=pool.token1, abi=TokenAbis.ERC20.abi)
            .functions.balanceOf(owner)
            .call()
        )
        if amount1_desired > token1_balance:
            raise ValueError("Not enough token1 balance")

    return int(amount0_desired), int(amount1_desired)
