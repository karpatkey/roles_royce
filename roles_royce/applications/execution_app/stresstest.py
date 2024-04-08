import collections
import logging
import logging.handlers
import threading
from dataclasses import dataclass

from decouple import config
from defabipedia.aura import Abis as AuraAbis
from defabipedia.balancer import Abis as BalancerAbis
from defabipedia.types import Chain
from joblib import Parallel, delayed
from web3 import Web3

from roles_royce.applications.execution_app.execute import execute_env
from roles_royce.applications.execution_app.pulley_fork import PulleyFork
from roles_royce.applications.execution_app.transaction_builder import build_transaction_env
from roles_royce.applications.execution_app.utils import ENV, recovery_mode_balancer, start_the_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@dataclass
class DAO:
    name: str
    blockchain: str
    avatar_safe_address: str
    roles_mod_address: str
    disassembler_address: str
    role: int


def initialize_logging(log_level, log_name="stresstest"):
    logger = logging.getLogger(f"{log_name}-{threading.get_native_id()}")
    logger.setLevel(log_level)

    mh = logging.handlers.MemoryHandler(100000, 100000)
    mh.setTarget(logging.StreamHandler())
    logger.handlers.clear()
    logger.addHandler(mh)

    mh.setFormatter(logging.Formatter("%(asctime)s -  %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.propagate = False
    return logger, mh


def single_stresstest(
    percentage: int, max_slippage: int, dao: str, blockchain: str, protocol: str, exec_config, web3: Web3
):
    id = f"{dao}-{blockchain}-{protocol}-{exec_config['function_name']}"
    logger, logger_handler = initialize_logging(logging.INFO, id)

    try:
        w3 = web3

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

        chain_id = {"ethereum": 1, "gnosis": 100}[blockchain.lower()]
        bc = Chain.get_blockchain_by_chain_id(chain_id)

        if protocol == "Balancer" and (
            exec_config["function_name"] == "exit_1_1" or exec_config["function_name"] == "exit_1_3"
        ):
            bpt_address = exit_arguments_dict["bpt_address"]
            test = recovery_mode_balancer(w3, bpt_address, exec_config["function_name"], blockchain=bc)
            if test:
                raise ValueError("Skip recovery")

        elif protocol == "Balancer" and (
            exec_config["function_name"] == "exit_2_1" or exec_config["function_name"] == "exit_2_3"
        ):
            gauge_address = exit_arguments_dict["gauge_address"]
            gauge_contract = w3.eth.contract(address=gauge_address, abi=BalancerAbis[bc].Gauge.abi)
            bpt_address = gauge_contract.functions.lp_token().call()
            test = recovery_mode_balancer(w3, bpt_address, exec_config["function_name"], blockchain=bc)
            if test:
                raise ValueError("Skip recovery")

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
                raise ValueError("Skip recovery")

        logger.info(f"Exit arguments: {exit_arguments}")

        env = ENV(DAO=dao or "", BLOCKCHAIN=blockchain)
        result = build_transaction_env(
            env=env,
            percentage=percentage,
            protocol=protocol,
            exit_strategy=exit_strategy,
            exit_arguments=exit_arguments,
            web3=web3,
        )
        if result["status"] != 200:
            logger.info(f'Error in transaction builder. Error1: {result["message"]}')
            exec_config["stresstest"] = False
            exec_config["stresstest_error"] = f"error: {result['message']}"
        else:
            logger.info(f'Status of transaction builder: {result["status"]}')
            tx = result["tx_data"]["transaction"]

            try:
                result = execute_env(env=env, transaction=tx, web3=web3)
                if result["status"] != 200:
                    logger.info(f'Error in execution. Error: {result["message"]}')
                    exec_config["stresstest"] = False
                    exec_config["stresstest_error"] = f"error: {result['message']}"
                else:
                    logger.info(f'Status of execution: {result["status"]}')
                    exec_config["stresstest"] = True

            except Exception as f:
                logger.info(f"Exception in execution. Error: {f}")
                exec_config["stresstest"] = False
                exec_config["stresstest_error"] = f"error: {str(f)}"

    except Exception as e:
        logger.info(f"Error in transaction builder. Error: {str(e)}")
        exec_config["stresstest"] = False
        exec_config["stresstest_error"] = f"error: {str(e)}"
    finally:
        print("")
        logger_handler.flush()


def stresstest(
    positions_dict: dict,
    percentage: int,
    max_slippage: int,
    dao: str | None = None,
    blockchain: str | None = None,
    w3: Web3 | None = None,
):
    dao = dao or positions_dict["dao"]
    blockchain = blockchain or positions_dict["blockchain"]
    logger = logging.getLogger(__name__)

    executions = []
    for position in positions_dict["positions"]:
        protocol = position["protocol"]
        for exec_config in position["exec_config"]:
            executions.append([percentage, max_slippage, dao, blockchain, protocol, exec_config])

    if w3:
        for args in executions:
            single_stresstest(*args, web3=w3)
    else:

        def with_pulley(*args):
            try:
                with PulleyFork(blockchain) as fork:
                    env = ENV(DAO=dao or "", BLOCKCHAIN=blockchain, local_fork_url=fork.url())
                    web3, _ = start_the_engine(env)

                    return single_stresstest(*args, web3=web3)
            except Exception as e:
                logger.error(f"CodeError in transaction builder. Error: {str(e)}")

        concurrency = config("STRESSTEST_CONCURRENCY", default=10, cast=int)
        results = Parallel(n_jobs=concurrency, backend="threading")(delayed(with_pulley)(*args) for args in executions)
        collections.deque(results, maxlen=0)

    return positions_dict
