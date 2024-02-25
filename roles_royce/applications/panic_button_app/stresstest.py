import json
from dataclasses import dataclass
import logging
import os
from pathlib import Path
import subprocess

from web3 import Web3

from defabipedia.types import Chain
from defabipedia.balancer import Abis as BalancerAbis
from defabipedia.aura import Abis as AuraAbis

from roles_royce.applications.panic_button_app.utils import recovery_mode_balancer
from roles_royce.applications.panic_button_app.transaction_builder import main as tx_builder
from roles_royce.applications.panic_button_app.execute import main as tx_execute_main

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

@dataclass
class DAO:
    name: str
    blockchain: str
    avatar_safe_address: str
    roles_mod_address: str
    disassembler_address: str
    role: int

def stresstest(w3: Web3, positions_dict: dict, percentage: int, max_slippage: int, dao: str = None, blockchain: str = None):
    file_path_transaction_builder = os.path.join(Path(os.path.dirname(__file__)).resolve().parent.parent.parent,
                                             'roles_royce', 'applications', 'panic_button_app',
                                             'transaction_builder.py')
    file_path_execute = os.path.join(Path(os.path.dirname(__file__)).resolve().parent.parent.parent, 'roles_royce',
                                 'applications', 'panic_button_app',
                                 'execute.py')
    if not dao:
        dao = positions_dict['dao']
    if not blockchain:
        blockchain = positions_dict['blockchain']

    #SOMETHING NOT WORKING WITH THE ITERATION ON POSITIONS, check the dicts die input zijn
    for position in positions_dict['positions']:
        protocol = position["protocol"]
        for exec_config in position["exec_config"]:

            logger.info(f'Running stresstest on DAO: {dao}, Blockchain: {blockchain}, Protocol: {protocol}')
            logger.info(f'Position: {exec_config["function_name"]}, description: {exec_config["description"]}')

            arguments_build = [
                'python', file_path_transaction_builder,
                '--percentage', str(percentage),
                '--dao', dao,
                '--blockchain', blockchain,
                '--protocol', protocol,
                '--exit-strategy', exec_config['function_name'],
            ]

            exit_arguments_dict = {}
            for item in exec_config['parameters']:
                if item['type'] == 'constant':
                    exit_arguments_dict[item['name']] = item['value']
                elif item['name'] == 'max_slippage':
                    exit_arguments_dict[item['name']] = max_slippage
                elif item['name'] == 'token_out_address':
                    exit_arguments_dict[item['name']] = item['options'][0]['value']
            exit_arguments = [exit_arguments_dict]

            blockchain = Chain.get_blockchain_from_web3(w3)
            if protocol == 'Balancer' and (exec_config['function_name'] == 'exit_1_1' or exec_config['function_name'] == 'exit_1_3'):
                bpt_address = exit_arguments_dict['bpt_address']
                test = recovery_mode_balancer(w3, bpt_address, exec_config['function_name'])
                if test:
                    continue
            elif protocol == 'Balancer' and (exec_config['function_name'] == 'exit_2_1' or exec_config['function_name'] == 'exit_2_3'):
                gauge_address = exit_arguments_dict['gauge_address']
                gauge_contract = w3.eth.contract(address=gauge_address,
                                                        abi=BalancerAbis[blockchain].Gauge.abi)
                bpt_address = gauge_contract.functions.lp_token().call()  
                test = recovery_mode_balancer(w3, bpt_address, exec_config['function_name'])
                if test:
                    continue
            elif protocol == 'Aura' and (exec_config['function_name'] == 'exit_2_1' or exec_config['function_name'] == 'exit_2_3'):
                aura_rewards_address = exit_arguments_dict['rewards_address']
                aura_rewards_contract = w3.eth.contract(address=aura_rewards_address,
                                                            abi=AuraAbis[blockchain].BaseRewardPool.abi)
                bpt_address = aura_rewards_contract.functions.asset().call()
                test = recovery_mode_balancer(w3, bpt_address, exec_config['function_name'])
                if test:
                    continue
                
            logger.info(f'Exit arguments: {exit_arguments}')

            parameters_json = json.dumps(exit_arguments)
            arguments_build.extend(['-a', parameters_json])

            try:
                main = subprocess.run(arguments_build, capture_output=True, text=True)
                if json.loads(main.stdout)["status"]!=200:
                    logger.error(f'Error in transaction builder. Error: {json.loads(main.stdout)["message"]}')
                else:
                    logger.info(f'Status of transaction builder: {json.loads(main.stdout)["status"]}')
                    dict_message_stdout = json.loads(main.stdout[:-1])
                    tx = json.dumps(dict_message_stdout['tx_data']['transaction'])

                    arguments_execute = [
                        'python', file_path_execute,
                        '--dao', dao,
                        '--blockchain', blockchain,
                        '--transaction', tx
                    ]

                    try:
                        main = subprocess.run(arguments_execute, capture_output=True, text=True)
                        if json.loads(main.stdout)["status"]!=200:
                            logger.error(f'Error in execution. Error: {json.loads(main.stdout)["message"]}')
                        else:
                            logger.info(f'Status of execution: {json.loads(main.stdout)["status"]}')
                            exec_config['stresstest'] = True
                    except Exception as f:
                        logger.error(f'Error in execution. Error: {str(f)}')

            except Exception as e:
                logger.error(f'Error in transaction builder. Error: {str(e)}')

    return positions_dict
       


            



        