from roles_royce.constants import Chain
from roles_royce.abi_utils import load_abi, AddressOrAbi
from ..tokens import Abis as TokenAbis


class Abis(TokenAbis):  # The inheritance with TokenAbis adds the ERC20 abi
    PriceOracle = AddressOrAbi(abi=load_abi('price_oracle.json'), name='price_oracle')
    LendingPool = AddressOrAbi(abi=load_abi('lending_pool.json'), name='lending_pool')


class EthereumAddresses:
    ProtocolDataProvider = AddressOrAbi(address='0xFc21d6d146E6086B8359705C8b28512a983db0cb',
                                        abi=load_abi('protocol_data_provider.json'),
                                        name='protocol_data_provider')
    PoolAddressesProvider = AddressOrAbi(address='0x02C3eA4e34C0cBd694D2adFa2c690EECbC1793eE',
                                         abi=load_abi('pool_addresses_provider.json'),
                                         name='pool_addresses_provider')


class EthereumAddressesAndAbis(Abis, EthereumAddresses):
    pass


AddressesAndAbis = {
    Chain.Ethereum: EthereumAddressesAndAbis
}
