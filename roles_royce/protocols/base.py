import json
from types import SimpleNamespace

from web3 import Web3

from roles_royce.roles_modifier import Operation

Address = str


class SimpleRepr(type):
    def __repr__(cls):
        return cls.__name__


class AvatarAddress(metaclass=SimpleRepr):
    pass


class InvalidArgument(Exception):
    pass


class Args(SimpleNamespace):
    pass


class ContractMethod:
    """Inherit this class to declare a contract function.

    At least ``name`` and ``target_address`` must be defined in the
    inherited class.
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

    def __init__(self, value: int = 0, avatar: None | str = None):
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
        result = contract.encodeABI(fn_name=self.name, args=self.args_list)
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

    def call(self, web3, *args, **kwargs):
        """Does a read call on the method.

        To use it the ``out_signature`` must be defined.
        """
        contract = web3.eth.contract(address=self.target_address, abi=self.abi)
        return contract.functions[self.name](*self.args_list).call(*args, **kwargs)

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
    """Inherit from this class to define an approval that the token is fixed.

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
