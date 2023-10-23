from roles_royce.constants import Chain, CrossChainAddr
from roles_royce.abi_utils import load_abi, AddressOrAbi


class EthereumAddressesAndAbis:
    Vault = AddressOrAbi(address=CrossChainAddr.BalancerVault,
                         abi=load_abi('vault.json'),
                         name='vault')
    Queries = AddressOrAbi(address="0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5",
                           abi=load_abi('queries.json'),
                           name='queries')
    ComposableStablePool = AddressOrAbi(abi=load_abi('composable_stable_pool.json'), name='composable_stable_pool')
    WeightedPool = AddressOrAbi(abi=load_abi('weighted_pool.json'), name='weighted_pool')
    MetaStablePool = AddressOrAbi(abi=load_abi('meta_stable_pool.json'), name='meta_stable_pool')
    StablePool = AddressOrAbi(abi=load_abi('stable_pool.json'), name='stable_pool')
    # The universal_bpt contains all the functions of all kinds of pools
    UniversalBPT = AddressOrAbi(abi=load_abi('universal_bpt.json'), name='universal_bpt')
    Gauge = AddressOrAbi(abi=load_abi('gauge.json'), name='gauge')


AddressesAndAbis = {
    Chain.Ethereum: EthereumAddressesAndAbis
}