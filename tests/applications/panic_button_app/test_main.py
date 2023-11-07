from roles_royce.applications.panic_button_app.panic_button_main import start_the_engine, gear_up, drive_away
from roles_royce.applications.panic_button_app.utils import ENV, ExecConfig, Environment
from tests.utils import assign_role, local_node_eth, accounts, fork_unlock_account
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
    monkeypatch.setenv('ETHEREUM_FALLBACK_RPC_ENDPOINT', 'DummyString')
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_AVATAR_SAFE_ADDRESS', avatar_safe_address)
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_ROLES_MOD_ADDRESS', roles_mod_address)
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_ROLE', role)
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_PRIVATE_KEY', private_key)
    # Without setting the ENVIRONMENT env it will default to DEVELOPMENT and use the local fork
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
    "simulate": False,
    "protocol": "Aura",
    "exit_strategy": "exit_2_1",
    "percentage": 21,
    "exit_arguments": {

        "rewards_address": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D",
        "max_slippage": 0.01
    }
}

exec_config = ExecConfig(percentage=JSON_FORM["percentage"],
                         simulate=JSON_FORM["simulate"],
                         dao=dao,
                         blockchain=blockchain,
                         protocol=JSON_FORM["protocol"],
                         exit_strategy=JSON_FORM["exit_strategy"],
                         exit_arguments=[JSON_FORM["exit_arguments"]])


def test_start_the_engine(monkeypatch):
    env = set_env(monkeypatch, "0x0000000000000000000000000000000000000000000000000000000000000000")

    w3 = start_the_engine(env)
    assert w3.is_connected()

    env.ENVIRONMENT = Environment.PRODUCTION
    with pytest.raises(Exception):
        start_the_engine(env)  # RPC endpoints are 'DummyString'


def test_gear_up(monkeypatch, local_node_eth):
    private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    env = set_env(monkeypatch, private_key)

    w3 = local_node_eth.w3
    local_node_eth.set_block(18437790)

    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
    assert disassembler.avatar_safe_address == '0x849D52316331967b6fF1198e5E32A0eB168D039d'
    assert txn_transactables[
               0].data == '0xc32e72020000000000000000000000000000000000000000000000111ed47dc81e6e5ad80000000000000000000000000000000000000000000000000000000000000001'
    assert txn_transactables[
               1].data == '0x8bdb39131e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000ae78736cd615f374d3085123a210448e74fc6393000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000007e9af502b84ea855b000000000000000000000000000000000000000000000008cc84206c7773d6ed000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000111ed47dc81e6e5ad8'


def test_drive_away(local_node_eth, accounts, monkeypatch):
    w3 = local_node_eth.w3
    block = 18421437
    local_node_eth.set_block(block)

    private_key = set_up_roles(local_node_eth, accounts)

    env = set_env(monkeypatch, private_key)
    fork_unlock_account(w3, env.DISASSEMBLER_ADDRESS)

    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)

    response = drive_away(disassembler=disassembler,
                          txn_transactables=txn_transactables,
                          env=env,
                          simulate=exec_config.simulate)

    assert response['status'] == 200
    assert response['message'] == "Transaction executed successfully"

    local_node_eth.set_block(block)
    env.DISASSEMBLER_ADDRESS = accounts[3].address  # Any address not member of the role
    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
    response_reverted = drive_away(disassembler=disassembler,
                                   txn_transactables=txn_transactables,
                                   env=env,
                                   simulate=exec_config.simulate)

    assert response_reverted['status'] == 422
    assert response_reverted['message'] == "Transaction reverted when simulated with local eth_call"

    local_node_eth.set_block(block)
    env.DISASSEMBLER_ADDRESS = '0x'
    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
    response_exception = drive_away(disassembler=disassembler,
                                    txn_transactables=txn_transactables,
                                    env=env,
                                    simulate=exec_config.simulate)

    assert response_exception['status'] == 500
    assert response_exception['message'] == "Error: ENS name: '0x' is invalid."


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

@pytest.mark.parametrize("args", positions_mock[0]['exec_config'])
def test_integration_main(local_node_eth, accounts, monkeypatch, args):
    private_key = set_up_roles(local_node_eth, accounts)
    set_env(monkeypatch, private_key)

    file_path_main = os.path.join(Path(os.path.dirname(__file__)).resolve().parent.parent.parent, 'roles_royce',
                                  'applications', 'panic_button_app',
                                  'panic_button_main.py')

    arguments = [
        'python', file_path_main,
        '-p', str(23),
        '-d', dao,
        '-b', blockchain,
        '-prot', positions_mock[0]['protocol'],
        '-s', args['function_name'],
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
    arguments.extend(['-a', parameters_json])
    main = subprocess.run(arguments, capture_output=True, text=True)

    assert main.returncode == 0
    dict_message_stdout = json.loads(main.stdout[:-1].replace("\'", "\""))
    assert dict_message_stdout['status'] == 200
    assert dict_message_stdout['message'] == "Transaction executed successfully"
