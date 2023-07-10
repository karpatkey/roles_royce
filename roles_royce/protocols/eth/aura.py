from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Method, BaseApproveForToken, Address


class ApproveForBooster(BaseApproveForToken):
    """approve LPToken with AURABooster as spender"""
    fixed_arguments = {"spender": ETHAddr.AURABooster}


class WithdrawAndUndwrapStakedBPT(Method):
    """withdraw and unwrap AURAVaultToken"""
    name = "withdrawAndUnwrap"
    in_signature = [("amount", "uint256"), ("claim", "bool")]
    fixed_arguments = {"claim": True}

    def __init__(self, reward_address: Address, amount: int):
        super().__init__()
        self.target_address = reward_address
        self.args.amount = amount


class DepositBPT(Method):
    """deposit BPT token"""
    name = "deposit"
    in_signature = [("pool_id", "uint256"), ("amount", "uint256"), ("stake", "bool")]
    fixed_arguments = {"stake": True}
    target_address = ETHAddr.AURABooster

    def __init__(self, pool_id: int, amount: int):
        super().__init__()
        self.args.pool_id = pool_id
        self.args.amount = amount
