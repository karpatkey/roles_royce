from ..types import Chains, load_abi, ContractSpec, ContractAbi
from ..tokens import Abis as TokenAbis

class EthereumContractSpecs:
    CowswapSigner = ContractSpec(address='0x23dA9AdE38E4477b23770DeD512fD37b12381FAB',
                         abi=load_abi('cowswap_signer.json'),
                         name='cowswap_signer')

#This is an old contract, but it's the only one we have for now (29-11-2023)
class GnosisContractSpecs:
    CowswapSigner = ContractSpec(address='0xE522f854b978650Dc838Ade0e39FbC1417A2FfB0',
                         abi=load_abi('cowswap_signer.json'),
                         name='cowswap_signer')
    
ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs,
    Chains.Gnosis: GnosisContractSpecs
}