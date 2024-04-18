import argparse
import json
import traceback

from web3 import Web3

from roles_royce.roles_modifier import ROLES_ERRORS, GasStrategies, set_gas_strategy

from .utils import ENV, ExecConfig, decode_transaction, disassembler_from_config, gear_up, start_the_engine


def transaction_check(dao, blockchain, protocol, tx_transactables, rpc_url: str | None = None):
    env = ENV(DAO=dao, BLOCKCHAIN=blockchain, local_fork_url=rpc_url)
    w3, _ = start_the_engine(env)

    try:
        disassembler = disassembler_from_config(w3=w3, env=env, protocol=protocol)
        if disassembler.check(txns=tx_transactables, from_address=env.DISASSEMBLER_ADDRESS):
            return {"status": 200, "check": "ok"}
        else:
            return {
                "status": 422,
                "message": "Error: Transaction reverted when simulated with local eth_call",
            }

    except Exception as e:
        if str(e) in ROLES_ERRORS:
            return {
                "status": 422,
                "message": f"Role permissions error: {e}",
            }
        else:
            return {
                "status": 500,
                "message": f"Error: {e}",
            }


def build_transaction_env(
    env: ENV, percentage, protocol, exit_strategy, exit_arguments, web3: Web3 | None = None, run_check: bool = True
):
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

    try:
        set_gas_strategy(GasStrategies.AGGRESIVE)
        disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
        if not txn_transactables:
            return {
                "status": 400,
                "message": "There are no funds in the position, no transactions to build",
            }

        decoded_transaction = decode_transaction(txns=txn_transactables, env=env)

        check_exit_tx = False
        if run_check:
            check_exit_tx = disassembler.check(txns=txn_transactables, from_address=env.DISASSEMBLER_ADDRESS)

        if not run_check or check_exit_tx:
            tx = disassembler.build(txns=txn_transactables, from_address=env.DISASSEMBLER_ADDRESS)
            return {
                "status": 200,
                "tx_data": {
                    "transaction": tx,
                    "decoded_transaction": decoded_transaction,
                    "transactables": txn_transactables,
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


def build_transaction(
    percentage,
    dao,
    blockchain,
    protocol,
    exit_strategy,
    exit_arguments,
    run_check: bool = True,
    rpc_url: str | None = None,
):
    try:
        env = ENV(DAO=dao, BLOCKCHAIN=blockchain, local_fork_url=rpc_url, prod_mode_override=not run_check)

        return build_transaction_env(
            env,
            percentage=percentage,
            protocol=protocol,
            exit_strategy=exit_strategy,
            exit_arguments=exit_arguments,
            run_check=run_check,
        )
    except Exception as e:
        print(traceback.format_exc())
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
