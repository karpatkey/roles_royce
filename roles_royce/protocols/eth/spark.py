from enum import IntEnum

from defabipedia.spark import ContractSpecs
from defabipedia.types import Blockchain

from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Address, AvatarAddress, BaseApprove, BaseApproveForToken, ContractMethod


class RateModel(IntEnum):
    STABLE = 1  # stable is not available at the moment
    VARIABLE = 2


class ApproveDAIforSDAI(BaseApprove):
    """approve DAI with sDAI as spender"""

    fixed_arguments = {"spender": ETHAddr.sDAI}
    token = ETHAddr.DAI


class ApproveToken(BaseApproveForToken):
    """approve Token with SparkLendingPoolV3 as spender"""

    fixed_arguments = {"spender": ETHAddr.SparkLendingPoolV3}


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


class RedeemSDAIforDAI(ContractMethod):
    """Sender redeems sDAI and withdraws DAI"""

    name = "redeem"
    in_signature = [("amount", "uint256"), ("receiver", "address"), ("owner", "address")]
    fixed_arguments = {"receiver": AvatarAddress, "owner": AvatarAddress}

    def __init__(self, blockchain: Blockchain, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].sDAI.address
        self.args.amount = amount


class SetUserUseReserveAsCollateral(ContractMethod):
    name = "setUserUseReserveAsCollateral"
    in_signature = [("asset", "address"), ("use_as_collateral", "bool")]

    def __init__(self, blockchain: Blockchain, asset: Address, use: bool):
        super().__init__()
        self.target_address = ContractSpecs[blockchain].LendingPoolV3.address
        self.args.asset = asset
        self.args.use_as_collateral = use


class Borrow(ContractMethod):
    """Sender receives Token and receives debtToken (stable or variable debt) token"""

    name = "borrow"
    in_signature = [
        ("asset", "address"),
        ("amount", "uint256"),
        ("rate_model", "uint256"),
        ("referral_code", "uint16"),
        ("on_behalf_of", "address"),
    ]
    fixed_arguments = {"on_behalf_of": AvatarAddress, "referral_code": 0}

    def __init__(self, blockchain: Blockchain, token: Address, amount: int, rate_model: RateModel, avatar: Address):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].LendingPoolV3.address
        self.args.asset = token
        self.args.amount = amount
        self.args.rate_model = rate_model


class Repay(ContractMethod):
    """Repay borrowed Token"""

    name = "repay"
    in_signature = [("asset", "address"), ("amount", "uint256"), ("rate_model", "uint256"), ("on_behalf_of", "address")]
    fixed_arguments = {"on_behalf_of": AvatarAddress}

    def __init__(self, blockchain: Blockchain, token: Address, amount: int, rate_model: RateModel, avatar: Address):
        super().__init__(avatar=avatar)
        self.target_address = ContractSpecs[blockchain].LendingPoolV3.address
        self.args.asset = token
        self.args.amount = amount
        self.args.rate_model = rate_model
