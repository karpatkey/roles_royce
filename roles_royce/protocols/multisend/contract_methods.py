from hexbytes import HexBytes

from defabipedia import Blockchain, Chain
from roles_royce import Transactable
from roles_royce.protocols.base import ContractMethod, Operation


MULTISENDS_DEPLOYS = {
    Chain.ETHEREUM: "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",
    Chain.GNOSIS: "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",
}


def encode_multisend_tx(operation: int, to, value: int, data: str):
    data = HexBytes(data) if data else b""
    operation = HexBytes("{:0>2x}".format(operation))  # Operation 1 byte
    to = HexBytes("{:0>40x}".format(int(to, 16)))  # Address 20 bytes
    value = HexBytes("{:0>64x}".format(value))  # Value 32 bytes
    data_length = HexBytes(
        "{:0>64x}".format(len(data))
    )  # Data length 32 bytes
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

    def __init__(
            self,
            blockchain: Blockchain,
            encoded_txns: bytes,
    ):
        super().__init__()
        self.operation: Operation = Operation.DELEGATE_CALL
        self.args.transactions = encoded_txns
        self.target_address = MULTISENDS_DEPLOYS.get(blockchain)

    @classmethod
    def from_transactables(
            cls,
            blockchain: Blockchain,
            txns: list[Transactable],
    ):
        encoded_data = b"".join([encode_multisend_tx(tx.operation, tx.contract_address, tx.value, tx.data) for tx in txns])
        return MultiSend(blockchain, encoded_data)
