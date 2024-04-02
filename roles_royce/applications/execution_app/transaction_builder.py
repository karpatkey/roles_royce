import argparse
import json

from web3 import Web3

from roles_royce.applications.execution_app.utils import ENV, ExecConfig, decode_transaction, gear_up, start_the_engine
from roles_royce.roles_modifier import ROLES_ERRORS, GasStrategies, set_gas_strategy


def build_transaction_env(env: ENV, percentage, protocol, exit_strategy, exit_arguments, web3: Web3 | None = None):
    exec_config = ExecConfig(
        percentage=percentage,
        dao=env.DAO,
        blockchain=env.BLOCKCHAIN,
        protocol=protocol,
        exit_strategy=exit_strategy,
        exit_arguments=exit_arguments,
    )

    if not web3:
        w3, _ = start_the_engine(env)
    else:
        w3 = web3

    set_gas_strategy(GasStrategies.AGGRESIVE)
    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
    decoded_transaction = decode_transaction(txns=txn_transactables, env=env)

    try:
        if not txn_transactables:
            return {
                "status": 200,
                "message": "There are no funds in the position, no transactions to build",
            }

        check_exit_tx = disassembler.check(txns=txn_transactables, from_address=env.DISASSEMBLER_ADDRESS)

        if check_exit_tx:
            tx = disassembler.build(txns=txn_transactables, from_address=env.DISASSEMBLER_ADDRESS)
            return {
                "status": 200,
                "tx_data": {
                    "transaction": tx,
                    "decoded_transaction": decoded_transaction,
                },
            }
        else:
            return {
                "status": 422,
                "tx_data": {"decoded_transaction": decoded_transaction},
                "message": "Error: Transaction reverted when simulated with local eth_call",
            }

    except Exception as e:
        if str(e) in ROLES_ERRORS:
            return {
                "status": 422,
                "tx_data": {"decoded_transaction": decoded_transaction},
                "message": f"Role permissions error: {e}",
            }
        else:
            return {
                "status": 500,
                "tx_data": {"decoded_transaction": decoded_transaction},
                "message": f"Error: {e}",
            }


def build_transaction(percentage, dao, blockchain, protocol, exit_strategy, exit_arguments):
    try:
        env = ENV(
            DAO=dao,
            BLOCKCHAIN=blockchain,
        )

        return build_transaction_env(
            env,
            percentage=percentage,
            protocol=protocol,
            exit_strategy=exit_strategy,
            exit_arguments=exit_arguments,
        )
    except Exception as e:
        return {"status": 500, "message": f"Error: {e}"}


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-p",
        "--percentage",
        type=float,
        default=100,
        help="Percentage of liquidity to be removed, defaults to 100.",
    )

    parser.add_argument("-d", "--dao", type=str, help="DAO whose funds are to be removed.")
    parser.add_argument("-b", "--blockchain", type=str, help="Blockchain where the funds are deposited.")

    parser.add_argument("--protocol", type=str, help="Protocol where the funds are deposited.")
    parser.add_argument(
        "-s",
        "--exit-strategy",
        type=str,
        help="Exit strategy to execute, e.g. exit_2_1, exit_3",
    )
    parser.add_argument(
        "-a",
        "--exit-arguments",
        type=str,
        default="[]",
        help="List of jsons with the custom exit arguments for each "
        'position and exit strategy, e.g. [{ "bpt_address": "0xsOmEAddResS", "max_slippage": '
        "0.01}]",
    )

    args = parser.parse_args()
    response = build_transaction(
        percentage=args.percentage,
        dao=args.dao,
        blockchain=args.blockchain,
        protocol=args.protocol,
        exit_strategy=args.exit_strategy,
        exit_arguments=json.loads(args.exit_arguments),
    )
    print(json.dumps(response))


if __name__ == "__main__":
    main()
