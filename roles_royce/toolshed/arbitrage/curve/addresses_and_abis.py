from roles_royce.constants import Chain
from roles_royce.abi_utils import load_abi, AddressOrAbi


class GnosisChainAddressesAndAbis:
    DepositZap = AddressOrAbi(address='0xE3FFF29d4DC930EBb787FeCd49Ee5963DADf60b6',
                                   abi=load_abi('abis/curve_zap_gnosis_chain_abi.json'),
                                   name='deposit_zap_gnosis_chain')


AddressesAndAbis = {
    Chain.GnosisChain: GnosisChainAddressesAndAbis
}