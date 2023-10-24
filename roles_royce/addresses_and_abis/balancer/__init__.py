from roles_royce.constants import Chain
from roles_royce.abi_utils import load_abi, AddressOrAbi
from ..tokens import Abis as TokenAbis


class Abis(TokenAbis): # The inheritance with TokenAbis adds the ERC20 abi
    ComposableStablePool = AddressOrAbi(abi=load_abi('composable_stable_pool.json'), name='composable_stable_pool')
    WeightedPool = AddressOrAbi(abi=load_abi('weighted_pool.json'), name='weighted_pool')
    MetaStablePool = AddressOrAbi(abi=load_abi('meta_stable_pool.json'), name='meta_stable_pool')
    StablePool = AddressOrAbi(abi=load_abi('stable_pool.json'), name='stable_pool')
    # The universal_bpt contains all the functions of all kinds of pools
    UniversalBPT = AddressOrAbi(abi=load_abi('universal_bpt.json'), name='universal_bpt')
    Gauge = AddressOrAbi(abi=load_abi('gauge.json'), name='gauge')


class EthereumAddresses:
    Vault = AddressOrAbi(address='0xBA12222222228d8Ba445958a75a0704d566BF2C8',
                         abi=load_abi('vault.json'),
                         name='vault')
    Queries = AddressOrAbi(address="0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5",
                           abi=load_abi('queries.json'),
                           name='queries')


class EthereumAddressesAndAbis(Abis, EthereumAddresses):
    pass


class GnosisAddresses:
    Vault = AddressOrAbi(address='0xBA12222222228d8Ba445958a75a0704d566BF2C8',
                         abi=load_abi('vault.json'),
                         name='vault')
    Queries = AddressOrAbi(address="0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5",
                           abi=load_abi('queries.json'),
                           name='queries')


class GnosisAddressesAndAbis(Abis, GnosisAddresses):
    pass


AddressesAndAbis = {
    Chain.Ethereum: EthereumAddressesAndAbis,
    Chain.Gnosis: GnosisAddressesAndAbis
}
