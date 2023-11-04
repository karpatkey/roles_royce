from roles_royce.constants import ZERO, MAX_UINT256
from defabipedia.types import Blockchain, Chains
from roles_royce.protocols.base import Address
from web3 import Web3
from decimal import Decimal
from roles_royce.protocols.balancer.types_and_enums import ComposableStablePoolExitKind, StablePoolExitKind, \
    StablePoolv2ExitKind
from .utils import Pool
from .contract_methods import Exit
from .types_and_enums import PoolKind


class _ExactBptSingleTokenExit(Exit):
   """
   A class representing a single asset exit where the user sends a precise quantity of BPT, and receives an estimated but 
   unknown (computed at run time) quantity of a single token.

   Attributes
   ----------
   user_data_abi : list
       A list of uint256 representing the ABI of the user data.
   exit_kind : ComposableStablePoolExitKind or StablePoolExitKind
       The kind of exit, determined by the pool kind.

   Methods
   -------
   __init__(blockchain, pool_kind, pool_id, avatar, assets, bpt_amount_in, exit_token_index, min_amounts_out)
       The constructor for the _ExactBptSingleTokenExit class.
   """

   user_data_abi = ['uint256', 'uint256', 'uint256']

   def __init__(self,
                blockchain: Blockchain,
                pool_kind: PoolKind,
                pool_id: str,
                avatar: Address,
                assets: list[Address],
                bpt_amount_in: int,
                exit_token_index: int,
                min_amounts_out: list[int]):
       """
       Constructs all the necessary attributes for the _ExactBptSingleTokenExit object.

       Parameters
       ----------
       blockchain : Blockchain
           The blockchain instance.
       pool_kind : PoolKind
           The kind of pool.
       pool_id : str
           The id of the pool.
       avatar : Address
           The avatar address.
       assets : list[Address]
           A list of addresses of the assets.
       bpt_amount_in : int
           The amount of BPT to be sent by the user.
       exit_token_index : int
           The index of the token to be received by the user.
       min_amounts_out : list[int]
           The minimum amounts of tokens to be received by the user.
       """

       if pool_kind == PoolKind.ComposableStablePool:
           self.exit_kind = ComposableStablePoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT
       else:
           self.exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT

       super().__init__(blockchain=blockchain,
                       pool_id=pool_id,
                       avatar=avatar,
                       assets=assets,
                       min_amounts_out=min_amounts_out,
                       user_data=[self.exit_kind, bpt_amount_in, exit_token_index])


class ExactBptSingleTokenExit(_ExactBptSingleTokenExit):
   """
   A class representing a single asset exit where the user sends a precise quantity of BPT, and receives an estimated but 
   unknown (computed at run time) quantity of a single token. This class is a subclass of _ExactBptSingleTokenExit.

   Attributes
   ----------
   w3 : Web3
       The Web3 instance.
   pool_id : str
       The id of the pool.
   avatar : Address
       The avatar address.
   bpt_amount_in : int
       The amount of BPT to be sent by the user.
   token_out_address : Address
       The address of the token to be received by the user.
   min_amount_out : int
       The minimum amount of token to be received by the user.
   assets : list[Address]
       A list of addresses of the assets.

   Methods
   -------
   __init__(w3, pool_id, avatar, bpt_amount_in, token_out_address, min_amount_out, assets=None)
       The constructor for the ExactBptSingleTokenExit class.
   """

   def __init__(self,
                w3: Web3,
                pool_id: str,
                avatar: Address,
                bpt_amount_in: int,
                token_out_address: Address,
                min_amount_out: int,
                assets: list[Address] = None):
       """
       Constructs all the necessary attributes for the ExactBptSingleTokenExit object.

       Parameters
       ----------
       w3 : Web3
           The Web3 instance.
       pool_id : str
           The id of the pool.
       avatar : Address
           The avatar address.
       bpt_amount_in : int
           The amount of BPT to be sent by the user.
       token_out_address : Address
           The address of the token to be received by the user.
       min_amount_out : int
           The minimum amount of token to be received by the user.
       assets : list[Address], optional
           A list of addresses of the assets. If not provided, it will be fetched from the pool.
       """

       if assets is None:
           assets = Pool(w3, pool_id).assets()
       pool_kind = Pool(w3, pool_id).pool_kind()
       exit_token_index = assets.index(token_out_address)
       min_amounts_out = [0] * exit_token_index + [min_amount_out] + [0] * (
               len(assets) - exit_token_index - 1)

       super().__init__(blockchain=Chains.get_blockchain_from_web3(w3),
                       pool_kind=pool_kind,
                       pool_id=pool_id,
                       avatar=avatar,
                       assets=assets,
                       bpt_amount_in=bpt_amount_in,
                       exit_token_index=exit_token_index,
                       min_amounts_out=min_amounts_out)


class _ExactBptProportionalExit(Exit):
  """
  A class representing a proportional exit where the user sends a precise quantity of BPT, and receives an estimated but 
  unknown (computed at run time) quantities of all tokens.

  Attributes
  ----------
  user_data_abi : list
      A list of uint256 representing the ABI of the user data.
  exit_kind : ComposableStablePoolExitKind or StablePoolExitKind
      The kind of exit, determined by the pool kind.

  Methods
  -------
  __init__(blockchain, pool_kind, pool_id, avatar, assets, bpt_amount_in, min_amounts_out)
      The constructor for the _ExactBptProportionalExit class.
  """

  user_data_abi = ['uint256', 'uint256']

  def __init__(self,
               blockchain: Blockchain,
               pool_kind: PoolKind,
               pool_id: str,
               avatar: Address,
               assets: list[Address],
               bpt_amount_in: int,
               min_amounts_out: list[int]):
      """
      Constructs all the necessary attributes for the _ExactBptProportionalExit object.

      Parameters
      ----------
      blockchain : Blockchain
          The blockchain instance.
      pool_kind : PoolKind
          The kind of pool.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      assets : list[Address]
          A list of addresses of the assets.
      bpt_amount_in : int
          The amount of BPT to be sent by the user.
      min_amounts_out : list[int]
          The minimum amounts of tokens to be received by the user.
      """

      if pool_kind == PoolKind.ComposableStablePool:
          exit_kind = ComposableStablePoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT
      else:
          exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT

      super().__init__(blockchain=blockchain,
                     pool_id=pool_id,
                     avatar=avatar,
                     assets=assets,
                     min_amounts_out=min_amounts_out,
                     user_data=[exit_kind, bpt_amount_in])


class ExactBptProportionalExit(_ExactBptProportionalExit):
  """
  A class representing a proportional exit where the user sends a precise quantity of BPT, and receives an estimated but 
  unknown (computed at run time) quantities of all tokens. This class is a subclass of _ExactBptProportionalExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  avatar : Address
      The avatar address.
  bpt_amount_in : int
      The amount of BPT to be sent by the user.
  min_amounts_out : list[int]
      The minimum amounts of tokens to be received by the user.
  assets : list[Address]
      A list of addresses of the assets.

  Methods
  -------
  __init__(w3, pool_id, avatar, bpt_amount_in, min_amounts_out, assets=None)
      The constructor for the ExactBptProportionalExit class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               avatar: Address,
               bpt_amount_in: int,
               min_amounts_out: list[int],
               assets: list[Address] = None):
      """
      Constructs all the necessary attributes for the ExactBptProportionalExit object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      bpt_amount_in : int
          The amount of BPT to be sent by the user.
      min_amounts_out : list[int]
          The minimum amounts of tokens to be received by the user.
      assets : list[Address], optional
          A list of addresses of the assets. If not provided, it will be fetched from the pool.
      """

      if assets is None:
          assets = Pool(w3, pool_id).assets()
      pool_kind = Pool(w3, pool_id).pool_kind()

      super().__init__(blockchain=Chains.get_blockchain_from_web3(w3),
                     pool_kind=pool_kind,
                     pool_id=pool_id,
                     avatar=avatar,
                     assets=assets,
                     bpt_amount_in=bpt_amount_in,
                     min_amounts_out=min_amounts_out)

class _ExactTokensExit(Exit):
 """
 A class representing a custom exit where the user sends an estimated but unknown (computed at run time) quantity of BPT, 
 and receives precise quantities of specified tokens.

 Attributes
 ----------
 user_data_abi : list
     A list of uint256 representing the ABI of the user data.
 exit_kind : ComposableStablePoolExitKind or StablePoolExitKind
     The kind of exit, determined by the pool kind.

 Methods
 -------
 __init__(blockchain, pool_kind, pool_id, avatar, assets, amounts_out, max_bpt_amount_in)
     The constructor for the _ExactTokensExit class.
 """

 user_data_abi = ['uint256', 'uint256[]', 'uint256']

 def __init__(self,
              blockchain: Blockchain,
              pool_kind: PoolKind,
              pool_id: str,
              avatar: Address,
              assets: list[Address],
              amounts_out: list[int],
              max_bpt_amount_in: int):
     """
     Constructs all the necessary attributes for the _ExactTokensExit object.

     Parameters
     ----------
     blockchain : Blockchain
         The blockchain instance.
     pool_kind : PoolKind
         The kind of pool.
     pool_id : str
         The id of the pool.
     avatar : Address
         The avatar address.
     assets : list[Address]
         A list of addresses of the assets.
     amounts_out : list[int]
         The amounts of each token to be withdrawn from the pool.
     max_bpt_amount_in : int
         The minimum acceptable BPT to burn in return for withdrawn tokens.
     """

     if pool_kind == PoolKind.ComposableStablePool:
         exit_kind = ComposableStablePoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT
     else:
         exit_kind = StablePoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT

     super().__init__(blockchain=blockchain,
                   pool_id=pool_id,
                   avatar=avatar,
                   assets=assets,
                   min_amounts_out=amounts_out,
                   user_data=[exit_kind, amounts_out, max_bpt_amount_in])


class ExactTokensExit(_ExactTokensExit):
  """
  A class representing a custom exit where the user sends an estimated but unknown (computed at run time) quantity of BPT, 
  and receives precise quantities of specified tokens. This class is a subclass of _ExactTokensExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  avatar : Address
      The avatar address.
  amounts_out : list[int]
      The amounts of each token to be withdrawn from the pool.
  max_bpt_amount_in : int
      The minimum acceptable BPT to burn in return for withdrawn tokens.
  assets : list[Address]
      A list of addresses of the assets.

  Methods
  -------
  __init__(w3, pool_id, avatar, amounts_out, max_bpt_amount_in, assets=None)
      The constructor for the ExactTokensExit class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               avatar: Address,
               amounts_out: list[int],
               max_bpt_amount_in: int,
               assets: list[Address] = None):
      """
      Constructs all the necessary attributes for the ExactTokensExit object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      amounts_out : list[int]
          The amounts of each token to be withdrawn from the pool.
      max_bpt_amount_in : int
          The minimum acceptable BPT to burn in return for withdrawn tokens.
      assets : list[Address], optional
          A list of addresses of the assets. If not provided, it will be fetched from the pool.
      """

      if assets is None:
          assets = Pool(w3, pool_id).assets()
      pool_kind = Pool(w3, pool_id).pool_kind()

      super().__init__(blockchain=Chains.get_blockchain_from_web3(w3),
                     pool_kind=pool_kind,
                     pool_id=pool_id,
                     avatar=avatar,
                     assets=assets,
                     amounts_out=amounts_out,
                     max_bpt_amount_in=max_bpt_amount_in)



class ExactSingleTokenExit(ExactTokensExit):
  """
  A class representing a single token exit where the user sends an estimated but unknown (computed at run time) quantity of BPT, 
  and receives a precise quantity of a specified token. This class is a subclass of ExactTokensExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  avatar : Address
      The avatar address.
  token_out_address : Address
      The address of the token to be received by the user.
  amount_out : int
      The amount of token to be received by the user.
  max_bpt_amount_in : int
      The maximum acceptable BPT to burn in return for withdrawn tokens.
  assets : list[Address]
      A list of addresses of the assets.

  Methods
  -------
  __init__(w3, pool_id, avatar, token_out_address, amount_out, max_bpt_amount_in, assets=None)
      The constructor for the ExactSingleTokenExit class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               avatar: Address,
               token_out_address: Address,
               amount_out: int,
               max_bpt_amount_in: int,
               assets: list[Address] = None):
      """
      Constructs all the necessary attributes for the ExactSingleTokenExit object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      token_out_address : Address
          The address of the token to be received by the user.
      amount_out : int
          The amount of token to be received by the user.
      max_bpt_amount_in : int
          The maximum acceptable BPT to burn in return for withdrawn tokens.
      assets : list[Address], optional
          A list of addresses of the assets. If not provided, it will be fetched from the pool.
      """

      if assets is None:
          assets = Pool(w3, pool_id).assets()

      exit_token_index = assets.index(token_out_address)
      amounts_out = [0] * exit_token_index + [amount_out] + [0] * (len(assets) - exit_token_index - 1)

      super().__init__(w3=w3,
                     pool_id=pool_id,
                     avatar=avatar,
                     amounts_out=amounts_out,
                     max_bpt_amount_in=max_bpt_amount_in,
                     assets=assets)


class _ExactBptRecoveryModeExit(Exit):
  """
  A class representing a recovery mode exit where the user sends a precise quantity of BPT, 
  and receives an estimated but unknown (computed at run time) quantities of all tokens.

  Attributes
  ----------
  user_data_abi : list
      A list of uint256 representing the ABI of the user data.
  exit_kind : StablePoolv2ExitKind
      The kind of exit, determined by the StablePoolv2ExitKind.

  Methods
  -------
  __init__(blockchain, pool_id, avatar, assets, bpt_amount_in, min_amounts_out)
      The constructor for the _ExactBptRecoveryModeExit class.
  """

  user_data_abi = ['uint256', 'uint256']

  def __init__(self,
               blockchain: Blockchain,
               pool_id: str,
               avatar: Address,
               assets: list[Address],
               bpt_amount_in: int,
               min_amounts_out: list[int]):
      """
      Constructs all the necessary attributes for the _ExactBptRecoveryModeExit object.

      Parameters
      ----------
      blockchain : Blockchain
          The blockchain instance.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      assets : list[Address]
          A list of addresses of the assets.
      bpt_amount_in : int
          The amount of BPT to be sent by the user.
      min_amounts_out : list[int]
          The minimum amounts of tokens to be received by the user.
      """

      exit_kind = StablePoolv2ExitKind.RECOVERY_MODE_EXIT_KIND

      super().__init__(blockchain=blockchain,
                     pool_id=pool_id,
                     avatar=avatar,
                     assets=assets,
                     min_amounts_out=min_amounts_out,
                     user_data=[exit_kind, bpt_amount_in])


class ExactBptRecoveryModeExit(_ExactBptRecoveryModeExit):
  """
  A class representing a recovery mode exit where the user sends a precise quantity of BPT, 
  and receives an estimated but unknown (computed at run time) quantities of all tokens. 
  This class is a subclass of _ExactBptRecoveryModeExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  avatar : Address
      The avatar address.
  bpt_amount_in : int
      The amount of BPT to be sent by the user.
  assets : list[Address]
      A list of addresses of the assets.

  Methods
  -------
  __init__(w3, pool_id, avatar, bpt_amount_in, assets=None)
      The constructor for the ExactBptRecoveryModeExit class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               avatar: Address,
               bpt_amount_in: int,
               assets: list[Address] = None):
      """
      Constructs all the necessary attributes for the ExactBptRecoveryModeExit object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      bpt_amount_in : int
          The amount of BPT to be sent by the user.
      assets : list[Address], optional
          A list of addresses of the assets. If not provided, it will be fetched from the pool.
      """

      if assets is None:
          assets = Pool(w3, pool_id).assets()

      min_amounts_out = [0] * len(assets)

      super().__init__(blockchain=Chains.get_blockchain_from_web3(w3),
                     pool_id=pool_id,
                     avatar=avatar,
                     assets=assets,
                     bpt_amount_in=bpt_amount_in,
                     min_amounts_out=min_amounts_out)


# -----------------------------------------------------------------------------------------------------------------------
# Query Exit


class QueryExitMixin:
  """
  A mixin class for query exit functionality.

  Attributes
  ----------
  name : str
      The name of the mixin.
  out_signature : list
      A list of strings representing the signature of the output.

  """

  name = "queryExit"
  out_signature = [("bpt_in", "uint256"), ("amounts_out", "uint256[]")]


class ExactBptSingleTokenQueryExit(QueryExitMixin, ExactBptSingleTokenExit):
  """
  A class representing a single token exit query where the user sends a precise quantity of BPT, 
  and receives a precise quantity of a specified token. This class is a subclass of QueryExitMixin and ExactBptSingleTokenExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  bpt_amount_in : int
      The amount of BPT to be sent by the user.
  token_out_address : Address
      The address of the token to be received by the user.

  Methods
  -------
  __init__(w3, pool_id, bpt_amount_in, token_out_address)
      The constructor for the ExactBptSingleTokenQueryExit class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               bpt_amount_in: int,
               token_out_address: Address):
      """
      Constructs all the necessary attributes for the ExactBptSingleTokenQueryExit object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      bpt_amount_in : int
          The amount of BPT to be sent by the user.
      token_out_address : Address
          The address of the token to be received by the user.
      """

      super().__init__(w3=w3,
                     pool_id=pool_id,
                     avatar=ZERO,
                     bpt_amount_in=bpt_amount_in,
                     token_out_address=token_out_address,
                     min_amount_out=0)



class ExactBptProportionalQueryExit(QueryExitMixin, ExactBptProportionalExit):
  """
  A class representing a proportional exit query where the user sends a precise quantity of BPT, 
  and receives an estimated but unknown (computed at run time) quantities of all tokens. 
  This class is a subclass of QueryExitMixin and ExactBptProportionalExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  bpt_amount_in : int
      The amount of BPT to be sent by the user.
  assets : list[Address]
      A list of addresses of the assets.

  Methods
  -------
  __init__(w3, pool_id, bpt_amount_in, assets=None)
      The constructor for the ExactBptProportionalQueryExit class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               bpt_amount_in: int,
               assets: list[Address] = None):
      """
      Constructs all the necessary attributes for the ExactBptProportionalQueryExit object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      bpt_amount_in : int
          The amount of BPT to be sent by the user.
      assets : list[Address], optional
          A list of addresses of the assets. If not provided, it will be fetched from the pool.
      """

      if assets is None:
          assets = Pool(w3, pool_id).assets()

      super().__init__(w3=w3,
                     pool_id=pool_id,
                     avatar=ZERO,
                     bpt_amount_in=bpt_amount_in,
                     min_amounts_out=[0] * len(assets),
                     assets=assets)



class ExactTokensQueryExit(QueryExitMixin, ExactTokensExit):
  """
  A class representing a tokens exit query where the user sends an estimated but unknown (computed at run time) quantity of BPT, 
  and receives precise quantities of specified tokens. This class is a subclass of QueryExitMixin and ExactTokensExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  amounts_out : list[int]
      The amounts of each token to be withdrawn from the pool.
  assets : list[Address]
      A list of addresses of the assets.

  Methods
  -------
  __init__(w3, pool_id, amounts_out, assets=None)
      The constructor for the ExactTokensQueryExit class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               amounts_out: list[int],
               assets: list[Address] = None):
      """
      Constructs all the necessary attributes for the ExactTokensQueryExit object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      amounts_out : list[int]
          The amounts of each token to be withdrawn from the pool.
      assets : list[Address], optional
          A list of addresses of the assets. If not provided, it will be fetched from the pool.
      """

      if assets is None:
          assets = Pool(w3, pool_id).assets()

      super().__init__(w3=w3,
                     pool_id=pool_id,
                     avatar=ZERO,
                     amounts_out=amounts_out,
                     max_bpt_amount_in=MAX_UINT256,
                     assets=assets)


class ExactSingleTokenQueryExit(QueryExitMixin, ExactSingleTokenExit):
  """
  A class representing a single token exit query where the user sends an estimated but unknown (computed at run time) quantity of BPT, 
  and receives a precise quantity of a specified token. This class is a subclass of QueryExitMixin and ExactSingleTokenExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  token_out_address : Address
      The address of the token to be received by the user.
  amount_out : int
      The amount of token to be received by the user.

  Methods
  -------
  __init__(w3, pool_id, token_out_address, amount_out)
      The constructor for the ExactSingleTokenQueryExit class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               token_out_address: Address,
               amount_out: int):
      """
      Constructs all the necessary attributes for the ExactSingleTokenQueryExit object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      token_out_address : Address
          The address of the token to be received by the user.
      amount_out : int
          The amount of token to be received by the user.
      """

      super().__init__(w3=w3,
                     pool_id=pool_id,
                     avatar=ZERO,
                     token_out_address=token_out_address,
                     amount_out=amount_out,
                     max_bpt_amount_in=MAX_UINT256)


# -----------------------------------------------------------------------------------------------------------------------
# The next are the classes ready to be used inputting max slippage

class ExactBptSingleTokenExitSlippage(ExactBptSingleTokenExit):
  """
  A class representing a single token exit with slippage control where the user sends a precise quantity of BPT, 
  and receives a precise quantity of a specified token, with a maximum slippage tolerance.
  This class is a subclass of ExactBptSingleTokenExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  avatar : Address
      The avatar address.
  bpt_amount_in : int
      The amount of BPT to be sent by the user.
  token_out_address : Address
      The address of the token to be received by the user.
  max_slippage : float
      The maximum slippage tolerance.
  assets : list[Address]
      A list of addresses of the assets.

  Methods
  -------
  __init__(w3, pool_id, avatar, bpt_amount_in, token_out_address, max_slippage, assets=None)
      The constructor for the ExactBptSingleTokenExitSlippage class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               avatar: Address,
               bpt_amount_in: int,
               token_out_address: Address,
               max_slippage: float,
               assets: list[Address] = None):
      """
      Constructs all the necessary attributes for the ExactBptSingleTokenExitSlippage object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      bpt_amount_in : int
          The amount of BPT to be sent by the user.
      token_out_address : Address
          The address of the token to be received by the user.
      max_slippage : float
          The maximum slippage tolerance.
      assets : list[Address], optional
          A list of addresses of the assets. If not provided, it will be fetched from the pool.
      """

      if assets is None:
          assets = Pool(w3, pool_id).assets()

      m = ExactBptSingleTokenQueryExit(w3=w3,
                                       pool_id=pool_id,
                                       bpt_amount_in=bpt_amount_in,
                                       token_out_address=token_out_address)
      exit_token_index = assets.index(token_out_address)
      bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)

      if not bpt_amount_in - 1 <= bpt_amount_in_sim <= bpt_amount_in + 1:
          raise ValueError(
              f"The bpt_amount_in = {bpt_amount_in} specified is not the same as the bpt_amount_in = {bpt_amount_in_sim} calculated by the query contract.")

      min_amount_out = int(Decimal(amounts_out_sim[exit_token_index]) * Decimal(1 - max_slippage))

      super().__init__(w3, pool_id, avatar, bpt_amount_in, token_out_address, min_amount_out, assets=assets)


class ExactSingleTokenExitSlippage(ExactSingleTokenExit):
  """
  A class representing a single token exit with slippage control where the user sends an estimated but unknown (computed at run time) quantity of BPT, 
  and receives a precise quantity of a specified token, with a maximum slippage tolerance.
  This class is a subclass of ExactSingleTokenExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  avatar : Address
      The avatar address.
  token_out_address : Address
      The address of the token to be received by the user.
  amount_out : int
      The amount of token to be received by the user.
  max_slippage : float
      The maximum slippage tolerance.

  Methods
  -------
  __init__(w3, pool_id, avatar, token_out_address, amount_out, max_slippage)
      The constructor for the ExactSingleTokenExitSlippage class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               avatar: Address,
               token_out_address: Address,
               amount_out: int,
               max_slippage: float):
      """
      Constructs all the necessary attributes for the ExactSingleTokenExitSlippage object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      token_out_address : Address
          The address of the token to be received by the user.
      amount_out : int
          The amount of token to be received by the user.
      max_slippage : float
          The maximum slippage tolerance.
      """

      m = ExactSingleTokenQueryExit(w3=w3,
                                    pool_id=pool_id,
                                    token_out_address=token_out_address,
                                    amount_out=amount_out)
      assets = Pool(w3, pool_id).assets()
      exit_token_index = assets.index(token_out_address)
      bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)

      if amount_out - 1 <= amounts_out_sim[exit_token_index] <= amount_out + 1:
          raise ValueError(
              f"The amount_out = {amount_out} specified is not the same as the amount_out = {amounts_out_sim[exit_token_index]} calculated by the query contract.")
      max_bpt_amount_in = int(Decimal(bpt_amount_in_sim) * Decimal(1 + max_slippage))

      super().__init__(w3, pool_id, avatar, token_out_address, amount_out, max_bpt_amount_in, assets=assets)


class ExactBptProportionalExitSlippage(ExactBptProportionalExit):
  """
  A class representing a proportional exit with slippage control where the user sends a precise quantity of BPT, 
  and receives an estimated but unknown (computed at run time) quantities of all tokens, with a maximum slippage tolerance.
  This class is a subclass of ExactBptProportionalExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  avatar : Address
      The avatar address.
  bpt_amount_in : int
      The amount of BPT to be sent by the user.
  max_slippage : float
      The maximum slippage tolerance.

  Methods
  -------
  __init__(w3, pool_id, avatar, bpt_amount_in, max_slippage)
      The constructor for the ExactBptProportionalExitSlippage class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               avatar: Address,
               bpt_amount_in: int,
               max_slippage: float):
      """
      Constructs all the necessary attributes for the ExactBptProportionalExitSlippage object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      bpt_amount_in : int
          The amount of BPT to be sent by the user.
      max_slippage : float
          The maximum slippage tolerance.
      """

      m = ExactBptProportionalQueryExit(w3=w3,
                                        pool_id=pool_id,
                                        bpt_amount_in=bpt_amount_in)

      bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)

      if not bpt_amount_in - 1 <= bpt_amount_in_sim <= bpt_amount_in + 1:
          raise ValueError(
              f"The bpt_amount_in = {bpt_amount_in} specified is not the same as the bpt_amount_in = {bpt_amount_in_sim} calculated by the query contract.")

      min_amounts_out = [int(Decimal(amount) * Decimal(1 - max_slippage)) for amount in amounts_out_sim]

      super().__init__(w3, pool_id, avatar, bpt_amount_in, min_amounts_out)

class ExactTokensExitSlippage(ExactTokensExit):
  """
  A class representing a tokens exit with slippage control where the user sends an estimated but unknown (computed at run time) quantity of BPT, 
  and receives precise quantities of specified tokens, with a maximum slippage tolerance.
  This class is a subclass of ExactTokensExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  avatar : Address
      The avatar address.
  amounts_out : list[int]
      The amounts of each token to be withdrawn from the pool.
  max_slippage : float
      The maximum slippage tolerance.

  Methods
  -------
  __init__(w3, pool_id, avatar, amounts_out, max_slippage)
      The constructor for the ExactTokensExitSlippage class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               avatar: Address,
               amounts_out: list[int],
               max_slippage: float):
      """
      Constructs all the necessary attributes for the ExactTokensExitSlippage object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      amounts_out : list[int]
          The amounts of each token to be withdrawn from the pool.
      max_slippage : float
          The maximum slippage tolerance.
      """

      m = ExactTokensQueryExit(w3=w3,
                               pool_id=pool_id,
                               amounts_out=amounts_out)
      bpt_in, amounts_out_sim = m.call(web3=w3)

      # If the pool is composable stable, remove the amount corresponding to the bpt
      pool_kind = Pool(w3, pool_id).pool_kind()
      if pool_kind == PoolKind.ComposableStablePool:
          bpt_index = Pool(w3, pool_id).bpt_index_from_composable()
          del amounts_out_sim[bpt_index]

      for index in range(len(amounts_out)):
          if not amounts_out[index] - 1 <= amounts_out_sim[index] <= amounts_out[index] + 1:
              raise ValueError(
                  f"The amounts_out = {amounts_out} specified are not the same as the amounts_out = {amounts_out_sim} calculated by the query contract.")

      max_bpt_amount_in = int(Decimal(bpt_in) * Decimal(1 + max_slippage))

      super().__init__(w3, pool_id, avatar, amounts_out, max_bpt_amount_in)

class ExactSingleTokenProportionalExitSlippage(ExactTokensExit):
  """
  A class representing a single token proportional exit with slippage control where the user sends an estimated but unknown (computed at run time) quantity of BPT, 
  and receives a precise quantity of a specified token proportional to the pool's balances, with a maximum slippage tolerance.
  This class is a subclass of ExactTokensExit.

  Attributes
  ----------
  w3 : Web3
      The Web3 instance.
  pool_id : str
      The id of the pool.
  avatar : Address
      The avatar address.
  token_out_address : Address
      The address of the token to be received by the user.
  amount_out : int
      The amount of token to be received by the user.
  max_slippage : float
      The maximum slippage tolerance.
  assets : list[Address]
      A list of addresses of the assets.

  Methods
  -------
  __init__(w3, pool_id, avatar, token_out_address, amount_out, max_slippage, assets=None)
      The constructor for the ExactSingleTokenProportionalExitSlippage class.
  """

  def __init__(self,
               w3: Web3,
               pool_id: str,
               avatar: Address,
               token_out_address: Address,
               amount_out: int,
               max_slippage: float,
               assets: list[Address] = None):
      """
      Constructs all the necessary attributes for the ExactSingleTokenProportionalExitSlippage object.

      Parameters
      ----------
      w3 : Web3
          The Web3 instance.
      pool_id : str
          The id of the pool.
      avatar : Address
          The avatar address.
      token_out_address : Address
          The address of the token to be received by the user.
      amount_out : int
          The amount of token to be received by the user.
      max_slippage : float
          The maximum slippage tolerance.
      assets : list[Address], optional
          A list of addresses of the assets. If not provided, it will be fetched from the pool.
      """

      if assets is None:
          assets = Pool(w3, pool_id).assets()

      token_index = assets.index(token_out_address)
      balances = Pool(w3, pool_id).pool_balances()

      # Get the corresponding proportional amounts out
      amounts_out = [int(Decimal(balance) * Decimal(amount_out) / Decimal(balances[token_index])) for balance in
                     balances]

      # If the pool is composable stable, remove the amount corresponding to the bpt
      pool_kind = Pool(w3, pool_id).pool_kind()
      if pool_kind == PoolKind.ComposableStablePool:
          bpt_index = Pool(w3, pool_id).bpt_index_from_composable()
          del amounts_out[bpt_index]

      m = ExactTokensQueryExit(w3=w3,
                               pool_id=pool_id,
                               amounts_out=amounts_out)

      bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)
      if not amount_out - 1 <= amounts_out_sim[token_index] <= amount_out + 1:
          raise ValueError(
              f"The amount_out = {amount_out} specified is not the same as the amount_out = {amounts_out_sim[token_index]} calculated by the query contract.")

      max_bpt_amount_in = int(Decimal(bpt_amount_in_sim) * Decimal(1 + max_slippage))

      super().__init__(w3, pool_id, avatar, amounts_out, max_bpt_amount_in, assets=assets)
