import traceback

from roles_royce.roles_modifier import ROLES_V1_ERRORS, GasStrategies, set_gas_strategy

from .code_transporter import CodeTransporter
from .utils import ENV, ExecConfig, decode_transaction, disassembler_from_config, gear_up, start_the_engine


def transaction_check_env(env, protocol, tx_transactables: str):
    w3 = env.web3 or start_the_engine(env)

    try:
        transactables = CodeTransporter().safe_deserialize(tx_transactables)

        disassembler = disassembler_from_config(w3=w3, env=env, protocol=protocol)
        if disassembler.check(txns=transactables, from_address=env.disassembler_address):
            return {"status": 200, "check": "ok"}
        else:
            return {
                "status": 422,
                "error": "Error: Transaction reverted when simulated with local eth_call",
            }

    except Exception as e:
        if str(e) in ROLES_V1_ERRORS:
            return {
                "status": 422,
                "error": f"Role permissions error: {e}",
            }
        else:
            return {
                "status": 500,
                "error": f"Error: {e}",
            }


def build_transaction_env(env: ENV, percentage, protocol, exit_strategy, exit_arguments, run_check: bool = True):
    exec_config = ExecConfig(
        percentage=percentage,
        protocol=protocol,
        exit_strategy=exit_strategy,
        exit_arguments=exit_arguments,
    )

    w3 = env.web3 or start_the_engine(env)

    decoded_transaction = ""
    try:
        set_gas_strategy(GasStrategies.AGGRESIVE)
        disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
        if not txn_transactables:
            return {
                "status": 400,
                "error": "There are no funds in the position, no transactions to build",
            }

        decoded_transaction = decode_transaction(txns=txn_transactables, env=env)

        check_exit_tx = False
        if run_check:
            check_exit_tx = disassembler.check(txns=txn_transactables, from_address=env.disassembler_address)

        if not run_check or check_exit_tx:
            tx = disassembler.build(txns=txn_transactables, from_address=env.disassembler_address)
            transactables = CodeTransporter().safe_serialize(txn_transactables)
            return {
                "status": 200,
                "tx_data": {
                    "transaction": tx,
                    "decoded_transaction": decoded_transaction,
                    "tx_transactables": transactables,
                },
            }
        else:
            return {
                "status": 422,
                "tx_data": {"decoded_transaction": decoded_transaction},
                "error": "Error: Transaction reverted when simulated with local eth_call",
            }

    except Exception as e:
        if str(e) in ROLES_V1_ERRORS:
            return {
                "status": 422,
                "tx_data": {"decoded_transaction": decoded_transaction},
                "error": f"Role permissions error: {e}",
            }
        else:
            traceback.print_exception(e)
            return {
                "status": 500,
                "tx_data": {"decoded_transaction": decoded_transaction},
                "error": f"Error: {e}",
            }
