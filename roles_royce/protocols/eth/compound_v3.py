import eth_abi

from roles_royce.constants import ETHAddr, StrEnum
from roles_royce.protocols.base import Address, AvatarAddress, BaseApproveForToken, ContractMethod


class Comet(StrEnum):
    cUSDCv3 = "0xc3d688B66703497DAA19211EEdff47f25384cdc3"
    cWETHv3 = "0xA17581A9E3356d9A858b789D68B4d866e593aE94"


def _to_hex_pad_64(value):
    return "0x" + value.hex().ljust(64, "0")


ACTION_SUPPLY_NATIVE_TOKEN = _to_hex_pad_64(b"ACTION_SUPPLY_NATIVE_TOKEN")
ACTION_WITHDRAW_NATIVE_TOKEN = _to_hex_pad_64(b"ACTION_WITHDRAW_NATIVE_TOKEN")


class Approve(BaseApproveForToken):
    def __init__(self, comet: Comet, token: Address, amount: int):
        super().__init__(token=token, amount=amount)
        self.args.spender = comet.value


class Allow(ContractMethod):
    """Allow

    The approval for the MainnetBulker is done once per wallet.
    """

    name = "allow"
    in_signature = [("manager", "address"), ("is_allowed", "bool")]
    fixed_arguments = {"manager": ETHAddr.COMPOUND_Bulker, "is_allowed": True}

    def __init__(self, comet: Comet):
        self.target_address = comet.value
        super().__init__()


class Supply(ContractMethod):
    """Supply token.

    If the supplied asset is the underlying token of the Comet then you get in exchange approximately
    the same amount of Comet token. Otherwise, the supplied amount of asset is transfered to the Comet as collateral.
    """

    name = "supply"
    in_signature = [("asset", "address"), ("amount", "uint256")]

    def __init__(self, comet: Comet, token: Address, amount: int):
        super().__init__()
        self.target_address = comet.value
        self.args.asset = token
        self.args.amount = amount


class _Invoke(ContractMethod):
    name = "invoke"
    in_signature = [("actions", "bytes32[]"), ("data", "bytes[]")]
    target_address = ETHAddr.COMPOUND_Bulker


class SupplyETH(_Invoke):
    """Supply ETH"""

    fixed_arguments = {"actions": [ACTION_SUPPLY_NATIVE_TOKEN]}

    def __init__(self, comet: Comet, avatar: Address, amount: int):
        super().__init__(value=amount)
        self.args.data = [eth_abi.encode(types=("address", "address", "uint256"), args=[comet.value, avatar, amount])]


class Withdraw(ContractMethod):
    """Withdraw asset.

    If the withdrawn asset is the underlying token of the Comet then you burn the amount of
    Comet token for the same amount of underlying token.  Otherwise, the withdrawn amount
    of asset is removed from the Comet as collateral
    """

    name = "withdraw"
    in_signature = [("asset", "address"), ("amount", "uint256")]

    def __init__(self, comet: Comet, token: Address, amount: int):
        super().__init__()
        self.target_address = comet.value
        self.args.asset = token
        self.args.amount = amount


class WithdrawETH(_Invoke):
    """Withdraw ETH"""

    fixed_arguments = {"actions": [ACTION_WITHDRAW_NATIVE_TOKEN]}

    def __init__(self, comet: Comet, avatar: Address, amount: int):
        super().__init__()
        self.args.data = [eth_abi.encode(types=("address", "address", "uint256"), args=[comet.value, avatar, amount])]


class Borrow(Withdraw):
    """Borrow. Same as Withdraw, but you can ONLY borrow the Comets’ underlying token"""


class Repay(Supply):
    """Repay. Same as Deposit, but you can ONLY repay the Comets’ underlying token"""


class Claim(ContractMethod):
    """Claim COMP rewards"""

    name = "claim"
    in_signature = [("comet", "address"), ("src", "address"), ("should_accrue", "bool")]
    fixed_arguments = {"src": AvatarAddress}
    target_address = ETHAddr.COMPOUND_CometRewards

    def __init__(self, comet: Comet, avatar: Address, should_accrue: bool):
        super().__init__(avatar=avatar)
        self.args.comet = comet.value
        self.args.should_accrue = should_accrue
