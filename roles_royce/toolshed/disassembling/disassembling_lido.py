from dataclasses import dataclass
from decimal import Decimal
from roles_royce.generic_method import Transactable
from roles_royce.protocols.eth import lido
from defabipedia.lido import Abis, ContractSpecs
from roles_royce.toolshed.disassembling.disassembler import Disassembler, validate_percentage
from web3 import Web3
from web3.exceptions import ContractLogicError
from roles_royce.protocols.base import Address
from roles_royce.constants import ETHAddr


@dataclass
class LidoDisassembler(Disassembler):

    def get_amount_to_redeem(self, address: Address, fraction: float | Decimal) -> int:
        if address == ETHAddr.stETH:
            contract = ContractSpecs[self.blockchain].stETH.contract(self.w3)
        else:
            contract = ContractSpecs[self.blockchain].wstETH.contract(self.w3)

        return int(Decimal(contract.functions.balanceOf(self.avatar_safe_address).call()) * Decimal(fraction))

    def exit_1(self, percentage: float, amount_to_redeem: int = None) -> list[
        Transactable]:
        """Unstake stETH from Lido

        Args:
            percentage (float): Percentage of token to remove.
            amount_to_redeem (int, optional):Amount of stETH to redeem. Defaults to None. If None, the 'percentage' of the balance of stETH will be redeemed.

        Returns:
            list[ Transactable]: List of transactions to execute.
        """

        fraction = validate_percentage(percentage)

        txns = []
        address = ETHAddr.stETH

        if amount_to_redeem is None: 
            amount_to_redeem = self.get_amount_to_redeem(address, fraction)

        set_allowance = lido.ApproveWithdrawalStETHWithUnstETH(amount = amount_to_redeem)
        request_withdrawal = lido.RequestWithdrawalsStETH(amounts = amount_to_redeem)

        txns.append(set_allowance)
        txns.append(request_withdrawal)


    def exit_2(self, percentage: float, amount_to_redeem: int = None) -> list[
        Transactable]:
        """Unwrap wstETH and unstake for ETH on Lido

        Args:
            percentage (float): Percentage of token to remove.
            amount_to_redeem (int, optional): Amount of wstETH to redeem. Defaults to None. If None, the 'percentage' of the balance of stETH will be redeemed.

        Returns:
            list[ Transactable]: List of transactions to execute.
        """

        fraction = validate_percentage(percentage)

        txns = []
        address = ETHAddr.wstETH

        if amount_to_redeem is None: 
            amount_to_redeem = self.get_amount_to_redeem(address, fraction)

        set_allowance = lido.ApproveWithdrawalWstETH(amount = amount_to_redeem)
        request_withdrawal = lido.RequestWithdrawalsWstETH(amounts = amount_to_redeem)

        txns.append(set_allowance)
        txns.append(request_withdrawal)

    def exit_3(self, percentage: float, exit_arguments: list[dict], amount_to_redeem: int = None) -> list[
        Transactable]:
        """Swap stETH for ETH

        Args:
            percentage (float): Percentage of token to remove.
            exit_arguments (list[dict]):  List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "max_slippage": 0.01
                    }
                ]
            amount_to_redeem (int, optional): Amount of stETH to redeem. Defaults to None. If None, the 'percentage' of the balance of stETH will be redeemed.


        Returns:
            list[ Transactable]: List of transactions to execute.
        """

    def exit_4(self, percentage: float, exit_arguments: list[dict], amount_to_redeem: int = None) -> list[
        Transactable]:
        """Swap wstETH for ETH

        Args:
            percentage (float): Percentage of token to remove.
            exit_arguments (list[dict]):  List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "max_slippage": 0.01
                    }
                ]
            amount_to_redeem (int, optional): Amount of wstETH to redeem. Defaults to None. If None, the 'percentage' of the balance of stETH will be redeemed.

        Returns:
            list[ Transactable]: List of transactions to execute.
        """