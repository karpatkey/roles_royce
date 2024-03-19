from enum import IntEnum

from defabipedia.aave_v3 import ContractSpecs
from defabipedia.types import Chain

from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import (
    Address,
    AvatarAddress,
    BaseApprove,
    BaseApproveForToken,
    ContractMethod,
    InvalidArgument,
)


class InterestRateMode(IntEnum):
    STABLE = 1  # stable is not available at the moment
    VARIABLE = 2

    @staticmethod
    def check(value):
        if value not in InterestRateMode:
            raise InvalidArgument(f"Invalid interestRateMode={value}")


class DelegationTarget:
    targets = [
        ContractSpecs[Chain.ETHEREUM].variableDebtWETH.address,
        ContractSpecs[Chain.ETHEREUM].stableDebtWETH.address,
    ]

    @staticmethod
    def check_delegation_target(target: Address):
        if target not in DelegationTarget.targets:
            raise InvalidArgument(f"Invalid delegationTarget={target}")


class DelegationType(IntEnum):
    VOTING = 0
    PROPOSITION = 1


class ApproveToken(BaseApproveForToken):
    """approve Token with AaveLendingPoolV3 as spender"""

    fixed_arguments = {"spender": ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address}


class ApproveAEthWETH(BaseApprove):
    """approve aEthWETH with WrappedTokenGatewayV3 as spender"""

    fixed_arguments = {"spender": ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address}
    token = ContractSpecs[Chain.ETHEREUM].aEthWETH.address


class ApproveForStkAAVE(BaseApprove):
    """Approve AAVE with stkAAVE as spender"""

    fixed_arguments = {"spender": ContractSpecs[Chain.ETHEREUM].stkAAVE.address}
    token = ContractSpecs[Chain.ETHEREUM].AAVE.address


class ApproveForStkABPT(BaseApprove):
    """Approve ABPT with stkABPT as spender"""

    fixed_arguments = {"spender": ContractSpecs[Chain.ETHEREUM].stkABPT.address}
    token = ContractSpecs[Chain.ETHEREUM].ABPT.address


class ApproveDelegation(ContractMethod):
    """sets the amount of allowance for WrappedTokenGatewayV3 to borrow
    variableDebtWETH or stableDebtWETH"""

    name = "approveDelegation"
    in_signature = (("delegatee", "address"), ("amount", "uint256"))
    fixed_arguments = {"delegatee": ContractSpecs[Chain.ETHEREUM].WrappedTokenGatewayV3.address}

    def __init__(self, target: DelegationTarget, amount: int):
        super().__init__()
        DelegationTarget.check_delegation_target(target)
        self.target_address = target
        self.args.amount = amount


class DepositToken(ContractMethod):
    """Sender deposits Token and receives aToken in exchange"""

    name = "supply"
    in_signature = (
        ("asset", "address"),
        ("amount", "uint256"),
        ("on_behalf_of", "address"),
        ("referral_code", "uint16"),
    )
    fixed_arguments = {"on_behalf_of": AvatarAddress, "referral_code": 0}
    target_address = ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address

    def __init__(self, asset: Address, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount


class WithdrawToken(ContractMethod):
    """Sender redeems aToken and withdraws Token"""

    name = "withdraw"
    in_signature = [("asset", "address"), ("amount", "uint256"), ("receiver", "address")]
    fixed_arguments = {"receiver": AvatarAddress}
    target_address = ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address

    def __init__(self, asset: Address, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount


class DepositETH(ContractMethod):
    """Sender deposits ETH and receives aETH in exchange"""

    name = "depositETH"
    in_signature = [("address", "address"), ("on_behalf_of", "address"), ("referral_code", "uint16")]
    fixed_arguments = {
        "address": ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address,
        "on_behalf_of": AvatarAddress,
        "referral_code": 0,
    }
    target_address = ContractSpecs[Chain.ETHEREUM].WrappedTokenGatewayV3.address

    def __init__(self, eth_amount: int, avatar: Address):
        super().__init__(value=eth_amount, avatar=avatar)


class WithdrawETH(ContractMethod):
    """Sender redeems aETH and withdraws ETH"""

    name = "withdrawETH"
    in_signature = [("address", "address"), ("amount", "uint256"), ("to", "address")]
    fixed_arguments = {"address": ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address, "to": AvatarAddress}
    target_address = ContractSpecs[Chain.ETHEREUM].WrappedTokenGatewayV3.address

    def __init__(self, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.amount = amount


class Collateralize(ContractMethod):
    """Set/unset asset as collateral"""

    name = "setUserUseReserveAsCollateral"
    in_signature = [("asset", "address"), ("use_as_collateral", "bool")]
    fixed_arguments = {}
    target_address = ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address

    def __init__(self, asset: Address, use_as_collateral: bool):
        super().__init__()
        self.args.asset = asset
        self.args.use_as_collateral = use_as_collateral


class Borrow(ContractMethod):
    """Sender receives Token and receives debtToken (stable or variable debt) token"""

    name = "borrow"
    in_signature = (
        ("asset", "address"),
        ("amount", "uint256"),
        ("interest_rate_mode", "uint256"),
        ("referral_code", "uint16"),
        ("on_behalf_of", "address"),
    )
    fixed_arguments = {"on_behalf_of": AvatarAddress, "referral_code": 0}
    target_address = ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address

    def __init__(self, asset: Address, amount: int, interest_rate_mode: InterestRateMode, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount
        InterestRateMode.check(interest_rate_mode)
        self.args.interest_rate_mode = interest_rate_mode


class Repay(ContractMethod):
    """Repay borrowed Token"""

    name = "repay"
    in_signature = (
        ("asset", "address"),
        ("amount", "uint256"),
        ("interest_rate_mode", "uint256"),
        ("on_behalf_of", "address"),
    )
    fixed_arguments = {"on_behalf_of": AvatarAddress}
    target_address = ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address

    def __init__(self, asset: Address, amount: int, interest_rate_mode: InterestRateMode, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount
        InterestRateMode.check(interest_rate_mode)
        self.args.interest_rate_mode = interest_rate_mode


class BorrowETH(ContractMethod):
    """Sender receives ETH and debtETH (stable or variable debt) token"""

    name = "borrowETH"
    in_signature = [
        ("address", "address"),
        ("amount", "uint256"),
        ("interest_rate_mode", "uint256"),
        ("referral_code", "uint16"),
    ]
    fixed_arguments = {"address": ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address, "referral_code": 0}
    target_address = ContractSpecs[Chain.ETHEREUM].WrappedTokenGatewayV3.address

    def __init__(self, amount: int, interest_rate_mode: InterestRateMode):
        super().__init__()
        self.args.amount = amount
        InterestRateMode.check(interest_rate_mode)
        self.args.interest_rate_mode = interest_rate_mode


class RepayETH(ContractMethod):
    """Repay borrowed ETH"""

    name = "repayETH"
    in_signature = [
        ("address", "address"),
        ("amount", "uint256"),
        ("interest_rate_mode", "uint256"),
        ("on_behalf_of", "address"),
    ]
    fixed_arguments = {"address": ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address, "on_behalf_of": AvatarAddress}
    target_address = ContractSpecs[Chain.ETHEREUM].WrappedTokenGatewayV3.address

    def __init__(self, eth_amount: int, interest_rate_mode: InterestRateMode, avatar: Address):
        super().__init__(value=eth_amount, avatar=avatar)
        self.args.amount = eth_amount
        InterestRateMode.check(interest_rate_mode)
        self.args.interest_rate_mode = interest_rate_mode


class SwapBorrowRateMode(ContractMethod):
    """Swaps the borrow rate mode"""

    name = "swapBorrowRateMode"
    in_signature = [("asset", "address"), ("interest_rate_mode", "uint256")]
    target_address = ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address

    def __init__(self, asset: Address, interest_rate_mode: InterestRateMode):
        super().__init__()
        self.args.asset = asset
        InterestRateMode.check(interest_rate_mode)
        self.args.interest_rate_mode = interest_rate_mode


class StakeAAVE(ContractMethod):
    """Stake AAVE in Aave’s safety module"""

    name = "stake"
    in_signature = [("on_behalf_of", "address"), ("amount", "uint256")]
    fixed_arguments = {"on_behalf_of": AvatarAddress}
    target_address = ContractSpecs[Chain.ETHEREUM].stkAAVE.address

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount


class StakeABPT(StakeAAVE):
    """Stake ABPT in Aave’s safety module"""

    target_address = ContractSpecs[Chain.ETHEREUM].stkABPT.address


class ClaimRewardsAndStake(ContractMethod):
    """claim AAVE rewards accrued from staking AAVE and restake"""

    name = "claimRewardsAndStake"
    in_signature = [("to", "address"), ("amount", "uint256")]
    fixed_arguments = {"to": AvatarAddress}
    target_address = ContractSpecs[Chain.ETHEREUM].stkAAVE.address

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount


class UnstakeAAVE(ContractMethod):
    """Unstake AAVE. Can only be called during the 2 days unstaking window after the 10 days cooldown period"""

    name = "redeem"
    in_signature = [("to", "address"), ("amount", "uint256")]
    fixed_arguments = {"to": AvatarAddress}
    target_address = ContractSpecs[Chain.ETHEREUM].stkAAVE.address

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount


class UnstakeABPT(UnstakeAAVE):
    """Unstake ABPT. Can only be called during the 2 days unstaking window after the 10 days cooldown period"""

    target_address = ContractSpecs[Chain.ETHEREUM].stkABPT.address


class CooldownStkAAVE(ContractMethod):
    """Initiates a 10 days cooldown period, once this is over the 2 days unstaking window opens"""

    name = "cooldown"
    in_signature = []
    fixed_arguments = {}
    target_address = ContractSpecs[Chain.ETHEREUM].stkAAVE.address


class CooldownStkABPT(CooldownStkAAVE):
    """Initiates a 10 days cooldown period, once this is over the 2 days unstaking window opens"""

    target_address = ContractSpecs[Chain.ETHEREUM].stkABPT.address


class ClaimAAVERewards(ContractMethod):
    """Claim AAVE rewards accrued from staking AAVE"""

    name = "claimRewards"
    in_signature = [("to", "address"), ("amount", "uint256")]
    fixed_arguments = {"to": AvatarAddress}
    target_address = ContractSpecs[Chain.ETHEREUM].stkAAVE.address

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount


class ClaimABPTRewards(ClaimAAVERewards):
    """Claim AAVE rewards accrued from staking ABPT"""

    target_address = ContractSpecs[Chain.ETHEREUM].stkABPT.address


class SwapAndRepay(ContractMethod):
    """Repay debt using collateral"""

    name = "swapAndRepay"
    in_signature = [
        ("collateral_asset", "address"),
        ("debt_asset", "address"),
        ("collateral_amount", "uint256"),
        ("debt_repay_amount", "uint256"),
        ("debt_rate_mode", "uint256"),
        ("buy_all_balance_offset", "uint256"),
        ("paraswap_data", "bytes"),
        (
            "permit",
            (
                (("amount", "uint256"), ("deadline", "uint256"), ("v", "uint8"), ("r", "bytes32"), ("s", "bytes32")),
                "tuple",
            ),
        ),
    ]
    target_address = ContractSpecs[Chain.ETHEREUM].ParaSwapRepayAdapter.address
    fixed_arguments = {}

    def __init__(
        self,
        collateral_asset: Address,
        debt_asset: Address,
        collateral_amount: int,
        debt_repay_amount: int,
        debt_rate_mode: InterestRateMode,
        buy_all_balance_offset: int,
        calldata,
        permit_amount,
        permit_deadline,
        permit_v,
        permit_r,
        permit_s,
    ):
        super().__init__()
        self.args.collateral_asset, self.args.collateral_amount = collateral_asset, collateral_amount
        self.args.debt_asset, self.args.debt_repay_amount = debt_asset, debt_repay_amount
        InterestRateMode.check(debt_rate_mode)
        self.args.debt_rate_mode = debt_rate_mode
        self.args.buy_all_balance_offset = buy_all_balance_offset
        self.args.paraswap_data = calldata
        self.args.amount = permit_amount
        self.args.deadline = permit_deadline
        self.args.v = permit_v
        self.args.r = permit_r
        self.args.s = permit_s


class SwapAndDeposit(ContractMethod):
    """Swaps an existing amount of a given collateral asset for another one"""

    name = "swapAndDeposit"
    in_signature = [
        ("from_asset", "address"),
        ("to_asset", "address"),
        ("amount", "uint256"),
        ("min_amount_to_receive", "uint256"),
        ("swap_all_balance_offset", "uint256"),
        ("swap_calldata", "bytes"),
        ("augustus", "address"),
        (
            "permit",
            (
                (("amount", "uint256"), ("deadline", "uint256"), ("v", "uint8"), ("r", "bytes32"), ("s", "bytes32")),
                "tuple",
            ),
        ),
    ]
    target_address = ContractSpecs[Chain.ETHEREUM].ParaSwapLiquidityAdapter.address

    def __init__(
        self,
        from_asset: Address,
        to_asset: Address,
        amount: int,
        min_amount_to_receive: int,
        swap_all_balance_offset: int,
        calldata,
        augustus,
        permit_amount,
        permit_deadline,
        permit_v,
        permit_r,
        permit_s,
    ):
        super().__init__()
        self.args.from_asset, self.args.to_asset = from_asset, to_asset
        self.args.amount = amount
        self.args.min_amount_to_receive = min_amount_to_receive
        self.args.swap_all_balance_offset = swap_all_balance_offset
        self.args.swap_calldata = calldata
        self.args.augustus = augustus
        self.args.amount = permit_amount
        self.args.deadline = permit_deadline
        self.args.v = permit_v
        self.args.r = permit_r
        self.args.s = permit_s


class DelegateAAVE(ContractMethod):
    """Delegate the AAVE voting power for all type of actions (Voting and Proposition)"""

    name = "delegate"
    in_signature = [("delegatee", "address")]
    target_address = ContractSpecs[Chain.ETHEREUM].AAVE.address

    def __init__(self, delegatee: Address):
        super().__init__()
        self.args.delegatee = delegatee


class DelegateAAVEByType(ContractMethod):
    """Delegate the AAVE voting power by type of action"""

    name = "delegateByType"
    in_signature = [("delegatee", "address"), ("delegation_type", "uint8")]
    target_address = ContractSpecs[Chain.ETHEREUM].AAVE.address

    def __init__(self, delegatee: Address, delegation_type: DelegationType):
        super().__init__()
        self.args.delegatee = delegatee
        self.args.delegation_type = delegation_type


class DelegatestkAAVE(DelegateAAVE):
    """Delegate the stkAAVE voting power for all type of actions (Voting and Proposition)"""

    target_address = ContractSpecs[Chain.ETHEREUM].stkAAVE.address


class DelegatestkAAVEByType(DelegateAAVEByType):
    """Delegate the stkAAVE voting power by type of action"""

    target_address = ContractSpecs[Chain.ETHEREUM].stkAAVE.address


class SubmitVote(ContractMethod):
    """Submit vote for a specific snapshot"""

    name = "submitVote"
    in_signature = [("proposal_id", "uint256"), ("support", "bool")]
    target_address = ContractSpecs[Chain.ETHEREUM].GovernanceV2.address

    def __init__(self, proposal_id: int, support: bool):
        super().__init__()
        self.args.proposal_id = proposal_id
        self.args.support = support


class LiquidationCall(ContractMethod):
    """Liquidate positions with a health factor below 1"""

    name = "liquidationCall"
    in_signature = [
        ("collateral_asset", "address"),
        ("debt_asset", "address"),
        ("user", "address"),
        ("debt_to_cover", "uint256"),
        ("receive_a_token", "bool"),
    ]
    target_address = ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address

    def __init__(
        self, collateral_asset: Address, debt_asset: Address, user: Address, debt_to_cover: int, receive_a_token: bool
    ):
        super().__init__()
        self.args.collateral_asset = collateral_asset
        self.args.debt_asset = debt_asset
        self.args.user = user
        self.args.debt_to_cover = debt_to_cover
        self.args.receive_a_token = receive_a_token
