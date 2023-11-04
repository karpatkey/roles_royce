from roles_royce.constants import MAX_UINT256
from defabipedia.types import Blockchain, Chains
from roles_royce.protocols.base import ContractMethod, AvatarAddress, Address
from roles_royce.protocols.balancer.types_and_enums import SwapKind
from web3 import Web3
from defabipedia.balancer import ContractSpecs

class SingleSwap(ContractMethod):
 """
 SingleSwap is a class that inherits from ContractMethod.
 It represents a single swap operation in a smart contract.

 Attributes
 ----------
 target_address : Address
    The address of the smart contract to be interacted with.
 name : str
    The name of the function to be called in the smart contract.
 in_signature : tuple
    The input signature of the function to be called in the smart contract.
 fixed_arguments : dict
    The arguments that remain constant across all function calls.

 Methods
 -------
 __init__(blockchain, pool_id, avatar, swap_kind, token_in_address, token_out_address, amount, limit)
 The constructor for the SingleSwap class.
"""
 target_address = None
 name = "swap"
 in_signature = (
        ("single_swap", (
            (
                ("pool_id", "bytes32"),
                ("kind", "uint8"),
                ("asset_in", "address"),
                ("asset_out", "address"),
                ("amount", "uint256"),
                ("user_data", "bytes"),
            ),
            "tuple"),
         ),
        ("funds", (
            (
                ("sender", "address"),
                ("from_internal_balance", "bool"),
                ("recipient", "address"),
                ("to_internal_balance", "bool")
            ),
            "tuple"),
         ),
        ("limit", "uint256"),
        ("deadline", "uint256")
    )
 fixed_arguments = {"sender": AvatarAddress, "recipient": AvatarAddress, "from_internal_balance": False,
                       "to_internal_balance": False, "user_data": "0x", "deadline": MAX_UINT256}
    
 def __init__(self,
     blockchain: Blockchain,
     pool_id: str,
     avatar: Address,
     swap_kind: SwapKind,
     token_in_address: Address,
     token_out_address: Address,
     amount: int,
     limit: int):
     """
     Constructs all the necessary attributes for the SingleSwap object.

        Parameters
        ----------
        blockchain : Blockchain
        An instance of Blockchain, representing the blockchain network.
     pool_id : str
            A string representing the ID of the pool.
     avatar : Address
       An instance of Address, representing the avatar of the pool.
     swap_kind : SwapKind
       An instance of SwapKind, representing the type of the swap.
     token_in_address : Address
       An instance of Address, representing the address of the input token.
     token_out_address : Address
       An instance of Address, representing the address of the output token.
     amount : int
       An integer representing the amount of the input token.
     limit : int
       An integer representing the maximum amount of the output token to be received.
     """

     self.target_address = ContractSpecs[blockchain].Vault.address
     super().__init__(avatar=avatar)
     self.args.single_swap["pool_id"] = pool_id
     self.args.single_swap["kind"] = swap_kind
     self.args.single_swap["asset_in"] = token_in_address
     self.args.single_swap["asset_out"] = token_out_address
     self.args.single_swap["amount"] = amount
     self.args.single_swap["user_data"] = self.fixed_arguments["user_data"]
     self.args.funds = [self.fixed_arguments["sender"], self.fixed_arguments["from_internal_balance"],
                      self.fixed_arguments["recipient"], self.fixed_arguments["to_internal_balance"]]
     self.args.deadline = self.fixed_arguments["deadline"]
     self.args.limit = limit


class ExactTokenInSingleSwap(SingleSwap):
 """
 ExactTokenInSingleSwap is a class that inherits from SingleSwap.
 It represents a single swap operation with a specified exact input token amount.

 Attributes
 ----------
 w3 : Web3
   An instance of Web3, used for interacting with the Ethereum blockchain.
 pool_id : str
   A string representing the ID of the pool.
 avatar : Address
   An instance of Address, representing the avatar of the pool.
 token_in_address : Address
   An instance of Address, representing the address of the input token.
 token_out_address : Address
   An instance of Address, representing the address of the output token.
 amount_in : int
   An integer representing the exact amount of the input token.
 min_amount_out : int
   An integer representing the minimum amount of the output token to be received.

 Methods
 -------
 __init__(w3, pool_id, avatar, token_in_address, token_out_address, amount_in, min_amount_out)
   The constructor for the ExactTokenInSingleSwap class.
 """

 def __init__(self,
            w3: Web3,
            pool_id: str,
            avatar: Address,
            token_in_address: Address,
            token_out_address: Address,
            amount_in: int,
            min_amount_out: int):
   """
   Constructs all the necessary attributes for the ExactTokenInSingleSwap object.

   Parameters
   ----------
   w3 : Web3
       An instance of Web3, used for interacting with the Ethereum blockchain.
   pool_id : str
       A string representing the ID of the pool.
   avatar : Address
       An instance of Address, representing the avatar of the pool.
   token_in_address : Address
       An instance of Address, representing the address of the input token.
   token_out_address : Address
       An instance of Address, representing the address of the output token.
   amount_in : int
       An integer representing the exact amount of the input token.
   min_amount_out : int
       An integer representing the minimum amount of the output token to be received.
   """

   swap_kind = SwapKind.OutGivenExactIn
   super().__init__(blockchain=Chains.get_blockchain_by_chain_id(w3),
                    pool_id=pool_id,
                    avatar=avatar,
                    swap_kind=swap_kind,
                    token_in_address=token_in_address,
                    token_out_address=token_out_address,
                    amount=amount_in,
                    limit=min_amount_out)

class ExactTokenOutSingleSwap(SingleSwap):
 """
 ExactTokenOutSingleSwap is a class that inherits from SingleSwap.
 It represents a single swap operation with a specified exact output token amount.

 Attributes
 ----------
 w3 : Web3
   An instance of Web3, used for interacting with the Ethereum blockchain.
 pool_id : str
   A string representing the ID of the pool.
 avatar : Address
   An instance of Address, representing the avatar of the pool.
 token_in_address : Address
   An instance of Address, representing the address of the input token.
 token_out_address : Address
   An instance of Address, representing the address of the output token.
 amount_out : int
   An integer representing the exact amount of the output token.
 max_amount_in : int
   An integer representing the maximum amount of the input token to be used.

 Methods
 -------
 __init__(w3, pool_id, avatar, token_in_address, token_out_address, amount_out, max_amount_in)
   The constructor for the ExactTokenOutSingleSwap class.
 """

 def __init__(self,
            w3: Web3,
            pool_id: str,
            avatar: Address,
            token_in_address: Address,
            token_out_address: Address,
            amount_out: int,
            max_amount_in: int):
   """
   Constructs all the necessary attributes for the ExactTokenOutSingleSwap object.

   Parameters
   ----------
   w3 : Web3
       An instance of Web3, used for interacting with the Ethereum blockchain.
   pool_id : str
       A string representing the ID of the pool.
   avatar : Address
       An instance of Address, representing the avatar of the pool.
   token_in_address : Address
       An instance of Address, representing the address of the input token.
   token_out_address : Address
       An instance of Address, representing the address of the output token.
   amount_out : int
       An integer representing the exact amount of the output token.
   max_amount_in : int
       An integer representing the maximum amount of the input token to be used.
   """

   swap_kind = SwapKind.InGivenExactOut
   super().__init__(blockchain=Chains.get_blockchain_by_chain_id(w3),
                    pool_id=pool_id,
                    avatar=avatar,
                    swap_kind=swap_kind,
                    token_in_address=token_in_address,
                    token_out_address=token_out_address,
                    amount=amount_out,
                    limit=max_amount_in)
