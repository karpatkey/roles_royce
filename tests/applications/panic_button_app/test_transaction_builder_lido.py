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


    disassembler_address = accounts[0].address
    private_key = accounts[0].key.hex()

    assign_role(local_node=local_node_eth,
                avatar_safe_address=avatar_safe_address,
                roles_mod_address=roles_mod_address,
                role=role,
                asignee=disassembler_address)
    return private_key


JSON_FORM = {
    "protocol": "Lido",
    "exit_strategy": "exit_3",
    "percentage": 21,
    "exit_arguments": {
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
        "position_id": "Lido_64",
        "protocol": "Lido",
        "exec_config": [
                {
                    "function_name": "exit_1",
                    "label": "Unstake stETH",
                    "test": False,
                    "description": "Unstake stETH for ETH",
                    "parameters": []
                },
                {
                    "function_name": "exit_3",
                    "label": "Swap stETH",
                    "test": False,
                    "description": "Swap stETH for ETH",
                    "parameters": [
                        {
                            "name": "max_slippage",
                            "type": "input",
                            "label": "Max slippage",
                            "rules": {
                                "min": 0,
                                "max": 100
                            }
                        }
                    ]
                }
            ]
    }
]

expected_outputs = [{'transaction': {'value': 0, 'chainId': 1, 'gas': 1031659, 'nonce': 606, 'to': '0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc', 'data': '0x6928e74b000000000000000000000000a238cbeb142c10ef7ad8442c6d1f9e89e07e7761000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000002248d80ff0a000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000001d200ae7ab96520de3a18e5e111b5eaab095312d7fe8400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044095ea7b3000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b10000000000000000000000000000000000000000000000ad0c3445fca5a2f81600889edc2edab5f40e902b864ad4d7ade8e412f9b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e4d66810420000000000000000000000000000000000000000000000000000000000000040000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000000a6ad73cab09c2f816000000000000000000000000000000000000000000000000000000000000000000000000000000000000', 'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'}, 'decoded_transaction': [{'name': 'approve', 'type': 'function', 'inputs': [{'name': 'spender', 'type': 'address', 'value': '0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1'}, {'name': 'amount', 'type': 'uint256', 'value': 3192166129530409515030}], 'outputs': [], 'to_address': '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84', 'value': 0, 'data': '0x095ea7b3000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b10000000000000000000000000000000000000000000000ad0c3445fca5a2f816', 'from_address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'}, {'name': 'requestWithdrawals', 'type': 'function', 'inputs': [{'name': 'amounts', 'type': 'uint256[]', 'value': [1000000000000000000000, 1000000000000000000000, 1000000000000000000000, 192166129530409515030]}, {'name': 'owner', 'type': 'address', 'value': '0x849D52316331967b6fF1198e5E32A0eB168D039d'}], 'outputs': [], 'to_address': '0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1', 'value': 0, 'data': '0xd66810420000000000000000000000000000000000000000000000000000000000000040000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000003635c9adc5dea0000000000000000000000000000000000000000000000000000a6ad73cab09c2f816', 'from_address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'}]},
                    {'transaction': {'value': 0, 'chainId': 1, 'gas': 1577482, 'nonce': 606, 'to': '0x8C33ee6E439C874713a9912f3D3debfF1Efb90Da', 
                                     'data': '0x6928e74b000000000000000000000000a238cbeb142c10ef7ad8442c6d1f9e89e07e7761000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000003a48d80ff0a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000352002a14db8d09db0542f6a371c0cb308a768227d67d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044c32e7202000000000000000000000000000000000000000000000006a6b78270110a57ef000000000000000000000000000000000000000000000000000000000000000100ba12222222228d8ba445958a75a0704d566bf2c8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002648bdb391393d199263632a4ef4bb438f1feb99e57b4b5f0bd0000000000000000000005c200000000000000000000000058e6c7ab55aa9012eacca16d1ed4c15795669e1c00000000000000000000000058e6c7ab55aa9012eacca16d1ed4c15795669e1c0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca000000000000000000000000093d199263632a4ef4bb438f1feb99e57b4b5f0bd000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000003f74041e57674bf430000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002231819c61133e89800000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000006a6b78270110a57ef000000000000000000000000000000000000000000000000000000000000000000000000000000000000', 
                                     'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'}, 'decoded_transaction':
                                       [{'name': 'withdrawAndUnwrap', 'type': 'function', 'inputs': [{'name': 'amount', 'type': 'uint256', 'value': 122693678391125235695},
                                                                                                      {'name': 'claim', 'type': 'bool', 'value': True}], 
                                                                                                      'outputs': [], 'to_address': '0x2a14dB8D09dB0542f6A371c0cB308A768227D67D', 
                                                                                                      'value': 0, 'data': '0xc32e7202000000000000000000000000000000000000000000000006a6b78270110a57ef0000000000000000000000000000000000000000000000000000000000000001',
                                                                                                        'from_address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'}, 
                                                                                                        {'name': 'exitPool', 'type': 'function', 'inputs':
                                                                                                          [{'name': 'pool_id', 'type': 'bytes32', 'value': '0x93d199263632a4ef4bb438f1feb99e57b4b5f0bd0000000000000000000005c2'},
                                                                                                            {'name': 'sender', 'type': 'address', 'value': '0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C'},
                                                                                                              {'name': 'recipient', 'type': 'address', 'value': '0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C'},
                                                                                                                {'name': 'request', 'type': 'tuple', 'components': [{'name': 'assets', 'type': 'address[]'}, 
                                                                                                                                                                    {'name': 'min_amounts_out', 'type': 'uint256[]'},
                                                                                                                                                                      {'name': 'user_data', 'type': 'bytes'}, {'name': 'to_internal_balance', 'type': 'bool'}],
                                                                                                                                                                        'value': [['0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0',
                                                                                                                                                                                    '0x93d199263632a4EF4Bb438F1feB99e57b4b5f0BD', 
                                                                                                                                                                                    '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'],
                                                                                                                                                                                 [73156544800797015875, 0, 39422287676670470296], 
                                                                                                                                                                                 '0x0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000006a6b78270110a57ef', False]}],
                                                                                                                                                                                   'outputs': [], 'to_address': '0xBA12222222228d8Ba445958a75a0704d566BF2C8', 'value': 0, 
                                                                                                                                                                                   'data': '0x8bdb391393d199263632a4ef4bb438f1feb99e57b4b5f0bd0000000000000000000005c200000000000000000000000058e6c7ab55aa9012eacca16d1ed4c15795669e1c00000000000000000000000058e6c7ab55aa9012eacca16d1ed4c15795669e1c0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca000000000000000000000000093d199263632a4ef4bb438f1feb99e57b4b5f0bd000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000003f74041e57674bf430000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002231819c61133e89800000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000006a6b78270110a57ef', 
                                                                                                                                                                                   'from_address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'}]}]

@pytest.mark.parametrize("args, expected", zip(positions_mock[0]['exec_config'], expected_outputs))
def test_transaction_builder_lido(local_node_eth, accounts, monkeypatch, args, expected):
    block = 19096100
    local_node_eth.set_block(block)
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
    response = dict_message_stdout['tx_data']
    print(response)
    assert dict_message_stdout['status'] == 200
    del response['transaction']['maxFeePerGas']  # Gas fees change even in the fork
    del response['transaction']['maxPriorityFeePerGas']  # Gas fees change even in the fork
    w3 = local_node_eth.w3
    print(response)
    # In the CI tests we get differences in the nonce, so we need to "hardcode" the nonce from the node
    expected['transaction']['nonce'] = w3.eth.get_transaction_count(w3.eth.account.from_key(private_key).address)
    assert response == expected
