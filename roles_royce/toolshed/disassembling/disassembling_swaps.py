from dataclasses import dataclass
from decimal import Decimal
from time import time

from defabipedia.balancer import Abis as BalancerAbis
from defabipedia.swap_pools import EthereumSwapPools, GnosisSwapPools, SwapPoolInstances
from defabipedia.tokens import Abis, Addresses
from defabipedia.types import Chain, SwapPools
from defabipedia.uniswap_v3 import ContractSpecs as UniContracts
from web3 import Web3
from web3.exceptions import ContractLogicError

from roles_royce.generic_method import Transactable
from roles_royce.protocols.balancer.methods_general import ApproveForVault
from roles_royce.protocols.balancer.methods_swap import ExactTokenInSingleSwap, QuerySwap, SingleSwap
from roles_royce.protocols.balancer.types_and_enums import SwapKind
from roles_royce.protocols.base import Address
from roles_royce.protocols import cowswap
from roles_royce.protocols.swap_pools.quote_methods import QuoteCurve, QuoteUniswapV3
from roles_royce.protocols.swap_pools.swap_methods import (
    ApproveCurve,
    ApproveUniswapV3,
    SwapCurve,
    SwapUniswapV3,
    WrapNativeToken,
)
from roles_royce.toolshed.disassembling.disassembler import Disassembler, validate_percentage


@dataclass
class SwapDisassembler(Disassembler):
    def get_wrapped_token(self) -> Address:
        if self.blockchain == Chain.ETHEREUM:
            return Addresses[self.blockchain].WETH
        elif self.blockchain == Chain.GNOSIS:
            return Addresses[self.blockchain].WXDAI
        else:
            raise ValueError("Blockchain not supported")

    def get_amount_to_redeem(self, token_in_address: Address, fraction: float | Decimal) -> int:
        native = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

        balance = 0
        if token_in_address == native:
            balance = self.w3.eth.get_balance(self.avatar_safe_address)
        else:
            token_in_contract = self.w3.eth.contract(address=token_in_address, abi=Abis.ERC20.abi)
            balance = token_in_contract.functions.balanceOf(self.avatar_safe_address).call()

        amount = int(Decimal(balance) * Decimal(fraction))

        if token_in_address == native:
            min_amount = 3
            if balance - amount <= Web3.to_wei(min_amount, "ether"):
                raise ValueError(f"Must keep at least a balance of {min_amount} of native token")

        return amount

    def get_pool_id(self, pool_address: Address) -> str:
        return (
            self.w3.eth.contract(address=pool_address, abi=BalancerAbis[self.blockchain].UniversalBPT.abi)
            .functions.getPoolId()
            .call()
        )

    def get_swap_pools(self, blockchain, protocol, token_in, token_out):
        """Returns all instances of SwapPools within the specified blockchain's SwapPools class, filtered by protocol and tokens."""
        pools_class = SwapPoolInstances[blockchain]

        instances = []
        for attr_name in dir(pools_class):
            attr_value = getattr(pools_class, attr_name)
            if isinstance(attr_value, SwapPools) and attr_value.protocol == protocol:
                if protocol == "UniswapV3" or protocol == "Balancer":
                    if token_in == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                        token_in = self.get_wrapped_token()
                    if token_out == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                        token_out = self.get_wrapped_token()
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
            amount_out = quote.call(web3=self.w3)
            return swap_pool, amount_out

        elif swap_pool.protocol == "UniswapV3":
            if token_in == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                token_in = self.get_wrapped_token()
            elif token_out == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                token_out = self.get_wrapped_token()
            quote = QuoteUniswapV3(self.blockchain, token_in, token_out, amount_in, swap_pool.uni_fee)
            amount_out = quote.call(web3=self.w3)
            return swap_pool, amount_out[0]

        elif swap_pool.protocol == "Balancer":
            if token_in == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                token_in = self.get_wrapped_token()
            elif token_out == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                token_out = self.get_wrapped_token()
            pool_id = self.get_pool_id(swap_pool.address)
            quote = QuerySwap(
                self.blockchain,
                pool_id,
                self.avatar_safe_address,
                token_in,
                token_out,
                amount_in,
            )
            amount_out = quote.call(web3=self.w3)
            return swap_pool, amount_out

        else:
            raise ValueError("Protocol not supported")

    def exit_1(
        self, percentage: float, exit_arguments: list[dict] = None, amount_to_redeem: int = None
    ) -> list[Transactable]:
        """Make a swap on CowSwap with best amount out
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

        max_slippage = exit_arguments[0]["max_slippage"] / 100
        token_in = exit_arguments[0]["token_in_address"]
        token_out = exit_arguments[0]["token_out_address"]
        fraction = validate_percentage(percentage)

        if amount_to_redeem is None:
            amount_to_redeem = self.get_amount_to_redeem(token_in, fraction)

        txns = []

        if amount_to_redeem == 0:
            return []

        if "anvil" in self.w3.client_version:
            fork = True
        else:
            fork = False

        if token_in == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            if amount_to_redeem != None:
                amount_to_redeem = self.get_amount_to_redeem(token_in, fraction)
            wraptoken = WrapNativeToken(blockchain=self.blockchain, eth_amount=amount_to_redeem)
            txns.append(wraptoken)
            token_in = self.get_wrapped_token()

        cow_txns = cowswap.create_order_and_swap(
            w3=self.w3,
            avatar=self.avatar_safe_address,
            sell_token=token_in,
            buy_token=token_out,
            amount=amount_to_redeem,
            kind=cowswap.SwapKind.SELL,
            max_slippage=max_slippage,
            valid_duration=20 * 60,
            fork=fork,
        )

        for cow_txn in cow_txns:
            txns.append(cow_txn)

        return txns

    def exit_2(
        self, percentage: float, exit_arguments: list[dict] = None, amount_to_redeem: int = None
    ) -> list[Transactable]:
        """Make a swap on Balancer with best amount out
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

            # get the pools where we get a quote from
            pools = self.get_swap_pools(self.blockchain, "Balancer", token_in, token_out)
            quotes = []
            if len(pools) == 0:
                raise ValueError("No pools found with the specified tokens")
            else:
                for pool in pools:
                    swap_pool, quote = self.get_quote(pool, token_in, token_out, amount_to_redeem)
                    quotes.append(quote)

            pool_id = self.get_pool_id(swap_pool.address)
            best_quote = max(quotes)
            amount_out_min_slippage = int(Decimal(best_quote) * Decimal(1 - max_slippage))
            if token_in == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                if amount_to_redeem != None:
                    amount_to_redeem = self.get_amount_to_redeem(token_in, fraction)
                wraptoken = WrapNativeToken(blockchain=self.blockchain, eth_amount=amount_to_redeem)
                txns.append(wraptoken)
                token_in = self.get_wrapped_token()
            elif token_out == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                token_out = self.get_wrapped_token()
            approve_vault = ApproveForVault(token=token_in, amount=amount_to_redeem)
            swap_balancer = SingleSwap(
                blockchain=self.blockchain,
                pool_id=pool_id,
                avatar=self.avatar_safe_address,
                kind=SwapKind.OutGivenExactIn,
                token_in_address=token_in,
                token_out_address=token_out,
                amount_in=amount_to_redeem,
                min_amount_out=amount_out_min_slippage,
                deadline=int(int(time()) + 600),
            )

            txns.append(approve_vault)
            txns.append(swap_balancer)
        return txns

    def exit_3(
        self, percentage: float, exit_arguments: list[dict] = None, amount_to_redeem: int = None
    ) -> list[Transactable]:
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

            # get the pools where we get a quote from
            pools = self.get_swap_pools(self.blockchain, "Curve", token_in, token_out)
            quotes = []
            if len(pools) == 0:
                raise ValueError("No pools found with the specified tokens")
            else:
                for pool in pools:
                    swap_pool, quote = self.get_quote(pool, token_in, token_out, amount_to_redeem)
                    quotes.append(quote)

            # get the best quote
            best_quote = max(quotes)
            amount_out_min_slippage = int(Decimal(best_quote) * Decimal(1 - max_slippage))

            if token_in == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                if amount_to_redeem != None:
                    amount_to_redeem = self.get_amount_to_redeem(token_in, fraction)
                eth_amount = amount_to_redeem
            else:
                eth_amount = 0
                approve_curve = ApproveCurve(
                    blockchain=self.blockchain,
                    token_address=token_in,
                    spender=swap_pool.address,
                    amount=amount_to_redeem,
                )
                txns.append(approve_curve)

            swap_curve = SwapCurve(
                blockchain=self.blockchain,
                pool_address=swap_pool.address,
                token_x=swap_pool.tokens.index(token_in),
                token_y=swap_pool.tokens.index(token_out),
                amount_x=amount_to_redeem,
                min_amount_y=amount_out_min_slippage,
                eth_amount=eth_amount,
            )

            txns.append(swap_curve)
        return txns

    def exit_4(
        self, percentage: float, exit_arguments: list[dict] = None, amount_to_redeem: int = None
    ) -> list[Transactable]:
        """Make a swap on UniswapV3 with best amount out
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

            # get the pools where we get a quote from
            pools = self.get_swap_pools(self.blockchain, "UniswapV3", token_in, token_out)
            quotes = []
            if len(pools) == 0:
                raise ValueError("No pools found with the specified tokens")
            else:
                for pool in pools:
                    swap_pool, quote = self.get_quote(pool, token_in, token_out, amount_to_redeem)
                    quotes.append(quote)

            # get the best quote
            best_quote = max(quotes)
            amount_out_min_slippage = int(Decimal(best_quote) * Decimal(1 - max_slippage))
            if token_in == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                if amount_to_redeem != None:
                    amount_to_redeem = self.get_amount_to_redeem(token_in, fraction)
                wraptoken = WrapNativeToken(blockchain=self.blockchain, eth_amount=amount_to_redeem)
                txns.append(wraptoken)
                token_in = self.get_wrapped_token()
            elif token_out == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                token_out = self.get_wrapped_token()

            approve_uniswapV3 = ApproveUniswapV3(
                blockchain=self.blockchain,
                token_address=token_in,
                amount=amount_to_redeem,
            )

            swap_uniswapV3 = SwapUniswapV3(
                blockchain=self.blockchain,
                token_in=token_in,
                token_out=token_out,
                avatar=self.avatar_safe_address,
                amount_in=amount_to_redeem,
                min_amount_out=amount_out_min_slippage,
                fee=swap_pool.uni_fee,
            )

            txns.append(approve_uniswapV3)
            txns.append(swap_uniswapV3)
        return txns
