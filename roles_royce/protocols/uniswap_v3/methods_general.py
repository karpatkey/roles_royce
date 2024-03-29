import math
from datetime import datetime
from decimal import Decimal

from defabipedia.tokens import EthereumTokenAddr as ETHAddr
from defabipedia.types import Chain
from defabipedia.uniswap_v3 import ContractSpecs
from karpatkit.constants import Address as GenAddr
from web3 import Web3

from roles_royce.generic_method import Transactable
from roles_royce.protocols.base import Address
from roles_royce.protocols.uniswap_v3.contract_methods import (
    ApproveForPositionsNFT,
    Collect,
    DecreaseLiquidity,
    IncreaseLiquidity,
    Mint,
    RefundETH,
    SweepToken,
    UnwrapWETH9,
)
from roles_royce.protocols.uniswap_v3.types_and_enums import FeeAmount
from roles_royce.protocols.uniswap_v3.utils import (
    NFTPosition,
    Pool,
    check_allowance,
    set_and_check_desired_amounts,
    validate_amounts,
    validate_price_percentage_deviation,
    validate_removed_liquidity_percentage,
    validate_slippage,
    validate_tokens,
)

COLLECT_AMOUNT_MAX = 340282366920938463463374607431768211455


def mint_nft(
    w3: Web3,
    avatar: Address,
    token0: Address,
    token1: Address,
    fee: FeeAmount,
    token0_min_price_perc_dev: float,
    token0_max_price_perc_dev: float,
    amount0_desired: float = None,
    amount1_desired: float = None,
    amount0_min_slippage: float = 1,
    amount1_min_slippage: float = 1,
) -> list[Transactable]:
    """Mint a position NFT in Uniswap V3 pool.

    Args:
        w3 (Web3): Web3 object.
        avatar (Address): avatar address.
        token0 (Address): token0 address of Uniswap V3 pool. token0 must be ZER0 or E address to indicate ETH.
        token1 (Address): token1 address of Uniswap V3 pool. token1 must be ZER0 or E address to indicate ETH.
        fee (FeeAmount): fee amount of Uniswap V3 pool.
        token0_min_price_perc_dev (float): Minimum range price of the position of token0 vs token1, expressed as a percentage deviation from the current pool rate. E.g.: if current_rate=10, and token0_min_price_perc_dev=15, token0_max_price_perc_dev=10, the price range of the posotion will be [8.5,11].
        token0_max_price_perc_dev (float): Maximum range price of the position of token0 vs token1, expressed as a percentage deviation from the current pool rate. E.g.: if current_rate=10, and token0_min_price_perc_dev=15, token0_max_price_perc_dev=10, the price range of the posotion will be [8.5,11].
        amount0_desired (float, optional): token0 amount desired. If this amount is greater than 0 then amount1_desired must be left to None since it's calculated automatically. Defaults to None.
        amount1_desired (float, optional): token1 amount desired. If this amount is greater than 0 then amount1_desired must be left to None since it's calculated automatically. Defaults to None.
        amount0_min_slippage (float, optional): token0 slippage percentage from the amount desired to obtain the amount0_min. Defaults to 1%.
        amount1_min_slippage (float, optional): token1 slippage percentage from the amount desired to obtain the amount1_min .Defaults to 1%.

    Returns:
        list[Transactable]: list of transactions to mint a NFT in Uniswap V3 pool.

    Raises:
        ValueError: If token0 is equeal to token1.
        ValueError: If amount0_desired and amount1_desired are both None or 0.
        ValueError: If amount0_desired and amount1_desired are both greater than 0.
        ValueError: If token0_min_price_perc_dev is not between 0 and 100.
        ValueError: If token0_max_price_perc_dev is not between 0 and 100.
        ValueError: If amount0_min_slippage is not between 0 and 100.
        ValueError: If amount1_min_slippage is not between 0 and 100.
        ValueError: If for the token0, token1 and fee combination there is no pool.
        ValueError: If the avatar has not enough funds to mint the NFT.
    """
    mint_trasactables = []

    mint = MintNFT(
        w3,
        avatar,
        token0,
        token1,
        fee,
        token0_min_price_perc_dev,
        token0_max_price_perc_dev,
        amount0_desired,
        amount1_desired,
        amount0_min_slippage,
        amount1_min_slippage,
    )

    blockchain = Chain.get_blockchain_from_web3(w3)
    if mint.value > 0:
        if mint.args.token0 != ETHAddr.WETH:
            if not check_allowance(
                w3,
                avatar,
                ContractSpecs[blockchain].PositionsNFT.address,
                mint.args.token0,
                mint.args.amount0_desired,
            ):
                mint_trasactables.append(
                    ApproveForPositionsNFT(blockchain, mint.args.token0, mint.args.amount0_desired)
                )
        else:
            if not check_allowance(
                w3,
                avatar,
                ContractSpecs[blockchain].PositionsNFT.address,
                mint.args.token1,
                mint.args.amount1_desired,
            ):
                mint_trasactables.append(
                    ApproveForPositionsNFT(blockchain, mint.args.token1, mint.args.amount1_desired)
                )

        mint_trasactables.append(mint)
        mint_trasactables.append(RefundETH(blockchain))
    else:
        if not check_allowance(
            w3,
            avatar,
            ContractSpecs[blockchain].PositionsNFT.address,
            mint.args.token0,
            mint.args.amount0_desired,
        ):
            mint_trasactables.append(ApproveForPositionsNFT(blockchain, mint.args.token0, mint.args.amount0_desired))
        if not check_allowance(
            w3,
            avatar,
            ContractSpecs[blockchain].PositionsNFT.address,
            mint.args.token1,
            mint.args.amount1_desired,
        ):
            mint_trasactables.append(ApproveForPositionsNFT(blockchain, mint.args.token1, mint.args.amount1_desired))

        mint_trasactables.append(mint)

    return mint_trasactables


def increase_liquidity_nft(
    w3: Web3,
    avatar: Address,
    nft_id: int,
    amount0_desired: float = None,
    amount1_desired: float = None,
    amount0_min_slippage: float = 1,
    amount1_min_slippage: float = 1,
    send_eth=False,
) -> list[Transactable]:
    """Increase liquidity of a position NFT in Uniswap V3 pool.

    Args:
        w3 (Web3): Web3 object.
        avatar (Address): avatar address.
        nft_id (int): NFT id of the position to increase liquidity.
        amount0_desired (float, optional): token0 amount desired. If this amount is greater than 0 then amount1_desired must be left to None since it's calculated automatically. Defaults to None.
        amount1_desired (float, optional): token1 amount desired. If this amount is greater than 0 then amount1_desired must be left to None since it's calculated automatically. Defaults to None.
        amount0_min_slippage (float, optional): token0 slippage percentage from the amount desired to obtain the amount0_min. Defaults to 1%.
        amount1_min_slippage (float, optional): token1 slippage percentage from the amount desired to obtain the amount1_min .Defaults to 1%.
        send_eth (bool, optional): indicates if the transaction will send ETH in case token0 or token1 is WETH. If send_eth is True then ETH will be sent, otherwise WETH will be sent. Defaults to False.

    Returns:
        list[Transactable]: list of transactions to increase liquidity of a position NFT in Uniswap V3 pool.

    Raises:
        ValueError: If amount0_desired and amount1_desired are both None or 0.
        ValueError: If amount0_desired and amount1_desired are both greater than 0.
        ValueError: If amount0_min_slippage is not between 0 and 100.
        ValueError: If amount1_min_slippage is not between 0 and 100.
        ValueError: If the avatar has not enough funds to increase the liquidity of the NFT.
    """
    increase_liquidity_trasactables = []

    increase_liquidity = IncreaseLiquidityNFT(
        w3,
        avatar,
        nft_id,
        amount0_desired,
        amount1_desired,
        amount0_min_slippage,
        amount1_min_slippage,
        send_eth,
    )

    blockchain = Chain.get_blockchain_from_web3(w3)
    if increase_liquidity.value > 0:
        if increase_liquidity.nft_position.pool.token0 != ETHAddr.WETH:
            if not check_allowance(
                w3,
                avatar,
                ContractSpecs[blockchain].PositionsNFT.address,
                increase_liquidity.nft_position.pool.token0,
                increase_liquidity.args.amount0_desired,
            ):
                increase_liquidity_trasactables.append(
                    ApproveForPositionsNFT(
                        blockchain,
                        increase_liquidity.nft_position.pool.token0,
                        increase_liquidity.args.amount0_desired,
                    )
                )
        else:
            if not check_allowance(
                w3,
                avatar,
                ContractSpecs[blockchain].PositionsNFT.address,
                increase_liquidity.nft_position.pool.token1,
                increase_liquidity.args.amount1_desired,
            ):
                increase_liquidity_trasactables.append(
                    ApproveForPositionsNFT(
                        blockchain,
                        increase_liquidity.nft_position.pool.token1,
                        increase_liquidity.args.amount1_desired,
                    )
                )

        increase_liquidity_trasactables.append(increase_liquidity)
        increase_liquidity_trasactables.append(RefundETH(blockchain))
    else:
        if not check_allowance(
            w3,
            avatar,
            ContractSpecs[blockchain].PositionsNFT.address,
            increase_liquidity.nft_position.pool.token0,
            increase_liquidity.args.amount0_desired,
        ):
            increase_liquidity_trasactables.append(
                ApproveForPositionsNFT(
                    blockchain,
                    increase_liquidity.nft_position.pool.token0,
                    increase_liquidity.args.amount0_desired,
                )
            )
        if not check_allowance(
            w3,
            avatar,
            ContractSpecs[blockchain].PositionsNFT.address,
            increase_liquidity.nft_position.pool.token1,
            increase_liquidity.args.amount1_desired,
        ):
            increase_liquidity_trasactables.append(
                ApproveForPositionsNFT(
                    blockchain,
                    increase_liquidity.nft_position.pool.token1,
                    increase_liquidity.args.amount1_desired,
                )
            )

        increase_liquidity_trasactables.append(increase_liquidity)

    return increase_liquidity_trasactables


def decrease_liquidity_nft(
    w3: Web3,
    recipient: Address,
    nft_id: int,
    removed_liquidity_percentage: float,
    amount0_min_slippage: float = 1,
    amount1_min_slippage: float = 1,
    withdraw_eth=False,
) -> list[Transactable]:
    """Decrease liquidity of a position NFT in Uniswap V3 pool.

    Args:
        w3 (Web3): Web3 object.
        recipient (Address): recipient address.
        nft_id (int): NFT id of the position to decrease liquidity.
        removed_liquidity_percentage (float): percentage of liquidity to remove from the position.
        amount0_min_slippage (float, optional): token0 slippage percentage from the amount desired to obtain the amount0_min. Defaults to 1%.
        amount1_min_slippage (float, optional): token1 slippage percentage from the amount desired to obtain the amount1_min .Defaults to 1%.
        withdraw_eth (bool, optional): indicates if the transaction will withdraw ETH in case token0 or token1 is WETH. If withdraw_eth is True then ETH will be withdrawn, otherwise WETH will be withdrawn. Defaults to False.

    Returns:
        list[Transactable]: list of transactions to decrease liquidity of a position NFT in Uniswap V3 pool.

    Raises:
        ValueError: If removed_liquidity_percentage is not between 0 and 100.
        ValueError: if amount0_min_slippage is not between 0 and 100.
        ValueError: if amount1_min_slippage is not between 0 and 100.
    """
    decrease_liquidity_trasactables = []

    decrease_liquidity = DecreaseLiquidityNFT(
        w3,
        nft_id,
        removed_liquidity_percentage,
        amount0_min_slippage,
        amount1_min_slippage,
    )

    blockchain = Chain.get_blockchain_from_web3(w3)
    if withdraw_eth:
        amount_minimum_unwrap = 0
        amount_minimum_sweep = 0

        if (
            decrease_liquidity.nft_position.pool.token0 != ETHAddr.WETH
            and decrease_liquidity.nft_position.pool.token1 != ETHAddr.WETH
        ):
            raise ValueError("One of the tokens must be WETH")
        elif decrease_liquidity.nft_position.pool.token0 == ETHAddr.WETH:
            amount_minimum_unwrap = decrease_liquidity.args.amount0_min
            amount_minimum_sweep = decrease_liquidity.args.amount1_min
            sweep_token = decrease_liquidity.nft_position.pool.token1
        else:
            amount_minimum_unwrap = decrease_liquidity.args.amount1_min
            amount_minimum_sweep = decrease_liquidity.args.amount0_min
            sweep_token = decrease_liquidity.nft_position.pool.token0

        decrease_liquidity_trasactables.append(decrease_liquidity)
        decrease_liquidity_trasactables.append(
            Collect(blockchain, GenAddr.ZERO, nft_id, COLLECT_AMOUNT_MAX, COLLECT_AMOUNT_MAX)
        )
        decrease_liquidity_trasactables.append(UnwrapWETH9(blockchain, recipient, amount_minimum_unwrap))
        decrease_liquidity_trasactables.append(SweepToken(blockchain, recipient, amount_minimum_sweep, sweep_token))
    else:
        decrease_liquidity_trasactables.append(decrease_liquidity)
        decrease_liquidity_trasactables.append(
            Collect(blockchain, recipient, nft_id, COLLECT_AMOUNT_MAX, COLLECT_AMOUNT_MAX)
        )

    return decrease_liquidity_trasactables


class MintNFT(Mint):
    def __init__(
        self,
        w3: Web3,
        avatar: Address,
        token0: Address,
        token1: Address,
        fee: FeeAmount,
        token0_min_price_perc_dev: float,
        token0_max_price_perc_dev: float,
        amount0_desired: float = None,
        amount1_desired: float = None,
        amount0_min_slippage: float = 1,
        amount1_min_slippage: float = 1,
    ):
        """Upper layer class for minting a position NFT in Uniswap V3 pool."""
        validate_tokens(token0, token1)
        validate_price_percentage_deviation(token0_min_price_perc_dev, token0_max_price_perc_dev)
        amount0_desired, amount1_desired = validate_amounts(amount0_desired, amount1_desired)
        validate_slippage(amount0_min_slippage, amount1_min_slippage)

        pool = Pool(w3, token0, token1, fee)

        if pool.token0 != token0 and pool.token1 != token1:
            token0, token1 = token1, token0
            amount0_desired, amount1_desired = amount1_desired, amount0_desired

        send_eth = False
        if token0 == GenAddr.E or token0 == GenAddr.ZERO:
            send_eth = True

        if token1 == GenAddr.E or token1 == GenAddr.ZERO:
            send_eth = True

        amount0_desired = Decimal(amount0_desired * 10**pool.token0_decimals)
        amount1_desired = Decimal(amount1_desired * 10**pool.token1_decimals)

        token0_min_price = pool.price * (1 - Decimal(token0_min_price_perc_dev) / 100)
        token0_max_price = pool.price * (1 + Decimal(token0_max_price_perc_dev) / 100)

        # tick_index_min = math.floor((math.log10(token0_min_price) + (pool.token1_decimals - pool.token0_decimals)) / math.log10(1.0001) / pool.tick_spacing)
        # tick_index_max = math.floor((math.log10(token0_max_price) + (pool.token1_decimals - pool.token0_decimals)) / math.log10(1.0001) / pool.tick_spacing)

        # self.token0_min_price = 1.0001**(tick_index_min * pool.tick_spacing) / 10**(pool.token1_decimals - pool.token0_decimals)
        # self.token0_max_price = 1.0001**(tick_index_max * pool.tick_spacing) / 10**(pool.token1_decimals - pool.token0_decimals)

        tick_lower = (
            math.ceil(
                (math.log10(token0_min_price) + (pool.token1_decimals - pool.token0_decimals))
                / math.log10(1.0001)
                / pool.tick_spacing
            )
            * pool.tick_spacing
        )
        tick_upper = (
            math.floor(
                (math.log10(token0_max_price) + (pool.token1_decimals - pool.token0_decimals))
                / math.log10(1.0001)
                / pool.tick_spacing
            )
            * pool.tick_spacing
        )

        amount0_desired, amount1_desired = set_and_check_desired_amounts(
            w3,
            avatar,
            amount0_desired,
            amount1_desired,
            pool,
            tick_lower,
            tick_upper,
            send_eth,
        )

        amount0_min = Decimal(amount0_desired) * (1 - Decimal(amount0_min_slippage) / 100)
        amount1_min = Decimal(amount1_desired) * (1 - Decimal(amount1_min_slippage) / 100)

        value = 0
        if token0 == GenAddr.E or token0 == GenAddr.ZERO:
            value = amount0_desired

        if token1 == GenAddr.E or token1 == GenAddr.ZERO:
            value = amount1_desired

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            avatar=avatar,
            token0=pool.token0,
            token1=pool.token1,
            fee=fee,
            tick_lower=tick_lower,
            tick_upper=tick_upper,
            amount0_desired=int(amount0_desired),
            amount1_desired=int(amount1_desired),
            amount0_min=int(amount0_min),
            amount1_min=int(amount1_min),
            deadline=math.floor(datetime.now().timestamp() + 1800),
            value=int(value),
        )


class IncreaseLiquidityNFT(IncreaseLiquidity):
    def __init__(
        self,
        w3: Web3,
        avatar: Address,
        nft_id: int,
        amount0_desired: float = None,
        amount1_desired: float = None,
        amount0_min_slippage: float = 1,
        amount1_min_slippage: float = 1,
        send_eth=False,
    ):
        """Upper layer class for increasing liquidity of a position NFT in Uniswap V3 pool."""
        amount0_desired, amount1_desired = validate_amounts(amount0_desired, amount1_desired)
        validate_slippage(amount0_min_slippage, amount1_min_slippage)

        self.nft_position = NFTPosition(w3, nft_id)

        amount0_desired = Decimal(amount0_desired * 10**self.nft_position.pool.token0_decimals)
        amount1_desired = Decimal(amount1_desired * 10**self.nft_position.pool.token1_decimals)

        amount0_desired, amount1_desired = set_and_check_desired_amounts(
            w3,
            avatar,
            amount0_desired,
            amount1_desired,
            self.nft_position.pool,
            self.nft_position.tick_lower,
            self.nft_position.tick_upper,
            send_eth,
        )

        amount0_min = amount0_desired * (1 - Decimal(amount0_min_slippage) / 100)
        amount1_min = amount1_desired * (1 - Decimal(amount1_min_slippage) / 100)

        value = 0
        if self.nft_position.pool.token0 == ETHAddr.WETH and send_eth:
            value = amount0_desired

        if self.nft_position.pool.token1 == ETHAddr.WETH and send_eth:
            value = amount1_desired

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            token_id=nft_id,
            amount0_desired=int(amount0_desired),
            amount1_desired=int(amount1_desired),
            amount0_min=int(amount0_min),
            amount1_min=int(amount1_min),
            deadline=math.floor(datetime.now().timestamp() + 1800),
            value=int(value),
        )


class DecreaseLiquidityNFT(DecreaseLiquidity):
    def __init__(
        self,
        w3: Web3,
        nft_id: int,
        removed_liquidity_percentage: float,
        amount0_min_slippage: float = 1,
        amount1_min_slippage: float = 1,
    ):
        """Upper layer class for decreasing liquidity of a position NFT in Uniswap V3 pool."""
        validate_removed_liquidity_percentage(removed_liquidity_percentage)
        validate_slippage(amount0_min_slippage, amount1_min_slippage)

        self.nft_position = NFTPosition(w3, nft_id)

        liquidity = self.nft_position.liquidity * removed_liquidity_percentage / 100

        balances = self.nft_position.get_balances(self.nft_position.pool.ic, self.nft_position.pool.sqrt_price)

        amount0_desired = balances[0] * removed_liquidity_percentage / 100
        amount1_desired = balances[1] * removed_liquidity_percentage / 100

        amount0_min = amount0_desired * Decimal((100 - amount0_min_slippage) / 100)
        amount1_min = amount1_desired * Decimal((100 - amount1_min_slippage) / 100)

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            token_id=nft_id,
            liquidity=int(liquidity),
            amount0_min=int(amount0_min),
            amount1_min=int(amount1_min),
            deadline=math.floor(datetime.now().timestamp() + 1800),
        )
