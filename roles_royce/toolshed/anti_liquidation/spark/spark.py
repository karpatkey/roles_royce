from web3 import Web3
from decimal import Decimal
from addresses_and_abis import addresses, protocol_data_provider_abi, pool_addresses_provider_abi, chainlink_native_usd_abi, price_oracle_abi, erc20_abi, lending_pool_abi


#Use an MEV blocker endpoint
w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/HblD4Hdh1e0s5Pe_7DOcdiWMfbZ2Rx1o'))
WALLET = '0x849D52316331967b6fF1198e5E32A0eB168D039d'

def get_spark_token_addresses(w3: Web3, blockchain = 'ethereum') -> dict:
    protocol_data_provider_contract = w3.eth.contract(address=addresses[blockchain]['protocol_data_provider'], abi=protocol_data_provider_abi)
    reserve_tokens = protocol_data_provider_contract.functions.getAllReservesTokens().call()
    spark_tokens = []
    for token in reserve_tokens:
        data = protocol_data_provider_contract.functions.getReserveTokensAddresses(token[1]).call()
        spark_tokens.append(
            {"underlying": token[1], "interest bearing": data[0], "stable debt": data[1], "variable debt": data[2]}
        )
    return spark_tokens

def get_cdp_data(w3: Web3, wallet: str, blockchain='ethereum') -> dict:
    spark_tokens = get_spark_token_addresses(w3)

    pool_addresses_provider_contract = w3.eth.contract(address=addresses[blockchain]['pool_addresses_provider'], abi=pool_addresses_provider_abi)
    price_oracle_address = pool_addresses_provider_contract.functions.getPriceOracle().call()
    price_oracle_contract = w3.eth.contract(price_oracle_address, abi=price_oracle_abi)
    protocol_data_provider_contract = w3.eth.contract(address=addresses[blockchain]['protocol_data_provider'], abi=protocol_data_provider_abi)

    result = []

    for element in spark_tokens:
        #Decimals
        token_contract = w3.eth.contract(address=element['underlying'], abi=erc20_abi)
        decimals = token_contract.functions.decimals().call()

        #Wallet balances
        wallet_data = protocol_data_provider_contract.functions.getUserReserveData(element['underlying'], wallet).call()
        # getUserReserveData returns a list with the following data:
        #[0] = currentATokenBalance,
        #[1] = currentStableDebt,
        #[2] = currentVariableDebt,
        #[3] = principalStableDebt,
        #[4] = scaledVariableDebt,
        #[5] = stableBorrowRate,
        #[6] = liquidityRate,
        #[7] = stableRateLastUpdated,
        #[8] = usageAsCollateralEnabled

        #Liquidation threshold
        liquidation_threshold = protocol_data_provider_contract.functions.getReserveConfigurationData(element['underlying']).call()[2]/Decimal(10_000)

        #Price
        currency_unit = price_oracle_contract.functions.BASE_CURRENCY_UNIT().call()
        price_USD = price_oracle_contract.functions.getAssetPrice(element['underlying']).call() / Decimal(currency_unit)

        result.append(
            {"underlying_address": element['underlying'], "interest_bearing_balance": wallet_data[0]/Decimal(10**decimals), "stable_debt_balance": wallet_data[1]/Decimal(10**decimals), "variable_debt_balance": wallet_data[2]/Decimal(10**decimals), "underlying_price_USD": price_USD, "collateral_enabled": wallet_data[8], "liquidation_threshold": liquidation_threshold}
        )
        for element in result:
            if element["interest_bearing_balance"] == 0 and element["stable_debt_balance"] == 0 and element[
                "variable_debt_balance"] == 0:
                result.remove(element)
    return result


def get_delta_of_token_to_repay(w3: Web3, wallet: str, target_health_factor: float | Decimal, token_in_address: str, blockchain: str ='ethereum') -> Decimal:
    cdp_data = get_cdp_data(w3, wallet, blockchain=blockchain)

    borrowed_amount_of_token_in = 0
    for element in cdp_data:
        if element['underlying_address'] == token_in_address:
            borrowed_amount_of_token_in = element["stable_debt_balance"] + element["variable_debt_balance"]
            break
    if token_in_address not in [element['underlying_address'] for element in cdp_data] or borrowed_amount_of_token_in == 0:
        raise ValueError('There is no borrowed amount of token %s.' % token_in_address)

    pool_addresses_provider_contract = w3.eth.contract(address=addresses[blockchain]['pool_addresses_provider'], abi=pool_addresses_provider_abi)
    lending_pool_address = pool_addresses_provider_contract.functions.getPool().call()
    lending_pool_contract = w3.eth.contract(address=lending_pool_address, abi=lending_pool_abi)
    health_factor = lending_pool_contract.functions.getUserAccountData(wallet).call()[5] / Decimal(1_000_000_000_000_000_000)
    # getUserAccountData returns a list with the following data:
    # [0] = totalCollateralETH,
    # [1] = totalDebtETH,
    # [2] = availableBorrowsETH,
    # [3] = currentLiquidationThreshold,
    # [4] = ltv,
    # [5] = healthFactor

    if health_factor >= target_health_factor:
        return 0

    collateral_sum = 0
    for element in cdp_data:
        if element["collateral_enabled"] == True:
            collateral_sum += element["interest_bearing_balance"] * element["underlying_price_USD"] * element["liquidation_threshold"]

    debt_sum = 0
    for element in cdp_data:
        if element['underlying_address'] != token_in_address:
            debt_sum += (element["stable_debt_balance"] + element["variable_debt_balance"]) * element["underlying_price_USD"]
        else:
            token_in_price = element["underlying_price_USD"]
            token_in_borrowed = element["stable_debt_balance"] + element["variable_debt_balance"]
    delta_of_token_to_repay = token_in_borrowed - (collateral_sum/Decimal(target_health_factor) - debt_sum) / token_in_price

    if delta_of_token_to_repay > borrowed_amount_of_token_in:
        return borrowed_amount_of_token_in
    else:
        return delta_of_token_to_repay


#print(get_delta_of_token_to_repay(w3, WALLET, 2.5418113383040037545,'0x6B175474E89094C44Da98b954EedeAC495271d0F'))