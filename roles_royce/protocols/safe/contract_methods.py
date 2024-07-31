from roles_royce.protocols.base import ContractMethod, Address


class EnableModule(ContractMethod):
    """Enable module"""

    name = "enableModule"
    in_signature = [
        ("module", "address"),
    ]

    def __init__(
        self,
        safe_address: Address,
        module: Address,
    ):
        super().__init__()
        self.target_address = safe_address
        self.args.module = module
