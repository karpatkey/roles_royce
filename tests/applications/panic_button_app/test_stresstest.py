from roles_royce.applications.panic_button_app.panic_button_main import start_the_engine, gear_up, drive_away
from roles_royce.applications.panic_button_app.utils import ENV, ExecConfig
from tests.utils import assign_role, local_node_eth, accounts

import json
from unittest.mock import patch
import pytest
import argparse
import subprocess

PERCENTAGE = 80
MAX_SLIPPAGE = 1

dao = 'GnosisDAO'
blockchain = 'mainnet'
avatar_safe_address = '0x849D52316331967b6fF1198e5E32A0eB168D039d'
roles_mod_address = '0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc'
role = 4

with open('strategiesGnosisDAOEthereum.json', 'r') as f:
    strategies = json.load(f)
list_of_positions = []
for position in strategies['positions']:
    for position_exec_config in position['position_exec_config']:
        list_of_positions.append(position_exec_config)


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


def set_env(monkeypatch, private_key: str) -> ENV:
    monkeypatch.setenv('GNOSISDAO_MAINNET_AVATAR_SAFE_ADDRESS', avatar_safe_address)
    monkeypatch.setenv('GNOSISDAO_MAINNET_ROLES_MOD_ADDRESS', roles_mod_address)
    monkeypatch.setenv('GNOSISDAO_MAINNET_ROLE', role)
    monkeypatch.setenv('GNOSISDAO_MAINNET_PRIVATE_KEY', private_key)
    return ENV(dao, blockchain)


@pytest.mark.skip("This test would take a huge time to run in the CI")
@pytest.mark.parametrize("args", list_of_positions)
def test_stresstest(local_node_eth, accounts, monkeypatch, args):
    private_key = set_up_roles(local_node_eth, accounts)

    env = set_env(monkeypatch, private_key)

    arguments = [
        'python', 'roles_royce/applications/panic_button_app/panic_button_main.py',
        '-p', str(PERCENTAGE),
        '-d', dao,
        '-b', blockchain,
        '-prot', position['protocol'],
        '-s', args['function_name'],
    ]

    exit_arguments_dict = {}
    for item in args['parameters']:
        if item['type'] == 'constant':
            exit_arguments_dict[item['name']] = item['value']
        elif item['name'] == 'max_slippage':
            exit_arguments_dict[item['name']] = MAX_SLIPPAGE
        elif item['name'] == 'token_out_address':
            exit_arguments_dict[item['name']] = item['options'][0]
        exit_arguments = [exit_arguments_dict]
    # Convert the parameters to a JSON string
    parameters_json = json.dumps(exit_arguments)
    arguments.extend(['-a', parameters_json])
    arguments.extend(['-t', '8546'])
    main = subprocess.run(arguments, capture_output=True, text=True)

    assert main.returncode == 0

    assert 'Expected output' in main.stdout
