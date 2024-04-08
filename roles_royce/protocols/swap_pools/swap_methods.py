from defabipedia.types import Blockchain
from defabipedia.uniswap_v3 import ContractSpecs

from roles_royce.protocols.base import Address, AvatarAddress, BaseApproveForToken, ContractMethod, Operation


class SwapCurve(ContractMethod):
    name = "exchange"
    in_signature = (("token_x", "int128"), ("token_y", "int128"), ("amount_x", "uint256"), ("min_amount_y", "uint256"))

    def __init__(
        self,
        blockchain: Blockchain,
        pool_address: Address,
        token_x: int,
        token_y: int,
        amount_x: int,
        min_amount_y: int,
    ):
        super().__init__()
        self.target_address = pool_address
        self.args.token_x = token_x
        self.args.token_y = token_y
        self.args.amount_x = amount_x
        self.args.min_amount_y = min_amount_y


class ApproveCurve(ContractMethod):
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]

    def __init__(self, blockchain: Blockchain, token_address: Address, spender: Address, amount: int):
        super().__init__()
        self.target_address = token_address
        self.args.spender = spender
        self.args.amount = amount


class SwapUniswapV3(ContractMethod):
    name = "exactInputSingle"
    in_signature = [
        (
            "params",
            (
                (
                    ("token_in", "address"),
                    ("token_out", "address"),
                    ("fee", "uint24"),
                    ("recipient", "address"),
                    ("amount_in", "uint256"),
                    ("min_amount_out", "uint256"),
                    ("limit_price", "uint160"),
                ),
                "tuple",
            ),
        )
    ]
    fixed_arguments = {"recipient": AvatarAddress, "limit_price": 0}
    out_signature = [("amount_out", "uint256")]

    def __init__(
        self,
        blockchain: Blockchain,
        token_in: Address,
        token_out: Address,
        avatar: Address,
        amount_in: int,
        min_amount_out: int,
        fee: int = 100,
    ):
        self.target_address = ContractSpecs[blockchain].UniV3_SwapRouter.address
        super().__init__(avatar=avatar)
        self.args.token_in = token_in
        self.args.token_out = token_out
        self.args.amount_in = amount_in
        self.args.min_amount_out = min_amount_out
        self.args.fee = fee
        self.args.receiver = avatar
        self.args.params = [
            self.args.token_in,
            self.args.token_out,
            self.args.fee,
            self.args.receiver,
            self.args.amount_in,
            self.args.min_amount_out,
            self.fixed_arguments["limit_price"],
        ]


class ApproveUniswapV3(ContractMethod):
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]

    def __init__(self, blockchain: Blockchain, token_address: Address, amount: int):
        super().__init__()
        self.target_address = token_address
        self.args.spender = ContractSpecs[blockchain].UniV3_SwapRouter.address
        self.args.amount = amount

class WrapEther(ContractMethod):
    name = "deposit"

    def __init__(self, blockchain: Blockchain, eth_amount: int):
        super().__init__(value=eth_amount)
        self.target_address = ContractSpecs[blockchain].WETH.address

