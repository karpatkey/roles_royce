from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from web3 import Web3, exceptions
from web3.types import Address, ChecksumAddress
from eth_account import Account


class TransactionWouldBeReverted(Exception):
    pass


class Operation(IntEnum):
    CALL = 0
    DELEGATE_CALL = 1


@dataclass
class RolesMod:
    """A class to handle role-based transactions on a blockchain."""

    role: int
    contract_address: Address | ChecksumAddress | str
    web3: Web3
    value: int = 0
    private_key: Optional[str] = None
    account: Optional[str] = None
    contract_abi: str = (
        '[{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},'
        '{"internalType":"bytes","name":"data","type":"bytes"},{"internalType":"enum Enum.Operation","name":"operation","type":"uint8"},'
        '{"internalType":"uint16","name":"role","type":"uint16"},{"internalType":"bool","name":"shouldRevert","type":"bool"}],"name":"execTransactionWithRole",'
        '"outputs":[{"internalType":"bool","name":"success","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]'
    )
    operation: Operation = Operation.CALL
    should_revert: bool = True
    nonce: Optional[int] = None

    def __post_init__(self):
        if not self.private_key and not self.account:
            raise ValueError("Either 'private_key' or 'account' must be filled.")
        if self.private_key:
            self.account = Account.from_key(self.private_key)
            self.account = self.account.address
        self.contract = self.web3.eth.contract(
            address=self.contract_address, abi=self.contract_abi
        )

    def get_base_fee_per_gas(self) -> int:
        latest_block = self.web3.eth.get_block("latest")
        base_fee_per_gas = latest_block["baseFeePerGas"]
        return base_fee_per_gas

    def check(self, contract_address: str, data: str, block='latest') -> bool:
        """make a static call to validate a transaction."""
        try:
            self._build_exec_transaction(contract_address, data).call({"from": self.account}, block_identifier=block)
            return True
        except exceptions.ContractLogicError:
            return False

    def estimate_gas(self, contract_address: str, data: str, block='latest') -> int:
        return self._build_exec_transaction(contract_address, data).estimate_gas({"from": self.account}, block_identifier=block)

    def execute(self,
                contract_address: str,
                data: str,
                max_priority_fee: int = None,
                max_fee_per_gas: int = None,
                check: bool = True,
                fee_multiplier: float = 1.2,
                gas_limit_multiplier: float = 1.1
                ) -> str:
        """Execute a role-based transaction. Returns the transaction hash as a str."""

        if check and not self.check(contract_address, data):
            raise TransactionWouldBeReverted()

        if not max_priority_fee:
            max_priority_fee = self.web3.eth.max_priority_fee

        if not max_fee_per_gas:
            max_fee_per_gas = max_priority_fee + int(self.get_base_fee_per_gas() * fee_multiplier)

        gas_limit = int(self.estimate_gas(contract_address, data) * gas_limit_multiplier)

        nonce = self.nonce or self.web3.eth.get_transaction_count(self.account)

        tx = self._build_transaction(contract_address, data, gas_limit, max_priority_fee, max_fee_per_gas, nonce)
        signed_txn = self._sign_transaction(tx)
        executed_txn = self._send_raw_transaction(signed_txn.rawTransaction)
        return executed_txn.hex()

    def _build_exec_transaction(self, contract_address: str, data: str):
        return self.contract.functions.execTransactionWithRole(
            contract_address,
            self.value,
            data,
            self.operation,
            self.role,
            self.should_revert,
        )

    def _build_transaction(self, contract_address: str,
                           data: str,
                           gas_limit: int,
                           max_priority_fee: int,
                           max_gas: int,
                           nonce: int):

        tx = self._build_exec_transaction(contract_address, data).build_transaction(
            {
                "chainId": self.web3.eth.chain_id,
                "gas": gas_limit,
                "maxFeePerGas": max_gas,
                "maxPriorityFeePerGas": max_priority_fee,
                "nonce": nonce,
            }
        )
        return tx

    def _sign_transaction(self, tx):
        return self.web3.eth.account.sign_transaction(tx, self.private_key)

    def _send_raw_transaction(self, raw_transaction):
        return self.web3.eth.send_raw_transaction(raw_transaction)

    def get_tx_receipt(self, tx_hash: str):
        try:
            transaction_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return transaction_receipt
        except exceptions.TransactionNotFound:
            return "Transaction not yet on blockchain"
