from defabipedia.types import Blockchain
from defabipedia.uniswap_v3 import ContractSpecs

from roles_royce.protocols.base import Address, AvatarAddress, ContractMethod


class ApproveForPositionsNFT(ContractMethod):
    """Approve Token with PositionsNFT as spender."""

    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]

    def __init__(self, blockchain: Blockchain, token: Address, amount: int):
        super().__init__()
        self.target_address = token
        self.args.spender = ContractSpecs[blockchain].PositionsNFT.address
        self.args.amount = amount


class Mint(ContractMethod):
    """Mint a position NFT in Uniswap V3 pool."""

    name = "mint"
    in_signature = (
        (
            "params",
            (
                (
                    ("token0", "address"),
                    ("token1", "address"),
                    ("fee", "uint24"),
                    ("tick_lower", "int24"),
                    ("tick_upper", "int24"),
                    ("amount0_desired", "uint256"),
                    ("amount1_desired", "uint256"),
                    ("amount0_min", "uint256"),
                    ("amount1_min", "uint256"),
                    ("recipient", "address"),
                    ("deadline", "uint256"),
                ),
                "tuple",
            ),
        ),
    )

    fixed_arguments = {"recipient": AvatarAddress}

    def __init__(
        self,
        blockchain: Blockchain,
        avatar: Address,
        token0: Address,
        token1: Address,
        fee: int,
        tick_lower: int,
        tick_upper: int,
        amount0_desired: int,
        amount1_desired: int,
        amount0_min: int,
        amount1_min: int,
        deadline: int,
        value: int = 0,
    ):
        self.target_address = ContractSpecs[blockchain].PositionsNFT.address
        super().__init__(avatar=avatar, value=value)
        self.token0 = token0
        self.token1 = token1
        self.amount0_desired = amount0_desired
        self.amount1_desired = amount1_desired
        self.amount0_min = amount0_min
        self.amount1_min = amount1_min
        self.args.params = [
            token0,
            token1,
            fee,
            tick_lower,
            tick_upper,
            amount0_desired,
            amount1_desired,
            amount0_min,
            amount1_min,
            self.avatar,
            deadline,
        ]


class RefundETH(ContractMethod):
    """Refund unused ETH to the sender."""

    name = "refundETH"
    in_signature = []

    def __init__(self, blockchain: Blockchain):
        self.target_address = ContractSpecs[blockchain].PositionsNFT.address
        super().__init__()


class IncreaseLiquidity(ContractMethod):
    """Increase liquidity of a position NFT in Uniswap V3 pool."""

    name = "increaseLiquidity"
    in_signature = (
        (
            "params",
            (
                (
                    ("token_id", "uint256"),
                    ("amount0_desired", "uint256"),
                    ("amount1_desired", "uint256"),
                    ("amount0_min", "uint256"),
                    ("amount1_min", "uint256"),
                    ("deadline", "uint256"),
                ),
                "tuple",
            ),
        ),
    )

    def __init__(
        self,
        blockchain: Blockchain,
        token_id: int,
        amount0_desired: int,
        amount1_desired: int,
        amount0_min: int,
        amount1_min: int,
        deadline: int,
        value: int = 0,
    ):
        self.target_address = ContractSpecs[blockchain].PositionsNFT.address
        super().__init__(value=value)
        self.amount0_desired = amount0_desired
        self.amount1_desired = amount1_desired
        self.args.params = [
            token_id,
            amount0_desired,
            amount1_desired,
            amount0_min,
            amount1_min,
            deadline,
        ]


class DecreaseLiquidity(ContractMethod):
    """Decrease liquidity of a position NFT in Uniswap V3 pool."""

    name = "decreaseLiquidity"
    in_signature = (
        (
            "params",
            (
                (
                    ("token_id", "uint256"),
                    ("liquidity", "uint128"),
                    ("amount0_min", "uint256"),
                    ("amount1_min", "uint256"),
                    ("deadline", "uint256"),
                ),
                "tuple",
            ),
        ),
    )

    def __init__(
        self,
        blockchain: Blockchain,
        token_id: int,
        liquidity: int,
        amount0_min: int,
        amount1_min: int,
        deadline: int,
    ):
        self.target_address = ContractSpecs[blockchain].PositionsNFT.address
        super().__init__()
        self.amount0_min = amount0_min
        self.amount1_min = amount1_min
        self.args.params = [token_id, liquidity, amount0_min, amount1_min, deadline]


class Collect(ContractMethod):
    """Collect fees from a position NFT in Uniswap V3 pool."""

    name = "collect"
    in_signature = (
        (
            "params",
            (
                (
                    ("token_id", "uint256"),
                    ("recipient", "address"),
                    ("amount0_max", "uint128"),
                    ("amount1_max", "uint128"),
                ),
                "tuple",
            ),
        ),
    )

    def __init__(
        self,
        blockchain: Blockchain,
        recipient: Address,
        token_id: int,
        amount0_max: int,
        amount1_max: int,
    ):
        self.target_address = ContractSpecs[blockchain].PositionsNFT.address
        super().__init__()
        self.args.params = [
            token_id,
            recipient,
            amount0_max,
            amount1_max,
        ]


class UnwrapWETH9(ContractMethod):
    """Unwrap WETH to ETH and send it to sender."""

    name = "unwrapWETH9"
    in_signature = [("amount_minimum", "uint256"), ("recipient", "address")]
    fixed_arguments = {"recipient": AvatarAddress}

    def __init__(self, blockchain: Blockchain, avatar: Address, amount_minimum: int):
        self.target_address = ContractSpecs[blockchain].PositionsNFT.address
        super().__init__(avatar=avatar)
        self.args.amount_minimum = amount_minimum


class SweepToken(ContractMethod):
    """Sweep tokens from a contract to the sender."""

    name = "sweepToken"
    in_signature = [
        ("token", "address"),
        ("amount_minimum", "uint256"),
        ("recipient", "address"),
    ]
    fixed_arguments = {"recipient": AvatarAddress}

    def __init__(
        self,
        blockchain: Blockchain,
        avatar: Address,
        amount_minimum: int,
        token: Address,
    ):
        self.target_address = ContractSpecs[blockchain].PositionsNFT.address
        super().__init__(avatar=avatar)
        self.args.token = token
        self.args.amount_minimum = amount_minimum
