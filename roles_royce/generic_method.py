from dataclasses import dataclass, field

from web3 import Web3
from web3.types import HexStr
from roles_royce.roles_modifier import Operation


@dataclass
class TxData:
    contract_address: str
    data: str
    operation: Operation
    value: int


@dataclass
class GenericMethodTransaction(TxData):
    function_name: str
    function_args: list
    contract_address: str
    contract_abi: str
    operation: Operation
    value: int
    data: str = field(init=False)

    def __post_init__(self):
        self.data = self._calc_data()

    def _calc_data(self) -> HexStr:
        """Create the data input for the contract function."""
        contract = Web3().eth.contract(address=None, abi=self.contract_abi)
        result = contract.encodeABI(fn_name=self.function_name, args=self.function_args)
        return result
