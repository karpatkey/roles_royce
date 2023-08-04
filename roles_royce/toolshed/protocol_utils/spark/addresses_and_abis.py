from roles_royce.constants import Chain
from roles_royce.abis_utils import load_abi
addresses = {
    Chain.ETHEREUM: {
        "maker_pot": "0x197E90f9FAD81970bA7976f33CbD77088E5D7cf7"
    }
}
maker_pot_abi = load_abi('maker_pot.json')
