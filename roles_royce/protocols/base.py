from roles_royce import Operation
from roles_royce.generic_method import TxData
from roles_royce.utils import to_data_input

AvatarSafeAddress = object()
Address = str

class InvalidArgument(Exception):
    pass

class Method(TxData):
    name = None
    signature = None
    fixed_arguments = dict()
    target_address = None
    avatar = None

    def __init__(self):
        pass

    def get_args_list(self):
        args_list = []
        for arg_name, arg_type in self.signature:
            if arg_name in self.fixed_arguments:
                value = self.fixed_arguments[arg_name]
                if value is AvatarSafeAddress:
                    value = self.avatar
            else:
                value = getattr(self, arg_name)
            args_list.append(value)
        return args_list

    @property
    def data(self):
        arg_types = [arg_type for arg_name, arg_type in self.signature]
        return to_data_input(self.name, arg_types, self.get_args_list())

    @property
    def arg_types(self):
        return [arg_type for arg_name, arg_type in self.signature]

    @property
    def contract_address(self):
        return self.target_address

    @property
    def operation(self):
        return Operation.CALL