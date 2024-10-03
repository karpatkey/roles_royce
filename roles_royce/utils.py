import functools
import logging
from typing import List

from defabipedia.types import Blockchain
from eth_abi import abi
from web3 import Web3

from .generic_method import Transactable
from .protocols.multisend import MULTISENDS_DEPLOYS as MULTISENDS  # For backwards compat
from .protocols.multisend import MultiSend

TENDERLY_API_URL = "https://api.tenderly.co/api/v1/"
TENDERLY_DASHBOARD_URL = "https://dashboard.tenderly.co/"

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1000)
def to_selector(short_signature):
    return Web3.keccak(text=short_signature).hex()[:10]


@functools.lru_cache(maxsize=1000)
def to_checksum_address(address):
    return Web3.to_checksum_address(address)


def to_data_input(name, signature, args):
    encoded_signature = to_selector(name + signature)
    encoded_args = abi.encode([signature], [args]).hex()
    return f"{encoded_signature}{encoded_args}"


def multi_or_one(txs: List[Transactable], blockchain: Blockchain) -> Transactable:
    if len(txs) > 1:
        multisend_method = MultiSend.from_transactables(blockchain, txs)
        return multisend_method
    elif len(txs) == 1:
        return txs[0]
    else:
        raise ValueError("No transactions found")
