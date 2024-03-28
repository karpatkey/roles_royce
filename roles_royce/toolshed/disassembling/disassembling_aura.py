from decimal import Decimal

from defabipedia.aura import Abis
from typing_extensions import TypedDict
from web3 import Web3
from web3.types import ChecksumAddress

from roles_royce.generic_method import Transactable
from roles_royce.protocols.eth import aura
from roles_royce.toolshed.disassembling.disassembling_balancer import (
    BalancerDisassembler,
    Disassembler,
    validate_percentage,
)


class Exit1ArgumentElement(TypedDict):
    rewards_address: str


class Exit21ArgumentElement(TypedDict):
    rewards_address: str
    max_slippage: float


class Exit22ArgumentElement(TypedDict):
    rewards_address: str
    max_slippage: float
    token_out_address: str


class AuraDisassembler(Disassembler):
    def aura_contracts_helper(self, aura_rewards_address: ChecksumAddress, fraction: float | Decimal) -> (str, int):
        aura_rewards_contract = self.w3.eth.contract(
            address=aura_rewards_address, abi=Abis[self.blockchain].BaseRewardPool.abi
        )
        aura_token_amount = aura_rewards_contract.functions.balanceOf(self.avatar_safe_address).call()
        bpt_address = aura_rewards_contract.functions.asset().call()

        amount_to_redeem = int(Decimal(aura_token_amount) * Decimal(fraction))

        return bpt_address, amount_to_redeem

    def exit_1(self, percentage: float, exit_arguments: list[Exit1ArgumentElement]) -> list[Transactable]:
        """Withdraw funds from Aura.

        Args:
            percentage (float): Percentage of liquidity to remove from Aura.
            exit_arguments (list[dict]): List of dictionaries with the Aura rewards addresses to withdraw from.
                arg_dicts = [
                        {
                            "rewards_address": "0xsOmEAddResS"
                        }
                ]

        Returns:
            list[Transactable]: List of transactions to execute.
        """

        fraction = validate_percentage(percentage)

        txns = []

        for element in exit_arguments:
            aura_rewards_address = Web3.to_checksum_address(element["rewards_address"])

            bpt_address, amount_to_redeem = self.aura_contracts_helper(
                aura_rewards_address=aura_rewards_address, fraction=fraction
            )
            if amount_to_redeem == 0:
                return []
            withdraw_aura = aura.WithdrawAndUndwrapStakedBPT(
                reward_address=aura_rewards_address, amount=amount_to_redeem
            )
            txns.append(withdraw_aura)

        return txns

    def exit_2_1(self, percentage: float, exit_arguments: list[Exit21ArgumentElement]) -> list[Transactable]:
        """Withdraw funds from Aura and then from the Balancer pool withdrawing all assets in proportional way
        (not used for pools in recovery mode!).

        Args:
            percentage (float): Percentage of liquidity to remove from Aura.
            exit_arguments (list[dict]): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "rewards_address": 0xsOmEAddResS",
                        "max_slippage": 1.27
                    }
                ]

        Returns:
            list[Transactable]: List of transactions to execute.
        """

        fraction = validate_percentage(percentage)

        txns = []

        for element in exit_arguments:
            aura_rewards_address = Web3.to_checksum_address(element["rewards_address"])
            max_slippage = element["max_slippage"]

            bpt_address, amount_to_redeem = self.aura_contracts_helper(
                aura_rewards_address=aura_rewards_address, fraction=fraction
            )

            if amount_to_redeem == 0:
                return []

            withdraw_aura = aura.WithdrawAndUndwrapStakedBPT(
                reward_address=aura_rewards_address, amount=amount_to_redeem
            )

            balancer_disassembler = BalancerDisassembler(
                w3=self.w3,
                avatar_safe_address=self.avatar_safe_address,
                roles_mod_address=self.roles_mod_address,
                role=self.role,
                signer_address=self.signer_address,
            )

            withdraw_balancer = balancer_disassembler.exit_1_1(
                percentage=100,
                exit_arguments=[{"bpt_address": bpt_address, "max_slippage": max_slippage}],
                amount_to_redeem=amount_to_redeem,
            )

            txns.append(withdraw_aura)
            for transactable in withdraw_balancer:
                txns.append(transactable)

        return txns

    def exit_2_2(self, percentage: float, exit_arguments: list[Exit22ArgumentElement]) -> list[Transactable]:
        """Withdraw funds from Aura and then from the Balancer pool withdrawing a single asset specified by the
        token index.

        Args:
            percentage (float): Percentage of liquidity to remove from Aura.
            exit_arguments (list[dict]): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "rewards_address": "0xsOmEAddResS",
                        "max_slippage": 0.1,
                        token_out_address": "0xAnoThERAdDResS"
                    }
                ]

        Returns:
            list[Transactable]: List of transactions to execute.
        """

        fraction = validate_percentage(percentage)

        txns = []

        for element in exit_arguments:
            aura_rewards_address = Web3.to_checksum_address(element["rewards_address"])
            max_slippage = element["max_slippage"]
            token_out_address = Web3.to_checksum_address(element["token_out_address"])

            bpt_address, amount_to_redeem = self.aura_contracts_helper(
                aura_rewards_address=aura_rewards_address, fraction=fraction
            )

            if amount_to_redeem == 0:
                return []

            withdraw_aura = aura.WithdrawAndUndwrapStakedBPT(
                reward_address=aura_rewards_address, amount=amount_to_redeem
            )

            balancer_disassembler = BalancerDisassembler(
                w3=self.w3,
                avatar_safe_address=self.avatar_safe_address,
                roles_mod_address=self.roles_mod_address,
                role=self.role,
                signer_address=self.signer_address,
            )

            withdraw_balancer = balancer_disassembler.exit_1_2(
                percentage=100,
                exit_arguments=[
                    {"bpt_address": bpt_address, "max_slippage": max_slippage, "token_out_address": token_out_address}
                ],
                amount_to_redeem=amount_to_redeem,
            )

            txns.append(withdraw_aura)
            for transactable in withdraw_balancer:
                txns.append(transactable)

        return txns

    def exit_2_3(self, percentage: float, exit_arguments: list[Exit1ArgumentElement]) -> list[Transactable]:
        """Withdraw funds from Aura and then from the Balancer pool withdrawing all assets in proportional way when
        pool is in recovery mode.

        Args:
            percentage (float): Percentage of liquidity to remove from Aura.
            exit_arguments (list[dict]): List of dictionaries with the withdrawal parameters.
                arg_dicts = [
                    {
                        "rewards_address": "0xsOmEAddResS"
                    }
                ]

        Returns:
            list[Transactable]: List of transactions to execute.
        """

        fraction = validate_percentage(percentage)

        txns = []

        for element in exit_arguments:
            aura_rewards_address = Web3.to_checksum_address(element[0]["value"])

            bpt_address, amount_to_redeem = self.aura_contracts_helper(
                aura_rewards_address=aura_rewards_address, fraction=fraction
            )

            if amount_to_redeem == 0:
                return []

            withdraw_aura = aura.WithdrawAndUndwrapStakedBPT(
                reward_address=aura_rewards_address, amount=amount_to_redeem
            )

            balancer_disassembler = BalancerDisassembler(
                w3=self.w3,
                avatar_safe_address=self.avatar_safe_address,
                roles_mod_address=self.roles_mod_address,
                role=self.role,
                signer_address=self.signer_address,
            )

            withdraw_balancer = balancer_disassembler.exit_1_3(
                percentage=100, exit_arguments=[{"bpt_address": bpt_address}], amount_to_redeem=amount_to_redeem
            )

            txns.append(withdraw_aura)
            for transactable in withdraw_balancer:
                txns.append(transactable)

        return txns
