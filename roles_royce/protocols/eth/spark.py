from enum import IntEnum

from defabipedia._1inch import Chain
from defabipedia.spark import ContractSpecs
from defabipedia.types import Blockchain

from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import (
    Address,
    AvatarAddress,
    BaseApprove,
    BaseApproveForToken,
    ContractMethod,
    InvalidArgument,
)

SupportedChains = list(ContractSpecs.keys())


class RateMode(IntEnum):
    STABLE = 1  # stable is not available at the moment
    VARIABLE = 2

    @staticmethod
    def check(value):
        if value not in RateMode:
            raise InvalidArgument(f"Invalid rate_mode={value}")


class DelegationTarget:
    targets = [
        ContractSpecs[Chain.ETHEREUM].variableDebtNATIVE.address,
        ContractSpecs[Chain.GNOSIS].variableDebtNATIVE.address,
    ]

    @staticmethod
    def check_delegation_target(target: Address):
        if target not in DelegationTarget.targets:
            raise InvalidArgument(f"Invalid delegationTarget={target}")


class ApproveDAIforSDAI(BaseApprove):
    """approve DAI with sDAI as spender"""

    fixed_arguments = {"spender": ETHAddr.sDAI}
    token = ETHAddr.DAI


class ApproveToken(BaseApproveForToken):
    """approve Token with LendingPoolV3 as spender"""

    def __init__(self, blockchain: Blockchain, token: Address, amount: int):
        self.fixed_arguments = {"spender": ContractSpecs[blockchain].LendingPoolV3.address}
        super().__init__(token, amount)


class ApproveDelegation(ContractMethod):
    """sets the amount of allowance for WrappedTokenGatewayV3 to borrow
    variableDebtNATIVE"""

    name = "approveDelegation"
    in_signature = [("delegatee", "address"), ("amount", "uint256")]

    def __init__(self, blockchain: Blockchain, target: Address, amount: int):
        super().__init__()
        self.fixed_arguments = {"delegatee": ContractSpecs[blockchain].WrappedTokenGatewayV3.address}
        self.args.asd = 1
        DelegationTarget.check_delegation_target(target)
        self.target_address = target
        self.args.amount = amount


class DepositToken(ContractMethod):
    """Sender deposits Token and receives spToken in exchange"""

    name = "deposit"
    in_signature = [
        ("asset", "address"),
        ("amount", "uint256"),
        ("on_behalf_of", "address"),
        ("referral_code", "uint16"),
    ]
    fixed_arguments = {"on_behalf_of": AvatarAddress, "referral_code": 0}

    def __init__(self, blockchain: Blockchain, token: Address, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].LendingPoolV3.address
        self.args.asset = token
        self.args.amount = amount


class DepositDAIforSDAI(ContractMethod):
    """Sender deposits DAI and receives sDAI in exchange (the DAI is deposited in Maker - DSR)"""

    name = "deposit"
    in_signature = [("amount", "uint256"), ("receiver", "address")]
    fixed_arguments = {"receiver": AvatarAddress}

    def __init__(self, blockchain: Blockchain, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].sDAI.address
        self.args.amount = amount


class DepositNative(ContractMethod):
    """Sender deposits Native Token"""

    name = "depositETH"
    in_signature = [("address", "address"), ("on_behalf_of", "address"), ("referral_code", "uint16")]

    def __init__(self, blockchain: Blockchain, eth_amount: int, avatar: Address):
        self.fixed_arguments = {
            "address": ContractSpecs[blockchain].LendingPoolV3.address,
            "on_behalf_of": AvatarAddress,
            "referral_code": 0,
        }
        self.target_address = ContractSpecs[blockchain].WrappedTokenGatewayV3.address
        super().__init__(value=eth_amount, avatar=avatar)


class WithdrawToken(ContractMethod):
    """Sender redeems spToken and withdraws Token"""

    name = "withdraw"
    in_signature = [("asset", "address"), ("amount", "uint256"), ("receiver", "address")]
    fixed_arguments = {"receiver": AvatarAddress}

    def __init__(self, blockchain: Blockchain, token: Address, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].LendingPoolV3.address
        self.args.asset = token
        self.args.amount = amount


class WithdrawNative(ContractMethod):
    """Sender redeems spToken and withdraws Native one"""

    name = "withdrawETH"
    in_signature = [("address", "address"), ("amount", "uint256"), ("to", "address")]

    def __init__(self, blockchain: Blockchain, amount: int, avatar: Address):
        self.fixed_arguments = {"address": ContractSpecs[blockchain].LendingPoolV3.address, "to": AvatarAddress}
        self.target_address = ContractSpecs[blockchain].WrappedTokenGatewayV3.address
        super().__init__(avatar=avatar)
        self.args.amount = amount


class RedeemSDAIforDAI(ContractMethod):
    """Sender redeems sDAI and withdraws DAI"""

    name = "redeem"
    in_signature = [("amount", "uint256"), ("receiver", "address"), ("owner", "address")]
    fixed_arguments = {"receiver": AvatarAddress, "owner": AvatarAddress}

    def __init__(self, blockchain: Blockchain, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].sDAI.address
        self.args.amount = amount


class Collateralize(ContractMethod):
    """Set/unset asset as collateral"""

    name = "setUserUseReserveAsCollateral"
    in_signature = [("asset", "address"), ("use_as_collateral", "bool")]
    fixed_arguments = {}

    def __init__(self, blockchain: Blockchain, asset: Address, use_as_collateral: bool):
        super().__init__()
        self.target_address = ContractSpecs[blockchain].LendingPoolV3.address
        self.args.asset = asset
        self.args.use_as_collateral = use_as_collateral


class Borrow(ContractMethod):
    """Sender receives Token and receives debtToken (stable or variable debt) token"""

    name = "borrow"
    in_signature = [
        ("asset", "address"),
        ("amount", "uint256"),
        ("rate_mode", "uint256"),
        ("referral_code", "uint16"),
        ("on_behalf_of", "address"),
    ]
    fixed_arguments = {"on_behalf_of": AvatarAddress, "referral_code": 0}

    def __init__(self, blockchain: Blockchain, token: Address, amount: int, rate_mode: RateMode, avatar: Address):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].LendingPoolV3.address
        self.args.asset = token
        self.args.amount = amount
        self.args.rate_mode = rate_mode


class Repay(ContractMethod):
    """Repay borrowed Token"""

    name = "repay"
    in_signature = [("asset", "address"), ("amount", "uint256"), ("rate_mode", "uint256"), ("on_behalf_of", "address")]
    fixed_arguments = {"on_behalf_of": AvatarAddress}

    def __init__(self, blockchain: Blockchain, token: Address, amount: int, rate_mode: RateMode, avatar: Address):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].LendingPoolV3.address
        self.args.asset = token
        self.args.amount = amount
        self.args.rate_mode = rate_mode


class RepayNative(ContractMethod):
    """Repay borrowed ETH"""

    name = "repayETH"
    in_signature = [
        ("address", "address"),
        ("amount", "uint256"),
        ("rate_mode", "uint256"),
        ("on_behalf_of", "address"),
    ]

    def __init__(self, blockchain: Blockchain, eth_amount: int, rate_mode: RateMode, avatar: Address):
        super().__init__(value=eth_amount, avatar=avatar)
        self.fixed_arguments = {
            "address": ContractSpecs[blockchain].LendingPoolV3.address,
            "on_behalf_of": AvatarAddress,
        }
        self.target_address = ContractSpecs[blockchain].WrappedTokenGatewayV3.address
        self.args.amount = eth_amount
        RateMode.check(rate_mode)
        self.args.rate_mode = rate_mode
