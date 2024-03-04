from dataclasses import dataclass
from decimal import Decimal
from roles_royce.generic_method import Transactable
from defabipedia.uniswap_v3 import ContractSpecs as UniContracts
from defabipedia.types import Chain, SwapPools
from defabipedia.swap_pools import EthereumSwapPools, GnosisSwapPools, SwapPoolInstances
from defabipedia.tokens import Abis
from roles_royce.toolshed.disassembling.disassembler import Disassembler, validate_percentage
from web3 import Web3
from web3.exceptions import ContractLogicError
from roles_royce.protocols.base import Address
from roles_royce.protocols.swap_pools.swap_methods import SwapCurve, SwapUniswapV3
from roles_royce.protocols.swap_pools.quote_methods import QuoteUniswapV3, QuoteCurve
from roles_royce.protocols.balancer.methods_swap import QuerySwap, SingleSwap
from time import time

@dataclass
class SwapDisassembler(Disassembler):
    def get_amount_to_redeem(self, token_in_address: Address, fraction: float | Decimal) -> int:
        token_in_contract = self.w3.eth.contract(address=token_in_address,
                                            abi=Abis[self.blockchain].ERC20.abi)

        return int(Decimal(token_in_contract.functions.balanceOf(self.avatar_safe_address).call()) * Decimal(fraction))
    
    def get_swap_pools(blockchain, protocol, token_in, token_out):
        """Returns all instances of SwapPools within the specified blockchain's SwapPools class, filtered by protocol and tokens."""
        pools_class = SwapPoolInstances[blockchain]

        instances = []
        for attr_name in dir(pools_class):
            attr_value = getattr(pools_class, attr_name)
            if isinstance(attr_value, SwapPools) and attr_value.protocol == protocol:
                # Check if both tokens are in the instance's tokens list
                if token_in in attr_value.tokens and token_out in attr_value.tokens:
                    instances.append(attr_value)
        return instances

    def get_quote(self, swap_pool: SwapPools, token_in: str, token_out: str, amount_in) -> Decimal:
        if swap_pool.protocol == "Curve":
            try:
                index_in = swap_pool.tokens.index(token_in)
            except ValueError:
                index_in = None

            try:
                index_out = swap_pool.tokens.index(token_out)
            except ValueError:
                index_out = None
            quote = QuoteCurve(self.blockchain, swap_pool.address, index_in, index_out, amount_in)

            return swap_pool, quote

        elif swap_pool.protocol == "UniswapV3":
            quote = QuoteUniswapV3(self.blockchain, token_in, token_out, amount_in, swap_pool.uni_fee)
            return swap_pool, quote
        
        elif swap_pool.protocol == "Balancer":
            quote = QuerySwap(self.blockchain, swap_pool.address, token_in, token_out, amount_in)
            return swap_pool, quote

        else:
            raise ValueError("Protocol not supported")

    def exit_1(self, percentage: float, exit_arguments: list[dict]=None, amount_to_redeem: int = None) -> list[
        Transactable]:
        """Make a swap on Uniswap, Balancer or Curve with best amount out
        Args:
            percentage (float): Percentage of token to remove.
            exit_arguments (list[dict], optional): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "token_in_address: "FillMewithTokenAddress",
                        "max_slippage": 0.01,
                        "token_out_address": "FillMewithTokenAddress"
                    }
                ]
            amount_to_redeem (int, optional): Amount of wallet token to redeem. Defaults to None.
        Returns:
            list[ Transactable]:  List of transactions to execute.
        """
        for element in exit_arguments:
            max_slippage = element["max_slippage"] / 100
            token_in = element["token_in_address"]
            token_out = element["token_out_address"] 
            fraction = validate_percentage(percentage)
            
            if amount_to_redeem is None: 
                amount_to_redeem = self.get_amount_to_redeem(token_in, fraction)

            txns = []  

            #get the pools where we get a quote from
            pools = self.get_swap_pools(self.blockchain, "Balancer", token_in, token_out)
            quotes = []
            if len(pools) == 0:
                raise ValueError("No pools found with the specified tokens")
            else:
                for pool in pools:
                    swap_pool, quote = self.get_quote(pool, token_in, token_out, amount_to_redeem)
                    quotes.append(quote)

            #get the best quote
            best_quote = max(quotes)
            amount_out_min_slippage = int(Decimal(best_quote) * Decimal(1 - max_slippage))

            #build the transaction
            swap_balancer = SingleSwap(blockchain=self.blockchain,
                                       pool_id=best_quote.pool_id,
                                       avatar=self.avatar_safe_address,
                                       token_in_address=token_in,
                                       token_out_address=token_out,
                                       amount_in=amount_to_redeem,
                                       min_amount_out=amount_out_min_slippage)
            
            txns.append(swap_balancer)
        return txns
    
    def exit_2(self, percentage: float, exit_arguments: list[dict]=None, amount_to_redeem: int = None) -> list[
        Transactable]:  
        """Make a swap on Curve with best amount out
        Args:
            percentage (float): Percentage of token to remove.
            exit_arguments (list[dict], optional): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "token_in_address: "FillMewithTokenAddress",
                        "max_slippage": 0.01,
                        "token_out_address": "FillMewithTokenAddress"
                    }
                ]
            amount_to_redeem (int, optional): Amount of wallet token to redeem. Defaults to None.
        Returns:
            list[ Transactable]:  List of transactions to execute.
        """
        for element in exit_arguments:
            max_slippage = element["max_slippage"] / 100
            token_in = element["token_in_address"]
            token_out = element["token_out_address"] 
            fraction = validate_percentage(percentage)
            
            if amount_to_redeem is None: 
                amount_to_redeem = self.get_amount_to_redeem(token_in, fraction)

            txns = []  

            #get the pools where we get a quote from
            pools = self.get_swap_pools(self.blockchain, "Curve", token_in, token_out)
            quotes = []
            if len(pools) == 0:
                raise ValueError("No pools found with the specified tokens")
            else:
                for pool in pools:
                    quote = self.get_quote(pool, token_in, token_out, amount_to_redeem)
                    quotes.append(quote)

            #get the best quote
            best_quote = max(quotes)
            amount_out_min_slippage = int(Decimal(best_quote) * Decimal(1 - max_slippage))

            swap_curve = SwapCurve(blockchain=self.blockchain,
                                   pool_address=pool.address,
                                   token_in_address=token_in,
                                   token_out_address=token_out,
                                   amount_in=amount_to_redeem,
                                   amount_out_min=amount_out_min_slippage)
            
            txns.append(swap_curve)
        return txns
    
    def exit_3(self, percentage: float, exit_arguments: list[dict]=None, amount_to_redeem: int = None) -> list[
        Transactable]:
        """Make a swap on Curve with best amount out
        Args:
            percentage (float): Percentage of token to remove.
            exit_arguments (list[dict], optional): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "token_in_address: "FillMewithTokenAddress",
                        "max_slippage": 0.01,
                        "token_out_address": "FillMewithTokenAddress"
                    }
                ]
            amount_to_redeem (int, optional): Amount of wallet token to redeem. Defaults to None.
        Returns:
            list[ Transactable]:  List of transactions to execute.
        """
        for element in exit_arguments:
            max_slippage = element["max_slippage"] / 100
            token_in = element["token_in_address"]
            token_out = element["token_out_address"] 
            fraction = validate_percentage(percentage)
            
            if amount_to_redeem is None: 
                amount_to_redeem = self.get_amount_to_redeem(token_in, fraction)

            txns = []  

            #get the pools where we get a quote from
            pools = self.get_swap_pools(self.blockchain, "UniswapV3", token_in, token_out)
            quotes = []
            if len(pools) == 0:
                raise ValueError("No pools found with the specified tokens")
            else:
                for pool in pools:
                    pool, quote = self.get_quote(pool, token_in, token_out, amount_to_redeem)
                    quotes.append({'pool': pool, 'quote': quote})

            #get the best quote
            best_quote = max(quote, key=lambda x: x['quote'])
            amount_out_min_slippage = int(Decimal(best_quote) * Decimal(1 - max_slippage))

            swap_uniswap_v3 = SwapUniswapV3(blockchain=self.blockchain,
                                            token_in=token_in,
                                            token_out=token_out,
                                            avatar=self.avatar_safe_address,
                                            deadline=int(time()) + 60,
                                            amount_in=amount_to_redeem,
                                            amount_out_min=amount_out_min_slippage,
                                            fee=pools.uni_fee)
            
            txns.append(swap_uniswap_v3)
        return txns
    
