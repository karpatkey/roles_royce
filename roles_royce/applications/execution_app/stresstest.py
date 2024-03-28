import collections
import logging
from dataclasses import dataclass

from defabipedia.aura import Abis as AuraAbis
from defabipedia.balancer import Abis as BalancerAbis
from defabipedia.types import Chain
from joblib import Parallel, delayed
from web3 import Web3

from roles_royce.applications.execution_app.execute import execute_env
from roles_royce.applications.execution_app.pulley_fork import PulleyFork
from roles_royce.applications.execution_app.transaction_builder import build_transaction_env
from roles_royce.applications.execution_app.utils import ENV, recovery_mode_balancer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


@dataclass
class DAO:
    name: str
    blockchain: str
    avatar_safe_address: str
    roles_mod_address: str
    disassembler_address: str
    role: int


# def single_stresstest(w3: Web3, percentage: int, dao, blockchain, protocol, exec_config, bc, max_slippage, percentage):
def single_stresstest(
    w3: Web3, percentage: int, max_slippage: int, dao: str, blockchain: str, protocol: str, exec_config, bc
):
    logger.info(f"Running stresstest on DAO: {dao}, Blockchain: {blockchain}, Protocol: {protocol}")
    logger.info(f'Position: {exec_config["function_name"]}, description: {exec_config["description"]}')

    exit_strategy = exec_config["function_name"]

    exit_arguments_dict = {}
    for item in exec_config["parameters"]:
        if item["type"] == "constant":
            exit_arguments_dict[item["name"]] = item["value"]
        elif item["name"] == "max_slippage":
            exit_arguments_dict[item["name"]] = max_slippage
        elif item["name"] == "token_out_address":
            exit_arguments_dict[item["name"]] = item["options"][0]["value"]
        elif item["name"] == "token_in_address":
            exit_arguments_dict[item["name"]] = item["options"][0]["value"]
    exit_arguments = [exit_arguments_dict]

    # blockchain = Chain.get_blockchain_from_web3(w3)
    chain_id = {"ethereum": 1, "gnosis": 100}.get(blockchain)
    bc = Chain.get_blockchain_by_chain_id(chain_id)

    if protocol == "Balancer" and (
        exec_config["function_name"] == "exit_1_1" or exec_config["function_name"] == "exit_1_3"
    ):
        bpt_address = exit_arguments_dict["bpt_address"]
        test = recovery_mode_balancer(w3, bpt_address, exec_config["function_name"], blockchain=bc)
        if test:
            return
    elif protocol == "Balancer" and (
        exec_config["function_name"] == "exit_2_1" or exec_config["function_name"] == "exit_2_3"
    ):
        gauge_address = exit_arguments_dict["gauge_address"]
        gauge_contract = w3.eth.contract(address=gauge_address, abi=BalancerAbis[bc].Gauge.abi)
        bpt_address = gauge_contract.functions.lp_token().call()
        test = recovery_mode_balancer(w3, bpt_address, exec_config["function_name"], blockchain=bc)
        if test:
            return
    elif protocol == "Aura" and (
        exec_config["function_name"] == "exit_2_1" or exec_config["function_name"] == "exit_2_3"
    ):
        aura_rewards_address = exit_arguments_dict["rewards_address"]
        aura_rewards_contract = w3.eth.contract(
            address=aura_rewards_address,
            abi=AuraAbis[bc].BaseRewardPool.abi,
        )
        bpt_address = aura_rewards_contract.functions.asset().call()
        test = recovery_mode_balancer(w3, bpt_address, exec_config["function_name"], blockchain=bc)
        if test:
            return

    logger.info(f"Exit arguments: {exit_arguments}")

    try:
        with PulleyFork(blockchain) as fork:
            env = ENV(DAO=dao or "", BLOCKCHAIN=blockchain, LOCAL_FORK_URL=fork.url())
            result = build_transaction_env(
                env=env,
                percentage=percentage,
                protocol=protocol,
                exit_strategy=exit_strategy,
                exit_arguments=exit_arguments,
            )
            if result["status"] != 200:
                logger.error(f'Error in transaction builder. Error1: {result["message"]}')
                exec_config["stresstest"] = f"false, with error: {result['message']}"
            else:
                logger.info(f'Status of transaction builder: {result["status"]}')
                tx = result["tx_data"]["transaction"]

                try:
                    result = execute_env(env=env, transaction=tx)
                    if result["status"] != 200:
                        logger.error(f'Error in execution. Error: {result["message"]}')
                        exec_config["stresstest"] = f"false, with error: {result['message']}"
                    else:
                        logger.info(f'Status of execution: {result["status"]}')
                        exec_config["stresstest"] = True

                except Exception as f:
                    logger.error(f"Exception in execution. Error: {f}")
                    exec_config["stresstest"] = f"false, with error: {str(f)}"

    except Exception as e:
        logger.error(f"Error in transaction builder. Error: {str(e)}")
        exec_config["stresstest"] = f"false, with error: {str(e)}"


def stresstest(
    w3: Web3,
    positions_dict: dict,
    percentage: int,
    max_slippage: int,
    dao: str | None = None,
    blockchain: str | None = None,
):
    dao = dao or positions_dict["dao"]
    blockchain = blockchain or positions_dict["blockchain"]
    chain_id = {"ethereum": 1, "gnosis": 100}.get(blockchain)
    bc = Chain.get_blockchain_by_chain_id(chain_id)

    executions = []
    for position in positions_dict["positions"]:
        protocol = position["protocol"]
        for exec_config in position["exec_config"]:
            executions.append([w3, percentage, max_slippage, dao, blockchain, protocol, exec_config, bc])

    results = Parallel(n_jobs=4, backend="threading")(delayed(single_stresstest)(*args) for args in executions)
    collections.deque(results, maxlen=0)

    return positions_dict
