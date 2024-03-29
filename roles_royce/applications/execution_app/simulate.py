import argparse
import json

from roles_royce.applications.execution_app.utils import ENV, start_the_engine
from roles_royce.toolshed.simulation import TenderlyCredentials, simulate_tx


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Script to simulate an exit transaction with Tenderly",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        parser.add_argument("-d", "--dao", type=str, help="DAO whose funds are to be removed.")
        parser.add_argument("-b", "--blockchain", type=str, help="Blockchain where the funds are deposited.")

        parser.add_argument("-t", "--transaction", type=str, help="Transaction to simulate, as a json")

        args = parser.parse_args()

        env = ENV(DAO=args.dao, BLOCKCHAIN=args.blockchain)
        tenderly_credentials = TenderlyCredentials(
            account_id=env.TENDERLY_ACCOUNT_ID, project=env.TENDERLY_PROJECT, api_token=env.TENDERLY_API_TOKEN
        )
        w3, w3_MEV = start_the_engine(env)
        block = w3.eth.block_number
        sim_data = simulate_tx(
            tx=json.loads(args.transaction),
            block=block,
            tenderly_credentials=tenderly_credentials,
            sim_type="full",  # TODO: check if 'quick' is enough
            share=True,
        )

        response_message = {
            "status": 200,
            "sim_data": {
                "share_url": sim_data["share_url"],
                "error_message": sim_data["simulation"].get("error_message"),
            },
        }

    except Exception as e:
        response_message = {"status": 500, "message": f"Error: {e}"}

    print(json.dumps(response_message))


if __name__ == "__main__":
    main()
