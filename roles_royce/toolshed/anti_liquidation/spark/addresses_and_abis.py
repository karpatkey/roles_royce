import json

addresses = {
    "ethereum": {
        "protocol_data_provider": "0xFc21d6d146E6086B8359705C8b28512a983db0cb",
        "pool_addresses_provider": "0x02C3eA4e34C0cBd694D2adFa2c690EECbC1793eE",
        "chainlink_native_usd": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"
    }
}

with open('abis/protocol_data_provider.json', "r") as file:
    protocol_data_provider_abi = json.load(file)

with open('abis/pool_addresses_provider.json', "r") as file:
    pool_addresses_provider_abi = json.load(file)

with open('abis/chainlink_native_usd.json', "r") as file:
    chainlink_native_usd_abi = json.load(file)

with open('abis/price_oracle.json', "r") as file:
    price_oracle_abi = json.load(file)

with open('abis/erc20.json', "r") as file:
    erc20_abi = json.load(file)

with open('abis/lending_pool.json', "r") as file:
    lending_pool_abi = json.load(file)