from roles_royce.constants import CrossChainAddr
from defabipedia.types import Chains
from roles_royce.protocols.base import BaseApproveForToken
from web3 import Web3
from roles_royce.protocols.base import Address
from .contract_methods import StakeInGauge, UnstakeFromGauge


class ApproveForVault(BaseApproveForToken):
  """
  A class representing the approval of a token to be spent by BalancerVault.
  This class is a subclass of BaseApproveForToken.

  Attributes
  ----------
  fixed_arguments : dict
      The fixed arguments for the approval.

  Methods
  -------
  __init__()
      The constructor for the ApproveForVault class.
  """

  fixed_arguments = {"spender": CrossChainAddr.BalancerVault}

class Stake(StakeInGauge):
  """
  A class representing the staking of a token in a gauge.
  This class is a subclass of StakeInGauge.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  gauge_address : Address
      The address of the gauge.
  amount : int
      The amount of token to be staked.

  Methods
  -------
  __init__(w3, gauge_address, amount)
      The constructor for the Stake class.
  """

  def __init__(self,
               w3: Web3,
               gauge_address: Address,
               amount: int):
      """
      Constructs all the necessary attributes for the Stake object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      gauge_address : Address
          The address of the gauge.
      amount : int
          The amount of token to be staked.
      """

      super().__init__(blockchain=Chains.get_blockchain_from_web3(w3),
                       gauge_address=gauge_address,
                       amount=amount)

class Unstake(UnstakeFromGauge):
  """
  A class representing the unstaking of a token from a gauge.
  This class is a subclass of UnstakeFromGauge.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  gauge_address : Address
      The address of the gauge.
  amount : int
      The amount of token to be unstaked.

  Methods
  -------
  __init__(w3, gauge_address, amount)
      The constructor for the Unstake class.
  """

  def __init__(self,
               w3: Web3,
               gauge_address: Address,
               amount: int):
      """
      Constructs all the necessary attributes for the Unstake object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      gauge_address : Address
          The address of the gauge.
      amount : int
          The amount of token to be unstaked.
      """

      super().__init__(blockchain=Chains.get_blockchain_from_web3(w3),
                       gauge_address=gauge_address,
                       amount=amount)
