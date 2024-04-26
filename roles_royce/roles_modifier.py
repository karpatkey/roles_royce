import logging
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Optional

from eth_account import Account
from web3 import Web3, exceptions
from web3.types import Address, ChecksumAddress, TxParams, TxReceipt

logger = logging.getLogger(__name__)

NORMAL_GAS_LIMIT_MULTIPLIER = 1.4
AGGRESIVE_GAS_LIMIT_MULTIPLIER = 3
NORMAL_FEE_MULTIPLER = 1.2
AGGRESIVE_FEE_MULTIPLER = 2

ROLES_ABI = (
    '[{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},'
    '{"internalType":"bytes","name":"data","type":"bytes"},{"internalType":"enum Enum.Operation","name":"operation","type":"uint8"},'
    '{"internalType":"uint16","name":"role","type":"uint16"},{"internalType":"bool","name":"shouldRevert","type":"bool"}],"name":"execTransactionWithRole",'
    '"outputs":[{"internalType":"bool","name":"success","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]'
)

ROLES_ERRORS = (
    "NoMembership()",
    "ArraysDifferentLength()",
    "FunctionSignatureTooShort()",
    "DelegateCallNotAllowed()",
    "TargetAddressNotAllowed()",
    "FunctionNotAllowed()",
    "SendNotAllowed()",
    "ParameterNotAllowed()",
    "ParameterNotOneOfAllowed()",
    "ParameterLessThanAllowed()",
    "ParameterGreaterThanAllowed()",
    "UnacceptableMultiSendOffset()",
    "UnsuitableOneOfComparison()",
    "UnsuitableRelativeComparison()",
    "UnsuitableStaticCompValueSize()",
    "UnsuitableDynamic32CompValueSize()",
    "ScopeMaxParametersExceeded()",
    "NotEnoughCompValuesForOneOf()",
    "CalldataOutOfBounds()",
)

ROLES_ERRORS_SELECTORS = {Web3.keccak(text=error).hex()[:10]: error for error in ROLES_ERRORS}


class TransactionWouldBeReverted(Exception):
    """It is used to indicate that if a transaction is executed, it will be reverted."""


class Operation(IntEnum):
    """Types of operations."""

    CALL = 0
    DELEGATE_CALL = 1


@dataclass
class GasStrategy:
    limit_multiplier: float
    fee_multiplier: float


class GasStrategies(GasStrategy, Enum):
    NORMAL = (NORMAL_GAS_LIMIT_MULTIPLIER, NORMAL_FEE_MULTIPLER)
    AGGRESIVE = (AGGRESIVE_GAS_LIMIT_MULTIPLIER, AGGRESIVE_FEE_MULTIPLER)


_gas_strategy = GasStrategies.NORMAL


def get_gas_strategy():
    """Get the global default gas strategy"""
    return _gas_strategy


def set_gas_strategy(strategy: GasStrategies):
    """Set a global default gas strategy"""
    global _gas_strategy
    _gas_strategy = strategy


@dataclass
class RolesMod:
    """A class to handle role-based transactions on a blockchain."""

    role: int
    contract_address: Address | ChecksumAddress | str
    web3: Web3
    value: int = 0
    private_key: Optional[str] = None
    account: Optional[str] = None
    contract_abi: str = ROLES_ABI
    operation: Operation = Operation.CALL
    should_revert: bool = True
    nonce: Optional[int] = None

    def __post_init__(self):
        if not self.private_key and not self.account:
            raise ValueError("Either 'private_key' or 'account' must be filled.")
        if self.private_key:
            self.account = Account.from_key(self.private_key)
            self.account = self.account.address
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.contract_abi)

    def get_base_fee_per_gas(self) -> int:
        latest_block = self.web3.eth.get_block("latest")
        base_fee_per_gas = latest_block["baseFeePerGas"]
        return base_fee_per_gas

    def build(
        self, contract_address: str, data: str, max_priority_fee: int | None = None, max_fee_per_gas: int | None = None
    ):
        """Creates a transaction ready to be sent"""
        gas_strategy = get_gas_strategy()
        if not max_priority_fee:
            max_priority_fee = self.web3.eth.max_priority_fee
        if not max_fee_per_gas:
            max_fee_per_gas = max_priority_fee + int(self.get_base_fee_per_gas() * gas_strategy.fee_multiplier)

        gas_limit = int(self.estimate_gas(contract_address, data) * gas_strategy.limit_multiplier)

        nonce = self.nonce or self.web3.eth.get_transaction_count(self.account)

        tx = self._build_transaction(contract_address, data, gas_limit, max_priority_fee, max_fee_per_gas, nonce)
        return tx

    def check(self, contract_address: str, data: str, block="latest") -> bool:
        """Make a static call to validate a transaction."""
        try:
            self._build_exec_transaction(contract_address, data).call({"from": self.account}, block_identifier=block)
            return True
        except exceptions.ContractCustomError as e:
            custom_roles_error = ROLES_ERRORS_SELECTORS.get(e.data, None)
            if custom_roles_error:
                raise TransactionWouldBeReverted(ROLES_ERRORS_SELECTORS.get(e.data))
            else:
                raise TransactionWouldBeReverted(e)

    def estimate_gas(self, contract_address: str, data: str, block="latest") -> int:
        """Estimate the gas that would be needed."""
        return self._build_exec_transaction(contract_address, data).estimate_gas(
            {"from": self.account}, block_identifier=block
        )

    def execute(
        self,
        contract_address: str,
        data: str,
        max_priority_fee: int | None = None,
        max_fee_per_gas: int | None = None,
        check: bool = True,
    ) -> str:
        """Execute a role-based transaction. Returns the transaction hash as a str."""

        if check:
            self.check(contract_address, data)

        tx = self.build(contract_address, data, max_priority_fee, max_fee_per_gas)
        logger.debug(f"Executing tx: {tx}")
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

    def _build_transaction(
        self,
        contract_address: str,
        data: str,
        gas_limit: int,
        max_priority_fee_per_gas: int,
        max_fee_per_gas: int,
        nonce: int,
    ):
        tx = self._build_exec_transaction(contract_address, data).build_transaction(
            {
                "chainId": self.web3.eth.chain_id,
                "gas": gas_limit,
                "maxFeePerGas": max_fee_per_gas,  # base + priority. The base is always 12.5% higher than the last block
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "nonce": nonce,
            }
        )
        return tx

    def _sign_transaction(self, tx):
        return self.web3.eth.account.sign_transaction(tx, self.private_key)

    def _send_raw_transaction(self, raw_transaction):
        return self.web3.eth.send_raw_transaction(raw_transaction)

    def get_tx_receipt(self, tx_hash: str) -> TxReceipt:
        """Get the transaction receipt from the blockchain.

        Args:
            tx_hash (str): Transaction hash.

        Returns:
            Transaction receipt as a TxReceipt object.
        """
        try:
            transaction_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return transaction_receipt
        except exceptions.TransactionNotFound:
            return "Transaction not yet on blockchain"


def update_gas_fees_parameters_and_nonce(w3: Web3, tx: dict) -> TxParams:
    """Updates the gas fees parameters and the nonce of a transaction fetching the data from the blockchain and using the global gas strategy multipliers

    Args:
        w3 (Web3): Web3 instance.
        tx (dict): Transaction dictionary as a TxParams object.

    Returns:
            Transaction dictionary as a TxParams object.
    """
    gas_strategy = get_gas_strategy()
    max_priority_fee = w3.eth.max_priority_fee
    latest_block = w3.eth.get_block("latest")
    base_fee_per_gas = latest_block["baseFeePerGas"]
    max_fee_per_gas = max_priority_fee + int(base_fee_per_gas * gas_strategy.fee_multiplier)
    tx["maxFeePerGas"] = max_fee_per_gas
    tx["maxPriorityFeePerGas"] = max_priority_fee
    tx["nonce"] = w3.eth.get_transaction_count(tx["from"])
    return tx
