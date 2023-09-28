from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import ContractMethod, Address
import eth_abi
from defi_protocols.functions import get_contract

class ApproveGem(ContractMethod):
    """approve gem with proxy as spender"""
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]

    def __init__(self, gem: Address, proxy: Address, amount: int):
        super().__init__()
        self.target_address = gem
        self.args.spender = proxy
        self.args.amount = amount

class ApproveDAI(ContractMethod):
    """approve DAI with proxy as spender"""
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]

    def __init__(self, proxy: Address, amount: int):
        super().__init__()
        self.target_address = ETHAddr.DAI
        self.args.spender = proxy
        self.args.amount = amount

class Build(ContractMethod):
    """build DSProxy"""
    name = "build"
    target_address = ETHAddr.MakerProxyRegistry
    in_signature = []

    def __init__(self):
        super().__init__()

class ProxyExecute(ContractMethod):
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

class ProxyAction(ProxyExecute):
    selector = None
    action_abi = None

    def __init__(self, proxy: Address, parameters:list, value:int = 0):
        super().__init__(proxy, self.selector, self.action_abi, parameters, value=value)

class ProxyActionOpen(ProxyAction):
    selector = "0x6aa3ee11" # open(address,address,bytes32)
    action_abi = ["address", "bytes32", "address"]

    def __init__(self, proxy: Address, ilk: str):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, ilk , proxy])

class ProxyActionLockGem(ProxyAction):
    selector = "0x3e29e565" # lockGem(address,address,uint256,uint256,bool)
    action_abi = ["address", "address", "uint256", "uint256", "bool"]

    def __init__(self, proxy: Address, gem_join: Address, cdp_id: int, wad: int, transfer_from: bool = True):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, gem_join, cdp_id, wad, transfer_from])

class ProxyActionLockETH(ProxyAction):
    selector = "0xe205c108" # lockETH(address,address,uint256)
    action_abi = ["address", "address", "uint256"]

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, value: int):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, eth_join, cdp_id], value=value)

class ProxyActionFreeGem(ProxyAction):
    selector = "0x6ab6a491" # freeGem(address,address,uint256,uint256)
    action_abi = ["address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, gem_join: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, gem_join, cdp_id, wad])

class ProxyActionFreeETH(ProxyAction):
    selector = "0x7b5a3b43" # freeETH(address,address,uint256,uint256)
    action_abi = ["address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, eth_join, cdp_id, wad])

class ProxyActionDraw(ProxyAction):
    selector = "0x9f6f3d5b" # draw(address,address,address,uint256,uint256)
    action_abi = ["address", "address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, ETHAddr.MakerJug, ETHAddr.MakerDaiJoin, cdp_id, wad])

class ProxyActionWipe(ProxyAction):
    selector = "0x4b666199" # wipe(address,address,uint256,uint256)
    action_abi = ["address", "address", "uint256", "uint256"]

    def __init__(self, proxy: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [ETHAddr.MakerCDPManager, ETHAddr.MakerDaiJoin, cdp_id, wad])



# gem_join = get_contract('0x10CD5fbe1b404B7E19Ef964B63939907bdaf42E2', 'ethereum')
# # ilk = bytes.fromhex(gem_join.functions.ilk().call().hex())
# ilk = gem_join.functions.ilk().call()
# open = ProxyActionOpen('0xD758500ddEc05172aaA035911387C8E0e789CF6a',  ilk)

# print(open.data)

# eth_join = get_contract('0x2F0b23f53734252Bda2277357e97e1517d6B042A', 'ethereum')
# ilk = eth_join.functions.ilk().call()
# lock_eth = ProxyActionLockETH('0xD758500ddEc05172aaA035911387C8E0e789CF6a',  eth_join.address, 31010, 1000000000000000000)

# print(lock_eth.data)

# build = Build()
# print(build.data)