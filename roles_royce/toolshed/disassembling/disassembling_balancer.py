from decimal import Decimal

from defabipedia.balancer import Abis
from typing_extensions import TypedDict
from web3 import Web3
from web3.exceptions import ContractLogicError

from roles_royce.generic_method import Transactable
from roles_royce.protocols import balancer
from roles_royce.protocols.base import Address
from roles_royce.utils import to_checksum_address

from .disassembler import Disassembler, validate_percentage


class Exit11ArgumentElement(TypedDict):
    bpt_address: str
    max_slippage: float


class Exit12ArgumemntElement(TypedDict):
    bpt_address: str
    max_slippage: float
    token_out_address: str


class Exit13ArgumentElement(TypedDict):
    bpt_address: str


class Exit21ArgumentElement(TypedDict):
    gauge_address: str
    max_slippage: float


class Exit22ArgumentElement(TypedDict):
    gauge_address: str
    max_slippage: float
    token_out_address: str


class Exit23ArgumentElement(TypedDict):
    gauge_address: str
    max_slippage: float


class BalancerDisassembler(Disassembler):
    def get_bpt_amount_to_redeem_from_gauge(self, gauge_address: Address, fraction: float | Decimal) -> int:
        gauge_contract = self.w3.eth.contract(address=gauge_address, abi=Abis[self.blockchain].Gauge.abi)

        return int(Decimal(gauge_contract.functions.balanceOf(self.avatar_safe_address).call()) * Decimal(fraction))

    def get_bpt_amount_to_redeem(self, bpt_address: Address, fraction: float | Decimal) -> int:
        bpt_contract = self.w3.eth.contract(address=bpt_address, abi=Abis[self.blockchain].UniversalBPT.abi)

        return int(Decimal(bpt_contract.functions.balanceOf(self.avatar_safe_address).call()) * Decimal(fraction))

    def exit_1_1(
        self, percentage: float, exit_arguments: list[Exit11ArgumentElement], amount_to_redeem: int = None
    ) -> list[Transactable]:
        """
        Withdraw funds from the Balancer pool withdrawing all assets in proportional way (not used for pools in recovery mode!).

        Args:
            percentage (float): Percentage of liquidity to remove.
            exit_arguments (list[dict]): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "bpt_address": "0xsOmEAddResS",
                        "max_slippage": 1.25
                    }
                ]
            amount_to_redeem (int, optional): Amount of BPT to redeem. Defaults to None. If None, the 'percentage' of the balance of the BPT will be redeemed.

        Returns:
            list[Transactable]: List of transactions to execute.
        """

        fraction = validate_percentage(percentage)

        txns = []

        for element in exit_arguments:
            bpt_address = to_checksum_address(element["bpt_address"])
            max_slippage = element["max_slippage"] / 100

            bpt_contract = self.w3.eth.contract(address=bpt_address, abi=Abis[self.blockchain].UniversalBPT.abi)

            if amount_to_redeem is None:  # The amount to redeem might be calculated in a previous step
                amount_to_redeem = self.get_bpt_amount_to_redeem(bpt_address, fraction)

            if amount_to_redeem == 0:
                return []

            bpt_pool_id = "0x" + bpt_contract.functions.getPoolId().call().hex()
            bpt_pool_paused_state = bpt_contract.functions.getPausedState().call()
            # TODO: Not all pools have recovery mode, the following has to be improved
            try:
                bpt_pool_recovery_mode = bpt_contract.functions.inRecoveryMode().call()
            except ContractLogicError:
                bpt_pool_recovery_mode = False

            if bpt_pool_paused_state[0]:
                raise ValueError("Pool is in paused state, no withdrawing is accepted.")
            if bpt_pool_recovery_mode:
                raise ValueError(
                    "This pool is in recovery mode, only proportional recovery mode exit possible, try that option."
                )

            withdraw_balancer = balancer.ExactBptProportionalExitSlippage(
                w3=self.w3,
                pool_id=bpt_pool_id,
                avatar=self.avatar_safe_address,
                bpt_amount_in=amount_to_redeem,
                max_slippage=max_slippage,
            )
            txns.append(withdraw_balancer)
        return txns

    def exit_1_2(
        self, percentage: float, exit_arguments: list[Exit12ArgumemntElement], amount_to_redeem: int = None
    ) -> list[Transactable]:
        """
        Withdraw funds from the Balancer pool withdrawing a single asset specified by the token index.

        Args:
            percentage (float): Percentage of liquidity to remove.
            exit_arguments (list[dict]): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "bpt_address": "0xsOmEAddResS",
                        "max_slippage": 1.25,
                        "token_out_address": "0xAnoThERAdDResS"
                    }
                ]
            amount_to_redeem (int, optional): Amount of BPT to redeem. Defaults to None. If None, the 'percentage' of the balance of the BPT will be redeemed.

        Returns:
            list[Transactable]: List of transactions to execute.
        """
        fraction = validate_percentage(percentage)

        txns = []

        for element in exit_arguments:
            bpt_address = to_checksum_address(element["bpt_address"])
            max_slippage = element["max_slippage"] / 100
            token_out_address = to_checksum_address(element["token_out_address"])

            bpt_contract = self.w3.eth.contract(address=bpt_address, abi=Abis[self.blockchain].UniversalBPT.abi)
            if amount_to_redeem is None:  # The amount to redeem might be calculated in a previous step
                amount_to_redeem = self.get_bpt_amount_to_redeem(bpt_address, fraction)

            if amount_to_redeem == 0:
                return []

            bpt_pool_id = "0x" + bpt_contract.functions.getPoolId().call().hex()
            bpt_pool_paused_state = bpt_contract.functions.getPausedState().call()
            # TODO: Not all pools have recovery mode, the following has to be improved
            try:
                bpt_pool_recovery_mode = bpt_contract.functions.inRecoveryMode().call()
            except ContractLogicError:
                bpt_pool_recovery_mode = False

            if bpt_pool_paused_state[0]:
                raise ValueError("Pool is in paused state, no withdrawing is accepted.")
            if bpt_pool_recovery_mode:
                raise ValueError("This pool is in recovery mode, only proportional exit possible, try that option.")
            withdraw_balancer = balancer.ExactBptSingleTokenExitSlippage(
                w3=self.w3,
                pool_id=bpt_pool_id,
                avatar=self.avatar_safe_address,
                bpt_amount_in=amount_to_redeem,
                token_out_address=token_out_address,
                max_slippage=max_slippage,
            )
            txns.append(withdraw_balancer)
        return txns

    def exit_1_3(
        self, percentage: float, exit_arguments: list[Exit13ArgumentElement], amount_to_redeem: int = None
    ) -> list[Transactable]:
        """
        Withdraw funds from the Balancer pool withdrawing all assets in proportional way for pools in recovery mode.

        Args:
            percentage (float): Percentage of liquidity to remove from Balancer.
            exit_arguments (list[dict]): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "bpt_address": "0xsOmEAddResS"
                    }
                ]
            amount_to_redeem (int, optional): Amount of BPT to redeem. Defaults to None. If None, the 'percentage' of the balance of the BPT will be redeemed.

        Returns:
            list[Transactable]: List of transactions to execute."""
        fraction = validate_percentage(percentage)

        txns = []
        for element in exit_arguments:
            bpt_address = to_checksum_address(element["bpt_address"])

            bpt_contract = self.w3.eth.contract(address=bpt_address, abi=Abis[self.blockchain].UniversalBPT.abi)

            try:
                bpt_pool_recovery_mode = bpt_contract.functions.inRecoveryMode().call()
            except ContractLogicError:
                bpt_pool_recovery_mode = False
            if bpt_pool_recovery_mode is False:
                raise ValueError("This pool is not in recovery mode.")

            bpt_pool_id = "0x" + bpt_contract.functions.getPoolId().call().hex()

            if amount_to_redeem is None:  # The amount to redeem might be calculated in a previous step
                amount_to_redeem = self.get_bpt_amount_to_redeem(bpt_address, fraction)

            if amount_to_redeem == 0:
                return []

            withdraw_balancer = balancer.ExactBptRecoveryModeExit(
                w3=self.w3, pool_id=bpt_pool_id, avatar=self.avatar_safe_address, bpt_amount_in=amount_to_redeem
            )

            txns.append(withdraw_balancer)

        return txns

    def exit_2_1(
        self, percentage: float, exit_arguments: list[Exit21ArgumentElement], amount_to_redeem: int = None
    ) -> list[Transactable]:
        """
        Unstake from gauge and withdraw funds from the Balancer pool withdrawing all assets in proportional way (not used for pools in recovery mode!).

        Args:
            percentage (float): Percentage of liquidity to remove.
            exit_arguments (list[dict]): List of dictionaries with the withdrawal parameters.
                e.g.= [
                        {
                            "gauge_address": "0xsOmEAddResS",
                            "max_slippage": 1.25
                        }
                    ]
            amount_to_redeem (int, optional): Amount of BPT to redeem. Defaults to None. IfNone, the 'percentage' of the
                balance of the BPT will be redeemed.

        Returns:
            list[Transactable]: List of transactions to execute.
        """
        fraction = validate_percentage(percentage)

        txns = []
        for element in exit_arguments:
            gauge_address = to_checksum_address(element["gauge_address"])
            max_slippage = element["max_slippage"] / 100

            if amount_to_redeem is None:  # The amount to redeem might be calculated in a previous step
                amount_to_redeem = self.get_bpt_amount_to_redeem_from_gauge(gauge_address, fraction)

            if amount_to_redeem == 0:
                return []

            unstake_gauge = balancer.UnstakeFromGauge(
                blockchain=self.blockchain,
                gauge_address=gauge_address,
                amount=amount_to_redeem,
            )
            txns.append(unstake_gauge)

            gauge_contract = self.w3.eth.contract(address=gauge_address, abi=Abis[self.blockchain].Gauge.abi)
            bpt_address = gauge_contract.functions.lp_token().call()

            withdraw_balancer = self.exit_1_1(
                percentage=fraction,
                exit_arguments=[{"bpt_address": bpt_address, "max_slippage": max_slippage}],
                amount_to_redeem=amount_to_redeem,
            )
            for transactable in withdraw_balancer:
                txns.append(transactable)

        return txns

    def exit_2_2(
        self, percentage: float, exit_arguments: list[Exit22ArgumentElement], amount_to_redeem: int = None
    ) -> list[Transactable]:
        """
        Unstake from gauge and withdraw funds from the Balancer pool withdrawing a single asset specified by the token index.

        Args:
            percentage (float): Percentage of liquidity to remove.
            exit_arguments (list[dict]): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "gauge_address": "0xsOmEAddResS",
                        "token_out_address" : "0xsOmEAddResS",
                        "max_slippage": 1.25
                    }
                ]
            amount_to_redeem (int, optional): Amount of BPT to redeem. Defaults to None. If None, the 'percentage' of the balance of the BPT will be redeemed.

        Returns:
            list[Transactable]: List of transactions to execute.
        """
        fraction = validate_percentage(percentage)

        txns = []
        for element in exit_arguments:
            gauge_address = to_checksum_address(element["gauge_address"])
            token_out_address = to_checksum_address(element["token_out_address"])

            max_slippage = element["max_slippage"] / 100

            if amount_to_redeem is None:  # The amount to redeem might be calculated in a previous step
                amount_to_redeem = self.get_bpt_amount_to_redeem_from_gauge(gauge_address, fraction)

            if amount_to_redeem == 0:
                return []

            unstake_gauge = balancer.Unstake(w3=self.w3, gauge_address=gauge_address, amount=amount_to_redeem)
            txns.append(unstake_gauge)

            gauge_contract = self.w3.eth.contract(address=gauge_address, abi=Abis[self.blockchain].Gauge.abi)
            bpt_address = gauge_contract.functions.lp_token().call()

            withdraw_balancer = self.exit_1_2(
                percentage=fraction,
                exit_arguments=[
                    {"bpt_address": bpt_address, "token_out_address": token_out_address, "max_slippage": max_slippage}
                ],
                amount_to_redeem=amount_to_redeem,
            )
            for transactable in withdraw_balancer:
                txns.append(transactable)

        return txns

    def exit_2_3(
        self, percentage: float, exit_arguments: list[Exit23ArgumentElement], amount_to_redeem: int = None
    ) -> list[Transactable]:
        """
        Unstake from gauge and withdraw funds from the Balancer pool withdrawing all assets in proportional way for pools in recovery mode.

        Args:
            percentage (float): Percentage of liquidity to remove.
            exit_arguments (list[dict]): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "gauge_address": "0xsOmEAddResS",
                    }
                ]
            amount_to_redeem (int, optional): Amount of BPT to redeem. Defaults to None. If None, the 'percentage' of the balance of the BPT will be redeemed.

        Returns:
            list[Transactable]: List of transactions to execute.
        """
        fraction = validate_percentage(percentage)

        txns = []
        for element in exit_arguments:
            gauge_address = to_checksum_address(element["gauge_address"])

            if amount_to_redeem is None:  # The amount to redeem might be calculated in a previous step
                amount_to_redeem = self.get_bpt_amount_to_redeem_from_gauge(gauge_address, fraction)

            if amount_to_redeem == 0:
                return []

            unstake_gauge = balancer.Unstake(w3=self.w3, gauge_address=gauge_address, amount=amount_to_redeem)
            txns.append(unstake_gauge)

            gauge_contract = self.w3.eth.contract(address=gauge_address, abi=Abis[self.blockchain].Gauge.abi)
            bpt_address = gauge_contract.functions.lp_token().call()

            withdraw_balancer = self.exit_1_3(
                percentage=fraction, exit_arguments=[{"bpt_address": bpt_address}], amount_to_redeem=amount_to_redeem
            )
            for transactable in withdraw_balancer:
                txns.append(transactable)

        return txns
