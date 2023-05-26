from enum import IntEnum

from roles_royce.constants import ETHAddr, CrossChainAddr
from roles_royce.protocols.base import Method, InvalidArgument, AvatarSafeAddress, Address
from roles_royce.protocols.eth.aave import Approve

class ApproveForBooster(Approve):
    """approve LPToken with AURABooster as spender"""
    fixed_arguments = {"spender": ETHAddr.AURABooster}

    def __init__(self, token: Address, amount: int):
        super().__init__(amount)
        self.token = token

class WithdrawAndUndwrapStakedBPT(Method):
    """withdraw and unwrap"""
    name = "withdrawAndUnwrap"
    signature = [("amount", "uint256"), ("claim", "bool")]
    fixed_arguments = {"claim": True}

    def __init__(self, amount: int, avatar: Address):
        self.amount = amount
        self.avatar = avatar

