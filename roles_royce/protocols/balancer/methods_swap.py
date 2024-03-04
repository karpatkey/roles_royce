from roles_royce.constants import MAX_UINT256
from defabipedia.types import Blockchain, Chain
from roles_royce.protocols.base import ContractMethod, AvatarAddress, Address
from roles_royce.protocols.balancer.types_and_enums import SwapKind
from web3 import Web3
from defabipedia.balancer import ContractSpecs


class SingleSwap(ContractMethod):
    target_address = None
    name = "swap"
    in_signature = (
        ("single_swap", (
            (
                ("pool_id", "bytes32"),
                ("kind", "uint8"),
                ("asset_in", "address"),
                ("asset_out", "address"),
                ("amount", "uint256"),
                ("user_data", "bytes"),
            ),
            "tuple"),
         ),
        ("funds", (
            (
                ("sender", "address"),
                ("from_internal_balance", "bool"),
                ("recipient", "address"),
                ("to_internal_balance", "bool")
            ),
            "tuple"),
         ),
        ("limit", "uint256"),
        ("deadline", "uint256")
    )
    fixed_arguments = {"sender": AvatarAddress, "recipient": AvatarAddress, "from_internal_balance": False,
                       "to_internal_balance": False, "user_data": "0x", "deadline": MAX_UINT256}

    def __init__(self,
                 blockchain: Blockchain,
                 pool_id: str,
                 avatar: Address,
                 swap_kind: SwapKind,
                 token_in_address: Address,
                 token_out_address: Address,
                 amount: int,
                 limit: int):
        self.target_address = ContractSpecs[blockchain].Vault.address
        super().__init__(avatar=avatar)
        self.args.single_swap["pool_id"] = pool_id
        self.args.single_swap["kind"] = swap_kind
        self.args.single_swap["asset_in"] = token_in_address
        self.args.single_swap["asset_out"] = token_out_address
        self.args.single_swap["amount"] = amount
        self.args.single_swap["user_data"] = self.fixed_arguments["user_data"]
        self.args.funds = [self.fixed_arguments["sender"], self.fixed_arguments["from_internal_balance"],
                           self.fixed_arguments["recipient"], self.fixed_arguments["to_internal_balance"]]
        self.args.deadline = self.fixed_arguments["deadline"]
        self.args.limit = limit


class ExactTokenInSingleSwap(SingleSwap):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 token_in_address: Address,
                 token_out_address: Address,
                 amount_in: int,
                 min_amount_out: int):
        swap_kind = SwapKind.OutGivenExactIn
        super().__init__(blockchain=Chain.get_blockchain_by_chain_id(w3),
                         pool_id=pool_id,
                         avatar=avatar,
                         swap_kind=swap_kind,
                         token_in_address=token_in_address,
                         token_out_address=token_out_address,
                         amount=amount_in,
                         limit=min_amount_out)


class ExactTokenOutSingleSwap(SingleSwap):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 token_in_address: Address,
                 token_out_address: Address,
                 amount_out: int,
                 max_amount_in: int):
        swap_kind = SwapKind.InGivenExactOut
        super().__init__(blockchain=Chain.get_blockchain_by_chain_id(w3),
                         pool_id=pool_id,
                         avatar=avatar,
                         swap_kind=swap_kind,
                         token_in_address=token_in_address,
                         token_out_address=token_out_address,
                         amount=amount_out,
                         limit=max_amount_in)
        
class QuerySwap:
    name = "querySwap"
    out_signature = [("amount_out", "uint256")]

class ExactSingleTokenInQuerySwap(QuerySwap, ExactTokenInSingleSwap):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 token_amount_in: int,
                 token_out_address: Address):
        super().__init__(w3=w3,
                         pool_id=pool_id,
                         avatar=AvatarAddress,
                         bpt_amount_in=token_amount_in,
                         token_out_address=token_out_address,
                         min_amount_out=0)