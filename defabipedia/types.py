import inspect
import json
import os
from dataclasses import dataclass

from web3 import Web3

__all__ = ['Blockchain', 'Chains', 'load_abi', 'load_local_abi', 'ContractSpec',
           'ContractAbi', 'ContractAddress']

@dataclass
class Blockchain:
    name: str
    chain_id: int

    def __str__(self):
        return self.name

    def __hash__(self):
        return self.chain_id


class Chains:
    Ethereum = Blockchain("ethereum", 0x1)
    Polygon = Blockchain("polygon", 0x89)
    Avalanche = Blockchain("avalanche", 0xA86A)
    Binance = Blockchain("binance", 0x38)
    Fantom = Blockchain("fantom", 0xFA)
    Gnosis = Blockchain("gnosisChain", 0x64)
    Arbitrum = Blockchain("arbitrum", 0xA4B1)
    Optimism = Blockchain("optimism", 0xA)

    _by_id = {}
    for attr_name, attr_value in locals().copy().items():
        if isinstance(attr_value, Blockchain):
            _by_id[attr_value.chain_id] = attr_value

    @classmethod
    def get_blockchain_by_chain_id(cls, chain_id) -> Blockchain:
        try:
            return cls._by_id.get(chain_id, None)
        except KeyError:
            raise ValueError(f"No Blockchain with chain_id {chain_id} found in Chain.")

    @classmethod
    def get_blockchain_from_web3(cls, w3: Web3) -> Blockchain:
        return cls.get_blockchain_by_chain_id(w3.eth.chain_id)


def load_abi(abi_filename):
    """Loads an ABI from a file placed in the same directory the call is made"""
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame[1]
    caller_file_directory = os.path.dirname(caller_filename)
    file_path = os.path.join(caller_file_directory, abi_filename)
    with open(file_path) as f:
        return json.load(f)


def load_local_abi(abi_filename):
    """Loads an ABI from the local abi directory placed in the same directory the call is made."""
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame[1]
    caller_file_directory = os.path.dirname(caller_filename)
    file_path = os.path.join(caller_file_directory, './abis', abi_filename)
    with open(file_path) as f:
        return json.load(f)


@dataclass
class ContractSpec:
    address: str
    name: str
    abi: str

    def __post_init__(self):
        if self.address is not None:
            self.address = Web3.to_checksum_address(self.address)

    def __str__(self):
        return self.name

    def contract(self, w3: Web3):
        return w3.eth.contract(address=self.address, abi=self.abi)


@dataclass
class ContractAbi:
    name: str
    abi: str

    def __str__(self):
        return self.name


@dataclass
class ContractAddress:
    name: str
    address: str

    def __str__(self):
        return self.name
