import argparse
import json

from web3 import Web3

from roles_royce.applications.execution_app.utils import ENV, start_the_engine
from roles_royce.roles_modifier import GasStrategies, set_gas_strategy, update_gas_fees_parameters_and_nonce


def execute_env(env, transaction, web3: Web3 | None = None):
    try:
        if not web3:
            w3, w3_MEV = start_the_engine(env)
        else:
            w3 = web3
            w3_MEV = web3

        set_gas_strategy(GasStrategies.AGGRESIVE)
        tx = update_gas_fees_parameters_and_nonce(w3, transaction)

        if env.MODE == "production":  # In production environment, send the transaction to the real blockchain
            signed = w3.eth.account.sign_transaction(tx, env.PRIVATE_KEY)
            tx_hash = w3_MEV.eth.send_raw_transaction(signed.rawTransaction)
        else:  # In development environment, send the transaction to the local fork with the unlocked account
            tx_hash = w3.eth.send_transaction(tx)
            w3.eth.wait_for_transaction_receipt(tx_hash)
            # fork_reset_state(w3, w3.manager.provider.endpoint_uri)
        return {"status": 200, "tx_hash": tx_hash.hex()}
    except Exception as e:
        return {"status": 500, "message": f"Error: {e}"}


def execute(dao, blockchain, transaction):
    try:
        env = ENV(DAO=dao, BLOCKCHAIN=blockchain)
        return execute_env(env, transaction)
    except Exception as e:
        return {"status": 500, "message": f"Error: {e}"}


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-d", "--dao", type=str, help="DAO whose funds are to be removed.")
    parser.add_argument(
        "-b",
        "--blockchain",
        type=str,
        help="Blockchain where the funds are deposited.",
    )

    parser.add_argument("-t", "--transaction", type=str, help="Transaction json to execute.")

    args = parser.parse_args()
    transaction = json.loads(args.transaction)

    response = execute(dao=args.dao, blockchain=args.blockchain, transaction=transaction)
    print(json.dumps(response))


if __name__ == "__main__":
    main()
