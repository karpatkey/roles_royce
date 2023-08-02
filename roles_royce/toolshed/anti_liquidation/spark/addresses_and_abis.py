from roles_royce.constants import Chain
from roles_royce.abis_utils import load_abi
addresses = {
    Chain.ETHEREUM: {
        "protocol_data_provider": "0xFc21d6d146E6086B8359705C8b28512a983db0cb",
        "pool_addresses_provider": "0x02C3eA4e34C0cBd694D2adFa2c690EECbC1793eE",
        "chainlink_native_usd": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"
    }
}
protocol_data_provider_abi = load_abi('protocol_data_provider.json')
pool_addresses_provider_abi = load_abi('pool_addresses_provider.json')
chainlink_native_usd_abi = load_abi('chainlink_native_usd.json')
price_oracle_abi = load_abi('price_oracle.json')
erc20_abi = load_abi('erc20.json')
lending_pool_abi = load_abi('lending_pool.json')