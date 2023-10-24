import json
import os
import inspect
from dataclasses import dataclass
from web3 import Web3


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
class AddressOrAbi:
    address: str = None
    name: str = None
    abi: str = None

    def __post_init__(self):
        if not self.address and not self.abi:
            raise ValueError("Either 'address' or 'abi' must be filled.")
        if self.address is not None:
            self.address = Web3.to_checksum_address(self.address)

    def __str__(self):
        return self.name
