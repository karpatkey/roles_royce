import functools
import logging
from typing import List

from defabipedia.types import Blockchain, Chain
from eth_abi import abi
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from web3 import Web3

from .generic_method import Transactable, TxData
from .roles_modifier import Operation

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


MULTISENDS = {
    Chain.ETHEREUM: "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",
    Chain.GNOSIS: "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",
}


class MultiSendOffline(MultiSend):
    def __init__(self, address, chain_id: int):
        self.chain_id = chain_id
        super().__init__(ethereum_client=None, address=address)

    def build_tx_data(self, multi_send_txs: List[MultiSendTx]) -> bytes:
        multisend_contract = self.get_contract()
        encoded_multisend_data = b"".join([x.encoded_data for x in multi_send_txs])
        return multisend_contract.functions.multiSend(encoded_multisend_data).build_transaction(
            {"gas": 1, "gasPrice": 1, "chainId": self.chain_id}
        )["data"]


def _make_multisend(txs: List[Transactable], blockchain: Blockchain) -> tuple:
    multisend_address = MULTISENDS.get(blockchain)
    transactions = [MultiSendTx(MultiSendOperation.CALL, tx.contract_address, tx.value, tx.data) for tx in txs]
    data = MultiSendOffline(
        address=multisend_address,
        chain_id=blockchain.chain_id,
    ).build_tx_data(transactions)
    return multisend_address, data


def multi_or_one(txs: List[Transactable], blockchain: Blockchain) -> TxData:
    if len(txs) > 1:
        contract_address, data = _make_multisend(txs, blockchain)
        return TxData(contract_address=contract_address, data=data, operation=Operation.DELEGATE_CALL, value=0)
    elif len(txs) == 1:
        return txs[0]
    else:
        raise ValueError("No transactions found")
