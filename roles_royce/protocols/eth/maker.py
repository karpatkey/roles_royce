from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import ContractMethod, Address, AvatarAddress
import eth_abi
from roles_royce.toolshed.protocol_utils.maker.addresses_and_abis import AddressesAndAbis
from roles_royce.constants import Chain


#-----------------------------------------------------#
"""Approvals"""
#-----------------------------------------------------#
class ApproveGem(ContractMethod):
    """approve gem to a given spender"""
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
    """approve DAI to a given spender"""
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
"""Proxy"""
#-----------------------------------------------------#
class Build(ContractMethod):
    """deploys a new proxy instance for the user (msg.sender)"""
    name = "build"
    target_address = AddressesAndAbis[Chain.Ethereum].ProxyRegistry.address
    in_signature = []

    def __init__(self):
        super().__init__()

class ProxyExecute(ContractMethod):
    """The DSProxy makes calls using the metafunction 
    execute(address,bytes) which inside executes a delegatecall 
    to the target address with the encoded function call (data)"""
    name = "execute"
    in_signature = [("target", "address"), ("data", "bytes")]

    def __init__(self, proxy: Address, target: Address, selector: str, action_abi: list, parameters: list, value:int = 0):
        super().__init__(value=value)
        self.target_address = proxy
        self.args.target = target
        self.args.data = self.get_call_data(selector, action_abi, parameters)

    def get_call_data(self, selector: str, action_abi: list, parameters: list):
        """
        Returns the call data for the proxy action

        Args:
            selector (str): selector of the action
            action_abi (list): abi of the action
            parameters (list): parameters of the action

            e.g.:
            selector = "0xe205c108" # lockETH(address,address,uint256)
            action_abi = ["address", "address", "uint256"]

        Returns:
            str: call data
        """
        abi_encoded = eth_abi.encode(action_abi, parameters)
        return selector + abi_encoded.hex()

class _ProxyAction(ProxyExecute):
    """Proxy action abstract class"""
    selector = None
    action_abi = None

    def __init__(self, proxy: Address, target: Address, parameters:list, value:int = 0):
        super().__init__(proxy, target, self.selector, self.action_abi, parameters, value=value)

#-----------------------------------------------------#
"""CDP Module - Proxy Actions"""
#-----------------------------------------------------#
class ProxyActionOpen(_ProxyAction):
    """creates an UrnHandler (cdp) for the address usr (for a specific ilk) 
    and allows the user to manage it via the internal registry of the manager"""
    selector = "0x6aa3ee11" # open(address,address,bytes32)
    action_abi = ["address", "bytes32", "address"]

    def __init__(self, proxy: Address, ilk: str):
        super().__init__(proxy, AddressesAndAbis[Chain.Ethereum].ProxyActions.address, [AddressesAndAbis[Chain.Ethereum].CdpManager.address, ilk , proxy])

class ProxyActionLockGem(_ProxyAction):
    """deposits wad amount of collateral in GemJoin adapter and executes frob 
    to cdp increasing the locked value. Gets funds from msg.sender 
    if transferFrom == true"""
    selector = "0x3e29e565" # lockGem(address,address,uint256,uint256,bool)
    action_abi = ["address", "address", "uint256", "uint256", "bool"]

    def __init__(self, proxy: Address, gem_join: Address, cdp_id: int, wad: int, transfer_from: bool = True):
        super().__init__(proxy, AddressesAndAbis[Chain.Ethereum].ProxyActions.address, [AddressesAndAbis[Chain.Ethereum].CdpManager.address, gem_join, cdp_id, wad, transfer_from])

class ProxyActionLockETH(_ProxyAction):
    """deposits msg.value amount of ETH in EthJoin adapter and executes frob 
    to cdp increasing the locked value"""
    selector = "0xe205c108" # lockETH(address,address,uint256)
    action_abi = ["address", "address", "uint256"]

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, value: int):
        super().__init__(proxy, AddressesAndAbis[Chain.Ethereum].ProxyActions.address, [AddressesAndAbis[Chain.Ethereum].CdpManager.address, eth_join, cdp_id], value=value)

class ProxyActionFreeGem(_ProxyAction):
    """executes frob to cdp decreasing locked collateral and withdraws wad 
    amount of collateral from GemJoin adapter"""
    selector = "0x6ab6a491" # freeGem(address,address,uint256,uint256)
    action_abi = ["address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, gem_join: Address, cdp_id: int, wad: int):
        super().__init__(proxy, AddressesAndAbis[Chain.Ethereum].ProxyActions.address, [AddressesAndAbis[Chain.Ethereum].CdpManager.address, gem_join, cdp_id, wad])

class ProxyActionFreeETH(_ProxyAction):
    """executes frob to cdp decreasing locked collateral and withdraws wad 
    amount of ETH from EthJoin adapte"""
    selector = "0x7b5a3b43" # freeETH(address,address,uint256,uint256)
    action_abi = ["address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, wad: int):
        super().__init__(proxy, AddressesAndAbis[Chain.Ethereum].ProxyActions.address, [AddressesAndAbis[Chain.Ethereum].CdpManager.address, eth_join, cdp_id, wad])

class ProxyActionDraw(_ProxyAction):
    """updates collateral fee rate, executes frob to cdp increasing debt 
    and exits wad amount of DAI token (minting it) from DaiJoin adapter"""
    selector = "0x9f6f3d5b" # draw(address,address,address,uint256,uint256)
    action_abi = ["address", "address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, cdp_id: int, wad: int):
        super().__init__(proxy, AddressesAndAbis[Chain.Ethereum].ProxyActions.address, [AddressesAndAbis[Chain.Ethereum].CdpManager.address, AddressesAndAbis[Chain.Ethereum].Jug.address, AddressesAndAbis[Chain.Ethereum].DaiJoin.address, cdp_id, wad])

class ProxyActionWipe(_ProxyAction):
    """joins wad amount of DAI token to DaiJoin adapter (burning it) and 
    executes frob to cdp for decreasing debt"""
    selector = "0x4b666199" # wipe(address,address,uint256,uint256)
    action_abi = ["address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, cdp_id: int, wad: int):
        super().__init__(proxy, AddressesAndAbis[Chain.Ethereum].ProxyActions.address, [AddressesAndAbis[Chain.Ethereum].CdpManager.address, AddressesAndAbis[Chain.Ethereum].DaiJoin.address, cdp_id, wad])

#-----------------------------------------------------#
"""CDP Module - CDPManager (no Proxy)"""
#-----------------------------------------------------#
class Open(ContractMethod):
    """opens a new Vault for usr to be used for an ilk collateral type"""
    name = "open"
    in_signature = [("ilk", "bytes32"), ("usr", "address")]
    target_address = AddressesAndAbis[Chain.Ethereum].CdpManager.address
    fixed_arguments = {"usr": AvatarAddress}

    def __init__(self, ilk: str, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.ilk = ilk

class Join(ContractMethod):
    """provides a mechanism for users to add the given token type to the Vat"""
    name = "join"
    in_signature = [("usr", "address"), ("wad", "uint256")]

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
    in_signature = [("cdp", "uint256"), ("dink", "int256"), ("dart", "int256")]
    target_address = AddressesAndAbis[Chain.Ethereum].CdpManager.address

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
    target_address = AddressesAndAbis[Chain.Ethereum].Jug.address

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
    target_address = AddressesAndAbis[Chain.Ethereum].CdpManager.address
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, cdp_id: int, avatar: Address, rad: int):
        super().__init__(avatar=avatar)
        self.args.cdp = cdp_id
        self.args.rad = rad

class Hope(ContractMethod):
    """enable wish for a pair of addresses, where wish checks whether an address
    is allowed to modify another address's Gem or DAI balance"""
    name = "hope"
    in_signature = [("usr", "address")]
    target_address = AddressesAndAbis[Chain.Ethereum].Vat.address
    fixed_arguments = {"usr": AddressesAndAbis[Chain.Ethereum].DaiJoin.address}

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
    target_address = AddressesAndAbis[Chain.Ethereum].CdpManager.address
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, cdp_id: int, avatar: Address, wad: int):
        super().__init__(avatar=avatar)
        self.args.cdp = cdp_id
        self.args.wad = wad

#-----------------------------------------------------#
"""DSR Module - Proxy Actions DSR"""
#-----------------------------------------------------#
class ProxyActionJoinDrs(_ProxyAction):
    """joins wad amount of DAI token to DaiJoin adapter (burning it) 
    and moves the balance to Pot for DSR"""
    selector = "0x9f6c3dbd" # join(address,address,uint256)
    action_abi = ["address", "address", "uint256"]

    def __init__(self, proxy: Address, wad: str):
        super().__init__(proxy, AddressesAndAbis[Chain.Ethereum].ProxyActionsDsr.address, [AddressesAndAbis[Chain.Ethereum].DaiJoin.address, AddressesAndAbis[Chain.Ethereum].Pot.address, wad])

class ProxyActionExitDsr(_ProxyAction):
    """retrieves wad amount of DAI from Pot and exits DAI token from 
    DaiJoin adapter (minting it)"""
    selector = "0x71006c09" # exit(address,address,uint256)
    action_abi = ["address", "address", "uint256"]

    def __init__(self, proxy: Address, wad: str):
        super().__init__(proxy, AddressesAndAbis[Chain.Ethereum].ProxyActionsDsr.address, [AddressesAndAbis[Chain.Ethereum].DaiJoin.address, AddressesAndAbis[Chain.Ethereum].Pot.address, wad])

class ProxyActionExitAllDsr(_ProxyAction):
    """performs the same actions as exit but for all of the available amount"""
    selector = "0xc77843b3" # exitAll(address,address)
    action_abi = ["address", "address"]

    def __init__(self, proxy: Address):
        super().__init__(proxy, AddressesAndAbis[Chain.Ethereum].ProxyActionsDsr.address, [AddressesAndAbis[Chain.Ethereum].DaiJoin.address, AddressesAndAbis[Chain.Ethereum].Pot.address])

#-----------------------------------------------------#
"""DSR Module - DSRManager (no Proxy)"""
#-----------------------------------------------------#
class JoinDsr(ContractMethod):
    """joins wad amount of DAI token to DaiJoin adapter (burning it) 
    and moves the balance to Pot for DSR"""
    name = "join"
    in_signature = [("dst", "address"), ("wad", "uint256")]
    target_address = AddressesAndAbis[Chain.Ethereum].DsrManager.address
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, avatar: Address, wad: int):
        super().__init__(avatar=avatar)
        self.args.wad = wad

class ExitDsr(ContractMethod):
    """retrieves wad amount of DAI from Pot and exits DAI token from
    DaiJoin adapter (minting it)"""
    name = "exit"
    in_signature = [("dst", "address"), ("wad", "uint256")]
    target_address = AddressesAndAbis[Chain.Ethereum].DsrManager.address
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, avatar: Address, wad: int):
        super().__init__(avatar=avatar)
        self.args.wad = wad

class ExitAllDsr(ContractMethod):
    """performs the same actions as exit but for all of the available amount"""
    name = "exitAll"
    in_signature = [("dst", "address")]
    target_address = AddressesAndAbis[Chain.Ethereum].DsrManager.address
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, avatar: Address):
        super().__init__(avatar=avatar)
