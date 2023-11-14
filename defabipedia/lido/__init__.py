from ..types import Chains, load_abi, ContractSpec, ContractAbi
from ..tokens import Abis as TokenAbis

class EthereumContractSpecs:
    stETH = ContractSpec(address='0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84',
                                        abi=load_abi('steth.json'),
                                        name='steth')
    wstETH = ContractSpec(address='0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0',
                                         abi=load_abi('wsteth.json'),
                                         name='wsteth')

class GnosisContractSpecs:
    #TODO not available at this point in gc
    # stETH = ContractSpec(address='0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84',
    #                                     abi=load_abi('steth.json'),
    #                                     name='steth')
    wstETH = ContractSpec(address='0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6',
                                         abi=load_abi('wsteth.json'),
                                         name='wsteth')

ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs,
    Chains.Gnosis: GnosisContractSpecs
}
