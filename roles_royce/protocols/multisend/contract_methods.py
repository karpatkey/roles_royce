from defabipedia import Blockchain
from defabipedia.multisend import ContractSpecs
from hexbytes import HexBytes

from roles_royce import Transactable
from roles_royce.protocols.base import ContractMethod, Operation


def encode_multisend_tx(operation: int, to, value: int, data: str):
    data = HexBytes(data) if data else b""
    operation = HexBytes("{:0>2x}".format(operation))  # Operation 1 byte
    to = HexBytes("{:0>40x}".format(int(to, 16)))  # Address 20 bytes
    value = HexBytes("{:0>64x}".format(value))  # Value 32 bytes
    data_length = HexBytes("{:0>64x}".format(len(data)))  # Data length 32 bytes
    return operation + to + value + data_length + data


class MultiSend(ContractMethod):
    """Sends multiple transactions and reverts all if one fails.

    Each transaction is encoded as a packed bytes of:
    * operation as a uint8 with 0 for a call or 1 for a delegatecall (=> 1 byte)
    * to as a address (=> 20 bytes)
    * value as a uint256 (=> 32 bytes)
    * data length as a uint256 (=> 32 bytes)
    * data as bytes.
    """

    name = "multiSend"
    in_signature = [
        ("transactions", "bytes"),
    ]

    def __init__(self, blockchain: Blockchain, encoded_txns: bytes, target_address: str | None = None):
        super().__init__()
        self.operation: Operation = Operation.DELEGATE_CALL
        self.args.transactions = encoded_txns
        self.target_address = target_address or ContractSpecs[blockchain].MultiSend.address

    @classmethod
    def from_transactables(cls, blockchain: Blockchain, txns: list[Transactable], target_address: str | None = None):
        encoded_data = b"".join(
            [encode_multisend_tx(tx.operation, tx.contract_address, tx.value, tx.data) for tx in txns]
        )
        return MultiSend(blockchain, encoded_data, target_address)
