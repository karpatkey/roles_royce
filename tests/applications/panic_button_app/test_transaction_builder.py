from roles_royce.applications.panic_button_app.utils import ENV, ExecConfig
from tests.utils import assign_role, local_node_eth, accounts
import os
import json
import pytest
import subprocess
from pathlib import Path

dao = 'GnosisDAO'
blockchain = 'ETHEREUM'
avatar_safe_address = '0x849D52316331967b6fF1198e5E32A0eB168D039d'
roles_mod_address = '0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc'
role = 4


def set_env(monkeypatch, private_key: str) -> ENV:
    monkeypatch.setenv('ETHEREUM_RPC_ENDPOINT', 'DummyString')
    monkeypatch.setenv('ETHEREUM_RPC_ENDPOINT_FALLBACK', 'DummyString')
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_AVATAR_SAFE_ADDRESS', avatar_safe_address)
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_ROLES_MOD_ADDRESS', roles_mod_address)
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_ROLE', role)
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_PRIVATE_KEY', private_key)
    # Without setting the MODE env it will default to DEVELOPMENT and use the local fork
    return ENV(dao, blockchain)


def set_up_roles(local_node_eth, accounts):
    block = 18421437
    local_node_eth.set_block(block)

    disassembler_address = accounts[0].address
    private_key = accounts[0].key.hex()

    assign_role(local_node=local_node_eth,
                avatar_safe_address=avatar_safe_address,
                roles_mod_address=roles_mod_address,
                role=role,
                asignee=disassembler_address)
    return private_key


JSON_FORM = {
    "protocol": "Aura",
    "exit_strategy": "exit_2_1",
    "percentage": 21,
    "exit_arguments": {

        "rewards_address": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D",
        "max_slippage": 0.01
    }
}

exec_config = ExecConfig(percentage=JSON_FORM["percentage"],
                         dao=dao,
                         blockchain=blockchain,
                         protocol=JSON_FORM["protocol"],
                         exit_strategy=JSON_FORM["exit_strategy"],
                         exit_arguments=[JSON_FORM["exit_arguments"]])

positions_mock = [
    {
        "position_id": "Aura_33",
        "protocol": "Aura",
        "exec_config": [
            {
                "function_name": "exit_1",
                "label": "Exit_1",
                "description": "Withdraw from Aura",
                "parameters": [
                    {
                        "name": "rewards_address",
                        "type": "constant",
                        "value": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D"
                    },
                    {
                        "name": "max_slippage",
                        "label": "Max slippage",
                        "type": "input",
                        "rules": {"min": 0, "max": 100}
                    }
                ]
            },
            {
                "function_name": "exit_2_1",
                "label": "Exit_2_1",
                "description": "Withdraw funds from Aura and then from the Balancer pool withdrawing all assets in proportional way (not used for pools in recovery mode!)",
                "parameters": [
                    {
                        "name": "rewards_address",
                        "type": "constant",
                        "value": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D"
                    },
                    {
                        "name": "max_slippage",
                        "label": "Max slippage",
                        "type": "input",
                        "rules": {"min": 0, "max": 100}
                    }
                ]
            },
            {
                "function_name": "exit_2_2",
                "label": "Exit_2_2",
                "description": "Withdraw funds from Aura and then from the Balancer pool withdrawing a single asset.",
                "parameters": [
                    {
                        "name": "rewards_address",
                        "type": "constant",
                        "value": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D"
                    },
                    {
                        "name": "max_slippage",
                        "label": "Max slippage",
                        "type": "input",
                        "rules": {"min": 0, "max": 100}
                    },
                    {
                        "name": "token_out_address",
                        "label": "Token out",
                        "type": "input",
                        "options": [
                            {"value": "0xae78736Cd615f374D3085123A210448E74Fc6393", "label": "rETH"},
                            {"value": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "label": "WETH"}
                        ]
                    }
                ]
            },
        ]
    }
]

expected_outputs = [{'decoded_transaction': [{
    'data': '0xc32e7202000000000000000000000000000000000000000000000012c03e0fdb2d857add0000000000000000000000000000000000000000000000000000000000000001',
    'from_address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
    'inputs': [{'name': 'amount',
                'type': 'uint256',
                'value': 345893920264646130397},
               {'name': 'claim',
                'type': 'bool',
                'value': True}],
    'name': 'withdrawAndUnwrap',
    'outputs': [],
    'to_address': '0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D',
    'type': 'function',
    'value': 0}],
    'transaction': {'chainId': 1,
                    'data': '0x6928e74b000000000000000000000000dd1fe5ad401d4777ce89959b7fa587e569bf125d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000044c32e7202000000000000000000000000000000000000000000000012c03e0fdb2d857add000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000',
                    'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
                    'gas': 1043653,
                    # 'maxFeePerGas': 3710601020, # Gas fees change even in the fork
                    # 'maxPriorityFeePerGas': 2608114460, # Gas fees change even in the fork
                    'nonce': 559,
                    'to': '0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc',
                    'value': 0}},
    {'decoded_transaction': [{
        'data': '0xc32e7202000000000000000000000000000000000000000000000012c03e0fdb2d857add0000000000000000000000000000000000000000000000000000000000000001',
        'from_address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
        'inputs': [{'name': 'amount',
                    'type': 'uint256',
                    'value': 345893920264646130397},
                   {'name': 'claim',
                    'type': 'bool',
                    'value': True}],
        'name': 'withdrawAndUnwrap',
        'outputs': [],
        'to_address': '0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D',
        'type': 'function',
        'value': 0},
        {
            'data': '0x8bdb39131e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000ae78736cd615f374d3085123a210448e74fc6393000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000008d67359c755786df0000000000000000000000000000000000000000000000009a450bae6cc334cae00000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000012c03e0fdb2d857add',
            'from_address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
            'inputs': [{'name': 'pool_id',
                        'type': 'bytes32',
                        'value': '0x1e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112'},
                       {'name': 'sender',
                        'type': 'address',
                        'value': '0x849D52316331967b6fF1198e5E32A0eB168D039d'},
                       {'name': 'recipient',
                        'type': 'address',
                        'value': '0x849D52316331967b6fF1198e5E32A0eB168D039d'},
                       {'components': [{'name': 'assets',
                                        'type': 'address[]'},
                                       {'name': 'min_amounts_out',
                                        'type': 'uint256[]'},
                                       {'name': 'user_data',
                                        'type': 'bytes'},
                                       {'name': 'to_internal_balance',
                                        'type': 'bool'}],
                        'name': 'request',
                        'type': 'tuple',
                        'value': [['0xae78736Cd615f374D3085123A210448E74Fc6393',
                                   '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'],
                                  [163026746048782036464,
                                   177860865584174156974],
                                  '0x0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000012c03e0fdb2d857add',
                                  False]}],
            'name': 'exitPool',
            'outputs': [],
            'to_address': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
            'type': 'function',
            'value': 0}],
        'transaction': {'chainId': 1,
                        'data': '0x6928e74b000000000000000000000000a238cbeb142c10ef7ad8442c6d1f9e89e07e7761000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000003648d80ff0a0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000031200dd1fe5ad401d4777ce89959b7fa587e569bf125d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044c32e7202000000000000000000000000000000000000000000000012c03e0fdb2d857add000000000000000000000000000000000000000000000000000000000000000100ba12222222228d8ba445958a75a0704d566bf2c8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002248bdb39131e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000ae78736cd615f374d3085123a210448e74fc6393000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000008d67359c755786df0000000000000000000000000000000000000000000000009a450bae6cc334cae00000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000012c03e0fdb2d857add000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
                        'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
                        'gas': 1422520,
                        'nonce': 559,
                        'to': '0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc',
                        'value': 0}},
    {'decoded_transaction': [{
        'data': '0xc32e7202000000000000000000000000000000000000000000000012c03e0fdb2d857add0000000000000000000000000000000000000000000000000000000000000001',
        'from_address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
        'inputs': [{'name': 'amount',
                    'type': 'uint256',
                    'value': 345893920264646130397},
                   {'name': 'claim',
                    'type': 'bool',
                    'value': True}],
        'name': 'withdrawAndUnwrap',
        'outputs': [],
        'to_address': '0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D',
        'type': 'function',
        'value': 0},
        {
            'data': '0x8bdb39131e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000ae78736cd615f374d3085123a210448e74fc6393000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000011b3112d5c8cbd51b6000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000012c03e0fdb2d857add0000000000000000000000000000000000000000000000000000000000000000',
            'from_address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
            'inputs': [{'name': 'pool_id',
                        'type': 'bytes32',
                        'value': '0x1e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112'},
                       {'name': 'sender',
                        'type': 'address',
                        'value': '0x849D52316331967b6fF1198e5E32A0eB168D039d'},
                       {'name': 'recipient',
                        'type': 'address',
                        'value': '0x849D52316331967b6fF1198e5E32A0eB168D039d'},
                       {'components': [{'name': 'assets',
                                        'type': 'address[]'},
                                       {'name': 'min_amounts_out',
                                        'type': 'uint256[]'},
                                       {'name': 'user_data',
                                        'type': 'bytes'},
                                       {'name': 'to_internal_balance',
                                        'type': 'bool'}],
                        'name': 'request',
                        'type': 'tuple',
                        'value': [['0xae78736Cd615f374D3085123A210448E74Fc6393',
                                   '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'],
                                  [326497793535977017782, 0],
                                  '0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000012c03e0fdb2d857add0000000000000000000000000000000000000000000000000000000000000000',
                                  False]}],
            'name': 'exitPool',
            'outputs': [],
            'to_address': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
            'type': 'function',
            'value': 0}],
        'transaction': {'chainId': 1,
                        'data': '0x6928e74b000000000000000000000000a238cbeb142c10ef7ad8442c6d1f9e89e07e7761000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000003848d80ff0a0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000033200dd1fe5ad401d4777ce89959b7fa587e569bf125d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044c32e7202000000000000000000000000000000000000000000000012c03e0fdb2d857add000000000000000000000000000000000000000000000000000000000000000100ba12222222228d8ba445958a75a0704d566bf2c8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002448bdb39131e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000ae78736cd615f374d3085123a210448e74fc6393000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000011b3112d5c8cbd51b6000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000012c03e0fdb2d857add0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
                        'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
                        'gas': 1440091,
                        'nonce': 559,
                        'to': '0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc',
                        'value': 0}}
]


@pytest.mark.parametrize("args, expected", zip(positions_mock[0]['exec_config'], expected_outputs))
def test_transaction_builder(local_node_eth, accounts, monkeypatch, args, expected):
    private_key = set_up_roles(local_node_eth, accounts)
    set_env(monkeypatch, private_key)

    file_path_main = os.path.join(Path(os.path.dirname(__file__)).resolve().parent.parent.parent, 'roles_royce',
                                  'applications', 'panic_button_app',
                                  'transaction_builder.py')

    arguments = [
        'python', file_path_main,
        '--percentage', str(23),
        '--dao', dao,
        '--blockchain', blockchain,
        '--protocol', positions_mock[0]['protocol'],
        '--exit-strategy', args['function_name'],
    ]

    exit_arguments_dict = {}
    for item in args['parameters']:
        if item['type'] == 'constant':
            exit_arguments_dict[item['name']] = item['value']
        elif item['name'] == 'max_slippage':
            exit_arguments_dict[item['name']] = 0.01
        elif item['name'] == 'token_out_address':
            exit_arguments_dict[item['name']] = item['options'][0]['value']
    exit_arguments = [exit_arguments_dict]
    # Convert the parameters to a JSON string
    parameters_json = json.dumps(exit_arguments)
    arguments.extend(['--exit-arguments', parameters_json])
    main = subprocess.run(arguments, capture_output=True, text=True)

    assert main.returncode == 0
    dict_message_stdout = json.loads(main.stdout[:-1])
    assert dict_message_stdout['status'] == 200
    response = dict_message_stdout['tx_data']
    del response['transaction']['maxFeePerGas']  # Gas fees change even in the fork
    del response['transaction']['maxPriorityFeePerGas']  # Gas fees change even in the fork
    assert response == expected