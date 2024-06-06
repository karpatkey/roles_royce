from dataclasses import dataclass
from decimal import Decimal
from defabipedia.spark import ContractSpecs
from defabipedia.tokens import EthereumTokenAddr, GnosisTokenAddr
from defabipedia.types import Chain
from roles_royce.generic_method import Transactable
from roles_royce.protocols.base import Address
from roles_royce.protocols.eth import spark
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

