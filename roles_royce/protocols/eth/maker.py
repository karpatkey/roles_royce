from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import ContractMethod, Address, AvatarAddress
import eth_abi

#-----------------------------------------------------#
"""Approvals"""
#-----------------------------------------------------#
class ApproveGem(ContractMethod):
    """approve gem with proxy as spender"""
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]

    # The spender can be the DSProxy or the GemJoin/EthJoin depending
    # on the approach used to handle the CDP
    def __init__(self, gem: Address, spender: Address, amount: int):
        super().__init__()
        self.target_address = gem
        self.args.spender = spender
        self.args.amount = amount

class ApproveDAI(ContractMethod):
    """approve DAI with proxy as spender"""
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]

    # The spender can be the DSProxy or the DaiJoin depending
    # on the approach used to handle the CDP
    def __init__(self, spender: Address, amount: int):
        super().__init__()
        self.target_address = ETHAddr.DAI
        self.args.spender = spender
        self.args.amount = amount

#-----------------------------------------------------#
"""CDP Module - Proxy Actions"""
#-----------------------------------------------------#
class Build(ContractMethod):
    """build DSProxy"""
    name = "build"
    target_address = ETHAddr.MakerProxyRegistry
    in_signature = []

    def __init__(self):
        super().__init__()

class ProxyExecute(ContractMethod):
    """execute proxy action"""
    name = "execute"
    in_signature = [("target", "address"), ("data", "bytes")]
    fixed_arguments = {"target": ETHAddr.MakerProxyActions}

    def __init__(self, proxy: Address, selector: str, action_abi: list, parameters: list, value:int = 0):
        super().__init__(value=value)
        self.target_address = proxy
        self.args.data = self.get_call_data(selector, action_abi, parameters)

    def get_call_data(self, selector: str, action_abi: list, parameters: list):
        abi_encoded = eth_abi.encode(action_abi, parameters)
        return selector + abi_encoded.hex()

class _ProxyAction(ProxyExecute):
    """Proxy action abstract class"""
    selector = None
    action_abi = None

    def __init__(self, proxy: Address, parameters:list, value:int = 0):
        super().__init__(proxy, self.selector, self.action_abi, parameters, value=value)

class ProxyActionOpen(_ProxyAction):
    """open CDP"""
    selector = "0x6aa3ee11" # open(address,address,bytes32)
    action_abi = ["address", "bytes32", "address"]

    def __init__(self, proxy: Address, ilk: str):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, ilk , proxy])

class ProxyActionLockGem(_ProxyAction):
    """lock gem"""
    selector = "0x3e29e565" # lockGem(address,address,uint256,uint256,bool)
    action_abi = ["address", "address", "uint256", "uint256", "bool"]

    def __init__(self, proxy: Address, gem_join: Address, cdp_id: int, wad: int, transfer_from: bool = True):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, gem_join, cdp_id, wad, transfer_from])

class ProxyActionLockETH(_ProxyAction):
    """lock ETH"""
    selector = "0xe205c108" # lockETH(address,address,uint256)
    action_abi = ["address", "address", "uint256"]

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, value: int):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, eth_join, cdp_id], value=value)

class ProxyActionFreeGem(_ProxyAction):
    """free gem"""
    selector = "0x6ab6a491" # freeGem(address,address,uint256,uint256)
    action_abi = ["address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, gem_join: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, gem_join, cdp_id, wad])

class ProxyActionFreeETH(_ProxyAction):
    """free ETH"""
    selector = "0x7b5a3b43" # freeETH(address,address,uint256,uint256)
    action_abi = ["address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, eth_join, cdp_id, wad])

class ProxyActionDraw(_ProxyAction):
    """draw DAI (borrow)"""
    selector = "0x9f6f3d5b" # draw(address,address,address,uint256,uint256)
    action_abi = ["address", "address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, ETHAddr.MakerJug, ETHAddr.MakerDaiJoin, cdp_id, wad])

class ProxyActionWipe(_ProxyAction):
    """wipe DAI (repay)"""
    selector = "0x4b666199" # wipe(address,address,uint256,uint256)
    action_abi = ["address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, ETHAddr.MakerDaiJoin, cdp_id, wad])

#-----------------------------------------------------#
"""CDP Module - CDPManager (no Proxy)"""
#-----------------------------------------------------#
class Open(ContractMethod):
    """open CDP"""
    name = "open"
    in_signature = [("ilk", "bytes32"), ("usr", "address")]
    target_address = ETHAddr.MakerCDPManager
    fixed_arguments = {"usr": AvatarAddress}

    def __init__(self, ilk: str, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.ilk = ilk

class Join(ContractMethod):
    """join token to the Vat"""
    name = "join"
    in_signature = [("usr", "bytes32"), ("wad", "uint256")]

    def __init__(self, assetJoin: Address, usr: Address, wad: int):
        super().__init__()
        self.target_address = assetJoin
        self.args.usr = usr
        self.args.wad = wad

class Frob(ContractMethod):
    """increments/decrements the ink amount of collateral 
    locked and increments/decrements the art amount of debt 
    in the cdp depositing the generated DAI or collateral freed 
    in the cdp address"""
    name = "frob"
    in_signature = [("cdp", "uint256"), ("dink", "uint256"), ("dart", "uint256")]
    target_address = ETHAddr.MakerCDPManager

    def __init__(self, cdp_id: int, dink: int, dart: int):
        super().__init__()
        self.args.cdp = cdp_id
        self.args.dink = dink
        self.args.dart = dart

class Drip(ContractMethod):
    """performs stability fee collection for a specific collateral 
    type when it is called (note that it is a public function and may 
    be called by anyone). drip does essentially three things: calculates 
    the change in the rate parameter for the collateral type specified 
    by ilk based on the time elapsed since the last update and the current 
    instantaneous rate (base + duty); calls Vat.fold to update the collateral's 
    rate, total tracked debt, and Vow surplus; updates ilks[ilk].rho to be 
    equal to the current timestamp"""
    name = "drip"
    in_signature = [("ilk", "bytes32")]
    target_address = ETHAddr.MakerJug

    def __init__(self, ilk: str):
        super().__init__()
        self.args.ilk = ilk

class Move(ContractMethod):
    """moves rad (precision 45) amount of DAI from the cdp (urn) to dst. 
    However, you still won't see the balance on your wallet. In order to 
    see the balance, you'll need to approve the DaiJoin adapter in Vat from 
    the system with the Vat.hope() function. After, you call the DaiJoin.exit() 
    to finally move the DAI to your wallet"""
    name = "move"
    in_signature = [("cdp", "uint256"), ("dst", "address"), ("rad", "uint256")]
    target_address = ETHAddr.MakerCDPManager
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, cdp_id: int, avatar: Address, wad: int):
        super().__init__(avatar=avatar)
        self.args.cdp = cdp_id
        self.args.wad = wad

class Hope(ContractMethod):
    """enable wish for a pair of addresses, where wish checks whether an address
    is allowed to modify another address's Gem or DAI balance"""
    name = "hope"
    in_signature = [("usr", "address")]
    target_address = ETHAddr.MakerVat
    fixed_arguments = {"usr": ETHAddr.MakerDaiJoin}

    def __init__(self):
        super().__init__()

class Exit(ContractMethod):
    """allows the the user to remove their desired token from the Vat"""
    name = "exit"
    in_signature = [("usr", "address"), ("wad", "uint256")]
    fixed_arguments = {"usr": AvatarAddress}

    def __init__(self, assetJoin: Address, avatar: Address, wad: int):
        super().__init__(avatar=avatar)
        self.target_address = assetJoin
        self.args.wad = wad

class Flux(ContractMethod):
    """moves wad amount of cdp collateral from cdp to dst"""
    name = "flux"
    in_signature = [("cdp", "uint256"), ("dst", "address"), ("wad", "uint256")]
    target_address = ETHAddr.MakerCDPManager
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, cdp_id: int, avatar: Address, wad: int):
        super().__init__(avatar=avatar)
        self.args.cdp = cdp_id
        self.args.wad = wad
