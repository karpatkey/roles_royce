from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Method, Address, AvatarAddress, BaseApprove


class ApproveWithdrawalDAI(BaseApprove):
    """approve stETH withdrawal with wstETH as spender"""
    fixed_arguments = {"spender": ETHAddr.sDAI}
    token = ETHAddr.DAI


class DepositDAI(Method):
    """Sender deposits DAI and receives sDAI in exchange (the DAI is deposited in Maker - DSR)"""
    name = "deposit"
    in_signature = [("amount", "uint256"), ("receiver", "address")]
    fixed_arguments = {"receiver": AvatarAddress}
    target_address = ETHAddr.sDAI

    def __init__(self, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.amount = amount


class WithdrawWithSDAI(Method):
    """Sender redeems sDAI and withdraws DAI"""
    name = "redeem"
    in_signature = [("amount", "uint256"), ("receiver", "address"), ("owner", "address")]
    fixed_arguments = {"receiver": AvatarAddress, "owner": AvatarAddress}
    target_address = ETHAddr.sDAI

    def __init__(self, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.amount = amount
