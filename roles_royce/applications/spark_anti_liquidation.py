from roles_royce.protocols.eth.spark import WithdrawDAIforSDAI, Repay
from web3 import Web3
from roles_royce.roles import build
from decimal import Decimal

# Protocol Data Provider - Ethereum
PROTOCOL_DATA_PROVIDER = "0xFc21d6d146E6086B8359705C8b28512a983db0cb"

POOL_ADDRESSES_PROVIDER = "0x02C3eA4e34C0cBd694D2adFa2c690EECbC1793eE"

CHAINLINK_NATIVE_USD = "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CHAINLINK PRICE FEEDS
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ETHEREUM
# ETH/USD Price Feed
CHAINLINK_ETH_USD = "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Protocol Data Provider ABI
ABI_PDP = '[{"inputs":[{"internalType":"contract IPoolAddressesProvider","name":"addressesProvider","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"ADDRESSES_PROVIDER","outputs":[{"internalType":"contract IPoolAddressesProvider","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getATokenTotalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getAllATokens","outputs":[{"components":[{"internalType":"string","name":"symbol","type":"string"},{"internalType":"address","name":"tokenAddress","type":"address"}],"internalType":"struct IPoolDataProvider.TokenData[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getAllReservesTokens","outputs":[{"components":[{"internalType":"string","name":"symbol","type":"string"},{"internalType":"address","name":"tokenAddress","type":"address"}],"internalType":"struct IPoolDataProvider.TokenData[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getDebtCeiling","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getDebtCeilingDecimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getFlashLoanEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getInterestRateStrategyAddress","outputs":[{"internalType":"address","name":"irStrategyAddress","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getLiquidationProtocolFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getPaused","outputs":[{"internalType":"bool","name":"isPaused","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveCaps","outputs":[{"internalType":"uint256","name":"borrowCap","type":"uint256"},{"internalType":"uint256","name":"supplyCap","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveConfigurationData","outputs":[{"internalType":"uint256","name":"decimals","type":"uint256"},{"internalType":"uint256","name":"ltv","type":"uint256"},{"internalType":"uint256","name":"liquidationThreshold","type":"uint256"},{"internalType":"uint256","name":"liquidationBonus","type":"uint256"},{"internalType":"uint256","name":"reserveFactor","type":"uint256"},{"internalType":"bool","name":"usageAsCollateralEnabled","type":"bool"},{"internalType":"bool","name":"borrowingEnabled","type":"bool"},{"internalType":"bool","name":"stableBorrowRateEnabled","type":"bool"},{"internalType":"bool","name":"isActive","type":"bool"},{"internalType":"bool","name":"isFrozen","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveData","outputs":[{"internalType":"uint256","name":"unbacked","type":"uint256"},{"internalType":"uint256","name":"accruedToTreasuryScaled","type":"uint256"},{"internalType":"uint256","name":"totalAToken","type":"uint256"},{"internalType":"uint256","name":"totalStableDebt","type":"uint256"},{"internalType":"uint256","name":"totalVariableDebt","type":"uint256"},{"internalType":"uint256","name":"liquidityRate","type":"uint256"},{"internalType":"uint256","name":"variableBorrowRate","type":"uint256"},{"internalType":"uint256","name":"stableBorrowRate","type":"uint256"},{"internalType":"uint256","name":"averageStableBorrowRate","type":"uint256"},{"internalType":"uint256","name":"liquidityIndex","type":"uint256"},{"internalType":"uint256","name":"variableBorrowIndex","type":"uint256"},{"internalType":"uint40","name":"lastUpdateTimestamp","type":"uint40"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveEModeCategory","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveTokensAddresses","outputs":[{"internalType":"address","name":"aTokenAddress","type":"address"},{"internalType":"address","name":"stableDebtTokenAddress","type":"address"},{"internalType":"address","name":"variableDebtTokenAddress","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getSiloedBorrowing","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getTotalDebt","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getUnbackedMintCap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"address","name":"user","type":"address"}],"name":"getUserReserveData","outputs":[{"internalType":"uint256","name":"currentATokenBalance","type":"uint256"},{"internalType":"uint256","name":"currentStableDebt","type":"uint256"},{"internalType":"uint256","name":"currentVariableDebt","type":"uint256"},{"internalType":"uint256","name":"principalStableDebt","type":"uint256"},{"internalType":"uint256","name":"scaledVariableDebt","type":"uint256"},{"internalType":"uint256","name":"stableBorrowRate","type":"uint256"},{"internalType":"uint256","name":"liquidityRate","type":"uint256"},{"internalType":"uint40","name":"stableRateLastUpdated","type":"uint40"},{"internalType":"bool","name":"usageAsCollateralEnabled","type":"bool"}],"stateMutability":"view","type":"function"}]'

# Lending Pool Addresses Provider Registry ABI - getPool, getPriceOracle
ABI_LPAPR = '[{"inputs":[],"name":"getPool","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getPriceOracle","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'

# Lending Pool ABI - getUserAccountData, getReserveData
ABI_LENDING_POOL = '[{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserAccountData","outputs":[{"internalType":"uint256","name":"totalCollateralETH","type":"uint256"},{"internalType":"uint256","name":"totalDebtETH","type":"uint256"},{"internalType":"uint256","name":"availableBorrowsETH","type":"uint256"},{"internalType":"uint256","name":"currentLiquidationThreshold","type":"uint256"},{"internalType":"uint256","name":"ltv","type":"uint256"},{"internalType":"uint256","name":"healthFactor","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveData","outputs":[{"components":[{"components":[{"internalType":"uint256","name":"data","type":"uint256"}],"internalType":"struct DataTypes.ReserveConfigurationMap","name":"configuration","type":"tuple"},{"internalType":"uint128","name":"liquidityIndex","type":"uint128"},{"internalType":"uint128","name":"variableBorrowIndex","type":"uint128"},{"internalType":"uint128","name":"currentLiquidityRate","type":"uint128"},{"internalType":"uint128","name":"currentVariableBorrowRate","type":"uint128"},{"internalType":"uint128","name":"currentStableBorrowRate","type":"uint128"},{"internalType":"uint40","name":"lastUpdateTimestamp","type":"uint40"},{"internalType":"address","name":"aTokenAddress","type":"address"},{"internalType":"address","name":"stableDebtTokenAddress","type":"address"},{"internalType":"address","name":"variableDebtTokenAddress","type":"address"},{"internalType":"address","name":"interestRateStrategyAddress","type":"address"},{"internalType":"uint8","name":"id","type":"uint8"}],"internalType":"struct DataTypes.ReserveData","name":"","type":"tuple"}],"stateMutability":"view","type":"function"}]'

# ChainLink: ETH/USD Price Feed ABI - latestAnswer, decimals
ABI_CHAINLINK_ETH_USD = '[{"inputs":[],"name":"latestAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}]'

# Price Oracle ABI - getAssetPrice, BASE_CURRENCY_UNIT
ABI_PRICE_ORACLE = '[{"inputs":[],"name":"BASE_CURRENCY_UNIT","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getAssetPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# Staked Aave ABI - REWARD_TOKEN, getTotalRewardsBalance, assets, balanceOf
ABI_STKAAVE = '[{"inputs":[],"name":"REWARD_TOKEN","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"staker","type":"address"}],"name":"getTotalRewardsBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"assets","outputs":[{"internalType":"uint128","name":"emissionPerSecond","type":"uint128"},{"internalType":"uint128","name":"lastUpdateTimestamp","type":"uint128"},{"internalType":"uint256","name":"index","type":"uint256"}],"stateMutability":"view","type":"function"},\
                {"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},\
                {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"pure","type":"function"}]'

# ABI Token Simplified - name, symbol, SYMBOL, decimals, balanceOf, totalSupply
ABI_TOKEN_SIMPLIFIED = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}, {"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function"}, {"constant":true,"inputs":[],"name":"SYMBOL","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}, {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"}, {"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}, {"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'


#Use an MEV blocker endpoint
w3 = Web3(Web3.HTTPProvider('sOmeRPCeNdPOinT'))
WALLET = '0x849D52316331967b6fF1198e5E32A0eB168D039d'

def get_spark_token_addresses() -> dict:
    protocol_data_provider_contract = w3.eth.contract(address=PROTOCOL_DATA_PROVIDER, abi=ABI_PDP)
    reserve_tokens = protocol_data_provider_contract.functions.getAllReservesTokens().call()
    spark_tokens = []
    for token in reserve_tokens:
        data = protocol_data_provider_contract.functions.getReserveTokensAddresses(token[1]).call()
        spark_tokens.append(
            {"underlying": token[1], "interest bearing": data[0], "stable debt": data[1], "variable debt": data[2]}
        )
    return spark_tokens

def get_cdp_data(wallet) -> dict:
    spark_tokens = get_spark_token_addresses()

    pool_addresses_provider_contract = w3.eth.contract(address=POOL_ADDRESSES_PROVIDER, abi=ABI_LPAPR)
    price_oracle_address = pool_addresses_provider_contract.functions.getPriceOracle().call()
    price_oracle_contract = w3.eth.contract(price_oracle_address, abi=ABI_PRICE_ORACLE)
    protocol_data_provider_contract = w3.eth.contract(address=PROTOCOL_DATA_PROVIDER, abi=ABI_PDP)

    result = []

    for element in spark_tokens:
        #Decimals
        token_contract = w3.eth.contract(address=element['underlying'], abi=ABI_TOKEN_SIMPLIFIED)
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


def get_delta_of_token_to_repay(wallet, target_health_factor, token_in_address):
    cdp_data = get_cdp_data(wallet)

    borrowed_amount_of_token_in = 0
    for element in cdp_data:
        if element['underlying_address'] == token_in_address:
            borrowed_amount_of_token_in = element["stable_debt_balance"] + element["variable_debt_balance"]
            break
    if token_in_address not in [element['underlying_address'] for element in cdp_data] or borrowed_amount_of_token_in == 0:
        raise ValueError('There is no borrowed amount of token %s.' % token_in_address)

    pool_addresses_provider_contract = w3.eth.contract(address=POOL_ADDRESSES_PROVIDER, abi=ABI_LPAPR)
    lending_pool_address = pool_addresses_provider_contract.functions.getPool().call()
    lending_pool_contract = w3.eth.contract(address=lending_pool_address, abi=ABI_LENDING_POOL)
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


#print(get_delta_of_token_to_repay(WALLET, 2.553241942,'0x6B175474E89094C44Da98b954EedeAC495271d0F'))


