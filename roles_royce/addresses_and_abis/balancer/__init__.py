from roles_royce.constants import Chains
from roles_royce.abi_utils import load_abi, ContractSpec, ContractAbi
from ..tokens import Abis as TokenAbis


class Abis(TokenAbis):  # The inheritance with TokenAbis adds the ERC20 abi
    ComposableStablePool = ContractAbi(abi=load_abi('composable_stable_pool.json'), name='composable_stable_pool')
    WeightedPool = ContractAbi(abi=load_abi('weighted_pool.json'), name='weighted_pool')
    MetaStablePool = ContractAbi(abi=load_abi('meta_stable_pool.json'), name='meta_stable_pool')
    StablePool = ContractAbi(abi=load_abi('stable_pool.json'), name='stable_pool')
    # The universal_bpt contains all the functions of all kinds of pools
    UniversalBPT = ContractAbi(abi=load_abi('universal_bpt.json'), name='universal_bpt')
    Gauge = ContractAbi(abi=load_abi('gauge.json'), name='gauge')


class EthereumContractSpecs:
    Vault = ContractSpec(address='0xBA12222222228d8Ba445958a75a0704d566BF2C8',
                         abi=load_abi('vault.json'),
                         name='vault')
    Queries = ContractSpec(address="0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5",
                           abi=load_abi('queries.json'),
                           name='queries')


class GnosisContractSpecs:
    Vault = ContractSpec(address='0xBA12222222228d8Ba445958a75a0704d566BF2C8',
                         abi=load_abi('vault.json'),
                         name='vault')
    Queries = ContractSpec(address="0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5",
                           abi=load_abi('queries.json'),
                           name='queries')


ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs,
    Chains.Gnosis: GnosisContractSpecs
}

Abis = {
    Chains.Ethereum: Abis,
}
