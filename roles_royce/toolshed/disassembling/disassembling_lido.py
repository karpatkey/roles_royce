from dataclasses import dataclass
from decimal import Decimal
from defabipedia.lido import ContractSpecs
from defabipedia.tokens import EthereumTokenAddr
from roles_royce.generic_method import Transactable
from roles_royce.protocols.base import Address
from roles_royce.protocols import cowswap
from roles_royce.protocols.eth import lido

from .disassembler import Disassembler, validate_percentage


@dataclass
class LidoDisassembler(Disassembler):
    def get_amount_to_redeem(self, address: Address, fraction: float | Decimal) -> int:
        """
        Calculates the amount of tokens to redeem based on the percentage of the total holdings.

        Args:
            address (Address): Token address; can be stETH or wstETH.
            fraction (float): Percentage of the total holdings to redeem.

        Returns:
            int: Amount of tokens to redeem.
        """
        if address == ContractSpecs[self.blockchain].wstETH.address:
            contract = ContractSpecs[self.blockchain].wstETH.contract(self.w3)
        elif address == ContractSpecs[self.blockchain].stETH.address:
            contract = ContractSpecs[self.blockchain].stETH.contract(self.w3)
        else:
            raise ValueError("Invalid token address")

        return int(Decimal(contract.functions.balanceOf(self.avatar_safe_address).call()) * Decimal(fraction))

    def exit_1(
            self, percentage: float, exit_arguments: list[dict] = None, amount_to_redeem: int = None
    ) -> list[Transactable]:
        """
        Unstakes stETH from Lido

        Args:
            percentage (float): Percentage of the total stETH holdings to redeem.
            amount_to_redeem (int, optional):Amount of stETH to redeem. Defaults to None. If None, the 'percentage' of
                the balance of stETH will be redeemed.

        Returns:
            list[Transactable]: List of transactions to execute.
        """

        fraction = validate_percentage(percentage)

        txns = []
        address = ContractSpecs[self.blockchain].stETH.address

        if amount_to_redeem is None:
            amount_to_redeem = self.get_amount_to_redeem(address, fraction)

        chunk_amount = amount_to_redeem
        if chunk_amount > 1000_000_000_000_000_000_000:
            chunks = []
            while chunk_amount >= 1000_000_000_000_000_000_000:
                chunks.append(1000_000_000_000_000_000_000)
                chunk_amount -= 1000_000_000_000_000_000_000
            if chunk_amount > 0:
                chunks.append(chunk_amount)

            set_allowance = lido.ApproveWithdrawalStETHWithUnstETH(amount=amount_to_redeem)
            request_withdrawal = lido.RequestWithdrawalsStETH(amounts=chunks, avatar=self.avatar_safe_address)

        else:
            set_allowance = lido.ApproveWithdrawalStETHWithUnstETH(amount=amount_to_redeem)
            request_withdrawal = lido.RequestWithdrawalsStETH(
                amounts=[amount_to_redeem], avatar=self.avatar_safe_address
            )

        txns.append(set_allowance)
        txns.append(request_withdrawal)
        return txns

    def exit_2(
            self, percentage: float, exit_arguments: list[dict] = None, amount_to_redeem: int = None
    ) -> list[Transactable]:

        """
        Unwraps wstETH and unstakes for ETH on Lido

        Args:
            percentage (float): Percentage of the total wstETH holdings to redeem.
            amount_to_redeem (int, optional): Amount of wstETH to redeem. Defaults to None. If None, the 'percentage' of the balance of stETH will be redeemed.

        Returns:
            list[Transactable]: List of transactions to execute.
        """

        fraction = validate_percentage(percentage)

        txns = []
        address = ContractSpecs[self.blockchain].wstETH.address

        if amount_to_redeem is None:
            amount_to_redeem = self.get_amount_to_redeem(address, fraction)

        chunk_amount = amount_to_redeem
        if chunk_amount > 1000_000_000_000_000_000_000:
            chunks = []
            while chunk_amount >= 1000_000_000_000_000_000_000:
                chunks.append(1000_000_000_000_000_000_000)
                chunk_amount -= 1000_000_000_000_000_000_000
            if chunk_amount > 0:
                chunks.append(chunk_amount)

            set_allowance = lido.ApproveWithdrawalWstETH(amount=amount_to_redeem)
            request_withdrawal = lido.RequestWithdrawalsWstETH(amounts=chunks, avatar=self.avatar_safe_address)

        else:
            set_allowance = lido.ApproveWithdrawalWstETH(amount=amount_to_redeem)
            request_withdrawal = lido.RequestWithdrawalsWstETH(
                amounts=[amount_to_redeem], avatar=self.avatar_safe_address
            )

        txns.append(set_allowance)
        txns.append(request_withdrawal)
        return txns

    def exit_3(self, percentage: float, exit_arguments: list[dict], amount_to_redeem: int = None) -> list[Transactable]:
        """
        Swaps stETH for ETH. Approves the Cowswap relayer to spend the stETH if needed, then creates the order using the
        Cow's order API and creates the sign_order transaction.
        Args:
            percentage (float): Percentage of the total stETH holdings to swap.
            exit_arguments (list[dict]):  List with one single dictionary with the order parameters from an already
             created order:
                arg_dicts = [
                    {
                        "max_slippage": 11.25
                    }
                ]
            amount_to_redeem (int, optional): Amount of stETH to swap. Defaults to None. If None, the 'percentage' of
                the total stETH holdings are swapped
        Returns:
            list[ Transactable]: List of transactions to execute
        """

        max_slippage = exit_arguments[0]["max_slippage"] / 100
        fraction = validate_percentage(percentage)

        if amount_to_redeem is None:
            amount_to_redeem = self.get_amount_to_redeem(EthereumTokenAddr.stETH, fraction)

        if amount_to_redeem == 0:
            return []

        return cowswap.create_order_and_swap(w3=self.w3,
                                             avatar=self.avatar_safe_address,
                                             sell_token=EthereumTokenAddr.stETH,
                                             buy_token=EthereumTokenAddr.E,
                                             amount=amount_to_redeem,
                                             kind=cowswap.SwapKind.SELL,
                                             max_slippage=max_slippage,
                                             valid_duration=20 * 60)

    def exit_4(self, percentage: float, exit_arguments: list[dict], amount_to_redeem: int = None) -> list[Transactable]:
        """
        Swaps wstETH for ETH. Approves the Cowswap relayer to spend the wstETH if needed, then creates the order using
        the Cow's order API and creates the sign_order transaction.
        Args:
            percentage (float): Percentage of the total wstETH holdings to swap.
            exit_arguments (list[dict]):  List with one single dictionary with the order parameters from an already
             created order:
                arg_dicts = [
                    {
                        'buy_amount': '2731745328645699409',
                        'sell_amount': '985693283370526960312',
                        'valid_to': 1712697525
                    }
                ]
            amount_to_redeem (int, optional): Amount of wstETH to swap. Defaults to None. If None, the 'percentage' of
                the total stETH holdings are swapped
        Returns:
            list[ Transactable]: List of transactions to execute.
        """

        max_slippage = exit_arguments[0]["max_slippage"] / 100
        fraction = validate_percentage(percentage)

        if amount_to_redeem is None:
            amount_to_redeem = self.get_amount_to_redeem(EthereumTokenAddr.wstETH, fraction)

        if amount_to_redeem == 0:
            return []

        return cowswap.create_order_and_swap(w3=self.w3,
                                             avatar=self.avatar_safe_address,
                                             sell_token=EthereumTokenAddr.wstETH,
                                             buy_token=EthereumTokenAddr.E,
                                             amount=amount_to_redeem,
                                             kind=cowswap.SwapKind.SELL,
                                             max_slippage=max_slippage,
                                             valid_duration=20 * 60)
