from defabipedia.types import Blockchain
from defabipedia.aura import ContractSpecs

from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Address, BaseApprove, BaseApproveForToken, ContractMethod


class ApproveForBooster(BaseApproveForToken):
    """approve LPToken with AURABooster as spender"""

    fixed_arguments = {"spender": ETHAddr.AURABooster}


class ApproveTokenDepWrapper(BaseApproveForToken):
    """approve token with AURA_rewardpool_dep_wrapper as spender"""

    fixed_arguments = {"spender": ETHAddr.AURA_rewardpool_dep_wrapper}


class ApproveAURABal(BaseApprove):
    """approve AURABal with AURABAL_bal_weth_depositor as spender"""

    fixed_arguments = {"spender": ETHAddr.AURABAL}
    token = ETHAddr.AURABAL_stakingrewarder


class ApproveB80Bal20WETH(BaseApprove):
    """approve B80Bal20WETH with AURABAL_bal_weth_depositor as spender"""

    fixed_arguments = {"spender": ETHAddr.AURABAL_bal_weth_depositor}
    token = ETHAddr.B_80BAL_20WETH


class ApproveBAL(BaseApprove):
    """approve BAL with AURABAL_bal_depositor as spender"""

    fixed_arguments = {"spender": ETHAddr.AURABAL_bal_depositor}
    token = ETHAddr.BAL


class ApproveAURABalStk(BaseApprove):
    """approve AURABal with stkAURABAL as spender"""

    fixed_arguments = {"spender": ETHAddr.stkAURABAL}
    token = ETHAddr.AURABAL


class ApproveAURA(BaseApprove):
    """approve AURA with AURALocker as spender"""

    fixed_arguments = {"spender": ETHAddr.AURALocker}
    token = ETHAddr.AURA


class WithdrawAndUnwrap(ContractMethod):
    """WIthdraws staked BPT and claims any corresponding unclaimed rewards."""

    name = "withdrawAndUnwrap"
    in_signature = [("amount", "uint256"), ("claim", "bool")]
    fixed_arguments = {"claim": True}

    def __init__(self, reward_address: Address, amount: int):
        super().__init__()
        self.target_address = reward_address
        self.args.amount = amount


class DepositBPT(ContractMethod):
    """deposit BPT token"""

    name = "deposit"
    in_signature = [("pool_id", "uint256"), ("amount", "uint256"), ("stake", "bool")]
    fixed_arguments = {"stake": True}
    target_address = ETHAddr.AURABooster

    def __init__(self, pool_id: int, amount: int):
        super().__init__()
        self.args.pool_id = pool_id
        self.args.amount = amount


class StakeAURABal(ContractMethod):
    """stake aurabal"""

    name = "stake"
    in_signature = [("amount", "uint256")]
    target_address = ETHAddr.AURABAL_stakingrewarder

    def __init__(self, amount: int):
        super().__init__()
        self.args.amount = amount


class Deposit80BAL20WETH(ContractMethod):
    """deposit 80% BAL and 20% WETH"""

    name = "deposit"
    in_signature = [("amount", "uint256"), ("lock", "bool"), ("stake_address", "address")]
    fixed_arguments = {"lock": True}
    target_address = ETHAddr.AURABAL_bal_weth_depositor

    def __init__(self, amount: int, stake_address: Address):
        super().__init__()
        self.args.amount = amount
        self.args.stake_address = stake_address


class DepositBAL(ContractMethod):
    """deposit BAL"""

    name = "deposit"
    in_signature = [("amount", "uint256"), ("min_out", "uint256"), ("lock", "bool"), ("stake_address", "address")]
    fixed_arguments = {"lock": True}
    target_address = ETHAddr.AURABAL_bal_depositor

    def __init__(self, amount: int, min_out: int, stake_address: Address):
        super().__init__()
        self.args.amount = amount
        self.args.min_out = min_out
        self.args.stake_address = stake_address


class WithdrawAuraBAL(ContractMethod):
    """withdraw aurabal"""

    name = "withdraw"
    in_signature = [("amount", "uint256"), ("claim", "bool")]
    target_address = ETHAddr.AURABAL_stakingrewarder

    def __init__(self, amount: int, claim: bool):
        super().__init__()
        self.args.amount = amount
        self.args.claim = claim


class CompounderStaking(ContractMethod):
    """compounder staking"""

    name = "deposit"
    in_signature = [("amount", "uint256"), ("avatar", "address")]
    target_address = ETHAddr.stkAURABAL

    def __init__(self, amount: int, avatar: Address):
        super().__init__()
        self.args.amount = amount
        self.args.avatar = avatar


class CompounderWithdraw(ContractMethod):
    """compounder withdraw unsaking"""

    name = "withdraw"
    in_signature = [("amount", "uint256"), ("receiver", "address"), ("avatar", "address")]
    target_address = ETHAddr.stkAURABAL

    def __init__(self, amount: int, receiver: Address, avatar: Address):
        super().__init__()
        self.args.amount = amount
        self.args.receiver = receiver
        self.args.avatar = avatar


class CompounderRedeem(ContractMethod):
    """compounder redeem"""

    name = "redeem"
    in_signature = [("amount", "uint256"), ("receiver", "address"), ("avatar", "address")]
    target_address = ETHAddr.stkAURABAL

    def __init__(self, amount: int, receiver: Address, avatar: Address):
        super().__init__()
        self.args.amount = amount
        self.args.receiver = receiver
        self.args.avatar = avatar


class LockAURA(ContractMethod):
    """lock aura"""

    name = "lock"
    in_signature = [("receiver", "address"), ("amount", "uint256")]
    target_address = ETHAddr.AURALocker

    def __init__(self, receiver: Address, amount: int):
        super().__init__()
        self.args.receiver = receiver
        self.args.amount = amount


class ProcessExpiredLocks(ContractMethod):
    """process expired locks"""

    name = "processExpiredLocks"
    in_signature = [("relock", "bool")]
    target_address = ETHAddr.AURALocker

    def __init__(self, relock: bool):
        super().__init__()
        self.args.relock = relock

class ClaimRewards(ContractMethod):
    """claim rewards"""

    name = "claimRewards"
    in_signature = (
        ("reward_contracts", "address[]"),
        ("extra_reward_contracts", "address[]"),
        ("token_reward_contracts", "address[]"),
        ("token_reward_tokens", "address[]"),
        (
            "amounts",
            (
                (
                    ("deposit_max_amount", "uint256"),
                    ("min_amounts_out", "uint256"),
                    ("deposit_max_amount_2", "uint256"),
                    ("deposit_max_amount_3", "uint256"),
                ),
                "tuple",
            ),
        ),
        (
            "options",
            (
                (
                    ("claim", "bool"),
                    ("claim_locked", "bool"),
                    ("lock", "bool"),
                    ("lock_deposited", "bool"),
                    ("use_all_wallet_funds", "bool"),
                    ("use_compounder", "bool"),
                    ("lock2", "bool")
                ),
                "tuple",
            )
        )
        )
    target_address = None

    def __init__(self, 
                 blockchain: Blockchain, 
                 reward_contracts: list, 
                 extra_reward_contracts: list, 
                 token_reward_contracts: list, 
                 token_reward_tokens: list, 
                 deposit_max_amount: int,
                 min_amounts_out: int,
                 deposit_max_amount_2: int,
                 deposit_max_amount_3: int,
                 claim: bool,
                 claim_locked: bool,
                 lock: bool,
                 lock_deposited: bool,
                 use_all_wallet_funds: bool,
                 use_compounder: bool,
                 lock2: bool):
        self.target_address = ContractSpecs[blockchain].ClaimZap.address
        super().__init__()
        self.args.reward_contracts = reward_contracts
        self.args.extra_reward_contracts = extra_reward_contracts
        self.args.token_reward_contracts = token_reward_contracts
        self.args.token_reward_tokens = token_reward_tokens
        self.args.deposit_max_amount = deposit_max_amount
        self.args.min_amounts_out = min_amounts_out
        self.args.deposit_max_amount_2 = deposit_max_amount_2
        self.args.deposit_max_amount_3 = deposit_max_amount_3
        self.args.amounts = [self.args.deposit_max_amount, 
                             self.args.min_amounts_out, 
                             self.args.deposit_max_amount_2, 
                             self.args.deposit_max_amount_3]
        self.args.claim = claim
        self.args.claim_locked = claim_locked
        self.args.lock = lock
        self.args.lock_deposited = lock_deposited
        self.args.use_all_wallet_funds = use_all_wallet_funds
        self.args.use_compounder = use_compounder
        self.args.lock2 = lock2
        self.args.options = [self.args.claim, 
                             self.args.claim_locked, 
                             self.args.lock, 
                             self.args.lock_deposited, 
                             self.args.use_all_wallet_funds, 
                             self.args.use_compounder, 
                             self.args.lock2]


