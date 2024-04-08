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
    "blockchain": "gnosis",
    "general_parameters": [
        {"name": "percentage", "label": "Percentage", "type": "input", "rules": {"min": 0.001, "max": 100}}
    ],
    "positions": [
        {
            "protocol": "Balancer",
            "position_id": "107",
            "position_id_tech": "0xa99FD9950B5D5dCeEaf4939E221dcA8cA9B938aB",
            "position_id_human_readable": "gnosis_Balancer_WETH_BAL_GNO_WXDAI",
            "exec_config": [
                {
                    "function_name": "exit_1_1",
                    "label": "Withdraw (proportional)",
                    "test": True,
                    "stresstest": True,
                    "stresstest_error": "None",
                    "description": "Exit pool on Balancer with proportional exit. (Not for recovery mode)",
                    "parameters": [
                        {
                            "name": "bpt_address",
                            "type": "constant",
                            "value": "0xa99FD9950B5D5dCeEaf4939E221dcA8cA9B938aB",
                        },
                        {
                            "name": "max_slippage",
                            "label": "Max slippage",
                            "type": "input",
                            "rules": {"min": 0.001, "max": 100},
                        },
                    ],
                },
                {
                    "function_name": "exit_1_3",
                    "label": "Withdraw (proportional) (Recovery mode)",
                    "test": True,
                    "stresstest": False,
                    "stresstest_error": "error: Skip recovery",
                    "description": "Exit pool on Balancer with proportional exit. (Recovery Mode)",
                    "parameters": [
                        {
                            "name": "bpt_address",
                            "type": "constant",
                            "value": "0xa99FD9950B5D5dCeEaf4939E221dcA8cA9B938aB",
                        },
                        {
                            "name": "max_slippage",
                            "label": "Max slippage",
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
    blockchain="GNOSIS",
    avatar_safe_address="0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f",
    roles_mod_address="0x10785356E66b93432e9E8D6F9e532Fa55e4fc058",
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

    with open(os.path.join(os.path.dirname(__file__), "test_stresstest_gno_gno.json"), "r") as f:
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
