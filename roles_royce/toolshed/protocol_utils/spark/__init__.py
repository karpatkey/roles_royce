from web3 import Web3
from decimal import Decimal
from .addresses_and_abis import addresses, maker_pot_abi
from dataclasses import dataclass
from roles_royce.constants import Chain

@dataclass
class SparkUtils:
    """A class to handle miscellaneous useful tools for Spark protocol."""
    w3: Web3

    @staticmethod
    def get_chi(w3: Web3, blockchain: Chain, block: int | str = 'latest') -> int:
        maker_pot_contract = w3.eth.contract(address=addresses[blockchain]['maker_pot'], abi=maker_pot_abi)
        ts = w3.eth.get_block(block)['timestamp']
        rho = maker_pot_contract.functions.rho().call(block_identifier=block)
        if ts > rho:
            chi = maker_pot_contract.functions.drip().call(block_identifier=block)
        else:
            chi = maker_pot_contract.functions.chi().call(block_identifier=block)
        return chi
