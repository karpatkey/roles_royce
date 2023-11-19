from time import time
from roles_royce.protocols.base import ContractMethod, Address, AvatarAddress, BaseApprove
from defabipedia.cowswap_signer import ContractSpecs
from defabipedia.types import Blockchain
from web3 import Web3

class SignOrder(ContractMethod):
    """sign an order with the cowswap signer contract"""
    target_address = None
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
            ("buy_token_balance", "bytes32"),
            ),
            "tuple"),
        ),
        ("valid_duration", "uint32"),
        ("fee_amount_bp", "uint256") 
    )
    fixed_arguments = {"receiver": AvatarAddress,
                       "app_data": Web3.keccak(text="santi_the_best"),
                       "partially_fillable": False,
                       "sell_token_balance": Web3.keccak(text="erc20"),
                       "buy_token_balance": Web3.keccak(text="erc20")}

    def __init__(self, 
                 blockchain: Blockchain,
                 avatar: Address,
                 sell_token: Address,
                 buy_token: Address,
                 sell_amount: int,
                 buy_amount: int,
                 fee_amount: int,
                 valid_to: int,
                 kind: str,
                 valid_duration: int,
                 fee_amount_bp: int):
        self.target_address = ContractSpecs[blockchain].CowswapSigner.address
        super().__init__(avatar=avatar)
        self.args.sell_token = sell_token
        self.args.buy_token = buy_token
        self.args.receiver = avatar
        self.args.sell_amount = sell_amount
        self.args.buy_amount = buy_amount
        self.args.valid_to = valid_to
        self.args.fee_amount = fee_amount
        self.args.kind = Web3.keccak(text=kind)
        self.args.order = [self.args.sell_token,
                            self.args.buy_token,
                            self.args.receiver,
                            self.args.sell_amount,
                            self.args.buy_amount,
                            self.args.valid_to,
                            self.fixed_arguments['app_data'],
                            self.args.fee_amount,
                            self.args.kind,
                            self.fixed_arguments['partially_fillable'],
                            self.fixed_arguments['sell_token_balance'],
                            self.fixed_arguments['buy_token_balance']]
        self.args.valid_duration = valid_duration
        self.args.fee_amount_bp = fee_amount_bp


        
        


