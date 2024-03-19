from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from defabipedia.spark import Abis, ContractSpecs
from defabipedia.tokens import erc20_contract
from defabipedia.types import Blockchain, Chain
from web3 import Web3
from web3.types import Address, ChecksumAddress

from roles_royce import roles
from roles_royce.protocols.eth import spark
from roles_royce.protocols.eth.spark import RateModel
from roles_royce.toolshed.protocol_utils.spark.utils import SparkToken, SparkUtils


class CDPData(Enum):
    UnderlyingAddress = ("underlying_address",)
    InterestBearingBalance = ("interest_bearing_balance",)
    StableDebtBalance = ("stable_debt_balance",)
    VariableDebtBalance = ("variable_debt_balance",)
    UnderlyingPriceUSD = ("underlying_price_usd",)
    CollateralEnabled = ("collateral_enabled",)
    LiquidationThreshold = "liquidation_threshold"

    def __str__(self):
        return self.name


@dataclass
class SparkCDP:
    owner_address: Address | ChecksumAddress | str
    blockchain: Blockchain
    block: int
    balances_data: list[dict]
    health_factor: Decimal

    def __str__(self):
        result = (
            f"SparkCDP(\n"
            f"  owner_address: {self.owner_address},\n"
            f"  blockchain: {self.blockchain},\n"
            f"  block: {self.block},\n"
            f"  health_factor: {self.health_factor},\n"
            f"  tokens_data: [\n"
        )
        for element in self.balances_data:
            result = result + (
                f"    {{\n"
                f"      {CDPData.UnderlyingAddress}: {element[CDPData.UnderlyingAddress]},\n"
                f"      {CDPData.InterestBearingBalance}: {element[CDPData.InterestBearingBalance]},\n"
                f"      {CDPData.StableDebtBalance}: {element[CDPData.StableDebtBalance]},\n"
                f"      {CDPData.VariableDebtBalance}: {element[CDPData.VariableDebtBalance]},\n"
                f"      {CDPData.UnderlyingPriceUSD}: {element[CDPData.UnderlyingPriceUSD]},\n"
                f"      {CDPData.CollateralEnabled}: {element[CDPData.CollateralEnabled]},\n"
                f"      {CDPData.LiquidationThreshold}: {element[CDPData.LiquidationThreshold]}\n"
            )
            result = result + f"    }},\n" if element != self.balances_data[-1] else result + f"    }}\n"
        result = result + f"  ]\n)"
        return result

    def __repr__(self):
        return f"SparkCDP dataclass for ownwer address {self.owner_address}."


@dataclass
class SparkCDPManager:
    """A class to handle a CDP in Spark protocol."""

    w3: Web3
    owner_address: Address | ChecksumAddress | str
    blockchain: Blockchain = field(init=False)
    token_addresses: list[dict] = field(init=False)
    token_addresses_block: int | str = "latest"

    def __post_init__(self):
        if not self.w3:
            raise ValueError("'w3' must be filled.")
        if not self.owner_address:
            raise ValueError("'owner_address' must be filled.")
        self.owner_address = Web3.to_checksum_address(self.owner_address)
        self.blockchain = Chain.get_blockchain_from_web3(self.w3)
        if self.token_addresses_block == "latest":
            self.token_addresses_block = self.w3.eth.block_number
        self.token_addresses = SparkUtils.get_spark_token_addresses(self.w3, block=self.token_addresses_block)

    def update_spark_token_addresses(self, block: int | str = "latest") -> None:
        """Updates the list of Spark tokens addresses."""
        if block == "latest":
            self.token_addresses_block = self.w3.eth.block_number
        else:
            self.token_addresses_block = block
        self.token_addresses = SparkUtils.get_spark_token_addresses(self.w3, block=self.token_addresses_block)

    def get_cdp_balances_data(self, block: int | str = "latest") -> list[dict]:
        """Returns a list of dictionaries with the Spark token balances data of the CDP."""
        spark_tokens = self.token_addresses

        if block == "latest":
            block = self.w3.eth.block_number

        pool_addresses_provider_contract = ContractSpecs[self.blockchain].PoolAddressesProvider.contract(self.w3)
        price_oracle_address = pool_addresses_provider_contract.functions.getPriceOracle().call(block_identifier=block)
        price_oracle_contract = self.w3.eth.contract(price_oracle_address, abi=Abis[self.blockchain].PriceOracle.abi)
        protocol_data_provider_contract = ContractSpecs[self.blockchain].ProtocolDataProvider.contract(self.w3)

        result = []

        for element in spark_tokens:
            # Decimals

            token_contract = erc20_contract(self.w3, element[SparkToken.UNDERLYING])
            decimals = token_contract.functions.decimals().call(block_identifier=block)

            # Wallet balances
            wallet_data = protocol_data_provider_contract.functions.getUserReserveData(
                element[SparkToken.UNDERLYING], self.owner_address
            ).call(block_identifier=block)
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
            liquidation_threshold = protocol_data_provider_contract.functions.getReserveConfigurationData(
                element[SparkToken.UNDERLYING]
            ).call(block_identifier=block)[2] / Decimal(10_000)

            # Price
            currency_unit = price_oracle_contract.functions.BASE_CURRENCY_UNIT().call(block_identifier=block)
            price_USD = price_oracle_contract.functions.getAssetPrice(element[SparkToken.UNDERLYING]).call(
                block_identifier=block
            ) / Decimal(currency_unit)

            result.append(
                {
                    CDPData.UnderlyingAddress: element[SparkToken.UNDERLYING],
                    CDPData.InterestBearingBalance: wallet_data[0] / Decimal(10**decimals),
                    CDPData.StableDebtBalance: wallet_data[1] / Decimal(10**decimals),
                    CDPData.VariableDebtBalance: wallet_data[2] / Decimal(10**decimals),
                    CDPData.UnderlyingPriceUSD: price_USD,
                    CDPData.CollateralEnabled: wallet_data[8],
                    CDPData.LiquidationThreshold: liquidation_threshold,
                }
            )
            for element in result:
                if (
                    element[CDPData.InterestBearingBalance] == 0
                    and element[CDPData.StableDebtBalance] == 0
                    and element[CDPData.VariableDebtBalance] == 0
                ):
                    result.remove(element)
        return result

    def get_health_factor(self, block: int | str = "latest") -> Decimal:
        """"""
        if block == "latest":
            block = self.w3.eth.block_number
        pool_addresses_provider_contract = ContractSpecs[self.blockchain].PoolAddressesProvider.contract(self.w3)
        lending_pool_address = pool_addresses_provider_contract.functions.getPool().call(block_identifier=block)
        lending_pool_contract = self.w3.eth.contract(
            address=lending_pool_address, abi=Abis[self.blockchain].LendingPool.abi
        )
        health_factor = lending_pool_contract.functions.getUserAccountData(self.owner_address).call(
            block_identifier=block
        )[5] / Decimal(1_000_000_000_000_000_000)
        # getUserAccountData returns a list with the following data:
        # [0] = totalCollateralETH,
        # [1] = totalDebtETH,
        # [2] = availableBorrowsETH,
        # [3] = currentLiquidationThreshold,
        # [4] = ltv,
        # [5] = healthFactor
        return health_factor

    def get_cdp_data(self, block: int | str = "latest") -> SparkCDP:
        if block == "latest":
            block = self.w3.eth.block_number
        balances_data = self.get_cdp_balances_data(block=block)
        health_factor = self.get_health_factor(block=block)
        return SparkCDP(
            owner_address=self.owner_address,
            blockchain=self.blockchain,
            block=block,
            balances_data=balances_data,
            health_factor=health_factor,
        )

    def check_if_token_is_in_debts(self, spark_cdp: SparkCDP, token_address: Address | ChecksumAddress | str) -> dict:
        token_address = self.w3.to_checksum_address(token_address)
        balances_data = spark_cdp.balances_data

        borrowed_amount_of_token_in_stable = 0
        borrowed_amount_of_token_in_variable = 0

        for element in balances_data:
            if element[CDPData.UnderlyingAddress] == token_address:
                borrowed_amount_of_token_in_stable = element[CDPData.StableDebtBalance]
                borrowed_amount_of_token_in_variable = element[CDPData.VariableDebtBalance]

                break

        return {
            RateModel.STABLE: True if borrowed_amount_of_token_in_stable > 0 else False,
            RateModel.VARIABLE: True if borrowed_amount_of_token_in_variable > 0 else False,
        }

    def get_delta_of_token_to_repay(
        self,
        spark_cdp: SparkCDP,
        target_health_factor: float | Decimal,
        token_in_address: str,
        rate_model: RateModel,
        block: int | str = "latest",
        tolerance: float = 0.01,
    ) -> int:
        token_in_address = Web3.to_checksum_address(token_in_address)

        if block == "latest":
            block = self.w3.eth.block_number

        token_in_decimals = erc20_contract(self.w3, token_in_address).functions.decimals().call(block_identifier=block)

        health_factor = spark_cdp.health_factor
        balances_data = spark_cdp.balances_data

        token_in_borrowed_status = self.check_if_token_is_in_debts(spark_cdp=spark_cdp, token_address=token_in_address)

        if (
            token_in_borrowed_status[RateModel.STABLE] is False
            and token_in_borrowed_status[RateModel.VARIABLE] is False
        ):
            raise ValueError("There is no borrowed amount of token %s." % token_in_address)
        elif token_in_borrowed_status[rate_model] is False and rate_model == RateModel.STABLE:
            raise ValueError("There is no stable borrowed amount of token %s." % token_in_address)
        elif token_in_borrowed_status[rate_model] is False and rate_model == RateModel.VARIABLE:
            raise ValueError("There is no variable borrowed amount of token %s." % token_in_address)

        if health_factor >= target_health_factor * (1 - tolerance):
            return 0

        collateral_sum = 0
        for element in balances_data:
            if element[CDPData.CollateralEnabled]:
                collateral_sum += (
                    element[CDPData.InterestBearingBalance]
                    * element[CDPData.UnderlyingPriceUSD]
                    * element[CDPData.LiquidationThreshold]
                )

        if rate_model is RateModel.STABLE:
            debt_type = CDPData.StableDebtBalance
        else:
            debt_type = CDPData.VariableDebtBalance

        other_debt_sum = 0
        for element in balances_data:
            if element[CDPData.UnderlyingAddress] != token_in_address:
                other_debt_sum += (element[CDPData.StableDebtBalance] + element[CDPData.VariableDebtBalance]) * element[
                    CDPData.UnderlyingPriceUSD
                ]
            else:
                token_in_price = element[CDPData.UnderlyingPriceUSD]
                token_in_borrowed = element[debt_type]
        delta_of_token_to_repay = (
            token_in_borrowed - (collateral_sum / Decimal(target_health_factor) - other_debt_sum) / token_in_price
        )

        if delta_of_token_to_repay > token_in_borrowed:
            return int(Decimal(token_in_borrowed) * Decimal(10**token_in_decimals))
        else:
            return int(Decimal(delta_of_token_to_repay) * Decimal(10**token_in_decimals))

    # TODO: the next function can be generalized so that it can repay the debts corresponding to a set of tokens
    # def repay_debt(self, spark_cdp: SparkCDP, token_in_addresses: list[str | ChecksumAddress],
    #                            rate_models: list[RateModel],
    #                            token_in_amounts: [int], roles_mod_address: str | ChecksumAddress,
    #                            role: int, private_key: str) -> object:
    def repay_single_token_debt(
        self,
        spark_cdp: SparkCDP,
        token_in_address: str | ChecksumAddress | Address,
        rate_model: RateModel,
        token_in_amount: int,
        roles_mod_address: str | ChecksumAddress | Address,
        role: int,
        private_key: str,
        w3: Web3 = None,
    ) -> object:
        token_in_address = Web3.to_checksum_address(token_in_address)
        roles_mod_address = Web3.to_checksum_address(roles_mod_address)

        token_in_borrowed_status = self.check_if_token_is_in_debts(spark_cdp=spark_cdp, token_address=token_in_address)

        if (
            token_in_borrowed_status[RateModel.STABLE] is False
            and token_in_borrowed_status[RateModel.VARIABLE] is False
        ):
            raise ValueError("There is no borrowed amount of token %s." % token_in_address)
        elif token_in_borrowed_status[rate_model] is False and rate_model == RateModel.STABLE:
            raise ValueError("There is no stable borrowed amount of token %s." % token_in_address)
        elif token_in_borrowed_status[rate_model] is False and rate_model == RateModel.VARIABLE:
            raise ValueError("There is no variable borrowed amount of token %s." % token_in_address)

        token_in_contract = erc20_contract(self.w3, token_in_address)
        pool_addresses_provider_contract = ContractSpecs[self.blockchain].PoolAddressesProvider.contract(self.w3)
        lending_pool_address = pool_addresses_provider_contract.functions.getPool().call()
        allowance = token_in_contract.functions.allowance(self.owner_address, lending_pool_address).call()

        if w3 is None:
            w3 = self.w3

        if token_in_amount > allowance:
            tx_receipt = roles.send(
                [
                    spark.ApproveToken(token=token_in_address, amount=token_in_amount),
                    spark.Repay(
                        token=token_in_address, amount=token_in_amount, rate_model=rate_model, avatar=self.owner_address
                    ),
                ],
                role=role,
                private_key=private_key,
                roles_mod_address=roles_mod_address,
                web3=w3,
            )
        elif token_in_amount == allowance:
            tx_receipt = roles.send(
                [
                    spark.Repay(
                        token=token_in_address, amount=token_in_amount, rate_model=rate_model, avatar=self.owner_address
                    ),
                ],
                role=role,
                private_key=private_key,
                roles_mod_address=roles_mod_address,
                web3=w3,
            )
        else:
            tx_receipt = roles.send(
                [
                    spark.Repay(
                        token=token_in_address, amount=token_in_amount, rate_model=rate_model, avatar=self.owner_address
                    ),
                    spark.ApproveToken(token=token_in_address, amount=0),
                ],
                role=role,
                private_key=private_key,
                roles_mod_address=roles_mod_address,
                web3=w3,
            )
        return tx_receipt
