from dataclasses import dataclass, field
from web3.types import Address, ChecksumAddress, TxReceipt, TxParams
from web3 import Web3
from defabipedia.types import Blockchain, Chains
from roles_royce.utils import TenderlyCredentials, tenderly_share_simulation, simulate_tx
from roles_royce import roles
from roles_royce.generic_method import Transactable


class Disassembler:
    def __init__(self,
                 w3: Web3,
                 avatar_safe_address: Address | ChecksumAddress | str,
                 roles_mod_address: Address | ChecksumAddress | str,
                 role: int,
                 tenderly_credentials: TenderlyCredentials = None,
                 signer_address: Address | ChecksumAddress | str | None = None
                 ):
        self.w3 = w3
        self.avatar_safe_address = Web3.to_checksum_address(avatar_safe_address)
        self.roles_mod_address = Web3.to_checksum_address(roles_mod_address)
        self.role = role
        self.blockchain: Blockchain = Chains.get_blockchain_from_web3(self.w3)
        self.tenderly_credentials = tenderly_credentials
        self.signer_address = signer_address

    def simulate(self, txns: list[Transactable], from_address: Address | ChecksumAddress | str | None = None) -> (object, str):
        """Simulate the multisend batched transactions with Tenderly.

        Args:
            txns (list[Transactable]): List of transactions to simulate
            from_address (Address | ChecksumAddress | str, optional): Address to simulate the transactions from.
            Defaults to None. If None, self.signer_address must be provided.

        Returns:
            str: Tenderly simulation link
        """
        if from_address:
            account = from_address
        elif self.signer_address:
            account = self.signer_address
        else:
            raise ValueError("Either from_address or self.signer_address must be provided.")

        tx = roles.build(txns,
                         role=self.role,
                         account=account,
                         roles_mod_address=self.roles_mod_address,
                         web3=self.w3)
        block = self.w3.eth.block_number
        sim_data = simulate_tx(tx,
                               block=block,
                               account_id=self.tenderly_credentials.account_id,
                               project=self.tenderly_credentials.project,
                               api_token=self.tenderly_credentials.api_token,
                               sim_type='quick')
        simulate_link = tenderly_share_simulation(account_id=self.tenderly_credentials.account_id,
                                                  project=self.tenderly_credentials.project,
                                                  api_token=self.tenderly_credentials.api_token,
                                                  simulation_id=sim_data['simulation']['id'])
        return sim_data, simulate_link

    def send(self, txns: list[Transactable], private_key: str, w3: Web3 = None) -> TxReceipt:
        """Execute the multisend batched transactions.

        Args:
            txns (list[Transactable]): List of transactions to execute
            private_key (str): Private key of the account to execute the transactions from
            w3 (Web3): Web3 instance to execute the transactions from that would override the self.w3 instance if w3 is
                not None. Useful for nodes with MEV protection to be used only for eth_sendTransaction. Defaults to None

        Returns:
            TxReceipt: Transaction receipt
        """
        if w3 is None:
            w3 = self.w3
        return roles.send(txns,
                          role=self.role,
                          private_key=private_key,
                          roles_mod_address=self.roles_mod_address,
                          web3=w3)

    def check(self, txns: list[Transactable], block: int | str = 'latest',
              from_address: Address | ChecksumAddress | str | None = None) -> TxParams:
        """Checks the multisend batched transactions with static call.

        Args:
            txns (list[Transactable]): List of transactions to execute
            block: int | str = 'latest': block number to check the tx
            from_address (Address | ChecksumAddress | str, optional): from address to build the transaction.
        Returns:
            TxReceipt: Transaction receipt
        """
        if from_address:
            account = from_address
        elif self.signer_address:
            account = self.signer_address
        else:
            raise ValueError("Either from_address or self.signer_address must be provided.")
        return roles.check(txns,
                           role=self.role,
                           account=account,
                           roles_mod_address=self.roles_mod_address,
                           web3=self.w3,
                           block=block)

    def build(self, txns: list[Transactable], from_address: Address | ChecksumAddress | str | None = None) -> TxParams:
        """Execute the multisend batched transactions.

        Args:
            txns (list[Transactable]): List of transactions to execute
            from_address (Address | ChecksumAddress | str, optional): from address to build the transaction.
        Returns:
            TxReceipt: Transaction receipt
        """
        if from_address is not None:
            account = from_address
        elif self.signer_address is not None:
            account = self.signer_address
        else:
            raise ValueError("Either from_address or self.signer_address must be provided.")
        return roles.build(txns,
                           role=self.role,
                           account=account,
                           roles_mod_address=self.roles_mod_address,
                           web3=self.w3)


def validate_percentage(percentage: float) -> float:
    if percentage <= 0 or percentage > 100:
        raise ValueError("Percentage of liquidity to remove must be greater than 0 and less or equal than 100.")
    else:
        return percentage / 100
