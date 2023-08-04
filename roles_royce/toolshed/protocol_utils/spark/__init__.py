import web3.eth
from web3 import Web3
from decimal import Decimal
from .addresses_and_abis import addresses, maker_pot_abi, protocol_data_provider_abi
from dataclasses import dataclass
from roles_royce.constants import Chain

@dataclass
class SparkUtils:
    """A class to handle miscellaneous useful tools for Spark protocol."""
    w3: Web3

    @staticmethod
    def get_chi(w3: Web3, block: int | str = 'latest') -> int:
        maker_pot_contract = w3.eth.contract(address=addresses[Chain.get_blockchain_by_chain_id(w3.eth.chain_id)]['maker_pot'], abi=maker_pot_abi)
        ts = w3.eth.get_block(block)['timestamp']
        rho = maker_pot_contract.functions.rho().call(block_identifier=block)
        if ts > rho:
            chi = maker_pot_contract.functions.drip().call(block_identifier=block)
        else:
            chi = maker_pot_contract.functions.chi().call(block_identifier=block)
        return chi
    @staticmethod
    def get_spark_token_addresses(self) -> list[dict]:
        blockchain = Chain.get_blockchain_by_chain_id(self.w3.eth.chain_id)
        protocol_data_provider_contract = self.w3.eth.contract(address=addresses[blockchain]['protocol_data_provider'],
                                                               abi=protocol_data_provider_abi)
        reserve_tokens = protocol_data_provider_contract.functions.getAllReservesTokens().call(block_identifier=self.block)
        spark_tokens = []
        for token in reserve_tokens:
            data = protocol_data_provider_contract.functions.getReserveTokensAddresses(token[1]).call(block_identifier=self.block)
            spark_tokens.append(
                {"underlying": token[1], "interest bearing": data[0], "stable debt": data[1], "variable debt": data[2]}
            )
        return spark_tokens
