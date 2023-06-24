from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Method, Address

class ApproveDAI(Method):
    """approve DAI with CDP manager as spender"""
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]
    target_address = ETHAddr.DAI

    def __init__(self, spender: Address, amount: int):
        self.spender = spender
        self.amount = amount

class ApproveWstETH(ApproveDAI):
    """approve stETH with CDP manager as spender"""
    target_address = ETHAddr.wstETH

class ApproveIOU(ApproveDAI):
    """approve IOU to get MKR undelegated"""
    target_address = ETHAddr.MakerIOU

class WithdrawCollateral(Method):
    """withdraw collateral from vault"""
    name = "freeGem"
    in_signature = [("cdp_manager", "address"), ("adapter", "address"),
                    ("cdp_vault", "uint256"), ("amount", "uint256")]
    fixed_arguments = {"cdp_manager": ETHAddr.MakerCDPManager}
    target_address = ETHAddr.MakerProxy

    def __init__(self, adapter: Address, cdp_vault: int, amount: int):
        self.adapter = adapter
        self.cdp_vault = cdp_vault
        self.amount = amount

class DepositCollateral(Method):
    """deposit collateral in vault"""
    name = "lockGem"
    in_signature = [("cdp_manager", "address"), ("adapter", "address"),
                    ("cdp_vault", "uint256"), ("amount", "uint256"),
                    ("transfer_from", "bool")]
    fixed_arguments = {"cdp_manager": ETHAddr.MakerCDPManager, "transfer_from": True}
    target_address = ETHAddr.MakerProxy

    def __init__(self, adapter: Address, cdp_vault: int, amount: int):
        self.adapter = adapter
        self.cdp_vault = cdp_vault
        self.amount = amount
 
class PayBack(WithdrawCollateral):
    """pay back borrowed"""
    name = "wipe"

class MintDAI(Method):
    """mint DAI to borrow"""
    name = "draw"
    in_signature = [("cdp_manager", "address"), ("jug", "address"),
                    ("adapter", "address"), ("cdp_vault", "uint256"),
                    ("amount", "uint256")]
    fixed_arguments = {"cdp_manager": ETHAddr.MakerCDPManager, "jug": ETHAddr.MakerJug} 
    target_address = ETHAddr.MakerProxy

    def __init__(self, adapter: Address, cdp_vault: int, amount: int):
        self.adapter = adapter
        self.cdp_vault = cdp_vault
        self.amount = amount
    
class PayBackAndWithdrawCol(Method):
    """be free"""
    name = "wipeAllAndFreeGem"
    in_signature = [("cdp_manager", "address"), ("adapter", "address"),
                    ("dai_join", "address"), ("cdp_vault", "uint256"),
                    ("amount", "uint256")]
    fixed_arguments = {"cdp_manager": ETHAddr.MakerCDPManager, "jug": ETHAddr.MakerJug}
    target_address = ETHAddr.MakerProxy  

    def __init__(self, adapter: Address, dai_join: Address, cdp_vault: int, amount: int):
        self.adapter = adapter
        self.cdp_vault = cdp_vault
        self.amount = amount
        self.dai_join = dai_join

class UndelegateMKR(Method):
    """undelegate any MKR"""
    name = "free"
    in_signature = [("amount", "uint256")]

    def __init__(self, amount: int):
        self.amount = amount
   