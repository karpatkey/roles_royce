import argparse
from web3 import Web3
from roles_royce.toolshed.disassembling import AuraDisassembler, BalancerDisassembler, Disassembler
from roles_royce.utils import TenderlyCredentials
from roles_royce.applications.panic_button_app.utils import ENV, ExecConfig
import time
from roles_royce.generic_method import Transactable
from roles_royce.toolshed.alerting.utils import get_tx_link
import json


def start_the_engine(env: ENV, local_fork_port: int = None) -> Web3:
    if local_fork_port is not None:
        w3 = Web3(Web3.HTTPProvider(f'http://localhost:{local_fork_port}'))
    else:
        w3 = Web3(Web3.HTTPProvider(env.RPC_ENDPOINT))
        if not w3.is_connected():
            w3 = Web3(Web3.HTTPProvider(env.FALLBACK_RPC_ENDPOINT))
            if not w3.is_connected():
                time.sleep(2)
                w3 = Web3(Web3.HTTPProvider(env.RPC_ENDPOINT))
                if not w3.is_connected():
                    w3 = Web3(Web3.HTTPProvider(env.FALLBACK_RPC_ENDPOINT))
                    if not w3.is_connected():
                        raise Exception("No connection to RPC endpoint")
    return w3


def gear_up(w3: Web3, env: ENV, exec_config: ExecConfig) -> (Disassembler, list[Transactable]):
    tenderly_credentials = TenderlyCredentials(account_id=env.TENDERLY_ACCOUNT_ID,
                                               project=env.TENDERLY_PROJECT,
                                               api_token=env.TENDERLY_API_TOKEN)

    disassembler_address = w3.eth.account.from_key(env.PRIVATE_KEY).address

    if exec_config.protocol == "Aura":
        disassembler = AuraDisassembler(w3=w3,
                                        avatar_safe_address=env.AVATAR_SAFE_ADDRESS,
                                        roles_mod_address=env.ROLES_MOD_ADDRESS,
                                        role=env.ROLE,
                                        tenderly_credentials=tenderly_credentials,
                                        signer_address=disassembler_address)

    elif exec_config.protocol == "Balancer":
        disassembler = BalancerDisassembler(w3=w3,
                                            avatar_safe_address=env.AVATAR_SAFE_ADDRESS,
                                            roles_mod_address=env.ROLES_MOD_ADDRESS,
                                            role=env.ROLE,
                                            tenderly_credentials=tenderly_credentials,
                                            signer_address=disassembler_address)
    else:
        raise Exception("Invalid protocol")

    exit_strategy = getattr(disassembler, exec_config.exit_strategy)

    txn_transactables = exit_strategy(percentage=exec_config.percentage, exit_arguments=exec_config.exit_arguments)

    return disassembler, txn_transactables


def drive_away(disassembler: Disassembler, txn_transactables: list[Transactable], private_key: str, simulate: bool) -> dict:

    if txn_transactables:
        try:
            disassembler_address = disassembler.w3.eth.account.from_key(private_key).address
            if simulate:
                tx_data, sim_link = disassembler.simulate(txns=txn_transactables,
                                                          from_address=disassembler_address)
                if tx_data['transaction']['status']:
                    response_message = {"status": 200, "link": sim_link,
                                        "message": "Transaction executed successfully in Tenderly"}
                else:
                    response_message = {"status": 422, "link": sim_link,
                                        "message": "Transaction reverted in Tenderly simulation"}
            else:
                check_exit_tx = disassembler.check(txns=txn_transactables,
                                                   from_address=disassembler_address)

                if check_exit_tx:
                    tx_receipt = disassembler.send(txns=txn_transactables, private_key=private_key)
                    tx_link = get_tx_link(tx_receipt, disassembler.blockchain)
                    if tx_receipt.status == 0:
                        response_message = {"status": 422, "link": tx_link,
                                            "message": "Transaction reverted"}
                    else:
                        response_message = {"status": 200, "link": tx_link,
                                            "message": "Transaction executed successfully"}
                else:
                    response_message = {"status": 422, "link": "No link",
                                        "message": "Transaction reverted when simulated in local execution"}
            return response_message
        except Exception as e:
            response_message = {"status": 500, "link": "", "message": f"Error: {e}"}
            return response_message

    else:
        return {"status": 200, "link": "No link", "message": "No transactions need to be executed for the desired "
                                                             "outcome"}


def main():
    parser = argparse.ArgumentParser(description="This is the real Gnosis DAO disassembling script",
                                     epilog='Build by karpatkey',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-sim", "--simulate", default=False, action='store_true',
                        help="If set simulates transaction in Tenderly")
    parser.add_argument("-p", "--percentage", type=int, default=100,
                        help="Percentage of liquidity to be removed, defaults to 100.")

    parser.add_argument("-d", "--dao", type=str, help="DAO whose funds are to be removed.")
    parser.add_argument("-b", "--blockchain", type=str, help="Blockchain where the funds are deposited.")

    parser.add_argument("-prot", "--protocol", type=str, help="Protocol where the funds are deposited.")
    parser.add_argument("-s", "--exitStrategy", type=str, help="Exit strategy to execute, e.g. exit_2_1, exit_3")
    parser.add_argument("-a", "--exitArguments", type=str,
                        help="List of dictionaries (cast as a string) with the custom exit arguments for each "
                             "position and exit strategy, e.g. [{ 'bpt_address': '0xsOmEAddResS', 'max_slippage': 0.01}]")

    parser.add_argument("-t", "--test", type=int, help="Local fork port to test the script.")
    args = parser.parse_args()

    simulate = args.simulate
    
    exec_config = ExecConfig(percentage=args.percentage,
                             simulate=args.simulate,
                             dao=args.dao,
                             blockchain=args.blockchain,
                             protocol=args.protocol,
                             exit_strategy=args.exitStrategy,
                             exit_arguments=json.loads(args.exitArguments))

    env = ENV(DAO=exec_config.dao, BLOCKCHAIN=exec_config.blockchain)
    w3 = start_the_engine(env, local_fork_port=args.test)
    disassembler, txn_transactables = gear_up(w3, env, exec_config)
    tx_message = drive_away(disassembler, txn_transactables, env.PRIVATE_KEY, simulate)
    print(tx_message)


if __name__ == "__main__":
    main()
