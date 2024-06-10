from dataclasses import dataclass
from decimal import Decimal
from defabipedia.spark import ContractSpecs
from defabipedia.tokens import Addresses
from defabipedia.types import Chain
from roles_royce.generic_method import Transactable
from roles_royce.protocols.base import Address
from roles_royce.protocols.eth import spark
from roles_royce.protocols import cowswap
from roles_royce.toolshed.disassembling.disassembling_swaps import SwapDisassembler

from .disassembler import Disassembler, validate_percentage


@dataclass
class SparkDisassembler(Disassembler):
    def get_amount_to_redeem_sdai(self, fraction: Decimal) -> int:
        sdai = ContractSpecs[self.blockchain].sDAI.contract(self.w3)
        balance = sdai.functions.balanceOf(self.avatar_safe_address).call()
        return int(Decimal(balance) * Decimal(fraction))
    

    def exit_1(self, percentage: float, exit_arguments: list[dict] = None, amount_to_redeem: int = None) -> list[Transactable]:
        """Withdraw funds from Spark with proxy.

        Args:
            percentage (float): Percentage of liquidity to remove from Spark.
            exit_arguments (list[str]): List of Spark token addresses to withdraw from.
            amount_to_redeem (int, optional): Amount of Spark tokens to withdraw. Defaults to None.

        Returns 
            list[Transactable]: List of transactions to exit Spark.
        """

        fraction = validate_percentage(percentage)

        txns = []
        if amount_to_redeem is None:
            amount_to_redeem = self.get_amount_to_redeem_sdai(fraction)

        exit_sdai = spark.RedeemSDAIforDAI(blockchain=self.blockchain, amount=amount_to_redeem, avatar=self.avatar_safe_address,)

        txns.append(exit_sdai)

        return txns
    
    def exit_2(self, percentage: float, exit_arguments: list[dict], amount_to_redeem: int = None) -> list[Transactable]:
        """
        Swaps sDAI for USDC. Approves the Cowswap relayer to spend the sDAI if needed, then creates the order using
        the Cow's order API and creates the sign_order transaction.
        Args:
            percentage (float): Percentage of the total sDAI holdings to swap.
            exit_arguments (list[dict]):  List with one single dictionary with the order parameters from an already
             created order:
                arg_dicts = [
                    {
                        "max_slippage": 11.25
                    }
                ]
            amount_to_redeem (int, optional): Amount of sDAI to swap. Defaults to None. If None, the 'percentage' of
                the total sDAI holdings are swapped
        Returns:
            list[ Transactable]: List of transactions to execute.
        """

        max_slippage = exit_arguments[0]["max_slippage"] / 100
        fraction = validate_percentage(percentage)

        if amount_to_redeem is None:
            amount_to_redeem = self.get_amount_to_redeem_sdai(fraction)

        if amount_to_redeem == 0:
            return []
        
        if 'anvil' in self.w3.client_version:
            fork = True
        else:
            fork = False

        return cowswap.create_order_and_swap(w3=self.w3,
                                             avatar=self.avatar_safe_address,
                                             sell_token=ContractSpecs[self.blockchain].sDAI.address,
                                             buy_token=Addresses[self.blockchain].USDC,
                                             amount=amount_to_redeem,
                                             kind=cowswap.SwapKind.SELL,
                                             max_slippage=max_slippage,
                                             valid_duration=20 * 60,
                                             fork=fork)

    

