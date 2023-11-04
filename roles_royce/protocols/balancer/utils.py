from web3 import Web3
from defabipedia.types import Chains
from defabipedia.balancer import ContractSpecs, Abis
from web3.exceptions import ContractLogicError
from .types_and_enums import PoolKind


class Pool:
 """
 Pool is a class that represents a pool in a blockchain network.
 It provides methods to interact with the pool, like getting the kind of pool, the assets of a pool, the token balances of a pool, the BPT index of a composable pool, and the BPT balance of an address.

 Attributes
 ----------
 w3 : Web3
   An instance of Web3, representing the blockchain network.
 pool_id : str
   A string representing the ID of the pool.
 vault_contract : Contract
   An instance of Contract, representing the vault contract in the blockchain network.
 bpt_contract : Contract
   An instance of Contract, representing the BPT contract in the blockchain network.

 Methods
 -------
 __init__(w3, pool_id)
   The constructor for the Pool class.
 pool_kind()
   Returns the kind of pool.
 assets()
   Returns the assets of a pool given a pool id.
 pool_balances()
   Returns the token balances of a pool given a pool id.
 bpt_index_from_composable()
   Returns the BPT index of a composable pool given a pool id.
 bpt_balance(address)
   Returns the BPT balance of an address.
 """

 def __init__(self, w3: Web3, pool_id: str):
   """
   Constructs all the necessary attributes for the Pool object.

   Parameters
   ----------
   w3 : Web3
       An instance of Web3, representing the blockchain network.
   pool_id : str
       A string representing the ID of the pool.
   """

   self.w3 = w3
   self.pool_id = pool_id
   blockchain = Chains.get_blockchain_from_web3(self.w3)
   self.vault_contract = ContractSpecs[blockchain].Vault.contract(self.w3)
   bpt_address = self.vault_contract.functions.getPool(self.pool_id).call()[0]
   self.bpt_contract = self.w3.eth.contract(address=bpt_address, abi=Abis[blockchain].UniversalBPT.abi)

 def pool_kind(self) -> PoolKind:
   """
   Returns the kind of pool.

   Returns
   -------
   PoolKind
       An instance of PoolKind, representing the kind of the pool.
   """

   try:
       self.bpt_contract.functions.getNormalizedWeights().call()
       return PoolKind.WeightedPool
   except ContractLogicError:
       try:
           self.bpt_contract.functions.getBptIndex().call()
           return PoolKind.ComposableStablePool
       except ContractLogicError:
           try:
               self.bpt_contract.functions.inRecoveryMode().call()
               return PoolKind.StablePool
           except ContractLogicError:
               return PoolKind.MetaStablePool

 def assets(self) -> list[str]:
   """
   Returns the assets of a pool given a pool id.

   Returns
   -------
   list[str]
       A list of strings, representing the assets of the pool.
   """

   return self.vault_contract.functions.getPoolTokens(self.pool_id).call()[0]

 def pool_balances(self) -> list[int]:
   """
   Returns the token balances of a pool given a pool id.

   Returns
   -------
   list[int]
       A list of integers, representing the token balances of the pool.
   """

   return self.vault_contract.functions.getPoolTokens(self.pool_id).call()[1]

 def bpt_index_from_composable(self) -> int:
   """
   Returns the BPT index of a composable pool given a pool id.

   Returns
   -------
   int
       An integer representing the BPT index of the pool.
   """

   pool_kind = self.pool_kind()
   if pool_kind != PoolKind.ComposableStablePool:
        raise ValueError("Pool is not a composable stable pool")
   else:

        return self.bpt_contract.functions.getBptIndex().call()

 def bpt_balance(self, address: str) -> int:
    return self.bpt_contract.functions.balanceOf(address).call()
