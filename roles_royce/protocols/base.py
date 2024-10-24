import json
from enum import IntEnum
from types import SimpleNamespace

from eth_typing import Address as EvmAddress
from web3 import Web3

Address = str | EvmAddress


class SimpleRepr(type):
    def __repr__(cls):
        return cls.__name__


class AvatarAddress(metaclass=SimpleRepr):
    """To be used in place of the avatar address for example in ContractMethod's fixed_arguments"""


class InvalidArgument(Exception):
    pass


class Args(SimpleNamespace):
    pass


class Operation(IntEnum):
    """Types of operations."""

    CALL = 0
    DELEGATE_CALL = 1


class ContractMethod:
    """Inherit this class to declare a contract function.

    At least ``name`` and ``target_address`` must be defined in the
    inherited class.
    Implements the Transactable protocol.
    """

    #: The name of the contract function
    name: str = ""
    #: The address of the contract
    target_address: str = ""
    #: The input signature
    in_signature: list[tuple[str, str]] = []
    #: The output signature. Only used to do a read call.
    out_signature: list[tuple[str, str]] = []
    #: Provide fixed defaults to some function attributes.
    fixed_arguments = dict()

    def __init__(self, value: int = 0, avatar: None | Address = None):
        """
        Args:
            value: The value of the tx, eg: amount of Wei in mainnet, xDai Weis in GC.
            avatar: Avatar address, usually a Safe address.
        """
        self.value = value  # Eg: amount of ETH in mainnet, xDai in GC
        self.avatar = avatar
        self.args = Args()
        self._initialized = True
        self.operation: Operation = Operation.CALL
        self._inputs = None

    @property
    def contract_address(self) -> str:
        return self.target_address

    @property
    def args_list(self):
        return [self._get_arg_value(e) for e in self.in_signature]

    @property
    def data(self) -> str:
        """Calldata of the method."""
        if not hasattr(self, "_initialized"):
            raise ValueError(f"Missing super().__init__() call in {self.__class__.__name__}.__init__ method")
        contract = Web3().eth.contract(address=None, abi=self.abi)
        result = contract.encode_abi(fn_name=self.name, args=self.args_list)
        # Decode what we encoded to re-use the web3py normalizers
        self._inputs = contract.decode_function_input(result)[1]
        return result

    @property
    def short_signature(self):
        """Something like 'deposit(address,uint256,address,uint16)'"""
        types = ",".join([self._get_arg_type(e) for e in self.in_signature])
        return f"{self.name}({types})"

    @property
    def abi(self):
        """The abi of the method, for example to be used with Web3."""
        inputs = [self._abi_for(e) for e in self.in_signature]
        outputs = [self._abi_for(e) for e in self.out_signature]
        abi = {"name": self.name, "type": "function", "inputs": inputs, "outputs": outputs}
        return json.dumps([abi])

    @property
    def inputs(self):
        """Return a dict with the arguments of the method"""
        if self._inputs is None:
            _ = self.data  # Calc the inputs
        return self._inputs

    def call(self, web3, *args, **kwargs):
        """Does a read call on the method.

        To use it the ``out_signature`` must be defined if the method's output is not empty.
        """
        contract = web3.eth.contract(address=self.target_address, abi=self.abi)
        return contract.functions[self.name](*self.args_list).call(*args, **kwargs)

    def transact(self, web3, txparams):
        """Performs transact on the method.

        To use it the ``out_signature`` must be defined if the method's output is not empty.
        """
        contract = web3.eth.contract(address=self.target_address, abi=self.abi)
        return contract.functions[self.name](*self.args_list).transact(txparams)

    def _get_arg_value(self, element):
        arg_name, arg_type = element
        if type(arg_type) in (list, tuple):
            value = tuple(self._get_arg_value(e) for e in arg_type[0])
        else:
            if arg_name in self.fixed_arguments:
                value = self.fixed_arguments[arg_name]
                if value is AvatarAddress:
                    value = self.avatar
            else:
                value = getattr(self.args, arg_name)
        return value

    def _abi_for(self, element):
        name, _type = element
        if type(_type) in (list, tuple):
            value = {
                "name": name,
                "type": _type[1],  # tuple or tuple[]
                "components": [self._abi_for(e) for e in _type[0]],
            }
        else:
            value = {"name": name, "type": _type}
        return value

    def _get_arg_type(self, element):
        _type = element[1]
        if type(_type) in (list, tuple):
            types = ",".join([self._get_arg_type(e) for e in _type[0]])
            value = f"({types})"
        else:
            value = _type
        return value


class BaseApprove(ContractMethod):
    """Inherit from this class to define an approval where the token is fixed.

    Specify the token using the token class attribute
    """

    name = "approve"
    in_signature = [("spender", "address"), ("amount", "uint256")]
    token = None

    def __init__(self, amount: int):
        if self.token is None:
            raise NotImplementedError("Subclass must define a token")
        super().__init__()
        self.args.amount = amount

    @property
    def target_address(self) -> str:
        """The token address."""
        return self.token


class BaseApproveForToken(BaseApprove):
    """Inherit from this class to define an approval that the token is specified dynamically."""

    def __init__(self, token: Address, amount: int):
        self.token = token
        super().__init__(amount)


class ApproveForToken(BaseApproveForToken):
    """Approve a token for a specific spender."""

    def __init__(self, token: Address, spender: Address, amount: int):
        self.token = token
        self.fixed_arguments = {"spender": spender}
        super().__init__(token, amount)
