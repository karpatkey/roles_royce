from roles_royce.protocols.base import ContractMethod, Address
from defabipedia.types import Blockchain
from defabipedia.uniswap_v3 import ContractSpecs

class QuoteCurve(ContractMethod):
    name = "get_dy"
    in_signature = (
        ("token_x", "int128"),
        ("token_y", "int128"),
        ("amount_x", "uint256")
    )
    out_signature = [("amount_y", "uint256")]

    def __init__(self,
                 blockchain: Blockchain,
                 pool_address: Address,
                 token_x: int,
                 token_y: int,
                 amount_x: int):
        super().__init__()
        self.target_address = pool_address
        self.args.token_x = token_x
        self.args.token_y = token_y
        self.args.amount_x = amount_x

class QuoteUniswapV3(ContractMethod):
    name = "quoteExactInputSingle"
    in_signature = (
        ("token_in", "address"),
        ("token_out", "address"),
        ("fee", "uint24"),
        ("amount_in", "uint256"),
        ("limit_price", "uint160")
    )
    fixed_arguments = {"limit_price": 0} 

    def __init__(self,
                 blockchain: Blockchain,
                 token_in: Address,
                 token_out: Address,
                 amount_in: int,
                 fee: int = 100):
        self.target_address = ContractSpecs[blockchain].UniV3_Quoter.address
        super().__init__()
        self.args.token_in = token_in
        self.args.token_out = token_out
        self.args.amount_in = amount_in
        self.args.fee = fee