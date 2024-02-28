import argparse
from roles_royce.applications.panic_button_app.utils import ENV, start_the_engine, fork_reset
import json
from roles_royce.roles_modifier import update_gas_fees_parameters_and_nonce, set_gas_strategy, GasStrategies


def main():
    try:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument("-d", "--dao", type=str, help="DAO whose funds are to be removed.")
        parser.add_argument("-b", "--blockchain", type=str, help="Blockchain where the funds are deposited.")

        parser.add_argument("-t", "--transaction", type=str, help="Transaction json to execute.")

        args = parser.parse_args()
        tx = json.loads(args.transaction)
        env = ENV(DAO=args.dao, BLOCKCHAIN=args.blockchain)
        w3, w3_MEV = start_the_engine(env)

        set_gas_strategy(GasStrategies.AGGRESIVE)
        tx = update_gas_fees_parameters_and_nonce(w3, tx)

        if env.MODE == 'production':  # In production environment, send the transaction to the real blockchain
            signed = w3.eth.account.sign_transaction(tx, env.PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        else:  # In development environment, send the transaction to the local fork with the unlocked account
            tx_hash = w3.eth.send_transaction(tx)
            w3.eth.wait_for_transaction_receipt(tx_hash)
            reset = fork_reset(w3, w3.manager.provider.endpoint_uri)
        response_message = {"status": 200, "tx_hash": tx_hash.hex()}
    except Exception as e:
        response_message = {"status": 500, "message": f"Error: {e}"}

    print(json.dumps(response_message))


if __name__ == "__main__":
    main()
