import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from roles_royce.applications.execution_app.utils import ENV, ExecConfig
from tests.utils import accounts, assign_role, local_node_eth

dao = "GnosisDAO"
blockchain = "ETHEREUM"
avatar_safe_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
roles_mod_address = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
role = 4


def set_env(monkeypatch, private_key: str) -> ENV:
    monkeypatch.setenv("ETHEREUM_RPC_ENDPOINT", "DummyString")
    monkeypatch.setenv("ETHEREUM_RPC_ENDPOINT_FALLBACK", "DummyString")
    monkeypatch.setenv("GNOSISDAO_ETHEREUM_AVATAR_SAFE_ADDRESS", avatar_safe_address)
    monkeypatch.setenv("GNOSISDAO_ETHEREUM_ROLES_MOD_ADDRESS", roles_mod_address)
    monkeypatch.setenv("GNOSISDAO_ETHEREUM_ROLE", role)
    monkeypatch.setenv("GNOSISDAO_ETHEREUM_PRIVATE_KEY", private_key)
    # Without setting the MODE env it will default to DEVELOPMENT and use the local fork
    return ENV(dao, blockchain)


def set_up_roles(local_node_eth, accounts):
    disassembler_address = accounts[0].address
    private_key = accounts[0].key.hex()

    assign_role(
        local_node=local_node_eth,
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_mod_address,
        role=role,
        asignee=disassembler_address,
    )
    return private_key


JSON_FORM = {"protocol": "Lido", "exit_strategy": "exit_3", "percentage": 21, "exit_arguments": {"max_slippage": 0.01}}

exec_config = ExecConfig(
    percentage=JSON_FORM["percentage"],
    dao=dao,
    blockchain=blockchain,
    protocol=JSON_FORM["protocol"],
    exit_strategy=JSON_FORM["exit_strategy"],
    exit_arguments=[JSON_FORM["exit_arguments"]],
)

positions_mock = [
    {
        "position_id": "Lido_64",
        "protocol": "Lido",
        "exec_config": [
            {
                "function_name": "exit_1",
                "label": "Unstake stETH",
                "test": False,
                "description": "Unstake stETH for ETH",
                "parameters": [],
            },
            {
                "function_name": "exit_3",
                "label": "Swap stETH",
                "test": False,
                "description": "Swap stETH for ETH",
                "parameters": [
                    {"name": "max_slippage", "type": "input", "label": "Max slippage", "rules": {"min": 0, "max": 100}}
                ],
            },
        ],
    }
]

expected_outputs = [
    {
        "transaction": {
            "value": 0,
            "chainId": 1,
            "gas": 1030233,
            "nonce": 615,
            "to": "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc",
            "data": "0x6928e74b000000000000000000000000a238cbeb142c10ef7ad8442c6d1f9e89e07e7761000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000002248d80ff0a000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000001d200ae7ab96520de3a18e5e111b5eaab095312d7fe8400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044095ea7b3000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b10000000000000000000000000000000000000000000000ad31b478b8ebb2470a00889edc2edab5f40e902b864ad4d7ade8e412f9b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e4d66810420000000000000000000000000000000000000000000000000000000000000040000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000000a90576f674fd2470a000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        },
        "decoded_transaction": [
            {
                "name": "approve",
                "type": "function",
                "inputs": [
                    {"name": "spender", "type": "address", "value": "0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1"},
                    {"name": "amount", "type": "uint256", "value": 3194868345091042461450},
                ],
                "outputs": [],
                "to_address": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
                "value": 0,
                "data": "0x095ea7b3000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b10000000000000000000000000000000000000000000000ad31b478b8ebb2470a",
                "from_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
            },
            {
                "name": "requestWithdrawals",
                "type": "function",
                "inputs": [
                    {
                        "name": "amounts",
                        "type": "uint256[]",
                        "value": [
                            1000000000000000000000,
                            1000000000000000000000,
                            1000000000000000000000,
                            194868345091042461450,
                        ],
                    },
                    {"name": "owner", "type": "address", "value": "0x849D52316331967b6fF1198e5E32A0eB168D039d"},
                ],
                "outputs": [],
                "to_address": "0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1",
                "value": 0,
                "data": "0xd66810420000000000000000000000000000000000000000000000000000000000000040000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000000a90576f674fd2470a",
                "from_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
            },
        ],
    },
    {
        "transaction": {
            "value": 0,
            "chainId": 1,
            "gas": 184909,
            "nonce": 615,
            "to": "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc",
            "data": "0x6928e74b00000000000000000000000023da9ade38e4477b23770ded512fd37b12381fab000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000001c4569d3489000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000ad31b478b8ebb2470a0000000000000000000000000000000000000000000000ad1c7c84f4b2d013840000000000000000000000000000000000000000000000000000000065bebe24970eb15ab11f171c843c2d1fa326b7f8f6bf06ac7f84bb1affcc86511c783f12000000000000000000000000000000000000000000000000004a93bc21257394f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee34677500000000000000000000000000000000000000000000000000000000000000005a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc95a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc90000000000000000000000000000000000000000000000000000000000000708000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000",
            "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        },
        "decoded_transaction": [
            {
                "name": "signOrder",
                "type": "function",
                "inputs": [
                    {
                        "name": "order",
                        "type": "tuple",
                        "components": [
                            {"name": "sell_token", "type": "address"},
                            {"name": "buy_token", "type": "address"},
                            {"name": "receiver", "type": "address"},
                            {"name": "sell_amount", "type": "uint256"},
                            {"name": "buy_amount", "type": "uint256"},
                            {"name": "valid_to", "type": "uint32"},
                            {"name": "app_data", "type": "bytes32"},
                            {"name": "fee_amount", "type": "uint256"},
                            {"name": "kind", "type": "bytes32"},
                            {"name": "partially_fillable", "type": "bool"},
                            {"name": "sell_token_balance", "type": "bytes32"},
                            {"name": "buy_token_balance", "type": "bytes32"},
                        ],
                        "value": [
                            "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
                            "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                            "0x849D52316331967b6fF1198e5E32A0eB168D039d",
                            3194868345091042461450,
                            3193339386468433400708,
                            1706999332,
                            "0x0x970eb15ab11f171c843c2d1fa326b7f8f6bf06ac7f84bb1affcc86511c783f12",
                            20991584495825812,
                            "0x0xf3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee346775",
                            False,
                            "0x0x5a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc9",
                            "0x0x5a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc9",
                        ],
                    },
                    {"name": "valid_duration", "type": "uint32", "value": 1800},
                    {"name": "fee_amount_bp", "type": "uint256", "value": 1},
                ],
                "outputs": [],
                "to_address": "0x23dA9AdE38E4477b23770DeD512fD37b12381FAB",
                "value": 0,
                "data": "0x569d3489000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000ad31b478b8ebb2470a0000000000000000000000000000000000000000000000ad1c7c84f4b2d013840000000000000000000000000000000000000000000000000000000065bebe24970eb15ab11f171c843c2d1fa326b7f8f6bf06ac7f84bb1affcc86511c783f12000000000000000000000000000000000000000000000000004a93bc21257394f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee34677500000000000000000000000000000000000000000000000000000000000000005a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc95a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc900000000000000000000000000000000000000000000000000000000000007080000000000000000000000000000000000000000000000000000000000000001",
                "from_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
            }
        ],
    },
]


# @pytest.mark.skip(reason="swap strategy does not work in the fork")
@pytest.mark.parametrize("args, expected", zip(positions_mock[0]["exec_config"], expected_outputs))
def test_transaction_builder_lido(local_node_eth, accounts, monkeypatch, args, expected):
    w3 = local_node_eth.w3
    block = w3.eth.default_block
    local_node_eth.set_block(block)
    private_key = set_up_roles(local_node_eth, accounts)
    set_env(monkeypatch, private_key)

    file_path_main = os.path.join(
        Path(os.path.dirname(__file__)).resolve().parent.parent.parent,
        "roles_royce",
        "applications",
        "execution_app",
        "transaction_builder.py",
    )

    arguments = [
        sys.executable,
        file_path_main,
        "--percentage",
        str(23),
        "--dao",
        dao,
        "--blockchain",
        blockchain,
        "--protocol",
        positions_mock[0]["protocol"],
        "--exit-strategy",
        args["function_name"],
    ]

    exit_arguments_dict = {}
    for item in args["parameters"]:
        if item["type"] == "constant":
            exit_arguments_dict[item["name"]] = item["value"]
        elif item["name"] == "max_slippage":
            exit_arguments_dict[item["name"]] = 0.01
        elif item["name"] == "token_out_address":
            exit_arguments_dict[item["name"]] = item["options"][0]["value"]
    exit_arguments = [exit_arguments_dict]
    # Convert the parameters to a JSON string
    parameters_json = json.dumps(exit_arguments)
    arguments.extend(["--exit-arguments", parameters_json])
    main = subprocess.run(arguments, capture_output=True, text=True)

    assert main.returncode == 0
    dict_message_stdout = json.loads(main.stdout[:-1])
    response = dict_message_stdout["tx_data"]
    assert dict_message_stdout["status"] == 200
    del response["transaction"]["maxFeePerGas"]  # Gas fees change even in the fork
    del response["transaction"]["maxPriorityFeePerGas"]  # Gas fees change even in the fork
    w3 = local_node_eth.w3
    # In the CI tests we get differences in the nonce, so we need to "hardcode" the nonce from the node
    expected["transaction"]["nonce"] = w3.eth.get_transaction_count(w3.eth.account.from_key(private_key).address)
    # assert response == expected
