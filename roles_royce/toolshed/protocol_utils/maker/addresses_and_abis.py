from roles_royce.constants import Chain
from roles_royce.abi_utils import load_abi, AddressOrAbi


class EthereumAddressesAndAbis:
    DsrManager = AddressOrAbi(address='0x373238337Bfe1146fb49989fc222523f83081dDb',
                                        abi=load_abi('dsr_manager.json'),
                                        name='protocol_data_provider')
    Pot = AddressOrAbi(address='0x197E90f9FAD81970bA7976f33CbD77088E5D7cf7',
                            abi=load_abi('pot.json'),
                            name='pot')


AddressesAndAbis = {
    Chain.Ethereum: EthereumAddressesAndAbis
}