from web3 import Web3
from .addresses_and_abis import AddressesAndAbis
from dataclasses import dataclass
from roles_royce.constants import Chain


@dataclass
class MakerUtils:
    """A class to handle miscellaneous tools for Spark protocol."""
    w3: Web3

    @staticmethod
    def get_chi(w3: Web3, block: int | str = 'latest') -> int:
        blockchain = Chain.get_blockchain_from_web3(w3)
        maker_pot_contract = w3.eth.contract(address=AddressesAndAbis[blockchain].Pot.address, abi=AddressesAndAbis[blockchain].Pot.abi)
        ts = w3.eth.get_block(block)['timestamp']
        rho = maker_pot_contract.functions.rho().call(block_identifier=block)
        if ts > rho:
            chi = maker_pot_contract.functions.drip().call(block_identifier=block)
        else:
            chi = maker_pot_contract.functions.chi().call(block_identifier=block)
        return chi
