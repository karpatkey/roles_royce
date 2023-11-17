from time import time
from roles_royce.protocols.base import ContractMethod, Address, AvatarAddress, BaseApprove

class SignOrder(ContractMethod):
    """sign an order with the cowswap signer contract"""
    name = "signOrder"
    in_signature = (
        ("order", (
            (
            ("sell_token", "address"),
            ("buy_token", "address"),
            ("receiver", "address"),
            ("sell_amount", "uint256"),
            ("buy_amount", "uint256"),
            ("valid_to", "uint32"),
            ("app_data", "bytes32"),
            ("fee_amount", "uint256"),
            ("kind", "bytes32"),
            ("partially_fillable", "bool"),
            ("sell_token_balance", "bytes32"),
            ("buy_token_balance", "bytes32")
            ),
            "tuple"),
        ),
        ("valid_duration", "uint32"),
        ("fee_amount_bp", "uint256") 
    )
    fixed_arguments = {"receiver": AvatarAddress,
                       "app_data": "0x00000000000000000000000000000000000000000000000000000000000sant1",
                       "partially_fillable": False,
                       "sell_token_balance": "erc20",
                       "buy_token_balance": "erc20"}

    def __init__(self, 
                 sell_token: Address,
                 buy_token: Address,
                 sell_amount: int,
                 buy_amount: int,
                 fee_amount: int,
                 kind: str,
                 valid_duration: int,
                 fee_amount_bp: int):
        super().__init__()
        self.args.sell_token = sell_token
        self.args.buy_token = buy_token
        self.args.sell_amount = sell_amount
        self.args.buy_amount = buy_amount
        self.args.valid_to = int(time.time()) + 120
        self.args.fee_amount = fee_amount
        self.args.kind = kind
        self.args.valid_duration = valid_duration
        self.args.fee_amount_bp = fee_amount_bp


        
        


