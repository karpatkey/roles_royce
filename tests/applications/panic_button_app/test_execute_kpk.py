from web3.exceptions import TimeExhausted
from roles_royce.applications.panic_button_app.utils import ENV, ExecConfig
from tests.utils import assign_role, local_node_eth, accounts
import os
import json
import pytest
import subprocess
from pathlib import Path
import time

dao = 'karpatkey'
blockchain = 'ETHEREUM'
avatar_safe_address = '0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C'
roles_mod_address = '0x8C33ee6E439C874713a9912f3D3debfF1Efb90Da'
role = 1


def set_env(monkeypatch, private_key: str) -> ENV:
    monkeypatch.setenv('ETHEREUM_RPC_ENDPOINT', 'DummyString')
    monkeypatch.setenv('ETHEREUM_RPC_ENDPOINT_FALLBACK', 'DummyString')
    monkeypatch.setenv('KARPATKEY_ETHEREUM_AVATAR_SAFE_ADDRESS', avatar_safe_address)
    monkeypatch.setenv('KARPATKEY_ETHEREUM_ROLES_MOD_ADDRESS', roles_mod_address)
    monkeypatch.setenv('KARPATKEY_ETHEREUM_ROLE', role)
    monkeypatch.setenv('KARPATKEY_ETHEREUM_PRIVATE_KEY', private_key)
    # Without setting the MODE env it will default to DEVELOPMENT and use the local fork
    return ENV(dao, blockchain)


def set_up_roles(local_node_eth, accounts):
    block = 19084800
    local_node_eth.set_block(block)

    disassembler_address = accounts[0].address
    private_key = accounts[0].key.hex()

    assign_role(local_node=local_node_eth,
                avatar_safe_address=avatar_safe_address,
                roles_mod_address=roles_mod_address,
                role=role,
                asignee=disassembler_address)
    return private_key


JSON_FORM = {
    "protocol": "Aura",
    "exit_strategy": "exit_2_1",
    "percentage": 21,
    "exit_arguments": {

        "rewards_address": "0x2a14dB8D09dB0542f6A371c0cB308A768227D67D",
        "max_slippage": 0.01
    }
}

exec_config = ExecConfig(percentage=JSON_FORM["percentage"],
                         dao=dao,
                         blockchain=blockchain,
                         protocol=JSON_FORM["protocol"],
                         exit_strategy=JSON_FORM["exit_strategy"],
                         exit_arguments=[JSON_FORM["exit_arguments"]])

transactions = [{'chainId': 1,
                 'data': '0x6928e74b0000000000000000000000002a14db8d09db0542f6a371c0cb308a768227d67d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000044c32e7202000000000000000000000000000000000000000000000006a6b78270110a57ef000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000',
                 'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
                 'gas': 1123651,
                 'maxFeePerGas': 1328552307,
                 'maxPriorityFeePerGas': 1194919766,
                 'nonce': 606,
                 'to': '0x8C33ee6E439C874713a9912f3D3debfF1Efb90Da',
                 'value': 0},
                {'chainId': 1,
                 'data': '0x6928e74b000000000000000000000000a238cbeb142c10ef7ad8442c6d1f9e89e07e7761000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000003a48d80ff0a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000352002a14db8d09db0542f6a371c0cb308a768227d67d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044c32e7202000000000000000000000000000000000000000000000006a6b78270110a57ef000000000000000000000000000000000000000000000000000000000000000100ba12222222228d8ba445958a75a0704d566bf2c8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002648bdb391393d199263632a4ef4bb438f1feb99e57b4b5f0bd0000000000000000000005c200000000000000000000000058e6c7ab55aa9012eacca16d1ed4c15795669e1c00000000000000000000000058e6c7ab55aa9012eacca16d1ed4c15795669e1c0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca000000000000000000000000093d199263632a4ef4bb438f1feb99e57b4b5f0bd000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000003f74041e57674bf430000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002231819c61133e89800000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000006a6b78270110a57ef000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
                 'from': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
                 'gas': 1577482,
                 'maxFeePerGas': 1287540767,
                 'maxPriorityFeePerGas': 1170588908,
                 'nonce': 606,
                 'to': '0x8C33ee6E439C874713a9912f3D3debfF1Efb90Da',
                 'value': 0}
                ]


@pytest.mark.parametrize("tx", transactions)
def test_execute(local_node_eth, accounts, monkeypatch, tx):
    private_key = set_up_roles(local_node_eth, accounts)
    set_env(monkeypatch, private_key)

    file_path_execute = os.path.join(Path(os.path.dirname(__file__)).resolve().parent.parent.parent, 'roles_royce',
                                     'applications', 'panic_button_app',
                                     'execute.py')

    arguments = [
        'python', file_path_execute,
        '--dao', dao,
        '--blockchain', blockchain,
        '--transaction', json.dumps(tx)
    ]

    main = subprocess.run(arguments, capture_output=True, text=True)

    assert main.returncode == 0
    dict_message_stdout = json.loads(main.stdout[:-1])
    assert dict_message_stdout['status'] == 200
    # #  If we don't wait for the transaction to be validated, the next test will fail when trying to reset Anvil
    # time.sleep(5)
    # w3 = local_node_eth.w3
    # try:
    #     w3.eth.wait_for_transaction_receipt(dict_message_stdout['tx_hash'], timeout=40, poll_latency=5)
    # except TimeExhausted:
    #     pass
