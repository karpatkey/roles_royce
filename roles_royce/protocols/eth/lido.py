from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Method


class Approve(Method):
    """approve stETH with wstETH as spender"""
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]
    fixed_arguments = {"spender": ETHAddr.wstETH}
    target_address = ETHAddr.stETH

    def __init__(self, amount: int):
        self.amount = amount


class Deposit(Method):
    """sender deposits ETH and receives stETH"""
    name = "submit"
    in_signature = [("referral", "address")]
    fixed_arguments = {"referral": ETHAddr.ZERO}
    target_address = ETHAddr.stETH

    def __init__(self, eth_amount: int):
        self.value = eth_amount


class Wrap(Method):
    """sender deposits stETH and receives wstETH"""
    name = "wrap"
    in_signature = [("amount", "uint256")]
    target_address = ETHAddr.wstETH

    def __init__(self, amount: int):
        """Amount of wstETH user receives after wrap"""
        self.amount = amount


class Unwrap(Method):
    """sender redeems wstETH and receives stETH"""
    name = "unwrap"
    in_signature = [("amount", "uint256")]
    target_address = ETHAddr.wstETH

    def __init__(self, amount: int):
        """Amount of stETH user receives after unwrap"""
        self.amount = amount
