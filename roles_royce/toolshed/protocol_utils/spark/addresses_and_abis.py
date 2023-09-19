from roles_royce.constants import Chain
from roles_royce.abi_utils import load_abi, AddressOrAbi


class EthereumAddressesAndAbis:
    ProtocolDataProvider = AddressOrAbi(address='0xFc21d6d146E6086B8359705C8b28512a983db0cb',
                                        abi=load_abi('protocol_data_provider.json'),
                                        name='protocol_data_provider')
    MakerPot = AddressOrAbi(address='0x197E90f9FAD81970bA7976f33CbD77088E5D7cf7',
                            abi=load_abi('maker_pot.json'),
                            name='maker_pot')


AddressesAndAbis = {
    Chain.Ethereum: EthereumAddressesAndAbis
}