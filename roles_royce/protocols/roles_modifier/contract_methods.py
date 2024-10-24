from roles_royce.protocols.base import Address, ContractMethod
from roles_royce.protocols.utils import format_bytes32_string


def get_roles_mod_version(role: str | int):
    """Returns the version of the roles_modifier mod based on the type."""
    if type(role) is str:
        version = 2
    elif type(role) is int:
        version = 1
    else:
        raise ValueError("role type must be either str (roles_modifier v2) or int (roles_modifier v1)")
    return version


def to_v2_key(key):
    return key if key.startswith("0x") else format_bytes32_string(key)


class ExecTransactionWithRoleV1(ContractMethod):
    """Execute transaction with Role for the V1 of the Roles Mod Contracts."""

    name = "execTransactionWithRole"
    in_signature = [
        ("to", "address"),
        ("value", "uint256"),
        ("data", "bytes"),
        ("operation", "uint8"),
        ("role", "uint16"),
        ("should_revert", "bool"),
    ]

    def __init__(
        self,
        roles_mod_address: Address,
        role: int,
        to: Address,
        data: str,
        operation: int,
        value: int,
        should_revert: bool = True,
    ):
        super().__init__()
        self.target_address = roles_mod_address
        self.args.role = role
        self.args.to = to
        self.args.data = data
        self.args.operation = operation
        self.args.value = value
        self.args.should_revert = should_revert


class ExecTransactionWithRoleV2(ContractMethod):
    """Execute transaction with Role for V2 of the Roles Mod Contracts."""

    name = "execTransactionWithRole"
    in_signature = [
        ("to", "address"),
        ("value", "uint256"),
        ("data", "bytes"),
        ("operation", "uint8"),
        ("role_key", "bytes32"),
        ("should_revert", "bool"),
    ]

    def __init__(
        self,
        roles_mod_address: Address,
        role: str,
        to: Address,
        data: str,
        operation: int,
        value: int,
        should_revert: bool = True,
    ):
        super().__init__()
        self.target_address = roles_mod_address
        self.args.role_key = to_v2_key(role)
        self.args.to = to
        self.args.data = data
        self.args.operation = operation
        self.args.value = value
        self.args.should_revert = should_revert


def get_exec_transaction_with_role_method(
    roles_mod_address: Address,
    role: str | int,
    to: Address,
    data: str,
    operation: int,
    value: int = 0,
    should_revert: bool = True,
):
    """Returns the proper version instance of ExecTransactionWithRole (V1 or V2)."""
    version = get_roles_mod_version(role)
    if version == 2:
        role_method = ExecTransactionWithRoleV2
    else:
        role_method = ExecTransactionWithRoleV1
    return role_method(roles_mod_address, role, to, data, operation, value, should_revert)


class EnableModule(ContractMethod):
    """Enable module"""

    name = "enableModule"
    in_signature = [
        ("module", "address"),
    ]

    def __init__(
        self,
        roles_mod_address: Address,
        module: Address,
    ):
        super().__init__()
        self.target_address = roles_mod_address
        self.args.module = module


class AssignRolesV1(ContractMethod):
    """Assign roles for the V1 of the Roles Mod Contracts."""

    name = "assignRoles"
    in_signature = [
        ("module", "address"),
        ("roles", "uint16[]"),
        ("member_of", "bool[]"),
    ]

    def __init__(
        self,
        roles_mod_address: Address,
        module: Address,
        assign_list: list[int] | None = None,
        revoke_list: list[int] | None = None,
    ):
        super().__init__()
        self.target_address = roles_mod_address
        self.args.module = module
        assign_list = assign_list or []
        revoke_list = revoke_list or []
        self.args.roles = assign_list + revoke_list
        self.args.member_of = [True] * len(assign_list) + [False] * len(revoke_list)


class AssignRolesV2(ContractMethod):
    """Assign roles for the V2 of the Roles Mod Contracts."""

    name = "assignRoles"
    in_signature = [
        ("module", "address"),
        ("role_keys", "bytes32[]"),
        ("member_of", "bool[]"),
    ]

    def __init__(
        self,
        roles_mod_address: Address,
        module: Address,
        assign_list: list[str] | None = None,
        revoke_list: list[str] | None = None,
    ):
        super().__init__()
        self.target_address = roles_mod_address
        self.args.module = module
        assign_list = assign_list or []
        revoke_list = revoke_list or []
        self.args.role_keys = [to_v2_key(k) for k in assign_list + revoke_list]
        self.args.member_of = [True] * len(assign_list) + [False] * len(revoke_list)


class ScopeTarget(ContractMethod):
    """Scope target for the V2 of the Roles Mod Contracts."""

    name = "scopeTarget"
    in_signature = [
        ("role_key", "bytes32"),
        ("target", "address"),
    ]

    def __init__(self, roles_mod_address: Address, role: str, target: Address):
        super().__init__()
        self.target_address = roles_mod_address
        self.args.role_key = to_v2_key(role)
        self.args.target = target


class ScopeFunction(ContractMethod):
    """Scope function for the V2 of the Roles Mod Contracts."""

    name = "scopeFunction"
    in_signature = [
        ("role_key", "bytes32"),
        ("target", "address"),
        ("selector", "bytes4"),
        (
            "conditions",
            [
                (
                    ("parent", "uint8"),
                    ("param_type", "uint8"),
                    ("operator", "uint8"),
                    ("compvalue", "bytes"),
                ),
                "tuple[]",
            ],
        ),
        ("options", "uint8"),
    ]

    def __init__(
        self,
        roles_mod_address: Address,
        role: str,
        target: Address,
        selector: str,
        conditions: list,
        options: int,
    ):
        super().__init__()
        self.target_address = roles_mod_address
        self.args.role_key = to_v2_key(role)
        self.args.target = target
        self.args.selector = selector
        self.args.conditions = conditions
        self.args.options = options


class AllowFunction(ContractMethod):
    """Allow function for the V2 of the Roles Mod Contracts."""

    name = "allowFunction"
    in_signature = [
        ("role_key", "bytes32"),
        ("target", "address"),
        ("selector", "bytes4"),
    ]

    def __init__(self, roles_mod_address: Address, role: str, target: Address, selector: str, options: int):
        super().__init__()
        self.target_address = roles_mod_address
        self.args.role_key = to_v2_key(role)
        self.args.target = target
        self.args.selector = selector
        self.args.options = options


class SetMultisend(ContractMethod):
    name = "setMultisend"
    in_signature = [
        ("multisend", "address"),
    ]

    def __init__(
        self,
        roles_mod_address: Address,
        multisend: Address,
    ):
        super().__init__()
        self.target_address = roles_mod_address
        self.args.multisend = multisend


class SetTransactionUnwrapper(ContractMethod):
    """Set Transaction Unwrapper"""

    name = "setTransactionUnwrapper"
    in_signature = [
        ("to", "address"),
        ("selector", "bytes4"),
        ("adapter", "address"),
    ]

    def __init__(self, roles_mod_address: Address, to: Address, selector: str, adapter: Address):
        super().__init__()
        self.target_address = roles_mod_address
        self.args.to = to
        self.args.selector = selector
        self.args.adapter = adapter
