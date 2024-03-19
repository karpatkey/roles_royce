from dataclasses import dataclass
from enum import Enum

from defabipedia.aave_v3 import ContractSpecs
from defabipedia.types import Chain
from web3 import Web3


class AaveV3Token(Enum):
    """An Enum to handle AaveV3 token types."""

    UNDERLYING = "underlying"
    INTEREST_BEARING = "interest_bearing"
    STABLE_DEBT = "stable_debt"
    VARIABLE_DEBT = "variable_debt"


@dataclass
class AaveV3Utils:
    """A class to handle miscellaneous tools for AaveV3 protocol."""

    w3: Web3

    @staticmethod
    def get_aave_v3_token_addresses(w3: Web3, block: int | str = "latest") -> list[dict]:
        blockchain = Chain.get_blockchain_from_web3(w3)
        protocol_data_provider_contract = w3.eth.contract(
            address=ContractSpecs[blockchain].ProtocolDataProvider.address,
            abi=ContractSpecs[blockchain].ProtocolDataProvider.abi,
        )
        reserve_tokens = protocol_data_provider_contract.functions.getAllReservesTokens().call(block_identifier=block)
        aave_v3_tokens = []
        for token in reserve_tokens:
            data = protocol_data_provider_contract.functions.getReserveTokensAddresses(token[1]).call(
                block_identifier=block
            )
            aave_v3_tokens.append(
                {
                    AaveV3Token.UNDERLYING: token[1],
                    AaveV3Token.INTEREST_BEARING: data[0],
                    AaveV3Token.STABLE_DEBT: data[1],
                    AaveV3Token.VARIABLE_DEBT: data[2],
                }
            )
        return aave_v3_tokens
