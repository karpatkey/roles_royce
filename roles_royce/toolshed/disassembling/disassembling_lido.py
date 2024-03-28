from dataclasses import dataclass
from decimal import Decimal
from time import time

from defabipedia.lido import ContractSpecs
from web3 import Web3
from web3.exceptions import ContractLogicError

from roles_royce.constants import ETHAddr
from roles_royce.generic_method import Transactable
from roles_royce.protocols.base import Address
from roles_royce.protocols.cowswap.contract_methods import SignOrder
from roles_royce.protocols.cowswap.utils import QuoteOrderCowSwap
from roles_royce.protocols.eth import lido
from roles_royce.toolshed.disassembling.disassembler import Disassembler, validate_percentage


@dataclass
class LidoDisassembler(Disassembler):
    def get_amount_to_redeem(self, address: Address, fraction: float | Decimal) -> int:
        if address == ContractSpecs[self.blockchain].wstETH.address:
            contract = ContractSpecs[self.blockchain].wstETH.contract(self.w3)
        else:
            contract = ContractSpecs[self.blockchain].stETH.contract(self.w3)

        return int(Decimal(contract.functions.balanceOf(self.avatar_safe_address).call()) * Decimal(fraction))

    def exit_1(
        self, percentage: float, exit_arguments: list[dict] = None, amount_to_redeem: int = None
    ) -> list[Transactable]:
        """Unstake stETH from Lido
        Args:
            percentage (float): Percentage of token to remove.
            amount_to_redeem (int, optional):Amount of stETH to redeem. Defaults to None. If None, the 'percentage' of the balance of stETH will be redeemed.
        Returns:
            list[ Transactable]: List of transactions to execute.
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
        """Unwrap wstETH and unstake for ETH on Lido
        Args:
            percentage (float): Percentage of token to remove.
            amount_to_redeem (int, optional): Amount of wstETH to redeem. Defaults to None. If None, the 'percentage' of the balance of stETH will be redeemed.
        Returns:
            list[ Transactable]: List of transactions to execute.
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
        for element in exit_arguments:
            max_slippage = element["max_slippage"] / 100
            fraction = validate_percentage(percentage)

            txns = []
            address = ContractSpecs[self.blockchain].stETH.address

            if amount_to_redeem is None:
                amount_to_redeem = self.get_amount_to_redeem(address, fraction)

            quote = QuoteOrderCowSwap(
                blockchain=self.blockchain,
                sell_token=address,
                buy_token=ETHAddr.ETH,
                receiver=self.avatar_safe_address,
                kind="sell",
                sell_amount=amount_to_redeem,
            )

            buy_amount = quote.buy_amount
            fee_amount = quote.fee_amount

            buy_amount_min_slippage = int(Decimal(buy_amount) * Decimal(1 - max_slippage))
            set_allowance = lido.ApproveRelayerStETH(amount=amount_to_redeem)
            moooooo = SignOrder(
                blockchain=self.blockchain,
                avatar=self.avatar_safe_address,
                sell_token=address,
                buy_token=ETHAddr.ETH,
                sell_amount=amount_to_redeem,
                buy_amount=buy_amount_min_slippage,
                fee_amount=fee_amount,
                valid_to=int(int(time()) + 600),
                kind="sell",
            )

            # txns.append(set_allowance)
            txns.append(moooooo)
        return txns

    def exit_4(self, percentage: float, exit_arguments: list[dict], amount_to_redeem: int = None) -> list[Transactable]:
        """Swap wstETH for ETH
        Args:
            percentage (float): Percentage of token to remove.
            exit_arguments (list[dict]):  List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "max_slippage": 0.01
                    }
                ]
            amount_to_redeem (int, optional): Amount of wstETH to redeem. Defaults to None. If None, the 'percentage' of the balance of wstETH will be redeemed.
        Returns:
            list[ Transactable]: List of transactions to execute.
        """

        for element in exit_arguments:
            max_slippage = element["max_slippage"] / 100
            fraction = validate_percentage(percentage)

            txns = []
            address = ContractSpecs[self.blockchain].wstETH.address

            if amount_to_redeem is None:
                amount_to_redeem = self.get_amount_to_redeem(address, fraction)

            quote = QuoteOrderCowSwap(
                blockchain=self.blockchain,
                sell_token=address,
                buy_token=ETHAddr.ETH,
                receiver=self.avatar_safe_address,
                kind="sell",
                sell_amount=amount_to_redeem,
            )

            buy_amount = quote.buy_amount
            fee_amount = quote.fee_amount

            buy_amount_min_slippage = int(Decimal(buy_amount) * Decimal(1 - max_slippage))
            set_allowance = lido.ApproveRelayerWstETH(amount=amount_to_redeem)
            moooooo = SignOrder(
                blockchain=self.blockchain,
                avatar=self.avatar_safe_address,
                sell_token=address,
                buy_token=ETHAddr.ETH,
                sell_amount=amount_to_redeem,
                buy_amount=buy_amount_min_slippage,
                fee_amount=fee_amount,
                valid_to=int(int(time()) + 600),
                kind="sell",
            )

            # txns.append(set_allowance)
            txns.append(moooooo)
        return txns
