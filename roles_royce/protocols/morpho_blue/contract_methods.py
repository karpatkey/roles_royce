from enum import IntEnum

from defabipedia.morpho import ContractSpecs
from defabipedia.types import Blockchain, Chain

from roles_royce.protocols.base import (
    Address,
    AvatarAddress,
    BaseApprove,
    BaseApproveForToken,
    ContractMethod,
    InvalidArgument,
)


class ApproveMorphoBlue(BaseApproveForToken):
    """approve Token with MorphoBlue as spender"""

    def __init__(self, blockchain: Blockchain, token: Address, amount: int):
        self.fixed_arguments = {"spender": ContractSpecs[blockchain].morpho_blue.address}
        super().__init__(token, amount)


class Supply(ContractMethod):
    """Supply token to morpho_blue and receive shares"""

    target_address = None
    name = "supply"
    in_signature = (
        (
            "market_params",
            (
                (
                    ("loan_token", "address"),
                    ("collateral_token", "address"),
                    ("oracle", "address"),
                    ("irm", "address"),
                    ("lltv", "uint256"),
                ),
                "tuple",
            ),
        ),
        ("assets", "uint256"),
        ("shares", "uint256"),
        ("on_behalf_of", "address"),
        ("data", "bytes"),
    )
    fixed_arguments = {
        "on_behalf_of": AvatarAddress,
        "data": "0x",
    }

    def __init__(
        self,
        blockchain: Blockchain,
        avatar: AvatarAddress,
        loan_token: Address,
        collateral_token: Address,
        oracle: Address,
        irm: Address,
        lltv: int,
        assets: int,
        shares: int,
    ):
        self.target_address = ContractSpecs[blockchain].morpho_blue.address
        super().__init__(avatar=avatar)
        self.args.loan_token = loan_token
        self.args.collateral_token = collateral_token
        self.args.oracle = oracle
        self.args.irm = irm
        self.args.lltv = lltv
        self.args.market_params = [
            self.args.loan_token,
            self.args.collateral_token,
            self.args.oracle,
            self.args.irm,
            self.args.lltv,
        ]
        self.args.assets = assets
        self.args.shares = shares


class Withdraw(ContractMethod):
    target_address = None
    name = "withdraw"
    in_signature = (
        (
            "market_params",
            (
                (
                    ("loan_token", "address"),
                    ("collateral_token", "address"),
                    ("oracle", "address"),
                    ("irm", "address"),
                    ("lltv", "uint256"),
                ),
                "tuple",
            ),
        ),
        ("assets", "uint256"),
        ("shares", "uint256"),
        ("on_behalf_of", "address"),
        ("receiver", "address"),
    )
    fixed_arguments = {
        "on_behalf_of": AvatarAddress,
        "receiver": AvatarAddress,
    }

    def __init__(
        self,
        blockchain: Blockchain,
        avatar: AvatarAddress,
        loan_token: Address,
        collateral_token: Address,
        oracle: Address,
        irm: Address,
        lltv: int,
        assets: int,
        shares: int,
    ):
        self.target_address = ContractSpecs[blockchain].morpho_blue.address
        super().__init__(avatar=avatar)
        self.args.loan_token = loan_token
        self.args.collateral_token = collateral_token
        self.args.oracle = oracle
        self.args.irm = irm
        self.args.lltv = lltv
        self.args.market_params = [
            self.args.loan_token,
            self.args.collateral_token,
            self.args.oracle,
            self.args.irm,
            self.args.lltv,
        ]
        self.args.assets = assets
        self.args.shares = shares
