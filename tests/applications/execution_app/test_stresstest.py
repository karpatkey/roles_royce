import json
import os
from dataclasses import dataclass

from roles_royce.applications.execution_app.stresstest import stresstest
from roles_royce.applications.execution_app.utils import ENV
from tests.utils import assign_role

PERCENTAGE = 20
MAX_SLIPPAGE = 1
TEST_ETH_BLOCK = 19590108
TEST_GNOSIS_BLOCK = 33291126


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
        local_node_eth.set_block(TEST_ETH_BLOCK)
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
        local_node_gc.set_block(TEST_GNOSIS_BLOCK)
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


def get_env(dao: DAO, disassembler, rpc_url) -> ENV:
    return ENV(
        rpc_url=rpc_url,
        rpc_fallback_url=rpc_url,
        avatar_safe_address=dao.avatar_safe_address,
        roles_mod_address=dao.roles_mod_address,
        disassembler_address=disassembler,
        role=dao.role,
        mode="development",
    )


stresstest_outcome = {
    "dao": "GnosisDAO",
    "blockchain": "ethereum",
    "general_parameters": [
        {"name": "percentage", "label": "Percentage", "type": "input", "rules": {"min": 0, "max": 100}}
    ],
    "positions": [
        {
            "protocol": "Wallet",
            "position_id": "34",
            "position_id_tech": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "position_id_human_readable": "ethereum_WalletPosition_WETH_to_DAI_in_CowSwap_to_USDT_in_CowSwap_to_USDC_in_CowSwap_to_USDT_in_UniswapV3",
            "exec_config": [
                {
                    "function_name": "exit_1",
                    "label": "Exchange Wallet Token on Cowswap",
                    "test": True,
                    "stresstest": True,
                    "stresstest_error": "None",
                    "description": "Exchange a wallet token through Cowswap",
                    "parameters": [
                        {
                            "name": "token_in_address",
                            "label": "Token In",
                            "type": "input",
                            "options": [
                                {
                                    "label": "WETH",
                                    "value": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                                }
                            ],
                        },
                        {
                            "name": "max_slippage",
                            "label": "Max Slippage",
                            "type": "input",
                            "rules": {"min": 0.001, "max": 100},
                        },
                        {
                            "name": "token_out_address",
                            "label": "Token Out",
                            "type": "input",
                            "options": [
                                {"value": "0x6B175474E89094C44Da98b954EedeAC495271d0F", "label": "DAI"},
                                {"value": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "label": "USDT"},
                                {"value": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "label": "USDC"},
                            ],
                        },
                    ],
                },
                {
                    "function_name": "exit_4",
                    "label": "Exchange Wallet Token on UniswapV3",
                    "test": True,
                    "stresstest": False,
                    "stresstest_error": "[USDT]: Error: ('ParameterNotAllowed()', None);\n[USDC]: Error: ('ParameterNotAllowed()', None)",
                    "description": "Exchange a wallet token through UniswapV3",
                    "parameters": [
                        {
                            "name": "token_in_address",
                            "label": "Token In",
                            "type": "input",
                            "options": [
                                {
                                    "label": "WETH",
                                    "value": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                                }
                            ],
                        },
                        {
                            "name": "max_slippage",
                            "label": "Max Slippage",
                            "type": "input",
                            "rules": {"min": 0.001, "max": 100},
                        },
                        {"name": "token_out_address", "label": "Token Out", "type": "input", "options": []},
                    ],
                },
            ],
        }
    ],
}


with open(os.path.join(os.path.dirname(__file__), "test_stresstest_token.json"), "r") as f:
    test_data = json.load(f)


def test_stresstest(local_node_eth, local_node_gc, accounts):
    w3, _ = set_up_roles(local_node_eth, local_node_gc, accounts, dao)
    if dao.blockchain == "ETHEREUM":
        rpc_url = local_node_eth.url
    elif dao.blockchain == "GNOSIS":
        rpc_url = local_node_gc.url
    else:
        raise ValueError(f"Blockchain {dao.blockchain} not supported")

    env = get_env(dao=dao, disassembler=accounts[0].address, rpc_url=rpc_url)

    stresstest_tester = stresstest(
        env=env,
        w3=w3,
        positions_dict=test_data,
        percentage=PERCENTAGE,
        max_slippage=MAX_SLIPPAGE,
    )

    assert stresstest_tester == stresstest_outcome
