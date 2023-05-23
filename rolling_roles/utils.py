import logging
from typing import List

from eth_abi import abi
from web3 import Web3
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from .roles_modifier import Operation
from .constants import Blockchain, Chain
from .generic_method import TxData

logger = logging.getLogger(__name__)


def to_data_input(name, arg_types, args):
    encoded_signature = Web3.keccak(text=f"{name}({','.join(arg_types)})").hex()[:10]
    encoded_args = abi.encode(arg_types, args).hex()
    return f"{encoded_signature}{encoded_args}"


MULTISEND_CALL_ONLY = '0x40A2aCCbd92BCA938b02010E17A5b8929b49130D'
MULTISENDS = {
    Chain.ETHEREUM: '0x998739BFdAAdde7C933B942a68053933098f9EDa',
    Chain.GC: '0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761'
}


class MultiSendOffline(MultiSend):
    def __init__(self, address, chain_id: int):
        self.chain_id = chain_id
        super().__init__(ethereum_client=None, address=address)

    def build_tx_data(self, multi_send_txs: List[MultiSendTx]) -> bytes:
        multisend_contract = self.get_contract()
        encoded_multisend_data = b"".join([x.encoded_data for x in multi_send_txs])
        return multisend_contract.functions.multiSend(
            encoded_multisend_data
        ).build_transaction({"gas": 1, "gasPrice": 1, "chainId": self.chain_id})["data"]


def _make_multisend(txs: List[TxData], blockchain: Blockchain) -> tuple:
    multisend_address = MULTISENDS.get(blockchain, MULTISEND_CALL_ONLY)  # FIXME: why this default value?!
    transactions = [
        MultiSendTx(
            MultiSendOperation.CALL,
            tx.contract_address,
            tx.value,
            tx.data
        ) for tx in txs
    ]
    data = MultiSendOffline(
        address=multisend_address,
        chain_id=blockchain.chain_id,
    ).build_tx_data(transactions)
    return multisend_address, data


def multi_or_one(txs: List[TxData], blockchain: Blockchain):
    if len(txs) > 1:
        contract_address, data = _make_multisend(txs, blockchain)
        operation = Operation.DELEGATE_CALL
    elif len(txs) == 1:
        tx = txs[0]
        contract_address = tx.contract_address
        data = tx.data
        operation = tx.operation
    else:
        raise ValueError("No transactions found")
    return operation, contract_address, data
