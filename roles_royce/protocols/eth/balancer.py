from enum import IntEnum

from roles_royce.constants import ETHAddr, CrossChainAddr
from roles_royce.protocols.base import Method, InvalidArgument, AvatarSafeAddress, Address
from roles_royce.protocols.eth.aave import Approve

    

class ApproveForVault(Approve):
    """approve Token with BalancerVault as spender"""
    fixed_arguments = {"spender": CrossChainAddr.BalancerVault}

    def __init__(self, token: Address, amount: int):
        super().__init__(amount)
        self.token = token   

class ExactBPTInForOneTokenOut(Method):
    signature = [("EXACT_BPT_IN_FOR_ONE_TOKEN_OUT", "uint256"), ("bptAmountIn", "uint256"), ("exitTokenIndex", "uint256")]
    fixed_arguments = {"EXACT_BPT_IN_FOR_ONE_TOKEN_OUT": 1}

    def __init__(self, bpt_amount_in: int, exit_token_index: int):
        self.bpt_amount_in = bpt_amount_in
        self.exit_token_index = exit_token_index

class ExactBPTInForTokensOut(Method):
    signature = [("EXACT_BPT_IN_FOR_TOKENS_OUT", "uint256"), ("bptAmountIn", "uint256")]
    fixed_arguments = {"EXACT_BPT_IN_FOR_ONE_TOKEN_OUT": 2}

    def __init__(self, bpt_amount_in: int):
        self.bpt_amount_in = bpt_amount_in

class ExactBPTInForTokensOut(Method):
    signature = [("BPT_IN_FOR_EXACT_TOKENS_OUT", "uint256"), ("amountsOut", "uint256"), ("maxBPTAmountIn", "uint256")]
    fixed_arguments = {"EXACT_BPT_IN_FOR_ONE_TOKEN_OUT": 3}

    def __init__(self, amounts_out: int, max_bpt_amount_in: int):
        self.amounts_out = amounts_out
        self.max_bpt_amount_in = max_bpt_amount_in

class Userdata(Method):
    signature = [()]

class ExitPoolRequest(Method):
    signature = [("assets", "address[]"), ("minAmountsOut", "uint256[]"), ("bytes", Userdata)]

class Exit(Method):
    signature = [("poolId", "bytes32"), ("sender", "address"), ("recipient", "address"), ("request", ExitPoolRequest)]

class QueryExit(Exit):
    """calculate amounts out for certain BPTin"""
    name = "queryExit"
    
class exitPool(Exit):
    name = "exitPool"
    target_address = CrossChainAddr.BalancerVault