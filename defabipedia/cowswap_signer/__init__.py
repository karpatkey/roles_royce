from ..types import Chains, load_abi, ContractSpec, ContractAbi
from ..tokens import Abis as TokenAbis

class EthereumContractSpecs:
    CowswapSigner = ContractSpec(address='0x23dA9AdE38E4477b23770DeD512fD37b12381FAB',
                         abi=load_abi('cowswap_signer.json'),
                         name='cowswap_signer')
    CowswapRelayer = ContractSpec(address='0xC92E8bdf79f0507f65a392b0ab4667716BFE0110',
                         abi=load_abi('cowswap_relayer.json'),
                         name='cowswap_relayer')

class GnosisContractSpecs:
    CowswapSigner = ContractSpec(address='0x23dA9AdE38E4477b23770DeD512fD37b12381FAB',
                         abi=load_abi('cowswap_signer.json'),
                         name='cowswap_signer')
    
ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs,
    Chains.Gnosis: GnosisContractSpecs
}