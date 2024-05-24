from web3 import Web3

from roles_royce.applications.execution_app.utils import ENV, start_the_engine
from roles_royce.roles_modifier import GasStrategies, set_gas_strategy, update_gas_fees_parameters_and_nonce


def execute_env(env: ENV, transaction, web3: Web3 | None = None):
    try:
        w3 = web3 or env.web3 or start_the_engine(env)

        set_gas_strategy(GasStrategies.AGGRESIVE)
        tx = update_gas_fees_parameters_and_nonce(w3, transaction)

        tx_hash = w3.eth.send_transaction(tx)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        # fork_reset_state(w3, w3.manager.provider.endpoint_uri)
        return {"status": 200, "tx_hash": tx_hash.hex()}
    except Exception as e:
        return {"status": 500, "message": f"Error: {e}"}
