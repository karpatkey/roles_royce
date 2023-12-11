from ..types import Chains, load_abi, ContractSpec, ContractAbi
from ..tokens import Abis as TokenAbis


class EthereumContractSpecs:
    xDaiBridge = ContractSpec(address='0x4aa42145Aa6Ebf72e164C9bBC74fbD3788045016',
                              abi=load_abi('xdai_bridge.json'),
                              name='xdai_bridge')


class GnosisContractSpecs:
    BridgeInterestReceiver = ContractSpec(address='0x670daeaF0F1a5e336090504C68179670B5059088',
                                          abi=load_abi('BRIDGE_INTEREST_RECEIVER.json'),
                                          name='bridge_interest_receiver')


ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs,
    Chains.Gnosis: GnosisContractSpecs
}
