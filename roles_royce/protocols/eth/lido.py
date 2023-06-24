from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Method, Address


class Approve(Method):
    """approve stETH with wstETH as spender"""
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]
    fixed_arguments = {"spender": ETHAddr.wstETH}
    target_address = ETHAddr.stETH

    def __init__(self, amount: int):
        super().__init__()
        self.args.amount = amount

class ApproveWithdrawalStETH(Approve):
    """approve stETH with withdrawal contract as spender"""
    fixed_arguments = {"spender": ETHAddr.unstETH}
    target_address = ETHAddr.stETH

class ApproveWithdrawalWstETH(Approve):
    """approve wstETH with withdrawal contract as spender"""
    fixed_arguments = {"spender": ETHAddr.unstETH}
    target_address = ETHAddr.wstETH

class Deposit(Method):
    """sender deposits ETH and receives stETH"""
    name = "submit"
    in_signature = [("referral", "address")]
    fixed_arguments = {"referral": ETHAddr.ZERO}
    target_address = ETHAddr.stETH

    def __init__(self, eth_amount: int):
        super().__init__(value=eth_amount)


class Wrap(Method):
    """sender deposits stETH and receives wstETH"""
    name = "wrap"
    in_signature = [("amount", "uint256")]
    target_address = ETHAddr.wstETH

    def __init__(self, amount: int):
        """Amount of wstETH user receives after wrap"""
        super().__init__()
        self.args.amount = amount


class Unwrap(Method):
    """sender redeems wstETH and receives stETH"""
    name = "unwrap"
    in_signature = [("amount", "uint256")]
    target_address = ETHAddr.wstETH

    def __init__(self, amount: int):
        """Amount of stETH user receives after unwrap"""
        super().__init__()
        self.args.amount = amount

class RequestWithdrawals(Method):
    """sender requests a claim on his ETH from stETH"""
    name = "requestWithdrawals"
    in_signature = [("amounts", "uint256[]"), ("owner", "address")]
    target_address = ETHAddr.unstETH

    def __init__(self, amounts: list, owner: Address):
        super().__init__()
        self.args.amounts = amounts
        self.args.owner = owner

#TODO: the amounts is a list, because it has a max of 1000 stETH per element, should built that in

class RequestWithdrawalsWstETH(RequestWithdrawals):
    """sender requests a claim on his ETH from wstETH"""
    name = "requestWithdrawalsWstETH"

class ClaimWithdrawals(Method):
    """sender wants to claim his ETH"""
    name = "claimWithdrawals"
    in_signature = [("requestIds", "uint256[]"), ("hints", "uint256[]")]
    target_address = ETHAddr.unstETH

    def __init__(self, requestIds: list, hints: list):
        """Amount of ETH user receives after claiming"""
        super().__init__()
        self.args.requestIds = requestIds
        self.args.hints = hints
