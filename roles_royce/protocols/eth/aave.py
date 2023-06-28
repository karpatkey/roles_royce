from enum import IntEnum

from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Method, InvalidArgument, AvatarSafeAddress, Address


class Approve(Method):
    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]
    token = None

    def __init__(self, amount: int):
        super().__init__()
        self.args.amount = amount

    @property
    def target_address(self):
        return self.token


class ApproveForAaveLendingPoolV2(Approve):
    """approve Token with AaveLendingPoolV2 as spender"""
    fixed_arguments = {"spender": ETHAddr.AaveLendingPoolV2}

    def __init__(self, token: Address, amount: int):
        super().__init__(amount)
        self.token = token


class ApproveForStkAAVE(Approve):
    """Approve AAVE with stkAAVE as spender"""
    fixed_arguments = {"spender": ETHAddr.stkAAVE}
    token = ETHAddr.AAVE


class ApproveForStkABPT(Approve):
    """Approve ABPT with stkABPT as spender"""
    fixed_arguments = {"spender": ETHAddr.stkABPT}
    token = ETHAddr.ABPT


class ApproveForParaSwap(Approve):
    """Approve Token with ParaSwapRepayAdapter as spender"""
    fixed_arguments = {"spender": ETHAddr.ParaSwapRepayAdapter}


class DepositToken(Method):
    """Sender deposits Token and receives aToken in exchange"""
    name = "deposit"
    in_signature = [("asset", "address"), ("amount", "uint256"), ("on_behalf_of", "address"), ("referral_code", "uint16")]
    fixed_arguments = {"on_behalf_of": AvatarSafeAddress, "referral_code": 0}
    target_address = ETHAddr.AaveLendingPoolV2

    def __init__(self, asset: Address, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount


class DepositETH(Method):
    """Sender deposits ETH and receives aETH in exchange"""
    name = "depositETH"
    in_signature = [("address", "address"), ("on_behalf_of", "address"), ("referral_code", "uint16")]
    fixed_arguments = {"address": ETHAddr.AaveLendingPoolV2, "on_behalf_of": AvatarSafeAddress, "referral_code": 0}
    target_address = ETHAddr.WrappedTokenGatewayV2

    def __init__(self, eth_amount: int, avatar: Address):
        super().__init__(value=eth_amount, avatar=avatar)


class WithdrawToken(Method):
    """Sender redeems aToken and withdraws Token"""
    name = "withdraw"
    in_signature = [("asset", "address"), ("amount", "uint256"), ("to", "address")]
    fixed_arguments = {"to": AvatarSafeAddress}
    target_address = ETHAddr.AaveLendingPoolV2

    def __init__(self, asset: Address, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount


class WithdrawETH(Method):
    """Sender redeems aETH and withdraws ETH"""
    name = "withdrawETH"
    in_signature = [("address", "address"), ("amount", "uint256"), ("to", "address")]
    fixed_arguments = {"address": ETHAddr.AaveLendingPoolV2, "to": AvatarSafeAddress}
    target_address = ETHAddr.WrappedTokenGatewayV2

    def __init__(self, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.amount = amount


class Collateralize(Method):
    """Set/unset asset as collateral"""
    name = "setUserUseReserveAsCollateral"
    in_signature = [("asset", "address"), ("use_as_collateral", "bool")]
    fixed_arguments = {}
    target_address = ETHAddr.AaveLendingPoolV2

    def __init__(self, asset: Address, use_as_collateral: bool):
        super().__init__()
        self.args.asset = asset
        self.args.use_as_collateral = use_as_collateral


class InterestRateModel(IntEnum):
    STABLE = 1
    VARIABLE = 2


class Borrow(Method):
    """Borrow"""
    name = "borrow"
    in_signature = [("asset", "address"), ("amount", "uint256"), ("interest_rate_model", "uint256"),
                    ("referral_code", "uint16"), ("on_behalf_of", "address")]
    fixed_arguments = {"referral_code": 0, "on_behalf_of": AvatarSafeAddress}
    target_address = ETHAddr.AaveLendingPoolV2

    def __init__(self, asset: Address, amount: int, interest_rate_model: InterestRateModel, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount
        if interest_rate_model not in InterestRateModel:
            raise InvalidArgument(f"Invalid interestRateModel={interest_rate_model}")
        self.args.interest_rate_model = interest_rate_model


class BorrowETH(Method):
    """Borrow ETH"""
    name = "borrowETH"
    in_signature = [("address", "address"), ("amount", "uint256"), ("interest_rate_model", "uint256"), ("referral_code", "uint16")]
    fixed_arguments = {"address": ETHAddr.AaveLendingPoolV2, "referral_code": 0}
    target_address = ETHAddr.WrappedTokenGatewayV2

    def __init__(self, amount: int, interest_rate_model: InterestRateModel):
        super().__init__()
        self.args.amount = amount
        if interest_rate_model not in InterestRateModel:
            raise InvalidArgument(f"Invalid interestRateModel={interest_rate_model}")
        self.args.interest_rate_model = interest_rate_model


class StakeAAVE(Method):
    name = 'stake'
    in_signature = [("on_behalf_of", "address"), ("amount", "uint256")]
    fixed_arguments = {"on_behalf_of": AvatarSafeAddress}
    target_address = ETHAddr.stkAAVE

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount


class StakeABPT(StakeAAVE):
    target_address = ETHAddr.stkABPT


class UnstakeAAVE(Method):
    """Unstake AAVE. Can only be called during the 2 days unstaking window after the 10 days cooldown period"""
    name = 'redeem'
    in_signature = [('to', 'address'), ('amount', 'uint256')]
    fixed_arguments = {'to': AvatarSafeAddress}
    target_address = ETHAddr.stkAAVE

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount


class UnstakeABPT(UnstakeAAVE):
    """Unstake ABPT. Can only be called during the 2 days unstaking window after the 10 days cooldown period"""
    target_address = ETHAddr.stkABPT


class CooldownStkAAVE(Method):
    """Initiates a 10 days cooldown period, once this is over the 2 days unstaking window opens"""
    name = 'cooldown'
    in_signature = []
    fixed_arguments = {}
    target_address = ETHAddr.stkAAVE


class CooldownStkABPT(CooldownStkAAVE):
    target_address = ETHAddr.stkABPT


class ClaimAAVERewards(Method):
    name = 'claimRewards'
    in_signature = [('to', 'address'), ('amount', 'uint256')]
    fixed_arguments = {'to': AvatarSafeAddress}
    target_address = ETHAddr.stkAAVE

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount


class ClaimABPTRewards(ClaimAAVERewards):
    target_address = ETHAddr.stkABPT


class Repay(Method):
    """Repay"""
    name = 'repay'
    in_signature = [('asset', 'address'), ('amount', 'uint256'), ('interest_rate_model', 'uint256'), ('on_behalf_of', 'address')]
    fixed_arguments = {'on_behalf_of': AvatarSafeAddress}
    target_address = ETHAddr.AaveLendingPoolV2

    def __init__(self, token: Address, amount: int, interest_rate_model: InterestRateModel):
        super().__init__()
        self.args.token = token
        self.args.amount = amount
        self.args.interest_rate_model = interest_rate_model


class RepayETH(Method):
    name = 'repayETH'
    in_signature = [('address', 'address'), ('amount', 'uint256'), ('interest_rate_model', 'uint256'), ('on_behalf_of', 'address')]
    fixed_arguments = {'address': ETHAddr.AaveLendingPoolV2, 'on_behalf_of': AvatarSafeAddress}
    target_address = ETHAddr.WrappedTokenGatewayV2

    def __init__(self, amount: int, interest_rate_model: InterestRateModel):
        super().__init__()
        self.args.amount = amount
        self.args.interest_rate_model = interest_rate_model
        raise NotImplementedError("Not yet implemented/validated")


class SwapAndRepay(Method):
    # TODO: review
    name = 'swapAndRepay'
    in_signature = [("collateral_asset", "address"),
                    ("debt_asset", "address"),
                    ("collateral_amount", "uint256"),
                    ("debt_repay_amount", "uint256"),
                    ("debt_rate_mode", "uint256"),
                    ("buy_all_balance_offset", "uint256"),
                    ("paraswap_data", "bytes"),
                    ("permit_sign_amount", "uint256"),
                    ("permit_sign_deadline", "uint256"),
                    ("permit_sign_v", "uint8"),
                    ("permit_sign_r", "bytes32"),
                    ("permit_sign_s", "bytes32")]
    target_address = ETHAddr.ParaSwapRepayAdapter
    fixed_arguments = {}

    def __init__(self, collateral_asset, debt_asset, collateral_amount, debt_repay_amount, debt_rate_mode,
                 buy_all_balance_offset, paraswap_data, permit_sign_amount, permit_sign_deadline,
                 permit_sign_v, permit_sign_r, permit_sign_s):
        super().__init__()
        self.collateral_asset, self.collateral_amount = collateral_asset, collateral_amount
        self.debt_asset, self.debt_repay_amount = debt_asset, debt_repay_amount
        self.debt_rate_mode = debt_rate_mode
        self.buy_all_balance_offset = buy_all_balance_offset
        self.paraswap_data = paraswap_data
        self.permit_sign_amount = permit_sign_amount
        self.permit_sign_deadline = permit_sign_deadline
        self.permit_sign_v, self.permit_sign_r, self.permit_sign_s = permit_sign_v, permit_sign_r, permit_sign_s
        raise NotImplementedError("Not yet implemented/validated")