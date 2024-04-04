import json
import os
from dataclasses import dataclass

from roles_royce.applications.execution_app.stresstest import stresstest
from roles_royce.applications.execution_app.utils import ENV
from tests.utils import (
    accounts,
    assign_role,
    fork_unlock_account,
    local_node_eth,
    local_node_gc,
    top_up_address,
    web3_eth,
    web3_gnosis,
)

PERCENTAGE = 20
MAX_SLIPPAGE = 1

stresstest_outcome = {
    "dao": "GnosisDAO",
    "blockchain": "ethereum",
    "general_parameters": [
        {"name": "percentage", "label": "Percentage", "type": "input", "rules": {"min": 0.001, "max": 100}}
    ],
    "positions": [
        {
            "position_id": "33",
            "position_id_tech": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D",
            "position_id_human_readable": "ethereum_Aura_rETH_WETH",
            "protocol": "Aura",
            "exec_config": [
                {
                    "function_name": "exit_1",
                    "label": "Unstake",
                    "test": True,
                    "stresstest": True,
                    "stresstest_error": "None",
                    "description": "Unstake BPT from Aura gauge",
                    "parameters": [
                        {
                            "name": "rewards_address",
                            "type": "constant",
                            "value": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D",
                        }
                    ],
                },
                {
                    "function_name": "exit_2_1",
                    "label": "Unstake + withdraw (proportional)",
                    "test": True,
                    "stresstest": True,
                    "stresstest_error": "None",
                    "description": "Unstake the BPT from Aura and exit pool on Balancer with proportional exit (Not for recovery mode)",
                    "parameters": [
                        {
                            "name": "rewards_address",
                            "type": "constant",
                            "value": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D",
                        },
                        {
                            "name": "max_slippage",
                            "label": "Max Slippage",
                            "type": "input",
                            "rules": {"min": 0.001, "max": 100},
                        },
                    ],
                },
                {
                    "function_name": "exit_2_3",
                    "label": "Unstake + withdraw (proportional) (Recovery mode)",
                    "test": True,
                    "stresstest": False,
                    "stresstest_error": "error: Skip recovery",
                    "description": "Unstake the BPT from Aura and exit pool on Balancer with proportional exit. (Recovery mode)",
                    "parameters": [
                        {
                            "name": "rewards_address",
                            "type": "constant",
                            "value": "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D",
                        },
                        {
                            "name": "max_slippage",
                            "label": "Max Slippage",
                            "type": "input",
                            "rules": {"min": 0.001, "max": 100},
                        },
                    ],
                },
            ],
        }
    ],
}


@dataclass
class DAO:
    name: str
    blockchain: str
    avatar_safe_address: str
    roles_mod_address: str
    role: int


dao = DAO(
    name="GnosisDAO",
    blockchain="ETHEREUM",
    avatar_safe_address="0x849D52316331967b6fF1198e5E32A0eB168D039d",
    roles_mod_address="0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc",
    role=4,
)


def set_up_roles(local_node_eth, local_node_gc, accounts, dao: DAO):
    if dao.blockchain == "ETHEREUM":
        block = local_node_eth.w3.eth.default_block
        local_node_eth.set_block(block)
        w3 = local_node_eth.w3
        disassembler_address = accounts[0].address
        private_key = accounts[0].key.hex()
        assign_role(
            local_node=local_node_eth,
            avatar_safe_address=dao.avatar_safe_address,
            roles_mod_address=dao.roles_mod_address,
            role=dao.role,
            asignee=disassembler_address,
        )
    elif dao.blockchain == "GNOSIS":
        block = local_node_gc.w3.eth.default_block
        local_node_gc.set_block(block)
        w3 = local_node_gc.w3
        disassembler_address = accounts[0].address
        private_key = accounts[0].key.hex()
        assign_role(
            local_node=local_node_gc,
            avatar_safe_address=dao.avatar_safe_address,
            roles_mod_address=dao.roles_mod_address,
            role=dao.role,
            asignee=disassembler_address,
        )
    else:
        raise ValueError(f"Blockchain {dao.blockchain} not supported")

    return w3, private_key


def set_env(monkeypatch, private_key: str, dao: DAO) -> ENV:
    monkeypatch.setenv(f"{dao.name.upper()}_{dao.blockchain.upper()}_AVATAR_SAFE_ADDRESS", dao.avatar_safe_address)
    monkeypatch.setenv(f"{dao.name.upper()}_{dao.blockchain.upper()}_ROLES_MOD_ADDRESS", dao.roles_mod_address)
    monkeypatch.setenv(f"{dao.name.upper()}_{dao.blockchain.upper()}_ROLE", dao.role)
    monkeypatch.setenv(f"{dao.name.upper()}_{dao.blockchain.upper()}_PRIVATE_KEY", private_key)
    return ENV(dao.name, dao.blockchain)


def test_stresstest(local_node_eth, local_node_gc, accounts, monkeypatch):
    w3, private_key = set_up_roles(local_node_eth, local_node_gc, accounts, dao)
    set_env(monkeypatch, private_key, dao)

    with open(os.path.join(os.path.dirname(__file__), "test_stresstest_v2_eth_gno.json"), "r") as f:
        test_data = json.load(f)

    stresstest_tester = stresstest(
        w3=w3,
        positions_dict=test_data,
        percentage=PERCENTAGE,
        max_slippage=MAX_SLIPPAGE,
        dao=dao.name,
        blockchain=dao.blockchain,
    )

    assert stresstest_tester == stresstest_outcome
