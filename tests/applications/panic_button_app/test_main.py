from roles_royce.applications.panic_button_app.panic_button_main import start_the_engine, gear_up, drive_away
from roles_royce.applications.panic_button_app.utils import ENV, ExecConfig
from tests.utils import assign_role, local_node_eth, accounts
import pytest

dao = 'GnosisDAO'
blockchain = 'mainnet'
avatar_safe_address = '0x849D52316331967b6fF1198e5E32A0eB168D039d'
roles_mod_address = '0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc'
role = 4


def set_env(monkeypatch, private_key: str) -> ENV:
    monkeypatch.setenv('MAINNET_RPC_ENDPOINT', 'DummyString')
    monkeypatch.setenv('MAINNET_FALLBACK_RPC_ENDPOINT', 'DummyString')
    monkeypatch.setenv('GNOSISDAO_MAINNET_AVATAR_SAFE_ADDRESS', avatar_safe_address)
    monkeypatch.setenv('GNOSISDAO_MAINNET_ROLES_MOD_ADDRESS', roles_mod_address)
    monkeypatch.setenv('GNOSISDAO_MAINNET_ROLE', role)
    monkeypatch.setenv('GNOSISDAO_MAINNET_PRIVATE_KEY', private_key)
    return ENV(dao, blockchain)


JSON_FORM = {
    "simulate": False,
    "protocol": "Aura",
    "exit_strategy": "exit_2_1",
    "percentage": 21,
    "exit_arguments": {

        "rewards_address": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D",
        "max_slippage": 0.01
    }
}

exec_config = ExecConfig(percentage=JSON_FORM["percentage"],
                         simulate=JSON_FORM["simulate"],
                         dao=dao,
                         blockchain=blockchain,
                         protocol=JSON_FORM["protocol"],
                         exit_strategy=JSON_FORM["exit_strategy"],
                         exit_arguments=[JSON_FORM["exit_arguments"]])


def test_start_the_engine(monkeypatch):
    env = set_env(monkeypatch, "DummyString")
    w3 = start_the_engine(env, local_fork_port=8546)
    assert w3.is_connected()

    with pytest.raises(Exception):
        start_the_engine(env) # RPC endpoints are 'DummyString'


def test_gear_up(monkeypatch, local_node_eth):
    private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    env = set_env(monkeypatch, private_key)

    w3 = local_node_eth.w3
    local_node_eth.set_block(18437790)

    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
    assert disassembler.avatar_safe_address == '0x849D52316331967b6fF1198e5E32A0eB168D039d'
    assert txn_transactables[
               0].data == '0xc32e72020000000000000000000000000000000000000000000000111ed47dc81e6e5ad80000000000000000000000000000000000000000000000000000000000000001'
    assert txn_transactables[
               1].data == '0x8bdb39131e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000ae78736cd615f374d3085123a210448e74fc6393000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000007e9af502b84ea855b000000000000000000000000000000000000000000000008cc84206c7773d6ed000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000111ed47dc81e6e5ad8'


def test_drive_away(local_node_eth, accounts, monkeypatch):
    w3 = local_node_eth.w3
    block = 18421437
    local_node_eth.set_block(block)

    disassembler_address = accounts[0].address
    private_key = accounts[0].key.hex()

    assign_role(local_node=local_node_eth,
                avatar_safe_address=avatar_safe_address,
                roles_mod_address=roles_mod_address,
                role=role,
                asignee=disassembler_address)

    env = set_env(monkeypatch, private_key)

    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)

    response = drive_away(disassembler=disassembler,
                          txn_transactables=txn_transactables,
                          private_key=private_key,
                          simulate=exec_config.simulate)

    assert response['status'] == 200
    assert response['message'] == "Transaction executed successfully"

    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
    response_reverted = drive_away(disassembler=disassembler,
                                   txn_transactables=txn_transactables,
                                   private_key=accounts[1].key.hex(),
                                   simulate=exec_config.simulate)

    assert response_reverted['status'] == 422
    assert response_reverted['message'] == "Transaction reverted when executed locally"

    disassembler, txn_transactables = gear_up(w3=w3, env=env, exec_config=exec_config)
    response_exception = drive_away(disassembler=disassembler,
                                    txn_transactables=txn_transactables,
                                    private_key='0x',
                                    simulate=exec_config.simulate)

    assert response_exception['status'] == 500
    assert response_exception['message'] == "Error: The private key must be exactly 32 bytes long, instead of 2 bytes."