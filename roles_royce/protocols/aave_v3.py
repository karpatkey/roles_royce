from enum import IntEnum
from roles_royce.constants import Chain
from roles_royce.toolshed.protocol_utils.aave_v3.addresses_and_abis import AddressesAndAbis
from roles_royce.protocols.base import ContractMethod, Address, AvatarAddress, InvalidArgument, BaseApprove, BaseApproveForToken


class InterestRateMode(IntEnum):
    STABLE = 1  # stable is not available at the moment
    VARIABLE = 2

    @staticmethod
    def check(value):
        if value not in InterestRateMode:
            raise InvalidArgument(f"Invalid interestRateMode={value}")

class DelegationTarget():
    targets = [AddressesAndAbis[Chain.Ethereum].variableDebtWETH.address,
                AddressesAndAbis[Chain.Ethereum].stableDebtWETH.address]

    @staticmethod
    def check_delegation_target(target: Address):
        if target not in DelegationTarget.targets:
            raise InvalidArgument(f"Invalid delegationTarget={target}")

class DelegationType(IntEnum):
    VOTING = 0
    PROPOSITION = 1

class ApproveToken(BaseApproveForToken):
    """approve Token with AaveLendingPoolV3 as spender"""
    fixed_arguments = {"spender": AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address}

class ApproveAEthWETH(BaseApproveForToken):
    """approve aEthWETH with WrappedTokenGatewayV3 as spender"""
    fixed_arguments = {"spender": AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address}
    token = AddressesAndAbis[Chain.Ethereum].aEthWETH.address

class ApproveForStkAAVE(BaseApprove):
    """Approve AAVE with stkAAVE as spender"""
    fixed_arguments = {"spender": AddressesAndAbis[Chain.Ethereum].stkAAVE.address}
    token = AddressesAndAbis[Chain.Ethereum].AAVE.address

class ApproveForStkABPT(BaseApprove):
    """Approve ABPT with stkABPT as spender"""
    fixed_arguments = {"spender": AddressesAndAbis[Chain.Ethereum].stkABPT.address}
    token = AddressesAndAbis[Chain.Ethereum].ABPT.address

class ApproveDelegation(ContractMethod):
    """sets the amount of allowance for WrappedTokenGatewayV3 to borrow 
    variableDebtWETH or stableDebtWETH"""
    name = "approveDelegation"
    in_signature = (("delegatee", "address"),
                    ("amount", "uint256"))
    fixed_arguments = {"delegatee": AddressesAndAbis[Chain.Ethereum].WrappedTokenGatewayV3.address}
    
    def __init__(self, target: DelegationTarget, amount: int):
        super().__init__()
        DelegationTarget.check_delegation_target(target)
        self.target_address = target
        self.args.amount = amount

class DepositToken(ContractMethod):
    """Sender deposits Token and receives aToken in exchange"""
    name = "supply"
    in_signature = (("asset", "address"),
                    ("amount", "uint256"),
                    ("on_behalf_of", "address"),
                    ("referral_code", "uint16"))
    fixed_arguments = {"on_behalf_of": AvatarAddress, "referral_code": 0}
    target_address = AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address

    def __init__(self, asset: Address, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount

class WithdrawToken(ContractMethod):
    """Sender redeems aToken and withdraws Token"""
    name = "withdraw"
    in_signature = [("asset", "address"), ("amount", "uint256"), ("receiver", "address")]
    fixed_arguments = {"receiver": AvatarAddress}
    target_address = AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address

    def __init__(self, asset: Address, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount

class DepositETH(ContractMethod):
    """Sender deposits ETH and receives aETH in exchange"""
    name = "depositETH"
    in_signature = [("address", "address"), ("on_behalf_of", "address"), ("referral_code", "uint16")]
    fixed_arguments = {"address": AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address, "on_behalf_of": AvatarAddress, "referral_code": 0}
    target_address = AddressesAndAbis[Chain.Ethereum].WrappedTokenGatewayV3.address

    def __init__(self, eth_amount: int, avatar: Address):
        super().__init__(value=eth_amount, avatar=avatar)

class WithdrawETH(ContractMethod):
    """Sender redeems aETH and withdraws ETH"""
    name = "withdrawETH"
    in_signature = [("address", "address"), ("amount", "uint256"), ("to", "address")]
    fixed_arguments = {"address": AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address, "to": AvatarAddress}
    target_address = AddressesAndAbis[Chain.Ethereum].WrappedTokenGatewayV3.address

    def __init__(self, amount: int, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.amount = amount

class Collateralize(ContractMethod):
    """Set/unset asset as collateral"""
    name = "setUserUseReserveAsCollateral"
    in_signature = [("asset", "address"), ("use_as_collateral", "bool")]
    fixed_arguments = {}
    target_address = AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address

    def __init__(self, asset: Address, use_as_collateral: bool):
        super().__init__()
        self.args.asset = asset
        self.args.use_as_collateral = use_as_collateral

class Borrow(ContractMethod):
    """Sender receives Token and receives debtToken (stable or variable debt) token"""
    name = "borrow"
    in_signature = (("asset", "address"),
                    ("amount", "uint256"),
                    ("interest_rate_mode", "uint256"),
                    ("referral_code", "uint16"),
                    ("on_behalf_of", "address"))
    fixed_arguments = {"on_behalf_of": AvatarAddress, "referral_code": 0}
    target_address = AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address

    def __init__(self, asset: Address, amount: int, interest_rate_mode: InterestRateMode, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount
        InterestRateMode.check(interest_rate_mode)
        self.args.interest_rate_mode = interest_rate_mode

class Repay(ContractMethod):
    """Repay borrowed Token"""
    name = "repay"
    in_signature = (("asset", "address"),
                    ("amount", "uint256"),
                    ("interest_rate_mode", "uint256"),
                    ("on_behalf_of", "address"))
    fixed_arguments = {"on_behalf_of": AvatarAddress}
    target_address = AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address

    def __init__(self, asset: Address, amount: int, interest_rate_mode: InterestRateMode, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount
        InterestRateMode.check(interest_rate_mode)
        self.args.rate_mode = interest_rate_mode

class BorrowETH(ContractMethod):
    """Sender receives ETH and debtETH (stable or variable debt) token"""
    name = "borrowETH"
    in_signature = [("address", "address"), ("amount", "uint256"), ("interest_rate_mode", "uint256"), ("referral_code", "uint16")]
    fixed_arguments = {"address": AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address, "referral_code": 0}
    target_address = AddressesAndAbis[Chain.Ethereum].WrappedTokenGatewayV3.address

    def __init__(self, amount: int, interest_rate_mode: InterestRateMode):
        super().__init__()
        self.args.amount = amount
        InterestRateMode.check(interest_rate_mode)
        self.args.interest_rate_mode = interest_rate_mode

class RepayETH(ContractMethod):
    """Repay borrowed ETH"""
    name = 'repayETH'
    in_signature = [('address', 'address'), ('amount', 'uint256'), ('interest_rate_mode', 'uint256'), ('on_behalf_of', 'address')]
    fixed_arguments = {'address': AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address, 'on_behalf_of': AvatarAddress}
    target_address = AddressesAndAbis[Chain.Ethereum].WrappedTokenGatewayV3.address

    def __init__(self, eth_amount: int, interest_rate_mode: InterestRateMode, avatar: Address):
        super().__init__(value=eth_amount, avatar=avatar)
        self.args.amount = eth_amount
        InterestRateMode.check(interest_rate_mode)
        self.args.interest_rate_mode = interest_rate_mode

class SwapBorrowRateMode(ContractMethod):
    """Swaps the borrow rate mode"""
    name = "swapBorrowRateMode"
    in_signature = [("asset", "address"), ("interest_rate_mode", "uint256")]
    target_address = AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address

    def __init__(self, asset: Address, interest_rate_mode: InterestRateMode):
        super().__init__()
        self.args.asset = asset
        InterestRateMode.check(interest_rate_mode)
        self.args.interest_rate_mode = interest_rate_mode

class StakeAAVE(ContractMethod):
    """Stake AAVE in Aave’s safety module"""
    name = 'stake'
    in_signature = [("on_behalf_of", "address"), ("amount", "uint256")]
    fixed_arguments = {"on_behalf_of": AvatarAddress}
    target_address = AddressesAndAbis[Chain.Ethereum].stkAAVE.address

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount

class StakeABPT(StakeAAVE):
    """Stake ABPT in Aave’s safety module"""
    target_address = AddressesAndAbis[Chain.Ethereum].stkABPT.address

class ClaimRewardsAndStake(ContractMethod):
    """claim AAVE rewards accrued from staking AAVE and restake"""
    name = 'claimRewardsAndStake'
    in_signature = [("to", "address"), ("amount", "uint256")]
    fixed_arguments = {"to": AvatarAddress}
    target_address = AddressesAndAbis[Chain.Ethereum].stkAAVE.address

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount

class UnstakeAAVE(ContractMethod):
    """Unstake AAVE. Can only be called during the 2 days unstaking window after the 10 days cooldown period"""
    name = 'redeem'
    in_signature = [('to', 'address'), ('amount', 'uint256')]
    fixed_arguments = {'to': AvatarAddress}
    target_address = AddressesAndAbis[Chain.Ethereum].stkAAVE.address

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount

class UnstakeABPT(UnstakeAAVE):
    """Unstake ABPT. Can only be called during the 2 days unstaking window after the 10 days cooldown period"""
    target_address = AddressesAndAbis[Chain.Ethereum].stkABPT.address

class CooldownStkAAVE(ContractMethod):
    """Initiates a 10 days cooldown period, once this is over the 2 days unstaking window opens"""
    name = 'cooldown'
    in_signature = []
    fixed_arguments = {}
    target_address = AddressesAndAbis[Chain.Ethereum].stkAAVE.address

class CooldownStkABPT(CooldownStkAAVE):
    """Initiates a 10 days cooldown period, once this is over the 2 days unstaking window opens"""
    target_address = AddressesAndAbis[Chain.Ethereum].stkABPT.address

class ClaimAAVERewards(ContractMethod):
    """Claim AAVE rewards accrued from staking AAVE"""
    name = 'claimRewards'
    in_signature = [('to', 'address'), ('amount', 'uint256')]
    fixed_arguments = {'to': AvatarAddress}
    target_address = AddressesAndAbis[Chain.Ethereum].stkAAVE.address

    def __init__(self, avatar: Address, amount: int):
        super().__init__(avatar=avatar)
        self.args.amount = amount

class ClaimABPTRewards(ClaimAAVERewards):
    """Claim AAVE rewards accrued from staking ABPT"""
    target_address = AddressesAndAbis[Chain.Ethereum].stkABPT.address

class DelegateAAVE(ContractMethod):
    """Delegate the AAVE voting power for all type of actions (Voting and Proposition)."""
    name = "delegate"
    in_signature = [("delegatee", "address")]
    target_address = AddressesAndAbis[Chain.Ethereum].AAVE.address

    def __init__(self, delegatee: Address):
        super().__init__()
        self.args.delegatee = delegatee

class DelegateAAVEByType(ContractMethod):
    """Delegate the AAVE voting power by type of action."""
    name = "delegateByType"
    in_signature = [("delegatee", "address"), ("delegation_type", "uint8")]
    target_address = AddressesAndAbis[Chain.Ethereum].AAVE.address

    def __init__(self, delegatee: Address, delegation_type: DelegationType):
        super().__init__()
        self.args.delegatee = delegatee
        self.args.delegation_type = delegation_type

class DelegatestkAAVE(DelegateAAVE):
    target_address = AddressesAndAbis[Chain.Ethereum].stkAAVE.address

class DelegatestkAAVEByType(DelegateAAVEByType):
    target_address = AddressesAndAbis[Chain.Ethereum].stkAAVE.address