import eth_abi
from defabipedia.balancer import ContractSpecs
from defabipedia.types import Blockchain

from roles_royce.constants import MAX_UINT256
from roles_royce.protocols.base import Address, AvatarAddress, ContractMethod

from .types_and_enums import SwapKind


class StakeInGauge(ContractMethod):
    """Stake BPT in gauge"""

    name = "deposit"
    in_signature = [("value", "uint256")]

    def __init__(self, blockchain: Blockchain, gauge_address: Address, amount: int):
        # The blockchain is not needed, but it is included for consistency
        super().__init__()
        self.target_address = gauge_address
        self.args.value = amount


class UnstakeFromGauge(ContractMethod):
    """Unstake BPT from gauge"""

    name = "withdraw"
    in_signature = [("value", "uint256")]

    def __init__(self, blockchain: Blockchain, gauge_address: Address, amount: int):
        # The blockchain is not needed, but it is included for consistency
        super().__init__()
        self.target_address = gauge_address
        self.args.value = amount


# When providing your assets, you must ensure that the tokens are sorted numerically by token address.
# It's also important to note that the values in minAmountsOut correspond to the same index value in assets,
# so these arrays must be made in parallel after sorting.


class Exit(ContractMethod):
    name = "exitPool"
    in_signature = (
        ("pool_id", "bytes32"),
        ("sender", "address"),
        ("recipient", "address"),
        (
            "request",
            (
                (
                    ("assets", "address[]"),  # list of tokens, ordered numerically
                    ("min_amounts_out", "uint256[]"),  # the lower limits for the tokens to receive
                    ("user_data", "bytes"),
                    # userData encodes a ExitKind to tell the pool what style of exit you're performing
                    ("to_internal_balance", "bool"),
                ),
                "tuple",
            ),
        ),
    )
    fixed_arguments = {"sender": AvatarAddress, "recipient": AvatarAddress, "to_internal_balance": False}
    user_data_abi = None

    def __init__(
        self,
        blockchain: Blockchain,
        pool_id: str,
        avatar: Address,
        assets: list[Address],
        min_amounts_out: list[int],
        user_data: list,
    ):
        if self.name == "queryExit":  # Target address might be specified beforehand by Mixins
            self.target_address = ContractSpecs[blockchain].Queries.address
        else:
            self.target_address = ContractSpecs[blockchain].Vault.address
        super().__init__(avatar=avatar)
        self.args.pool_id = pool_id
        self.args.assets = assets
        self.args.min_amounts_out = min_amounts_out
        self.args.user_data = self.encode_user_data(user_data)
        self.args.request = [
            self.args.assets,
            self.args.min_amounts_out,
            self.args.user_data,
            self.fixed_arguments["to_internal_balance"],
        ]

    def encode_user_data(self, user_data):
        return eth_abi.encode(self.user_data_abi, user_data)


class Join(ContractMethod):
    name = "joinPool"
    in_signature = (
        ("pool_id", "bytes32"),
        ("sender", "address"),
        ("recipient", "address"),
        (
            "request",
            (
                (
                    ("assets", "address[]"),  # list of tokens, ordered numerically
                    ("max_amounts_in", "uint256[]"),  # the lower limits for the tokens to receive
                    ("user_data", "bytes"),
                    # userData encodes a ExitKind to tell the pool what style of exit you're performing
                    ("to_internal_balance", "bool"),
                ),
                "tuple",
            ),
        ),
    )
    fixed_arguments = {"sender": AvatarAddress, "recipient": AvatarAddress, "to_internal_balance": False}
    user_data_abi = None

    def __init__(
        self,
        blockchain: Blockchain,
        pool_id: str,
        avatar: Address,
        assets: list[Address],
        max_amounts_in: list[int],
        user_data: list,
    ):
        if self.name == "queryJoin":  # Target address might be specified beforehand by Mixins
            self.target_address = ContractSpecs[blockchain].Queries.address
        else:
            self.target_address = ContractSpecs[blockchain].Vault.address
        super().__init__(avatar=avatar)
        self.args.pool_id = pool_id
        self.args.assets = assets
        self.args.max_amounts_in = max_amounts_in
        self.args.user_data = self.encode_user_data(user_data)
        self.args.request = [
            self.args.assets,
            self.args.max_amounts_in,
            self.args.user_data,
            self.fixed_arguments["to_internal_balance"],
        ]

    def encode_user_data(self, user_data):
        return eth_abi.encode(self.user_data_abi, user_data)


class SingleSwap(ContractMethod):
    target_address = None
    name = "swap"
    in_signature = (
        (
            "single_swap",
            (
                (
                    ("pool_id", "bytes32"),
                    ("kind", "uint8"),
                    ("asset_in", "address"),
                    ("asset_out", "address"),
                    ("amount", "uint256"),
                    ("user_data", "bytes"),
                ),
                "tuple",
            ),
        ),
        (
            "funds",
            (
                (
                    ("sender", "address"),
                    ("from_internal_balance", "bool"),
                    ("recipient", "address"),
                    ("to_internal_balance", "bool"),
                ),
                "tuple",
            ),
        ),
        ("limit", "uint256"),
        ("deadline", "uint256"),
    )
    fixed_arguments = {
        "sender": AvatarAddress,
        "recipient": AvatarAddress,
        "from_internal_balance": False,
        "to_internal_balance": False,
        "user_data": "0x",
        "deadline": MAX_UINT256,
    }

    def __init__(
        self,
        blockchain: Blockchain,
        pool_id: str,
        avatar: Address,
        swap_kind: SwapKind,
        token_in_address: Address,
        token_out_address: Address,
        amount: int,
        limit: int,
    ):
        self.target_address = ContractSpecs[blockchain].Vault.address
        super().__init__(avatar=avatar)
        self.args.single_swap["pool_id"] = pool_id
        self.args.single_swap["kind"] = swap_kind
        self.args.single_swap["asset_in"] = token_in_address
        self.args.single_swap["asset_out"] = token_out_address
        self.args.single_swap["amount"] = amount
        self.args.single_swap["user_data"] = self.fixed_arguments["user_data"]
        self.args.funds = [
            self.fixed_arguments["sender"],
            self.fixed_arguments["from_internal_balance"],
            self.fixed_arguments["recipient"],
            self.fixed_arguments["to_internal_balance"],
        ]
        self.args.deadline = self.fixed_arguments["deadline"]
        self.args.limit = limit
