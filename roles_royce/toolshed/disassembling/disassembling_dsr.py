from dataclasses import dataclass
from decimal import Decimal
from defabipedia.maker import ContractSpecs
from roles_royce.generic_method import Transactable
from roles_royce.protocols.base import Address
from roles_royce.protocols.eth import maker

from .disassembler import Disassembler, validate_percentage


@dataclass
class DSRDisassembler(Disassembler):
    def get_amount_to_redeem(self, fraction: Decimal, proxy_address: Address = None) -> int:
        pot_contract = ContractSpecs[self.blockchain].Pot.contract(self.w3)
        dsr_contract = ContractSpecs[self.blockchain].DsrManager.contract(self.w3)
        if proxy_address:
            pie = pot_contract.functions.pie(proxy_address).call()    
        else:
            pie = dsr_contract.functions.pieOf(self.avatar_safe_address).call()
        chi = pot_contract.functions.chi().call() / (10**27)
        amount_to_redeem = pie * chi
        return int(Decimal(amount_to_redeem) * Decimal(fraction))


    def exit_1(self, percentage: float, exit_arguments: list[dict] = None, amount_to_redeem: int = None) -> list[Transactable]:
        """Withdraw funds from DSR with proxy.

        Args:
            percentage (float): Percentage of liquidity to remove from DSR.
            exit_arguments (list[str]): List of DSR token addresses to withdraw from.
            amount_to_redeem (int, optional): Amount of DSR tokens to withdraw. Defaults to None.

        Returns 
            list[Transactable]: List of transactions to exit DSR.
        """

        fraction = validate_percentage(percentage)

        txns = []

        proxy_registry = ContractSpecs[self.blockchain].ProxyRegistry.contract(self.w3)
        proxy_address = proxy_registry.functions.proxies(self.avatar_safe_address).call()

        if amount_to_redeem is None:
            amount_to_redeem = self.get_amount_to_redeem(fraction, proxy_address)

        approve_dai = maker.ApproveDAI(spender=proxy_address, amount=amount_to_redeem)
        exit_dai = maker.ProxyActionExitDsr(proxy=proxy_address, wad=amount_to_redeem)

        txns.append(approve_dai)
        txns.append(exit_dai)

        return txns
    
    def exit_2(self, percentage: float, exit_arguments: list[dict] = None, amount_to_redeem: int = None) -> list[Transactable]:
        """Withdraw funds from DSR without proxy.

        Args:
            percentage (float): Percentage of liquidity to remove from DSR.
            exit_arguments (list[str]): List of DSR token addresses to withdraw from.
            amount_to_redeem (int, optional): Amount of DSR tokens to withdraw. Defaults to None.

        Returns
            list[Transactable]: List of transactions to exit DSR.
        """

        fraction = validate_percentage(percentage)

        txns = []

        if amount_to_redeem is None:
            amount_to_redeem = self.get_amount_to_redeem(fraction)
        dsr_manager_address = ContractSpecs[self.blockchain].DsrManager.contract(self.w3).address
        approve_dai = maker.ApproveDAI(spender=dsr_manager_address, amount=amount_to_redeem)
        exit_dai = maker.ExitDsr(avatar=self.avatar_safe_address, wad=amount_to_redeem)

        txns.append(approve_dai)
        txns.append(exit_dai)

        return txns
