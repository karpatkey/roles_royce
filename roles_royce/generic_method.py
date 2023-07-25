from dataclasses import dataclass, field
from typing import Protocol
from web3 import Web3
from web3.types import HexStr
from roles_royce.roles_modifier import Operation


class Transactable(Protocol):
    operation: Operation
    value: int

    @property
    def data(self) -> str: return ...

    @property
    def contract_address(self) -> str: return ...


@dataclass(kw_only=True)
class TxData:
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
        result = contract.encodeABI(fn_name=self.function_name, args=self.function_args)
        return result
