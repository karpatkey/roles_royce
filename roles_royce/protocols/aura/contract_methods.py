from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import ContractMethod, BaseApproveForToken, BaseApprove, Address
from defabipedia.types import Blockchain


class ApproveForBooster(BaseApproveForToken):
   """
   A class to approve LPToken with AURABooster as spender.

   Attributes:
       fixed_arguments (dict): A dictionary containing the spender's Ethereum address.
   """
   fixed_arguments = {"spender": ETHAddr.AURABooster}


class ApproveTokenDepWrapper(BaseApproveForToken):
   """
   A class to approve token with AURA_rewardpool_dep_wrapper as spender.

   Attributes:
       fixed_arguments (dict): A dictionary containing the spender's Ethereum address.
   """
   fixed_arguments = {"spender": ETHAddr.AURA_rewardpool_dep_wrapper}



class ApproveAURABal(BaseApprove):
   """
   A class to approve AURABal with AURABAL_bal_weth_depositor as spender.

   Attributes:
       fixed_arguments (dict): A dictionary containing the spender's Ethereum address.
       token (str): The Ethereum address of the token to be approved.
   """
   fixed_arguments = {"spender": ETHAddr.AURABAL}
   token = ETHAddr.AURABAL_stakingrewarder


class ApproveB80Bal20WETH(BaseApprove):
   """
   A class to approve B80Bal20WETH with AURABAL_bal_weth_depositor as spender.

   Attributes:
       fixed_arguments (dict): A dictionary containing the spender's Ethereum address.
       token (str): The Ethereum address of the token to be approved.
   """
   fixed_arguments = {"spender": ETHAddr.AURABAL_bal_weth_depositor}
   token = ETHAddr.B_80BAL_20WETH



class ApproveBAL(BaseApprove):
   """
   A class to approve BAL with AURABAL_bal_depositor as spender.

   Attributes:
       fixed_arguments (dict): A dictionary containing the spender's Ethereum address.
       token (str): The Ethereum address of the token to be approved.
   """
   fixed_arguments = {"spender": ETHAddr.AURABAL_bal_depositor}
   token = ETHAddr.BAL



class ApproveAURABalStk(BaseApprove):
  """
  A class to approve AURABal with stkAURABAL as spender.

  Attributes:
      fixed_arguments (dict): A dictionary containing the spender's Ethereum address.
      token (str): The Ethereum address of the token to be approved.
  """
  fixed_arguments = {"spender": ETHAddr.stkAURABAL}
  token = ETHAddr.AURABAL



class ApproveAURA(BaseApprove):
  """
  A class to approve AURA with AURALocker as spender.

  Attributes:
      fixed_arguments (dict): A dictionary containing the spender's Ethereum address.
      token (str): The Ethereum address of the token to be approved.
  """
  fixed_arguments = {"spender": ETHAddr.AURALocker}
  token = ETHAddr.AURA



class WithdrawAndUnwrap(ContractMethod):
  """
  A class to withdraw staked BPT and claim any corresponding unclaimed rewards.

  Attributes:
      name (str): The name of the method.
      in_signature (list): A list of tuples containing the method's input parameters and their types.
      fixed_arguments (dict): A dictionary containing the method's fixed arguments.

  Methods:
      __init__(reward_address: Address, amount: int): Initializes the method with the given reward address and amount.
  """
  name = "withdrawAndUnwrap"
  in_signature = [("amount", "uint256"), ("claim", "bool")]
  fixed_arguments = {"claim": True}

  def __init__(self, reward_address: Address, amount: int):
      super().__init__()
      self.target_address = reward_address
      self.args.amount = amount


class DepositBPT(ContractMethod):
 """
 A class to deposit BPT token.

 Attributes:
     name (str): The name of the method.
     in_signature (list): A list of tuples containing the method's input parameters and their types.
     fixed_arguments (dict): A dictionary containing the method's fixed arguments.
     target_address (str): The Ethereum address of the target.

 Methods:
     __init__(pool_id: int, amount: int): Initializes the method with the given pool id and amount.
 """
 name = "deposit"
 in_signature = [("pool_id", "uint256"), ("amount", "uint256"), ("stake", "bool")]
 fixed_arguments = {"stake": True}
 target_address = ETHAddr.AURABooster

 def __init__(self, pool_id: int, amount: int):
     super().__init__()
     self.args.pool_id = pool_id
     self.args.amount = amount


class StakeAURABal(ContractMethod):
 """
 A class to stake aurabal.

 Attributes:
     name (str): The name of the method.
     in_signature (list): A list of tuples containing the method's input parameters and their types.
     target_address (str): The Ethereum address of the target.

 Methods:
     __init__(amount: int): Initializes the method with the given amount.
 """
 name = "stake"
 in_signature = [("amount", "uint256")]
 target_address = ETHAddr.AURABAL_stakingrewarder

 def __init__(self, amount: int):
     super().__init__()
     self.args.amount = amount


class Deposit80BAL20WETH(ContractMethod):
 """
 A class to deposit 80% BAL and 20% WETH.

 Attributes:
     name (str): The name of the method.
     in_signature (list): A list of tuples containing the method's input parameters and their types.
     fixed_arguments (dict): A dictionary containing the method's fixed arguments.
     target_address (str): The Ethereum address of the target.

 Methods:
     __init__(amount: int, stake_address: Address): Initializes the method with the given amount and stake address.
 """
 name = "deposit"
 in_signature = [("amount", "uint256"), ("lock", "bool"), ("stake_address", "address")]
 fixed_arguments = {"lock": True}
 target_address = ETHAddr.AURABAL_bal_weth_depositor

 def __init__(self, amount: int, stake_address: Address):
     super().__init__()
     self.args.amount = amount
     self.args.stake_address = stake_address

class DepositBAL(ContractMethod):
 """
 A class to deposit BAL.

 Attributes:
    name (str): The name of the method.
    in_signature (list): A list of tuples containing the method's input parameters and their types.
    fixed_arguments (dict): A dictionary containing the method's fixed arguments.
    target_address (str): The Ethereum address of the target.

 Methods:
    __init__(amount: int, min_out: int, stake_address: Address): Initializes the method with the given amount, minimum output, and stake address.
 """
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
 """
 A class to withdraw aurabal.

 Attributes:
    name (str): The name of the method.
    in_signature (list): A list of tuples containing the method's input parameters and their types.
    target_address (str): The Ethereum address of the target.

 Methods:
    __init__(amount: int, claim: bool): Initializes the method with the given amount and claim status.
 """
 name = "withdraw"
 in_signature = [("amount", "uint256"), ("claim", "bool")]
 target_address = ETHAddr.AURABAL_stakingrewarder

 def __init__(self, amount: int, claim: bool):
    super().__init__()
    self.args.amount = amount
    self.args.claim = claim


class CompounderStaking(ContractMethod):
 """
 A class for compounder staking.

 Attributes:
    name (str): The name of the method.
    in_signature (list): A list of tuples containing the method's input parameters and their types.
    target_address (str): The Ethereum address of the target.

 Methods:
    __init__(amount: int, avatar: Address): Initializes the method with the given amount and avatar.
 """
 name = "deposit"
 in_signature = [("amount", "uint256"), ("avatar", "address")]
 target_address = ETHAddr.stkAURABAL

 def __init__(self, amount: int, avatar: Address):
    super().__init__()
    self.args.amount = amount
    self.args.avatar = avatar


class CompounderWithdraw(ContractMethod):
 """
 A class for compounder withdraw unsaking.

 Attributes:
    name (str): The name of the method.
    in_signature (list): A list of tuples containing the method's input parameters and their types.
    target_address (str): The Ethereum address of the target.

 Methods:
    __init__(amount: int, receiver: Address, avatar: Address): Initializes the method with the given amount, receiver, and avatar.
 """
 name = "withdraw"
 in_signature = [("amount", "uint256"), ("receiver", "address"), ("avatar", "address")]
 target_address = ETHAddr.stkAURABAL

 def __init__(self, amount: int, receiver: Address, avatar: Address):
    super().__init__()
    self.args.amount = amount
    self.args.receiver = receiver
    self.args.avatar = avatar

class CompounderRedeem(ContractMethod):
 """
 A class for compounder redeem.

 Attributes:
   name (str): The name of the method.
   in_signature (list): A list of tuples containing the method's input parameters and their types.
   target_address (str): The Ethereum address of the target.

 Methods:
   __init__(amount: int, receiver: Address, avatar: Address): Initializes the method with the given amount, receiver, and avatar.
 """
 name = "redeem"
 in_signature = [("amount", "uint256"), ("receiver", "address"), ("avatar", "address")]
 target_address = ETHAddr.stkAURABAL

 def __init__(self, amount: int, receiver: Address, avatar: Address):
   super().__init__()
   self.args.amount = amount
   self.args.receiver = receiver
   self.args.avatar = avatar



class LockAURA(ContractMethod):
 """
 A class to lock aura.

 Attributes:
   name (str): The name of the method.
   in_signature (list): A list of tuples containing the method's input parameters and their types.
   target_address (str): The Ethereum address of the target.

 Methods:
   __init__(receiver: Address, amount: int): Initializes the method with the given receiver and amount.
 """
 name = "lock"
 in_signature = [("receiver", "address"), ("amount", "uint256")]
 target_address = ETHAddr.AURALocker

 def __init__(self, receiver: Address, amount: int):
   super().__init__()
   self.args.receiver = receiver
   self.args.amount = amount


class ProcessExpiredLocks(ContractMethod):
 """
 A class to process expired locks.

 Attributes:
   name (str): The name of the method.
   in_signature (list): A list of tuples containing the method's input parameters and their types.
   target_address (str): The Ethereum address of the target.

 Methods:
   __init__(relock: bool): Initializes the method with the given relock status.
 """
 name = "processExpiredLocks"
 in_signature = [("relock", "bool")]
 target_address = ETHAddr.AURALocker

 def __init__(self, relock: bool):
   super().__init__()
   self.args.relock = relock

