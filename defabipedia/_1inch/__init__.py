from defabipedia.types import Chains, load_abi, ContractSpec

class EthereumContractSpecs:
    AggregationRouterV5 = ContractSpec(address='0x1111111254EEB25477B68fb85Ed929f73A960582',
                                    abi=load_abi('aggregation_router_v5.json'),
                                    name='AggregationRouterV5')

ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs
}