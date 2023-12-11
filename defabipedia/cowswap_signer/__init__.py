from ..types import Chains, load_abi, ContractSpec, ContractAbi
from ..tokens import Abis as TokenAbis

class EthereumContractSpecs:
    CowswapSigner = ContractSpec(address='0x23dA9AdE38E4477b23770DeD512fD37b12381FAB',
                         abi=load_abi('cowswap_signer.json'),
                         name='cowswap_signer')

class GnosisContractSpecs:
    CowswapSigner = ContractSpec(address='0x23dA9AdE38E4477b23770DeD512fD37b12381FAB',
                         abi=load_abi('cowswap_signer.json'),
                         name='cowswap_signer')
    
ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs,
    Chains.Gnosis: GnosisContractSpecs
}