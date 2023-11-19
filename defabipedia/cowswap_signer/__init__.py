from ..types import Chains, load_abi, ContractSpec, ContractAbi
from ..tokens import Abis as TokenAbis


class GnosisContractSpecs:
    CowswapSigner = ContractSpec(address='0xE522f854b978650Dc838Ade0e39FbC1417A2FfB0',
                         abi=load_abi('cowswap_signer.json'),
                         name='cowswap_signer')
    
ContractSpecs = {
    Chains.Gnosis: GnosisContractSpecs
}