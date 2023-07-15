from gnosis.safe import addresses, Safe, SafeOperation
from gnosis.eth import EthereumNetwork, EthereumClient
from eth_account.signers.local import LocalAccount

from roles_royce.generic_method import TxData
from roles_royce.constants import ETHAddr, Chain
from roles_royce.utils import multi_or_one


class SimpleSafe(Safe):
    """A simple Safe with one signer to be used in tests"""

    def __init__(self, address, ethereum_client: EthereumClient, signer_key):
        self.signer_key = signer_key
        super().__init__(address, ethereum_client)

    def send(self, txs: list[TxData]):
        tx = multi_or_one(txs, Chain.ETHEREUM)
        safe_tx = self.build_multisig_tx(to=tx.contract_address, value=tx.value,
                                         data=tx.data, operation=tx.operation,
                                         safe_tx_gas=500000,
                                         base_gas=500000, gas_price=1, gas_token=ETHAddr.ZERO, refund_receiver=ETHAddr.ZERO)
        safe_tx.sign(self.signer_key)
        return safe_tx.execute(self.signer_key)

    @classmethod
    def build(cls, owner: LocalAccount, node_url) -> "SimpleSafe":
        ethereum_client = EthereumClient(node_url)
        ethereum_tx_sent = cls.create(ethereum_client, deployer_account=owner,
                                             master_copy_address=addresses.MASTER_COPIES[EthereumNetwork.MAINNET][0][0],
                                             owners=[owner.address], threshold=1)

        safe = SimpleSafe(ethereum_tx_sent.contract_address, ethereum_client, signer_key=owner.key)
        return safe