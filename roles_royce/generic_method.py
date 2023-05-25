from dataclasses import dataclass, field
import json

from web3 import Web3
from web3.types import HexStr
from web3._utils.abi import get_abi_input_types, filter_by_name
from eth_abi import encode
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
        name = filter_by_name(self.function_name, json.loads(self.contract_abi))[0]
        types = get_abi_input_types(name)
        signature = (
            Web3.keccak(text=f"{self.function_name}({','.join(types)})").hex()[:10]
        )
        result = HexStr(f"{signature}{encode(types, self.function_args).hex()}")
        return result
