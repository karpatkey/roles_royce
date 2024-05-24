import pytest

from roles_royce.applications.execution_app.utils import (
    ENV,
    ExecConfig,
    Modes,
    decode_transaction,
    gear_up,
    start_the_engine,
)
from tests.fork_fixtures import accounts, local_node_eth

dao = "GnosisDAO"
blockchain = "ETHEREUM"
avatar_safe_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
roles_mod_address = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
role = 4


def get_env() -> ENV:
    return ENV(
        rpc_url="DummyString",
        rpc_fallback_url="DummyString",
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_mod_address,
        role=role,
        disassembler_address="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        mode="development",
    )


JSON_FORM = {
    "simulate": False,
    "protocol": "Aura",
    "exit_strategy": "exit_2_1",
    "percentage": 21,
    "exit_arguments": {"rewards_address": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D", "max_slippage": 1},
}

exec_config = ExecConfig(
    percentage=JSON_FORM["percentage"],
    # blockchain=blockchain,
    protocol=JSON_FORM["protocol"],
    exit_strategy=JSON_FORM["exit_strategy"],
    exit_arguments=[JSON_FORM["exit_arguments"]],
)


def test_start_the_engine_dev(local_node_eth):
    env = get_env()
    env.rpc_url = local_node_eth.url

    w3 = start_the_engine(env)
    assert w3.is_connected()


def test_start_the_engine_prod():
    env = get_env()

    env.mode = Modes.PRODUCTION
    with pytest.raises(Exception):
        start_the_engine(env)  # RPC endpoints are 'DummyString'


def test_gear_up(monkeypatch, local_node_eth):
    env = get_env()

    w3 = local_node_eth.w3
    local_node_eth.set_block(18437790)

    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
    assert disassembler.avatar_safe_address == "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    assert (
        txn_transactables[0].data
        == "0xc32e72020000000000000000000000000000000000000000000000111ed47dc81e6e5ad80000000000000000000000000000000000000000000000000000000000000001"
    )
    assert (
        txn_transactables[1].data
        == "0x8bdb39131e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000ae78736cd615f374d3085123a210448e74fc6393000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000007e9af502b84ea855b000000000000000000000000000000000000000000000008cc84206c7773d6ed000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000111ed47dc81e6e5ad8"
    )


def test_decode_transaction(local_node_eth, accounts, monkeypatch):
    env = get_env()

    w3 = local_node_eth.w3
    local_node_eth.set_block(18437790)

    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)

    decoded = decode_transaction(txn_transactables, env)

    expected = [
        {
            "data": "0xc32e72020000000000000000000000000000000000000000000000111ed47dc81e6e5ad80000000000000000000000000000000000000000000000000000000000000001",
            "from_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
            "inputs": [
                {"name": "amount", "type": "uint256", "value": 315816188067720354520},
                {"name": "claim", "type": "bool", "value": True},
            ],
            "name": "withdrawAndUnwrap",
            "outputs": [],
            "to_address": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D",
            "type": "function",
            "value": 0,
        },
        {
            "data": "0x8bdb39131e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000ae78736cd615f374d3085123a210448e74fc6393000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000007e9af502b84ea855b000000000000000000000000000000000000000000000008cc84206c7773d6ed000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000111ed47dc81e6e5ad8",
            "from_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
            "inputs": [
                {
                    "name": "pool_id",
                    "type": "bytes32",
                    "value": "0x1e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112",
                },
                {"name": "sender", "type": "address", "value": "0x849D52316331967b6fF1198e5E32A0eB168D039d"},
                {"name": "recipient", "type": "address", "value": "0x849D52316331967b6fF1198e5E32A0eB168D039d"},
                {
                    "components": [
                        {"name": "assets", "type": "address[]"},
                        {"name": "min_amounts_out", "type": "uint256[]"},
                        {"name": "user_data", "type": "bytes"},
                        {"name": "to_internal_balance", "type": "bool"},
                    ],
                    "name": "request",
                    "type": "tuple",
                    "value": (
                        ["0xae78736Cd615f374D3085123A210448E74Fc6393", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"],
                        [145965974195572213083, 162310892120572155629],
                        "0x00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000111ed47dc81e6e5ad8",
                        False,
                    ),
                },
            ],
            "name": "exitPool",
            "outputs": [],
            "to_address": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
            "type": "function",
            "value": 0,
        },
    ]

    assert decoded == expected
