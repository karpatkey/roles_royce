from defabipedia.balancer import ContractSpecs
from defabipedia.types import Blockchain, Chain
from web3 import Web3

from roles_royce.constants import MAX_UINT256
from roles_royce.protocols.balancer.types_and_enums import SwapKind
from roles_royce.protocols.base import Address, AvatarAddress, ContractMethod
from roles_royce.roles_modifier import Operation


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
                    ("amount_in", "uint256"),
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
        ("min_amount_out", "uint256"),
        ("deadline", "uint256"),
    )
    fixed_arguments = {
        "sender": AvatarAddress,
        "recipient": AvatarAddress,
        "from_internal_balance": False,
        "to_internal_balance": False,
        "user_data": "0x",
    }

    def __init__(
        self,
        blockchain: str,
        pool_id: str,
        avatar: Address,
        kind: SwapKind,
        token_in_address: Address,
        token_out_address: Address,
        amount_in: int,
        min_amount_out: int,
        deadline: int,
    ):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].Vault.address
        self.args.pool_id = pool_id
        self.args.kind = kind
        self.args.asset_in = token_in_address
        self.args.asset_out = token_out_address
        self.args.amount_in = amount_in
        self.args.user_data = self.fixed_arguments["user_data"]
        self.args.single_swap = [
            self.args.pool_id,
            self.args.kind,
            self.args.asset_in,
            self.args.asset_out,
            self.args.amount_in,
            self.args.user_data,
        ]
        self.args.funds = [
            self.fixed_arguments["sender"],
            self.fixed_arguments["from_internal_balance"],
            self.fixed_arguments["recipient"],
            self.fixed_arguments["to_internal_balance"],
        ]
        self.args.deadline = deadline
        self.args.min_amount_out = min_amount_out


class ExactTokenInSingleSwap(SingleSwap):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        token_in_address: Address,
        token_out_address: Address,
        amount_in: int,
        min_amount_out: int,
    ):
        swap_kind = SwapKind.OutGivenExactIn
        super().__init__(
            blockchain=Chain.get_blockchain_by_chain_id(w3),
            pool_id=pool_id,
            avatar=avatar,
            swap_kind=swap_kind,
            token_in_address=token_in_address,
            token_out_address=token_out_address,
            amount_in=amount_in,
            min_amount_out=min_amount_out,
        )


class ExactTokenOutSingleSwap(SingleSwap):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        token_in_address: Address,
        token_out_address: Address,
        amount_out: int,
        max_amount_in: int,
    ):
        swap_kind = SwapKind.InGivenExactOut
        super().__init__(
            blockchain=Chain.get_blockchain_by_chain_id(w3),
            pool_id=pool_id,
            avatar=avatar,
            swap_kind=swap_kind,
            token_in_address=token_in_address,
            token_out_address=token_out_address,
            amount=amount_out,
            max_amount_in=max_amount_in,
        )


class QuerySwap(ContractMethod):
    target_address = None
    name = "querySwap"
    out_signature = [("amount_out", "uint256")]
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
    )
    fixed_arguments = {
        "sender": AvatarAddress,
        "recipient": AvatarAddress,
        "from_internal_balance": False,
        "to_internal_balance": False,
        "user_data": "0x",
        "kind": SwapKind.OutGivenExactIn,
    }

    def __init__(
        self,
        blockchain: Blockchain,
        pool_id: str,
        avatar: Address,
        token_in_address: Address,
        token_out_address: Address,
        amount: int,
    ):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].Queries.address
        self.args.pool_id = pool_id
        self.args.asset_in = token_in_address
        self.args.asset_out = token_out_address
        self.args.amount = amount
        self.args.user_data = self.fixed_arguments["user_data"]
        self.args.single_swap = [
            self.args.pool_id,
            self.fixed_arguments["kind"],
            self.args.asset_in,
            self.args.asset_out,
            self.args.amount,
            self.args.user_data,
        ]
        self.args.funds = [
            self.fixed_arguments["sender"],
            self.fixed_arguments["from_internal_balance"],
            self.fixed_arguments["recipient"],
            self.fixed_arguments["to_internal_balance"],
        ]
