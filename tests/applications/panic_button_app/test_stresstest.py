from roles_royce.applications.panic_button_app.utils import ENV
from tests.utils import assign_role, local_node_eth, accounts
import os
import json
import pytest
import subprocess
from pathlib import Path

PERCENTAGE = 20
MAX_SLIPPAGE = 1

dao = 'GnosisDAO'
blockchain = 'ETHEREUM'
avatar_safe_address = '0x849D52316331967b6fF1198e5E32A0eB168D039d'
roles_mod_address = '0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc'
role = 4

file_path_main = os.path.join(Path(os.path.dirname(__file__)).resolve().parent.parent.parent, 'roles_royce', 'applications', 'panic_button_app',
                              'panic_button_main.py')
file_path_json = os.path.join(Path(os.path.dirname(__file__)).resolve().parent.parent.parent, 'roles_royce', 'applications', 'panic_button_app',
                              'config', 'strategiesGnosisDAOEthereum.json')
with open(file_path_json, 'r') as f:
    strategies = json.load(f)
exec_configs = []
for position in strategies['positions']:
    for element in position["exec_config"]:
        if element["test"]:
            item = element.copy()
            item['protocol'] = position['protocol']
            exec_configs.append(item)


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
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_AVATAR_SAFE_ADDRESS', avatar_safe_address)
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_ROLES_MOD_ADDRESS', roles_mod_address)
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_ROLE', role)
    monkeypatch.setenv('GNOSISDAO_ETHEREUM_PRIVATE_KEY', private_key)
    return ENV(dao, blockchain)


@pytest.mark.skipif(not os.environ.get("RR_RUN_STRESSTEST", False), reason="Long position integration test not running by default.")
@pytest.mark.parametrize("exec_config", exec_configs)
def test_stresstest(local_node_eth, accounts, monkeypatch, exec_config):
    private_key = set_up_roles(local_node_eth, accounts)
    set_env(monkeypatch, private_key)

    arguments = [
        'python', file_path_main,
        '-p', str(PERCENTAGE),
        '-d', dao,
        '-b', blockchain,
        '-prot', exec_config['protocol'],
        '-s', exec_config['function_name'],
    ]

    exit_arguments_dict = {}
    for item in exec_config['parameters']:
        if item['type'] == 'constant':
            exit_arguments_dict[item['name']] = item['value']
        elif item['name'] == 'max_slippage':
            exit_arguments_dict[item['name']] = MAX_SLIPPAGE
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
    assert dict_message_stdout['message'] == "Transaction executed successfully" or dict_message_stdout['message'] == 'There are no funds in the position, no transaction needs to be executed'
