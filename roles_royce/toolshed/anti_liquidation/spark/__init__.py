from web3 import Web3
from decimal import Decimal
from .addresses_and_abis import addresses, protocol_data_provider_abi, pool_addresses_provider_abi, price_oracle_abi, \
    erc20_abi, lending_pool_abi
from roles_royce.constants import Chain
from roles_royce.protocols.eth.spark import RateModel

# Use an MEV blocker endpoint
w3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
WALLET = '0x849D52316331967b6fF1198e5E32A0eB168D039d'

from dataclasses import dataclass
from enum import IntEnum
import logging
from typing import Optional

from web3 import Web3, exceptions
from web3.types import Address, ChecksumAddress

logger = logging.getLogger(__name__)


@dataclass
class SparkCDP:
    """A class to handle a CDP in Spark protocol."""
    w3: Web3
    owner_address: Address | ChecksumAddress | str
    block: Optional[int | str] = None

    def __post_init__(self):
        if not self.w3:
            raise ValueError("'w3' must be filled.")
        if not self.owner_address:
            raise ValueError("'owner_address' must be filled.")
        self.blockchain = Chain.get_blockchain_by_chain_id(self.w3.eth.chain_id)
        self.update_data(self.block)

    def get_spark_token_addresses(self) -> list[dict]:
        blockchain = Chain.get_blockchain_by_chain_id(self.w3.eth.chain_id)
        protocol_data_provider_contract = self.w3.eth.contract(address=addresses[blockchain]['protocol_data_provider'],
                                                               abi=protocol_data_provider_abi)
        reserve_tokens = protocol_data_provider_contract.functions.getAllReservesTokens().call(block_identifier=self.block)
        spark_tokens = []
        for token in reserve_tokens:
            data = protocol_data_provider_contract.functions.getReserveTokensAddresses(token[1]).call(block_identifier=self.block)
            spark_tokens.append(
                {"underlying": token[1], "interest bearing": data[0], "stable debt": data[1], "variable debt": data[2]}
            )
        return spark_tokens

    def get_cdp_data(self) -> dict:
        spark_tokens = self.get_spark_token_addresses()

        pool_addresses_provider_contract = self.w3.eth.contract(
            address=addresses[self.blockchain]['pool_addresses_provider'],
            abi=pool_addresses_provider_abi)
        price_oracle_address = pool_addresses_provider_contract.functions.getPriceOracle().call(block_identifier=self.block)
        price_oracle_contract = self.w3.eth.contract(price_oracle_address, abi=price_oracle_abi)
        protocol_data_provider_contract = self.w3.eth.contract(
            address=addresses[self.blockchain]['protocol_data_provider'],
            abi=protocol_data_provider_abi)

        result = []

        for element in spark_tokens:
            # Decimals
            token_contract = self.w3.eth.contract(address=element['underlying'], abi=erc20_abi)
            decimals = token_contract.functions.decimals().call(block_identifier=self.block)

            # Wallet balances
            wallet_data = protocol_data_provider_contract.functions.getUserReserveData(element['underlying'],
                                                                                       self.owner_address).call(block_identifier=self.block)
            # getUserReserveData returns a list with the following data:
            # [0] = currentATokenBalance,
            # [1] = currentStableDebt,
            # [2] = currentVariableDebt,
            # [3] = principalStableDebt,
            # [4] = scaledVariableDebt,
            # [5] = stableBorrowRate,
            # [6] = liquidityRate,
            # [7] = stableRateLastUpdated,
            # [8] = usageAsCollateralEnabled

            # Liquidation threshold
            liquidation_threshold = \
                protocol_data_provider_contract.functions.getReserveConfigurationData(element['underlying']).call(block_identifier=self.block)[
                    2] / Decimal(10_000)

            # Price
            currency_unit = price_oracle_contract.functions.BASE_CURRENCY_UNIT().call(block_identifier=self.block)
            price_USD = price_oracle_contract.functions.getAssetPrice(element['underlying']).call(block_identifier=self.block) / Decimal(
                currency_unit)

            result.append(
                {"underlying_address": element['underlying'],
                 "interest_bearing_balance": wallet_data[0] / Decimal(10 ** decimals),
                 "stable_debt_balance": wallet_data[1] / Decimal(10 ** decimals),
                 "variable_debt_balance": wallet_data[2] / Decimal(10 ** decimals), "underlying_price_USD": price_USD,
                 "collateral_enabled": wallet_data[8], "liquidation_threshold": liquidation_threshold}
            )
            for element in result:
                if element["interest_bearing_balance"] == 0 and element["stable_debt_balance"] == 0 and element[
                    "variable_debt_balance"] == 0:
                    result.remove(element)
        return result

    def get_health_factor(self) -> Decimal:
        pool_addresses_provider_contract = self.w3.eth.contract(
            address=addresses[self.blockchain]['pool_addresses_provider'], abi=pool_addresses_provider_abi)
        lending_pool_address = pool_addresses_provider_contract.functions.getPool().call(block_identifier=self.block)
        lending_pool_contract = self.w3.eth.contract(address=lending_pool_address, abi=lending_pool_abi)
        health_factor = lending_pool_contract.functions.getUserAccountData(self.owner_address).call(block_identifier=self.block)[5] / Decimal(
            1_000_000_000_000_000_000)
        # getUserAccountData returns a list with the following data:
        # [0] = totalCollateralETH,
        # [1] = totalDebtETH,
        # [2] = availableBorrowsETH,
        # [3] = currentLiquidationThreshold,
        # [4] = ltv,
        # [5] = healthFactor
        return health_factor

    def update_data(self, block=None):
        if block is not None:
            self.block = block
        else:
            self.block = self.w3.eth.block_number
        self.data = self.get_cdp_data()
        self.health_factor = self.get_health_factor()

    def get_delta_of_token_to_repay(self, target_health_factor: float | Decimal, token_in_address: str,
                                    rate_model: RateModel) -> Decimal:
        cdp_data = self.data

        borrowed_amount_of_token_in_stable = 0
        borrowed_amount_of_token_in_variable = 0

        for element in cdp_data:
            if element['underlying_address'] == token_in_address:
                borrowed_amount_of_token_in_stable = element["stable_debt_balance"]
                borrowed_amount_of_token_in_variable = element["variable_debt_balance"]

                break
        if token_in_address not in [element['underlying_address'] for element in
                                    cdp_data] or (
                borrowed_amount_of_token_in_stable == 0 and borrowed_amount_of_token_in_variable == 0):
            raise ValueError('There is no borrowed amount of token %s.' % token_in_address)

        if self.health_factor >= target_health_factor * (1 - 0.01):
            return Decimal(0)

        collateral_sum = 0
        for element in cdp_data:
            if element["collateral_enabled"]:
                collateral_sum += element["interest_bearing_balance"] * element["underlying_price_USD"] * element[
                    "liquidation_threshold"]

        if rate_model is RateModel.STABLE:
            debt_type = "stable_debt_balance"
        else:
            debt_type = "variable_debt_balance"

        other_debt_sum = 0
        for element in cdp_data:
            if element['underlying_address'] != token_in_address:
                other_debt_sum += (element["stable_debt_balance"] + element["variable_debt_balance"]) * element[
                    "underlying_price_USD"]
            else:
                token_in_price = element["underlying_price_USD"]
                token_in_borrowed = element[debt_type]
        delta_of_token_to_repay = token_in_borrowed - (
                collateral_sum / Decimal(target_health_factor) - other_debt_sum) / token_in_price

        if delta_of_token_to_repay > token_in_borrowed:
            return token_in_borrowed
        else:
            return delta_of_token_to_repay
