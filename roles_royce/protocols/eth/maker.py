from roles_royce.constants import ETHAddr, StrEnum
from roles_royce.protocols.base import Address, AvatarAddress, ContractMethod
from roles_royce.utils import to_data_input


class MakerAddr(StrEnum):
    CdpManager = "0x5ef30b9986345249bc32d8928B7ee64DE9435E39"
    DaiJoin = "0x9759A6Ac90977b93B58547b4A71c78317f391A28"
    DsrManager = "0x373238337Bfe1146fb49989fc222523f83081dDb"
    Jug = "0x19c0976f590D67707E62397C87829d896Dc0f1F1"
    Pot = "0x197E90f9FAD81970bA7976f33CbD77088E5D7cf7"
    ProxyActions = "0x82ecD135Dce65Fbc6DbdD0e4237E0AF93FFD5038"
    ProxyActionsDsr = "0x07ee93aEEa0a36FfF2A9B95dd22Bd6049EE54f26"
    ProxyRegistry = "0x4678f0a6958e4D2Bc4F1BAF7Bc52E8F3564f3fE4"
    Vat = "0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B"


# -----------------------------------------------------#
# Approvals


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


# -----------------------------------------------------#
# Proxy


class Build(ContractMethod):
    """deploys a new proxy instance for the user (msg.sender)"""

    name = "build"
    target_address = MakerAddr.ProxyRegistry
    in_signature = []

    def __init__(self):
        super().__init__()


class ProxyExecute(ContractMethod):
    """The DSProxy makes calls using the metafunction
    execute(address,bytes) which inside executes a delegatecall
    to the target address with the encoded function call (data)
    """

    name = "execute"
    in_signature = [("target", "address"), ("data", "bytes")]

    def __init__(self, proxy: Address, target: Address, short_signature: str, parameters: list, value: int = 0):
        super().__init__(value=value)
        self.target_address = proxy
        self.args.target = target
        start_of_sign = short_signature.index("(")
        self.args.data = to_data_input(short_signature[:start_of_sign], short_signature[start_of_sign:], parameters)


class _ProxyAction(ProxyExecute):
    """Proxy action abstract class"""

    short_signature = None
    target = None

    def __init__(self, proxy: Address, parameters: list, value: int = 0):
        super().__init__(proxy, self.target, self.short_signature, parameters, value=value)


# -----------------------------------------------------#
# CDP Module - Proxy Actions


class _ProxyActionCDP(_ProxyAction):
    target = MakerAddr.ProxyActions


class ProxyActionOpen(_ProxyActionCDP):
    """creates an UrnHandler (cdp) for the address usr (for a specific ilk)
    and allows the user to manage it via the internal registry of the manager
    """

    short_signature = "open(address,bytes32,address)"

    def __init__(self, proxy: Address, ilk: str):
        super().__init__(proxy, [MakerAddr.CdpManager, ilk, proxy])


class ProxyActionLockGem(_ProxyActionCDP):
    """deposits wad amount of collateral in GemJoin adapter and executes frob
    to cdp increasing the locked value. Gets funds from msg.sender
    if transferFrom == true
    """

    short_signature = "lockGem(address,address,uint256,uint256,bool)"

    def __init__(self, proxy: Address, gem_join: Address, cdp_id: int, wad: int, transfer_from: bool = True):
        super().__init__(proxy, [MakerAddr.CdpManager, gem_join, cdp_id, wad, transfer_from])


class ProxyActionLockETH(_ProxyActionCDP):
    """deposits msg.value amount of ETH in EthJoin adapter and executes frob
    to cdp increasing the locked value
    """

    short_signature = "lockETH(address,address,uint256)"

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, value: int):
        super().__init__(proxy, [MakerAddr.CdpManager, eth_join, cdp_id], value=value)


class ProxyActionFreeGem(_ProxyActionCDP):
    """executes frob to cdp decreasing locked collateral and withdraws wad
    amount of collateral from GemJoin adapter
    """

    short_signature = "freeGem(address,address,uint256,uint256)"

    def __init__(self, proxy: Address, gem_join: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [MakerAddr.CdpManager, gem_join, cdp_id, wad])


class ProxyActionFreeETH(_ProxyActionCDP):
    """executes frob to cdp decreasing locked collateral and withdraws wad
    amount of ETH from EthJoin adapte
    """

    short_signature = "freeETH(address,address,uint256,uint256)"

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [MakerAddr.CdpManager, eth_join, cdp_id, wad])


class ProxyActionDraw(_ProxyActionCDP):
    """updates collateral fee rate, executes frob to cdp increasing debt
    and exits wad amount of DAI token (minting it) from DaiJoin adapter
    """

    short_signature = "draw(address,address,address,uint256,uint256)"

    def __init__(self, proxy: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [MakerAddr.CdpManager, MakerAddr.Jug, MakerAddr.DaiJoin, cdp_id, wad])


class ProxyActionWipe(_ProxyActionCDP):
    """joins wad amount of DAI token to DaiJoin adapter (burning it) and
    executes frob to cdp for decreasing debt
    """

    short_signature = "wipe(address,address,uint256,uint256)"

    def __init__(self, proxy: Address, cdp_id: int, wad: int):
        super().__init__(proxy, [MakerAddr.CdpManager, MakerAddr.DaiJoin, cdp_id, wad])


class ProxyActionLockGemAndDraw(_ProxyActionCDP):
    """combines lockGem and draw"""

    short_signature = "lockGemAndDraw(address,address,address,address,uint256,uint256,uint256,bool)"

    def __init__(
        self, proxy: Address, gem_join: Address, cdp_id: int, wad_c: int, wad_d: int, transfer_from: bool = True
    ):
        super().__init__(
            proxy,
            [MakerAddr.CdpManager, MakerAddr.Jug, gem_join, MakerAddr.DaiJoin, cdp_id, wad_c, wad_d, transfer_from],
        )


class ProxyActionLockETHAndDraw(_ProxyActionCDP):
    """combines lockETH and draw"""

    short_signature = "lockETHAndDraw(address,address,address,address,uint256,uint256)"

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, wad_d: int, value: int):
        super().__init__(
            proxy, [MakerAddr.CdpManager, MakerAddr.Jug, eth_join, MakerAddr.DaiJoin, cdp_id, wad_d], value=value
        )


class ProxyActionOpenLockGemAndDraw(_ProxyActionCDP):
    """combines open, lockGem and draw"""

    short_signature = "openLockGemAndDraw(address,address,address,address,bytes32,uint256,uint256,bool)"

    def __init__(self, proxy: Address, gem_join: Address, ilk: str, wad_c: int, wad_d: int, transfer_from: bool = True):
        super().__init__(
            proxy, [MakerAddr.CdpManager, MakerAddr.Jug, gem_join, MakerAddr.DaiJoin, ilk, wad_c, wad_d, transfer_from]
        )


class ProxyActionOpenLockETHAndDraw(_ProxyActionCDP):
    """combines open, lockETH and draw"""

    short_signature = "openLockETHAndDraw(address,address,address,address,bytes32,uint256)"

    def __init__(self, proxy: Address, eth_join: Address, ilk: str, wad_d: int, value: int):
        super().__init__(
            proxy, [MakerAddr.CdpManager, MakerAddr.Jug, eth_join, MakerAddr.DaiJoin, ilk, wad_d], value=value
        )


class ProxyActionWipeAndFreeGem(_ProxyActionCDP):
    """combines wipe and freeGem"""

    short_signature = "wipeAndFreeGem(address,address,address,uint256,uint256,uint256)"

    def __init__(self, proxy: Address, gem_join: Address, cdp_id: int, wad_c: int, wad_d: int):
        super().__init__(proxy, [MakerAddr.CdpManager, gem_join, MakerAddr.DaiJoin, cdp_id, wad_c, wad_d])


class ProxyActionWipeAndFreeETH(_ProxyActionCDP):
    """combines wipe and freeETH"""

    short_signature = "wipeAndFreeETH(address,address,address,uint256,uint256,uint256)"

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, wad_c: int, wad_d: int):
        super().__init__(proxy, [MakerAddr.CdpManager, eth_join, MakerAddr.DaiJoin, cdp_id, wad_c, wad_d])


class ProxyActionWipeAllAndFreeGem(_ProxyActionCDP):
    """combines wipeAll and freeGem"""

    short_signature = "wipeAllAndFreeGem(address,address,address,uint256,uint256)"

    def __init__(self, proxy: Address, gem_join: Address, cdp_id: int, wad_c: int):
        super().__init__(proxy, [MakerAddr.CdpManager, gem_join, MakerAddr.DaiJoin, cdp_id, wad_c])


class ProxyActionWipeAllAndFreeETH(_ProxyActionCDP):
    """combines wipeAll and freeETH"""

    short_signature = "wipeAllAndFreeETH(address,address,address,uint256,uint256)"

    def __init__(self, proxy: Address, eth_join: Address, cdp_id: int, wad_c: int):
        super().__init__(proxy, [MakerAddr.CdpManager, eth_join, MakerAddr.DaiJoin, cdp_id, wad_c])


# -----------------------------------------------------#
# CDP Module - CDPManager (no Proxy)"""


class Open(ContractMethod):
    """opens a new Vault for usr to be used for an ilk collateral type"""

    name = "open"
    in_signature = [("ilk", "bytes32"), ("usr", "address")]
    target_address = MakerAddr.CdpManager
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
    in the cdp address
    """

    name = "frob"
    in_signature = [("cdp", "uint256"), ("dink", "int256"), ("dart", "int256")]
    target_address = MakerAddr.CdpManager

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
    equal to the current timestamp
    """

    name = "drip"
    in_signature = [("ilk", "bytes32")]
    target_address = MakerAddr.Jug

    def __init__(self, ilk: str):
        super().__init__()
        self.args.ilk = ilk


class Move(ContractMethod):
    """moves rad (precision 45) amount of DAI from the cdp (urn) to dst.
    However, you still won't see the balance on your wallet. In order to
    see the balance, you'll need to approve the DaiJoin adapter in Vat from
    the system with the Vat.hope() function. After, you call the DaiJoin.exit()
    to finally move the DAI to your wallet
    """

    name = "move"
    in_signature = [("cdp", "uint256"), ("dst", "address"), ("rad", "uint256")]
    target_address = MakerAddr.CdpManager
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, cdp_id: int, avatar: Address, rad: int):
        super().__init__(avatar=avatar)
        self.args.cdp = cdp_id
        self.args.rad = rad


class Hope(ContractMethod):
    """enable wish for a pair of addresses, where wish checks whether an address
    is allowed to modify another address's Gem or DAI balance
    """

    name = "hope"
    in_signature = [("usr", "address")]
    target_address = MakerAddr.Vat
    fixed_arguments = {"usr": MakerAddr.DaiJoin}

    def __init__(self):
        super().__init__()


class Exit(ContractMethod):
    """allows the user to remove their desired token from the Vat"""

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
    target_address = MakerAddr.CdpManager
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, cdp_id: int, avatar: Address, wad: int):
        super().__init__(avatar=avatar)
        self.args.cdp = cdp_id
        self.args.wad = wad


# -----------------------------------------------------#
#  DSR Module - Proxy Actions DSR


class _ProxyActionDSR(_ProxyAction):
    target = MakerAddr.ProxyActionsDsr


class ProxyActionJoinDsr(_ProxyActionDSR):
    """joins wad amount of DAI token to DaiJoin adapter (burning it)
    and moves the balance to Pot for DSR
    """

    short_signature = "join(address,address,uint256)"

    def __init__(self, proxy: Address, wad: int):
        super().__init__(proxy, [MakerAddr.DaiJoin, MakerAddr.Pot, wad])


class ProxyActionExitDsr(_ProxyActionDSR):
    """retrieves wad amount of DAI from Pot and exits DAI token from
    DaiJoin adapter (minting it)
    """

    short_signature = "exit(address,address,uint256)"

    def __init__(self, proxy: Address, wad: int):
        super().__init__(proxy, [MakerAddr.DaiJoin, MakerAddr.Pot, wad])


class ProxyActionExitAllDsr(_ProxyActionDSR):
    """performs the same actions as exit but for all of the available amount"""

    short_signature = "exitAll(address,address)"

    def __init__(self, proxy: Address):
        super().__init__(proxy, [MakerAddr.DaiJoin, MakerAddr.Pot])


# -----------------------------------------------------#
# DSR Module - DSRManager (no Proxy)


class JoinDsr(ContractMethod):
    """joins wad amount of DAI token to DaiJoin adapter (burning it)
    and moves the balance to Pot for DSR
    """

    name = "join"
    in_signature = [("dst", "address"), ("wad", "uint256")]
    target_address = MakerAddr.DsrManager
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, avatar: Address, wad: int):
        super().__init__(avatar=avatar)
        self.args.wad = wad


class ExitDsr(ContractMethod):
    """retrieves wad amount of DAI from Pot and exits DAI token from
    DaiJoin adapter (minting it)
    """

    name = "exit"
    in_signature = [("dst", "address"), ("wad", "uint256")]
    target_address = MakerAddr.DsrManager
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, avatar: Address, wad: int):
        super().__init__(avatar=avatar)
        self.args.wad = wad


class ExitAllDsr(ContractMethod):
    """performs the same actions as exit but for all of the available amount"""

    name = "exitAll"
    in_signature = [("dst", "address")]
    target_address = MakerAddr.DsrManager
    fixed_arguments = {"dst": AvatarAddress}

    def __init__(self, avatar: Address):
        super().__init__(avatar=avatar)
