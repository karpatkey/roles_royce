from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Method, Address


class Approve(Method):
    """approve stETH with wstETH as spender"""
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]
    fixed_arguments = {"spender": ETHAddr.wstETH}
    target_address = ETHAddr.stETH

    def __init__(self, amount: int):
        self.amount = amount

class ApproveWithdrawal(Method):
    """approve stETH with withdrawal contract as spender"""
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]
    fixed_arguments = {"spender": ETHAddr.unstETH}
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

class RequestWithdrawals(Method):
    """sender requests a claim on his ETH"""
    name = "requestWithdrawals"
    in_signature = [("_amounts", "uint256[]"), ("_owner", "address")]
    target_address = ETHAddr.unstETH

    def __init__(self, _amounts: list, _owner: Address):
        self._amounts = _amounts
        self._owner = _owner

#TODO: the amounts is a list, because it has a max of 1000 stETH per element, should built that in

class ClaimWithdrawals(Method):
    """sender wants to claim his ETH"""
    name = "claimWithdrawals"
    in_signature = [("_requestIds", "uint256[]"), ("_hints", "uint256[]")]
    target_address = ETHAddr.unstETH

    def __init__(self, _requestIds: list, _hints: list):
        """Amount of ETH user receives after claiming"""
        self._requestIds = _requestIds
        self._hints = _hints   