import argparse
import json
import traceback

from roles_royce.toolshed.simulation import TenderlyCredentials, simulate_tx

from .utils import ENV, start_the_engine


def simulate(dao, blockchain, transaction, rpc_url: str | None = None):
    try:
        env = ENV(DAO=dao, BLOCKCHAIN=blockchain, local_fork_url=rpc_url)
        tenderly_credentials = TenderlyCredentials(
            account_id=env.TENDERLY_ACCOUNT_ID, project=env.TENDERLY_PROJECT, api_token=env.TENDERLY_API_TOKEN
        )
        w3, _ = start_the_engine(env)
        block = w3.eth.block_number
        sim_data = simulate_tx(
            tx=transaction,
            block=block,
            tenderly_credentials=tenderly_credentials,
            sim_type="full",  # TODO: check if 'quick' is enough
            share=True,
        )

        return {
            "status": 200,
            "sim_data": {
                "share_url": sim_data["share_url"],
                "error_message": sim_data["simulation"].get("error_message"),
            },
        }

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return {"status": 500, "message": f"Error: {e}"}


def main():
    parser = argparse.ArgumentParser(
        description="Script to simulate an exit transaction with Tenderly",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-d", "--dao", type=str, help="DAO whose funds are to be removed.")
    parser.add_argument("-b", "--blockchain", type=str, help="Blockchain where the funds are deposited.")
    parser.add_argument("-t", "--transaction", type=str, help="Transaction to simulate, as a json")
    args = parser.parse_args()

    transaction = json.loads(args.transaction)
    response = simulate(dao=args.dao, blockchain=args.blockchain, transaction=transaction)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
