from enum import IntEnum

from roles_royce.constants import ETHAddr, CrossChainAddr
from roles_royce.protocols.base import Method, InvalidArgument, AvatarSafeAddress, Address
from roles_royce.protocols.eth.aave import Approve

class ApproveForBalancerVault(Approve):
    """approve Token with BalancerVault as spender"""
    fixed_arguments = {"spender": CrossChainAddr.BalancerVault}

    def __init__(self, token: Address, amount: int):
        super().__init__(amount)
        self.token = token

class ApproveForWETH(Approve):
    """Approve WETH with BalancerVault as spender"""
    fixed_arguments = {"spender": CrossChainAddr.BalancerVault}
    token = ETHAddr.WETH

class ApproveForBAL(Approve):
    """Approve BAL with BalancerVault as spender"""
    fixed_arguments = {"spender": CrossChainAddr.BalancerVault}
    token = ETHAddr.BAL

class RemoveLiquidity(Method):
    """Sender exits pool"""
    name = "exitPool"
    request = [("assets", "address[]"), ("limits", "uint256[]"), ("userData", "bytes"), ("useInternalBalance", "bool")]
    signature = [("poolId", "bytes32"), ("sender", "address"), ("recipient", "address"), (request, "tuple")]
    fixed_arguments = {"useInternalData": False}
    