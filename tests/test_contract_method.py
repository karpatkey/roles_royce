import json

from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import AvatarAddress, ContractMethod

AVATAR_ADDRESS = "0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89"

BALANCER_EXIT_ABI = [
    {
        "name": "exitPool",
        "type": "function",
        "inputs": [
            {"name": "pool_id", "type": "bytes32"},
            {"name": "sender", "type": "address"},
            {"name": "recipient", "type": "address"},
            {
                "components": [
                    {"name": "assets", "type": "address[]"},
                    {"name": "min_amounts_out", "type": "uint256[]"},
                    {"name": "user_data", "type": "bytes"},
                    {"name": "to_internal_balance", "type": "bool"},
                ],
                "name": "request",
                "type": "tuple",
            },
        ],
    }
]

LIDO_STATUS_ABI = [
    {
        "type": "function",
        "name": "getWithdrawalStatus",
        "inputs": [{"name": "_requestIds", "type": "uint256[]"}],
        "outputs": [
            {
                "components": [
                    {"name": "amountOfStETH", "type": "uint256"},
                    {"name": "amountOfShares", "type": "uint256"},
                    {"name": "owner", "type": "address"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "isFinalized", "type": "bool"},
                    {"name": "isClaimed", "type": "bool"},
                ],
                "name": "statuses",
                "type": "tuple[]",
            }
        ],
    }
]


class DepositToken(ContractMethod):
    """Sender deposits Token and receives aToken in exchange."""

    name = "deposit"
    in_signature = [
        ("asset", "address"),
        ("amount", "uint256"),
        ("on_behalf_of", "address"),
        ("referral_code", "uint16"),
    ]
    fixed_arguments = {"on_behalf_of": AvatarAddress, "referral_code": 0}
    target_address = ETHAddr.AAVE_V2_LendingPool

    def __init__(self, asset, amount, avatar):
        super().__init__(avatar=avatar)
        self.args.asset = asset
        self.args.amount = amount


def test_method_abi():
    method = DepositToken(asset=ETHAddr.WETH, amount=10, avatar=AVATAR_ADDRESS)
    assert method.short_signature == "deposit(address,uint256,address,uint16)"


def test_method_with_tuple():
    class Exit(ContractMethod):
        name = "exitPool"
        in_signature = (
            ("pool_id", "bytes32"),
            ("sender", "address"),
            ("recipient", "address"),
            (
                "request",
                (
                    (
                        ("assets", "address[]"),
                        ("min_amounts_out", "uint256[]"),
                        ("user_data", "bytes"),
                        ("to_internal_balance", "bool"),
                    ),
                    "tuple",
                ),
            ),
        )

    method = Exit()
    assert method.short_signature == "exitPool(bytes32,address,address,(address[],uint256[],bytes,bool))"
    abi = json.loads(method.abi)[0]
    assert abi["name"] == "exitPool"
    assert abi["inputs"][3] == {
        "name": "request",
        "type": "tuple",
        "components": [
            {"name": "assets", "type": "address[]"},
            {"name": "min_amounts_out", "type": "uint256[]"},
            {"name": "user_data", "type": "bytes"},
            {"name": "to_internal_balance", "type": "bool"},
        ],
    }


def test_method_with_tuple_array():
    class GetWithdrawalStatus(ContractMethod):
        name = "getWithdrawalStatus"
        in_signature = [("request_ids", "uint256[]")]
        out_signature = [
            (
                "statuses",
                (  # an array of structs
                    (
                        ("amount_of_stETH", "uint256"),
                        ("amount_of_shares", "uint256"),
                        ("owner", "address"),
                        ("timestamp", "uint256"),
                        ("is_finalized", "bool"),
                        ("is_claimed", "bool"),
                    ),
                    "tuple[]",
                ),
            )
        ]

    method = GetWithdrawalStatus()
    abi = json.loads(method.abi)[0]
    assert abi["outputs"][0]["type"] == "tuple[]"



def test_method_values():
    class MyDeposit(ContractMethod):
        name = "deposit"
        in_signature = [
            ("asset", "address"),
            ("amount", "uint256"),
            ("on_behalf_of", "address"),
            ("referral_code", "uint16"),
        ]
        fixed_arguments = {"on_behalf_of": AVATAR_ADDRESS, "referral_code": 0}

    assert MyDeposit().value == 0
    MyDeposit().value = 1
    assert MyDeposit().value == 0


def test_method_inputs():
    method = DepositToken(asset=ETHAddr.WETH, amount=10, avatar=AVATAR_ADDRESS)
    assert method.inputs == {"asset": ETHAddr.WETH, "amount": 10, "on_behalf_of": AVATAR_ADDRESS, "referral_code": 0}
