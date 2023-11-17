import argparse
from web3 import Web3
from roles_royce.toolshed.disassembling import AuraDisassembler, BalancerDisassembler, Disassembler
from roles_royce.applications.panic_button_app.utils import ENV, ExecConfig, Modes, fork_unlock_account, \
    top_up_address, start_the_engine
from roles_royce.generic_method import Transactable
import json


def decode_transaction(txns: list[Transactable], env: ENV) -> list[dict]:
    result = []
    for transactable in txns:
        tx = json.loads(transactable.abi)[0]
        for item, arg in zip(tx["inputs"], transactable.args_list):
            item["value"] = arg
        tx["to_address"] = transactable.contract_address
        tx["value"] = transactable.value
        tx["data"] = transactable.data
        tx["from_address"] = env.DISASSEMBLER_ADDRESS
        result.append(tx)
    return result


def gear_up(w3: Web3, env: ENV, exec_config: ExecConfig) -> (Disassembler, list[Transactable]):
    if exec_config.protocol == "Aura":
        disassembler = AuraDisassembler(w3=w3,
                                        avatar_safe_address=env.AVATAR_SAFE_ADDRESS,
                                        roles_mod_address=env.ROLES_MOD_ADDRESS,
                                        role=env.ROLE,
                                        signer_address=env.DISASSEMBLER_ADDRESS)

    elif exec_config.protocol == "Balancer":
        disassembler = BalancerDisassembler(w3=w3,
                                            avatar_safe_address=env.AVATAR_SAFE_ADDRESS,
                                            roles_mod_address=env.ROLES_MOD_ADDRESS,
                                            role=env.ROLE,
                                            signer_address=env.DISASSEMBLER_ADDRESS)
    else:
        raise Exception("Invalid protocol")

    exit_strategy = getattr(disassembler, exec_config.exit_strategy)

    txn_transactables = exit_strategy(percentage=exec_config.percentage, exit_arguments=exec_config.exit_arguments)

    return disassembler, txn_transactables


def main():
    try:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument("--simulate", default=False, action='store_true',
                            help="If set simulates transaction in Tenderly")
        parser.add_argument("-p", "--percentage", type=int, default=100,
                            help="Percentage of liquidity to be removed, defaults to 100.")

        parser.add_argument("-d", "--dao", type=str, help="DAO whose funds are to be removed.")
        parser.add_argument("-b", "--blockchain", type=str, help="Blockchain where the funds are deposited.")

        parser.add_argument("--protocol", type=str, help="Protocol where the funds are deposited.")
        parser.add_argument("-s", "--exit-strategy", type=str, help="Exit strategy to execute, e.g. exit_2_1, exit_3")
        parser.add_argument("-a", "--exit-arguments", type=str,
                            help='List of jsons with the custom exit arguments for each '
                                 'position and exit strategy, e.g. [{ "bpt_address": "0xsOmEAddResS", "max_slippage": '
                                 '0.01}]')

        args = parser.parse_args()

        exec_config = ExecConfig(percentage=args.percentage,
                                 simulate=args.simulate,
                                 dao=args.dao,
                                 blockchain=args.blockchain,
                                 protocol=args.protocol,
                                 exit_strategy=args.exit_strategy,
                                 exit_arguments=json.loads(args.exit_arguments))

        env = ENV(DAO=exec_config.dao, BLOCKCHAIN=exec_config.blockchain)
        w3, w3_MEV = start_the_engine(env)
        disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
        check_exit_tx = disassembler.check(txns=txn_transactables, from_address=env.DISASSEMBLER_ADDRESS)

        if check_exit_tx:
            tx = disassembler.build(txns=txn_transactables, from_address=env.DISASSEMBLER_ADDRESS)
            decoded_transaction = decode_transaction(txns=txn_transactables, env=env)
            response_message = {"status": 200, "message": {"transaction": tx, "decoded_transaction": decoded_transaction}}
        else:
            response_message = {"status": 422, "message": "Error: Transaction reverted when simulated with local eth_call"}

    except Exception as e:
        response_message = {"status": 500, "message": f"Error: {e}"}

    print(json.dumps(response_message))


if __name__ == "__main__":
    main()
