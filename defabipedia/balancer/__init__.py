from ..types import Chains, load_abi, ContractSpec, ContractAbi
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
    BPT_COW_WETH = ContractSpec(address="0xde8C195Aa41C11a0c4787372deFBbDdAa31306D2",
                                abi=load_abi('weighted_pool.json'),
                                name='bpt_COW_WETH')
    BPT_rETH_WETH = ContractSpec(address="0x1E19CF2D73a72Ef1332C882F20534B6519Be0276",
                                 abi=load_abi('meta_stable_pool.json'),
                                 name='bpt_rETH_WETH')
    BPT_COW_GNO = ContractSpec(address="0x92762B42A06dCDDDc5B7362Cfb01E631c4D44B40",
                               abi=load_abi('weighted_pool.json'),
                               name='bpt_COW_GNO')
    LiquidityGaugeFactory = ContractSpec(address="0x4E7bBd911cf1EFa442BC1b2e9Ea01ffE785412EC",
                                            abi=load_abi('liquidity_gauge_factory.json'),
                                            name='liquidity_gauge_factory')


class GnosisContractSpecs:
    Vault = ContractSpec(address='0xBA12222222228d8Ba445958a75a0704d566BF2C8',
                         abi=load_abi('vault.json'),
                         name='vault')
    Queries = ContractSpec(address='0x0F3e0c4218b7b0108a3643cFe9D3ec0d4F57c54e',
                           abi=load_abi('queries.json'),
                           name='queries')


ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs,
    Chains.Gnosis: GnosisContractSpecs
}

Abis = {
    Chains.Ethereum: Abis,
    Chains.Gnosis: Abis
}
