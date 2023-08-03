from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Method, Address

class ApproveDAI(Method):
    """approve DAI with CDP manager as spender"""
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]
    target_address = ETHAddr.DAI

    def __init__(self, spender: Address, amount: int):
        super().__init__()
        self.args.spender = spender
        self.args.amount = amount

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
        super().__init__()
        self.args.adapter = adapter
        self.args.cdp_vault = cdp_vault
        self.args.amount = amount

class DepositCollateral(Method):
    """deposit collateral in vault"""
    name = "lockGem"
    in_signature = [("cdp_manager", "address"), ("adapter", "address"),
                    ("cdp_vault", "uint256"), ("amount", "uint256"),
                    ("transfer_from", "bool")]
    fixed_arguments = {"cdp_manager": ETHAddr.MakerCDPManager, "transfer_from": True}
    target_address = ETHAddr.MakerProxy

    def __init__(self, adapter: Address, cdp_vault: int, amount: int):
        super().__init__()
        self.args.adapter = adapter
        self.args.cdp_vault = cdp_vault
        self.args.amount = amount
 
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
        super().__init__()
        self.args.adapter = adapter
        self.args.cdp_vault = cdp_vault
        self.args.amount = amount
    
class PayBackAndWithdrawCol(Method):
    """be free"""
    name = "wipeAllAndFreeGem"
    in_signature = [("cdp_manager", "address"), ("adapter", "address"),
                    ("dai_join", "address"), ("cdp_vault", "uint256"),
                    ("amount", "uint256")]
    fixed_arguments = {"cdp_manager": ETHAddr.MakerCDPManager, "jug": ETHAddr.MakerJug}
    target_address = ETHAddr.MakerProxy  

    def __init__(self, adapter: Address, dai_join: Address, cdp_vault: int, amount: int):
        super().__init__()
        self.args.adapter = adapter
        self.args.cdp_vault = cdp_vault
        self.args.amount = amount
        self.args.dai_join = dai_join

class UndelegateMKR(Method):
    """undelegate any MKR"""
    name = "free"
    in_signature = [("amount", "uint256")]

    def __init__(self, amount: int):
        super().__init__()
        self.args.amount = amount

class DelegateMKR(Method):
    """delegate MKR"""
    name = "lock"
    in_signature = [("amount", "uint256")]

    def __init__(self, amount: int):
        super().__init__()
        self.args.amount = amount

class JoinPot(Method):
    """join the pot through DSR Manager"""
    name = "join"
    in_signature = [("destination","address"),("amount", "uint256")]
    target_address = ETHAddr.MakerDSRManager

    def __init__(self, destination: Address, amount: int):
        super().__init__()
        self.args.destination = destination
        self.args.amount = amount

class ExitPot(Method):
    """exit the pot through DSR Manager"""
    name = "exit"
    in_signature = [("destination","address"),("amount", "uint256")]
    target_address = ETHAddr.MakerDSRManager

    def __init__(self, destination: Address, amount: int):
        super().__init__()
        self.args.destination = destination
        self.args.amount = amount

class DripThePot(Method):
    """drip the pot to be able to join and exit"""
    name = "drip"
    in_signature = []
    target_address = ETHAddr.MakerDSRManager

    def __init__(self):
        super().__init__()
   