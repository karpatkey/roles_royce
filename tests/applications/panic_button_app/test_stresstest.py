from roles_royce.applications.panic_button_app.utils import ENV
from tests.utils import assign_role, local_node_eth, accounts, web3_eth, local_node_gc, web3_gnosis
import os
import json
import pytest
import subprocess
from pathlib import Path
from dataclasses import dataclass
import logging
from time import sleep

logging.basicConfig(filename='stresstest.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

PERCENTAGE = 20
MAX_SLIPPAGE = 1


@dataclass
class DAO:
    name: str
    blockchain: str
    avatar_safe_address: str
    roles_mod_address: str
    role: int


daos = [DAO(name="GnosisDAO",
            blockchain="ETHEREUM",
            avatar_safe_address="0x849D52316331967b6fF1198e5E32A0eB168D039d",
            roles_mod_address="0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc",
            role=4),
        DAO(name="GnosisDAO",
            blockchain="GNOSIS",
            avatar_safe_address="0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f",
            roles_mod_address="0x10785356E66b93432e9E8D6F9e532Fa55e4fc058",
            role=4),
        DAO(name="GnosisLtd",
            blockchain="ETHEREUM",
            avatar_safe_address="0x4971DD016127F390a3EF6b956Ff944d0E2e1e462",
            roles_mod_address="0xEF4A73A20e2c6C6771C334e18a417A19Abb29c09",
            role=4),
        DAO(name="GnosisLtd",
            blockchain="GNOSIS",
            avatar_safe_address="0x10E4597fF93cbee194F4879f8f1d54a370DB6969",
            roles_mod_address="0x494ec5194123487E8A6ba0b6bc96D57e340025e7",
            role=4),
        DAO(name="karpatkey",
            blockchain="ETHEREUM",
            avatar_safe_address="0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C",
            roles_mod_address="0x8C33ee6E439C874713a9912f3D3debfF1Efb90Da",
            role=1),
        # DAO(name="BalancerDAO",
        #     blockchain="ETHEREUM",
        #     avatar_safe_address="0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C",
        #     roles_mod_address="0x8C33ee6E439C874713a9912f3D3debfF1Efb90Da",
        #     role=1),
        # DAO(name="ENS",
        #     blockchain="ETHEREUM",
        #     avatar_safe_address="0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89",
        #     roles_mod_address="0xd8dd9164E765bEF903E429c9462E51F0Ea8514F9",
        #     role=1)

        ]

file_path_transaction_builder = os.path.join(Path(os.path.dirname(__file__)).resolve().parent.parent.parent,
                                             'roles_royce', 'applications', 'panic_button_app',
                                             'transaction_builder.py')
file_path_execute = os.path.join(Path(os.path.dirname(__file__)).resolve().parent.parent.parent, 'roles_royce',
                                 'applications', 'panic_button_app',
                                 'execute.py')
# -----------------------------------------------------------------------------------------------------------------------
daos_exec_configs = []
for dao in daos:
    file_path_json = os.path.join(Path(os.path.dirname(__file__)).resolve().parent.parent.parent, 'roles_royce',
                                  'applications', 'panic_button_app',
                                  'config', 'strategies', f'{dao.name}-{dao.blockchain.lower()}.json')
    with open(file_path_json, 'r') as f:
        strategies = json.load(f)
    exec_configs = []
    for position in strategies['positions']:
        for element in position["exec_config"]:
            if element["test"]:
                item = element.copy()
                item['protocol'] = position['protocol']
                exec_configs.append(item)
    daos_exec_configs.append(exec_configs)

test_parameters = [(dao, exec_config) for dao, sublist in zip(daos, daos_exec_configs) for exec_config in sublist]


# -----------------------------------------------------------------------------------------------------------------------


def set_up_roles(local_node_eth, local_node_gc, accounts, dao: DAO):
    if dao.blockchain == 'ETHEREUM':
        block = local_node_eth.w3.eth.default_block
        local_node_eth.set_block(block)
        logging.info(f'Block number: {local_node_eth.w3.eth.block_number}')
        disassembler_address = accounts[0].address
        private_key = accounts[0].key.hex()
        assign_role(local_node=local_node_eth,
                    avatar_safe_address=dao.avatar_safe_address,
                    roles_mod_address=dao.roles_mod_address,
                    role=dao.role,
                    asignee=disassembler_address)
    elif dao.blockchain == 'GNOSIS':
        block = local_node_gc.w3.eth.default_block
        local_node_gc.set_block(block)
        logging.info(f'Block number: {local_node_gc.w3.eth.block_number}')
        disassembler_address = accounts[0].address
        private_key = accounts[0].key.hex()
        assign_role(local_node=local_node_gc,
                    avatar_safe_address=dao.avatar_safe_address,
                    roles_mod_address=dao.roles_mod_address,
                    role=dao.role,
                    asignee=disassembler_address)
    else:
        raise ValueError(f'Blockchain {dao.blockchain} not supported')

    return private_key


def set_env(monkeypatch, private_key: str, dao: DAO) -> ENV:
    monkeypatch.setenv(f'{dao.name.upper()}_{dao.blockchain.upper()}_AVATAR_SAFE_ADDRESS', dao.avatar_safe_address)
    monkeypatch.setenv(f'{dao.name.upper()}_{dao.blockchain.upper()}_ROLES_MOD_ADDRESS', dao.roles_mod_address)
    monkeypatch.setenv(f'{dao.name.upper()}_{dao.blockchain.upper()}_ROLE', dao.role)
    monkeypatch.setenv(f'{dao.name.upper()}_{dao.blockchain.upper()}_PRIVATE_KEY', private_key)
    return ENV(dao.name, dao.blockchain)


@pytest.mark.skipif(not os.environ.get("RR_RUN_STRESSTEST", False),
                    reason="Long position integration test not running by default.")
@pytest.mark.parametrize("dao, exec_config", test_parameters)
def test_stresstest(local_node_eth, local_node_gc, accounts, monkeypatch, dao, exec_config):
    private_key = set_up_roles(local_node_eth, local_node_gc, accounts, dao)
    set_env(monkeypatch, private_key, dao)

    logging.info(f'Running stresstest on DAO: {dao.name}, Blockchain: {dao.blockchain}, Protocol: {exec_config["protocol"]}')
    logging.info(f'Position: {exec_config["function_name"]}, description: {exec_config["description"]}')

    arguments_build = [
        'python', file_path_transaction_builder,
        '--percentage', str(PERCENTAGE),
        '--dao', dao.name,
        '--blockchain', dao.blockchain,
        '--protocol', exec_config['protocol'],
        '--exit-strategy', exec_config['function_name'],
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

    logging.info(f'Exit arguments: {exit_arguments}')

    # Convert the parameters to a JSON string
    parameters_json = json.dumps(exit_arguments)
    arguments_build.extend(['-a', parameters_json])

    try:
        main = subprocess.run(arguments_build, capture_output=True, text=True)
        if json.loads(main.stdout)["status"]!=200:
            logging.error(f'Error in transaction builder. Error: {json.loads(main.stdout)["message"]}')
        else:
            logging.info(f'Status of transaction builder: {json.loads(main.stdout)["status"]}')
    except Exception as e:
        logging.error(f'Error in transaction builder. Error: {str(e)}')

    assert main.returncode == 0
    dict_message_stdout = json.loads(main.stdout[:-1])
    assert dict_message_stdout['status'] == 200

    tx = json.dumps(dict_message_stdout['tx_data']['transaction'])

    arguments_execute = [
        'python', file_path_execute,
        '--dao', dao.name,
        '--blockchain', dao.blockchain,
        '--transaction', tx
    ]

    try:
        main = subprocess.run(arguments_execute, capture_output=True, text=True)
        if json.loads(main.stdout)["status"]!=200:
            logging.error(f'Error in execution. Error: {json.loads(main.stdout)["message"]}')
        else:
            logging.info(f'Status of execution: {json.loads(main.stdout)["status"]}')
    except Exception as f:
        logging.error(f'Error in execution. Error: {str(f)}')

    assert main.returncode == 0
    dict_message_stdout = json.loads(main.stdout[:-1])
    assert dict_message_stdout['status'] == 200

# The following test is meant to test individual exit strategies by specifying the index. If left empty ([]) the test
# will be skipped, if [3] is set, test_parameters[3] will be tested.
@pytest.mark.parametrize("index", [])
def test_stresstest_single(local_node_eth, local_node_gc, accounts, monkeypatch, index):
    dao = test_parameters[index][0]
    exec_config = test_parameters[index][1]
    private_key = set_up_roles(local_node_eth, local_node_gc, accounts, dao)
    set_env(monkeypatch, private_key, dao)

    logging.info(f'Running stresstest on DAO: {dao.name}, Blockchain: {dao.blockchain}, Protocol: {exec_config["protocol"]}')
    logging.info(f'Position: {exec_config["function_name"]}, description: {exec_config["description"]}')

    arguments_build = [
        'python', file_path_transaction_builder,
        '--percentage', str(PERCENTAGE),
        '--dao', dao.name,
        '--blockchain', dao.blockchain,
        '--protocol', exec_config['protocol'],
        '--exit-strategy', exec_config['function_name'],
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

    logging.info(f'Exit arguments: {exit_arguments}')

    # Convert the parameters to a JSON string
    parameters_json = json.dumps(exit_arguments)
    arguments_build.extend(['-a', parameters_json])

    try:
        main = subprocess.run(arguments_build, capture_output=True, text=True)
        if json.loads(main.stdout)["status"]!=200:
            logging.error(f'Error in transaction builder. Error: {json.loads(main.stdout)["message"]}')
        else:
            logging.info(f'Status of transaction builder: {json.loads(main.stdout)["status"]}')
    except Exception as e:
        logging.error(f'Error in transaction builder. Error: {str(e)}')

    assert main.returncode == 0
    dict_message_stdout = json.loads(main.stdout[:-1])
    assert dict_message_stdout['status'] == 200

    tx = json.dumps(dict_message_stdout['tx_data']['transaction'])

    arguments_execute = [
        'python', file_path_execute,
        '--dao', dao.name,
        '--blockchain', dao.blockchain,
        '--transaction', tx
    ]

    try:
        main = subprocess.run(arguments_execute, capture_output=True, text=True)
        if json.loads(main.stdout)["status"]!=200:
            logging.error(f'Error in execution. Error: {json.loads(main.stdout)["message"]}')
        else:
            logging.info(f'Status of execution: {json.loads(main.stdout)["status"]}')
    except Exception as f:
        logging.error(f'Error in execution. Error: {str(f)}')

    assert main.returncode == 0
    dict_message_stdout = json.loads(main.stdout[:-1])
    assert dict_message_stdout['status'] == 200
