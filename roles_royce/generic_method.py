from dataclasses import dataclass, field
from typing import Protocol

from web3 import Web3
from web3.types import HexStr

from .protocols.base import Operation


class TransactableWithProperties(Protocol):
    """Base interface for operations that can be sent to the blockchain."""

    #: the operation type
    operation: Operation
    #: the value quantity, eg: `value = 1` is one Wei in Mainnet.
    value: int

    @property
    def data(self) -> str:
        """The calldata of the operation"""
        return ...

    @property
    def contract_address(self) -> str:
        """Contract address to be called"""
        return ...


class TransactableWithValues(Protocol):
    """Base interface for operations that can be sent to the blockchain."""

    #: the operation type
    operation: Operation
    #: the value quantity, eg: `value = 1` is one Wei in Mainnet.
    value: int
    #: The calldata of the operation
    data: str
    #: Contract address to be called
    contract_address: str


Transactable = TransactableWithProperties | TransactableWithValues


@dataclass(kw_only=True)
class TxData:
    """Implements the Transactable protocol as a dataclass"""

    contract_address: str
    data: str
    operation: Operation = Operation.CALL
    value: int = 0


@dataclass
class GenericMethodTransaction:
    function_name: str
    function_args: list
    contract_abi: str
    contract_address: str
    data: str = field(init=False)
    operation: Operation = Operation.CALL
    value: int = 0

    def __post_init__(self):
        self.data = self._calc_data()

    def _calc_data(self) -> HexStr:
        """Create the data input for the contract function."""
        contract = Web3().eth.contract(address=None, abi=self.contract_abi)
        result = contract.encode_abi(fn_name=self.function_name, args=self.function_args)
        return result
