from roles_royce.applications.panic_button_app.utils import ENV, ExecConfig
from tests.utils import assign_role, local_node_eth, accounts
import os
import json
import pytest
import subprocess
from pathlib import Path

dao = 'karpatkey'
blockchain = 'ETHEREUM'
avatar_safe_address = '0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C'
roles_mod_address = '0x8C33ee6E439C874713a9912f3D3debfF1Efb90Da'
role = 1


def set_env(monkeypatch, private_key: str) -> ENV:
    monkeypatch.setenv('ETHEREUM_RPC_ENDPOINT', 'DummyString')
    monkeypatch.setenv('ETHEREUM_RPC_ENDPOINT_FALLBACK', 'DummyString')
    monkeypatch.setenv('KARPATKEY_ETHEREUM_AVATAR_SAFE_ADDRESS', avatar_safe_address)
    monkeypatch.setenv('KARPATKEY_ETHEREUM_ROLES_MOD_ADDRESS', roles_mod_address)
    monkeypatch.setenv('KARPATKEY_ETHEREUM_ROLE', role)
    monkeypatch.setenv('KARPATKEY_ETHEREUM_PRIVATE_KEY', private_key)
    # Without setting the MODE env it will default to DEVELOPMENT and use the local fork
    return ENV(dao, blockchain)


def set_up_roles(local_node_eth, accounts):
    block = 19084800
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

        "rewards_address": "0x2a14dB8D09dB0542f6A371c0cB308A768227D67D",
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
        "position_id": "Aura_268",
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
                        "value": "0x2a14dB8D09dB0542f6A371c0cB308A768227D67D"
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
                        "value": "0x2a14dB8D09dB0542f6A371c0cB308A768227D67D"
                    },
                    {
                        "name": "max_slippage",
                        "label": "Max slippage",
                        "type": "input",
                        "rules": {"min": 0, "max": 100}
                    }
                ]
            },
        ]
    }
]

expected_outputs = [{'transaction': {'value': 0, 'chainId': 1, 'gas': 1123651, 'nonce': 606, 'to': '0x8C33ee6E439C874713a9912f3D3debfF1Efb90Da', 
                                     'data': '0x6928e74b0000000000000000000000002a14db8d09db0542f6a371c0cb308a768227d67d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000044c32e7202000000000000000000000000000000000000000000000006a6b78270110a57ef000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000', 
                                     'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'}, 'decoded_transaction': 
                                     [{'name': 'withdrawAndUnwrap', 'type': 'function', 'inputs': [{'name': 'amount', 'type': 'uint256', 
                                                                                                    'value': 122693678391125235695}, 
                                                                                                    {'name': 'claim', 'type': 'bool', 'value': True}], 
                                                                                                    'outputs': [], 'to_address': '0x2a14dB8D09dB0542f6A371c0cB308A768227D67D', 
                                                                                                    'value': 0, 'data': '0xc32e7202000000000000000000000000000000000000000000000006a6b78270110a57ef0000000000000000000000000000000000000000000000000000000000000001', 
                                                                                                    'from_address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'}]},
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
def test_transaction_builder_kpk(local_node_eth, accounts, monkeypatch, args, expected):
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
    w3 = local_node_eth.w3
    # In the CI tests we get differences in the nonce, so we need to "hardcode" the nonce from the node
    expected['transaction']['nonce'] = w3.eth.get_transaction_count(w3.eth.account.from_key(private_key).address)
    assert response == expected
