from roles_royce import Operation
from roles_royce.utils import to_data_input

AvatarSafeAddress = object()
Address = str

class InvalidArgument(Exception):
    pass

class Method:
    name = None
    signature = None
    fixed_arguments = dict()
    target_address = None
    avatar = None

    def __init__(self):
        pass

    def get_args_list(self):
        return [self.get_arg_value(e) for e in self.signature]

    def get_arg_value(self, element):
        arg_name, arg_type = element
        if type(arg_type) in (list, tuple):
            value = tuple(self.get_arg_value(e) for e in arg_type)
        else:
            if arg_name in self.fixed_arguments:
                value = self.fixed_arguments[arg_name]
                if value is AvatarSafeAddress:
                    value = self.avatar
            else:
                value = getattr(self, arg_name)
        if type(arg_type) is str and arg_type.startswith("byte") and type(value) is str:
            value = bytes.fromhex(value[2:])
        return value

    @property
    def data(self):
        return to_data_input(self.name, self.short_signature, self.get_args_list())

    @property
    def short_signature(self):
        return "(" + ",".join([self.get_arg_type(e) for e in self.signature]) + ")"

    def get_arg_type(self, element):
        _, _type = element
        if type(_type) in (list, tuple):
            value = "(" + ",".join([self.get_arg_type(e) for e in _type]) + ")"
        else:
            value = _type
        return value

    @property
    def contract_address(self):
        return self.target_address

    @property
    def operation(self):
        return Operation.CALL