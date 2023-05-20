from enum import IntEnum

from rolling_roles.constants import ETHAddr
from rolling_roles.protocols.base import Method, InvalidArgument, AvatarSafeAddress


Address = str


class Approve(Method):
    name = "approve"
    signature = [("spender", "address"), ("amount", "uint256")]
    token = None
    eth_amount = None

    def __init__(self, amount: int):
        self.amount = amount

    @property
    def target_address(self):
        return self.token

    @property
    def value(self):
        return self.eth_amount

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

class DeposiToken(Method):
    """Sender deposits Token and receives aToken in exchange"""
    name = "deposit"
    signature = [("asset", "address"), ("amount", "uint256"), ("onBehalfOf", "address"), ("referralCode", "uint16")]
    fixed_arguments = {"onBehalfOf": AvatarSafeAddress, "referralCode": 0}
    target_address = ETHAddr.AaveLendingPoolV2

    def __init__(self, asset: Address, amount: int, avatar: Address):
        self.asset = asset
        self.amount = amount
        self.avatar = avatar

class DepositETH(Method):
    """Sender deposits ETH and receives aETH in exchange"""
    name = "depositETH"
    signature = [("address", "address"), ("onBehalfOf", "address"), ("referralCode", "uint16")]
    fixed_arguments = {"address": ETHAddr.AaveLendingPoolV2, "onBehalfOf": AvatarSafeAddress, "referralCode": 0}
    target_address = ETHAddr.WrappedTokenGatewayV2

    def __init__(self, eth_amount: int, avatar: Address):
        self.eth_amount = eth_amount
        self.avatar = avatar

class WithdrawToken(Method):
    """Sender redeems aToken and withdraws Token"""
    name = "withdraw"
    signature = [("asset", "address"), ("amount", "uint256"), ("to", "address")]
    fixed_arguments = {"to": AvatarSafeAddress}
    target_address = ETHAddr.AaveLendingPoolV2

    def __init__(self, asset: Address, amount: int, avatar: Address):
        self.asset = asset
        self.amount = amount
        self.avatar = avatar

class WithdrawETH(Method):
    """Sender redeems aETH and withdraws ETH"""
    name = "withdrawETH"
    signature = [("address", "address"), ("amount", "uint256"), ("to", "address")]
    fixed_arguments = {"address": ETHAddr.AaveLendingPoolV2, "to": AvatarSafeAddress}
    target_address = ETHAddr.WrappedTokenGatewayV2

    def __init__(self, amount: int, avatar: Address):
        self.amount = amount
        self.avatar = avatar

class Collateralize(Method):
    """Set/unset asset as collateral"""
    name = "setUserUseReserveAsCollateral"
    signature = [("asset", "address"), ("useAsCollateral", "bool")]
    fixed_arguments = {}
    target_address = ETHAddr.AaveLendingPoolV2

    def __init__(self, asset: Address, use_as_collateral: bool):
        self.asset = asset
        self.useAsCollateral = use_as_collateral

class InterestRateModel(IntEnum):
    STABLE = 1
    VARIABLE = 2

class Borrow(Method):
    """Borrow"""
    name = "borrow"
    signature = [("asset", "address"), ("amount", "uint256"), ("interestRateModel", "uint256"),
                 ("referralCode", "uint16"), ("onBehalfOf", "address")]
    fixed_arguments = {"referralCode": 0, "onBehalfOf": AvatarSafeAddress}
    target_address = ETHAddr.AaveLendingPoolV2

    def __init__(self, asset: Address, amount: int, interest_rate_model: InterestRateModel, avatar: Address):
        self.asset = asset
        self.amount = amount
        self.avatar = avatar
        if interest_rate_model not in InterestRateModel:
            raise InvalidArgument(f"Invalid interestRateModel={interest_rate_model}")
        self.interestRateModel = interest_rate_model

class BorrowETH(Method):
    """Borrow ETH"""
    name = "borrowETH"
    signature = [("address", "address"), ("amount", "uint256"), ("interestRateModel", "uint256"), ("referralCode", "uint16")]
    fixed_arguments = {"address": ETHAddr.AaveLendingPoolV2, "referralCode": 0}
    target_address = ETHAddr.WrappedTokenGatewayV2

    def __init__(self, amount: int, interest_rate_model: InterestRateModel):
        self.amount = amount
        if interest_rate_model not in InterestRateModel:
            raise InvalidArgument(f"Invalid interestRateModel={interest_rate_model}")
        self.interestRateModel = interest_rate_model

class Stake(Method):
    name = 'stake'
    signature = [("onBehalfOf", "address"), ("amount", "uint256")]
    fixed_arguments = {"onBehalfOf": AvatarSafeAddress}
    target_address = ETHAddr.stkAAVE

    def __init__(self, amount: int, avatar: Address):
        self.amount = amount
        self.avatar = avatar

ACTION_DEPOSIT = [ApproveForAaveLendingPoolV2, DeposiToken, DepositETH, WithdrawToken, WithdrawETH, Collateralize]
ACTION_BORROW = [ApproveForAaveLendingPoolV2, Borrow, BorrowETH, ] # TODO: repay, etc
ACTION_STAKE = [] # TODO: ....

"""
### Categorized Methods:

- Approve:
    - Method 1: approve (spender: AaveLendingPoolV2)
        - Description: approve token with AaveLendingPoolV2 as spender
        - Target Address: Token
        - Function signature: approve(address,uint256)
        - Parameters:
            1. spender: AaveLendingPoolV2
            2. amount
    - Method 2: approve AAVE (spender: stkAAVE)
        - Description: approve AAVE with stkAAVE as spender
        - Target Address: AAVE
        - Function signature: approve(address,uint256)
        - Parameters:
            1. spender: stkAAVE
            2. amount
    - Method 3: approve ABPT (spender: stkABPT)
        - Description: approve ABPT with stkABPTas spender
        - Target Address: ABPT
        - Function signature: approve(address,uint256)
        - Parameters:
            1. spender: stkABPT
            2. amount
    - Method 4: approve (spender: ParaSwapRepayAdapter)
        - Description: approve token with ParaSwapRepayAdapter as spender
        - Target Address: Token
        - Function signature: approve(address,uint256)
        - Parameters:
            1. spender: ParaSwapRepayAdapter
            2. amount
- Deposit:
    - Method 1: deposit
        - Description: deposit
        - Target Address: AaveLendingPoolV2
        - Function signature: deposit(address,uint256,address,uint16)
        - Parameters:
            1. asset: Token
            2. amount
            3. onBehalfOf: AVATAR
            4. referralCode: 0x
    - Method 2: depositETH
        - Description: depositETH
        - Target Address: WrappedTokenGatewayV2
        - Function signature: depositETH(address,address,uint16)
        - Parameters:
            1. address: AaveLendingPoolV2
            2. onBehalfOf: AVATAR
            3. referralCode: usually 0x
        - Value: True
- Withdraw:
    - Method 1: withdraw
        - Description: withdraw
        - Target Address: AaveLendingPoolV2
        - Function signature: withdraw(address,uint256,address)
        - Parameters:
            1. asset: Token
            2. amount
            3. to: AVATAR
    - Method 2: withdrawETH
        - Description: withdrawETH
        - Target Address: WrappedTokenGatewayV2
        - Function signature: withdrawETH(address,uint256,address)
        - Parameters:
            1. address: AaveLendingPoolV2
            2. amount
            3. to: AVATAR
- Collateralize:
    - Method 1: setUserUseReserveAsCollateral
        - Description: set/unset asset as collateral
        - Target Address: AaveLendingPoolV2
        - Function signature: setUserUseReserveAsCollateral(address,bool)
        - Parameters:
            1. asset: Token
            2. useAsCollateral: True/False
- Borrow:
    - Method 1: borrow
        - Description: borrow
        - Target Address: AaveLendingPoolV2
        - Function signature: borrow(address,uint256,uint256,uint16,address)
        - Parameters:
            1. asset: Token
            2. amount
            3. interestRateModel: 1 (Stable), 2 (Variable)
            4. referralCode: 0x
            5. onBehalfOf: AVATAR
    - Method 2: borrowETH
        - Description: borrowETH
        - Target Address: WrappedTokenGatewayV2
        - Function signature: borrowETH(address,uint256,uint256,uint16)
        - Parameters:
            1. address: AaveLendingPoolV2
            2. amount
            3. interestRateModel: 1 (Stable), 2 (Variable)
            4. referralCode: 0x
- Repay:
    - Method 1: repay
        - Description: repay
        - Target Address: AaveLendingPoolV2
        - Function signature: repay(address,uint256,uint256,address)
        - Parameters:
            1. asset: Token
            2. amount
            3. rateModel: 1 (Stable), 2 (Variable)
            4. onBehalfOf: AVATAR
    - Method 2: repayETH
        - Description: repayETH
        - Target Address: WrappedTokenGatewayV2
        - Function signature: repayETH(address,uint256,uint256,address)
        - Parameters:
            1. address: AaveLendingPoolV2
            2. amount
            3. rateModel: 1 (Stable), 2 (Variable)
            4. onBehalfOf: AVATAR
        - Value: True
- Stake:
    - Method 1: stake AAVE
        - Description: stake AAVE
        - Target Address: stkAAVE
        - Function signature: stake(address,uint256)
        - Parameters:
            1. onBehalfOf: AVATAR
            2. amount
    - Method 2: stake ABPT
        - Description: stake ABPT
        - Target Address: stkABPT
        - Function signature: stake(address,uint256)
        - Parameters:
            1. onBehalfOf: AVATAR
            2. amount
- Unstake:
    - Method 1: unstake AAVE
        - Description: unstake AAVE can only be called during the 2 days unstaking window after the 10 days cooldown period
        - Target Address: stkAAVE
        - Function signature: redeem(address,uint256)
        - Parameters:
            1. to: AVATAR
            2. amount
    - Method 2: unstake ABPT
        - Description: unstake ABPT can only be called during the 2 days unstaking window after the 10 days cooldown period
        - Target Address: stkABPT
        - Function signature: redeem(address,uint256)
        - Parameters:
            1. to: AVATAR
            2. amount
- Cooldown:
    - Method 1: cooldown stkAAVE
        - Description: initiates a 10 days cooldown period, once this is over the 2 days unstaking window opens
        - Target Address: stkAAVE
        - Function signature: cooldown()
    - Method 2: cooldown stkABPT
        - Description: initiates a 10 days cooldown period, once this is over the 2 days unstaking window opens
        - Target Address: stkABPT
        - Function signature: cooldown()
- Claim:
    - Method 1: claimRewards from staking AAVE
        - Description: claim AAVE rewards from staking AAVE
        - Target Address: stkAAVE
        - Function signature: claimRewards(address,uint256)
        - Parameters:
            1. to: AVATAR
            2. amount
    - Method 2: claimRewards from staking ABPT
        - Description: claim AAVE rewards from staking ABPT
        - Target Address: stkABPT
        - Function signature: claimRewards(address,uint256)
        - Parameters:
            1. to: AVATAR
            2. amount
- Swap and Repay:
    - Method 1: swapAndRepay
        - Target Address: ParaSwapRepayAdapter
        - Function signature: swapAndRepay(address,address,uint256,uint256,uint256,uint256,bytes,(uint256,uint256,uint8,bytes32,bytes32))
        - Parameters:
            1. collateralAsset
            2. debtAsset
            3. collateralAmount
            4. debtRepayAmount
            5. debtRateMode
            6. buyAllBalanceOffset
            7. paraswapData
            8. permitSignature.amount
            9. permitSignature.deadline
            10. permitSignature.v
            11. permitSignature.r
            12. permitSignature.s

### Actions with their methods

- deposit:
    - Signature: deposit(address token, address avatar)
    - List of methods:
        1. Approve/1: approve (spender: AaveLendingPoolV2)
        2. Deposit/1: deposit
        3. Deposit/2: depositETH
        4. Withdraw/1: withdraw
        5. Withdraw/2: withdrawETH
        6. Collateralize/1: setUserUseReserveAsCollateral
- borrow:
    - Signature: borrow(address token, address avatar)
    - List of methods:
        1. Approve/1: approve (spender: AaveLendingPoolV2)
        2. Borrow/1: borrow
        3. Borrow/2: borrowETH
        4. Repay/1: repay
        5. Repay/2: repayETH
- stake:
    - Signature: stake(address token, address avatar)
    - List of methods:
        1. Approve/2: approve AAVE (spender: stkAAVE)
        2. Approve/3: approve ABPT (spender: stkABPT)
        3. Stake/1: stake AAVE
        4. Stake/2: stake ABPT
        5. Unstake/1: unstake AAVE
        6. Unstake/2: unstake ABPT
        7. Cooldown/1: cooldown stkAAVE
        8. Cooldown/2: cooldown stkAAVE
        9. Claim/1: claimRewards from staking AAVE
        10. Claim/2: claimRewards from staking ABPT
"""



