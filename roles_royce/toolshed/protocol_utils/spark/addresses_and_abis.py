from roles_royce.constants import Chain
from roles_royce.abis_utils import load_abi
addresses = {
    Chain.ETHEREUM: {
        "protocol_data_provider": "0xFc21d6d146E6086B8359705C8b28512a983db0cb",
        "maker_pot": "0x197E90f9FAD81970bA7976f33CbD77088E5D7cf7"
    }
}
protocol_data_provider_abi = load_abi('protocol_data_provider.json')
maker_pot_abi = load_abi('maker_pot.json')
