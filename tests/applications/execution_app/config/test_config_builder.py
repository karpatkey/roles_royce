import json
import os
from unittest.mock import mock_open, patch

from defabipedia.types import Chain

from roles_royce.applications.execution_app.config.config_builder import (
    DAO,
    AuraPosition,
    BalancerPosition,
    DAOStrategiesBuilder,
    WalletPosition,
)
from tests.utils import local_node_eth, local_node_gc

# Load the contents of your test JSON file
with open(os.path.join(os.path.dirname(__file__), "test_aura_template.json"), "r") as f:
    test_data = json.load(f)

# Convert the data to a string
test_data_str = json.dumps(test_data)


# Use patch to replace the open function
@patch("builtins.open", mock_open(read_data=test_data_str))
def test_build_aura_positions(local_node_gc):
    with patch(
        "roles_royce.applications.execution_app.config.config_builder.get_aura_gauge_from_bpt"
    ) as mock_get_aura_gauge_from_bpt, patch(
        "roles_royce.applications.execution_app.config.config_builder.get_tokens_from_bpt"
    ) as mock_get_tokens_from_bpt:
        dao = DAO.GnosisDAO
        blockchain = Chain.GNOSIS
        aura_position = AuraPosition(position_id="226", bpt_address="0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56")
        w3 = local_node_gc.w3
        block = 32101684
        local_node_gc.set_block(block)

        mock_get_aura_gauge_from_bpt.return_value = "0x750c5ED835d300d4ba5054cf2Fad946f0a0df0CD"
        mock_get_tokens_from_bpt.return_value = [
            {"address": "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1", "symbol": "WETH"},
            {"address": "0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6", "symbol": "wstETH"},
        ]

        builder = DAOStrategiesBuilder(dao, blockchain, aura=[aura_position])
        result = builder.build_aura_positions(w3, [aura_position])

        assert result == [
            {
                "position_id": "226",
                "position_id_tech": "0x750c5ED835d300d4ba5054cf2Fad946f0a0df0CD",
                "position_id_human_readable": "gnosis_Aura_WETH_wstETH",
                "protocol": "Aura",
                "exec_config": [
                    {
                        "function_name": "exit_1",
                        "label": "Unstake",
                        "test": True,
                        "stresstest": False,
                        "description": "Unstake BPT from Aura gauge",
                        "parameters": [
                            {
                                "name": "rewards_address",
                                "type": "constant",
                                "value": "0x750c5ED835d300d4ba5054cf2Fad946f0a0df0CD",
                            }
                        ],
                    },
                    {
                        "function_name": "exit_2_1",
                        "label": "Unstake + withdraw (proportional)",
                        "test": True,
                        "stresstest": False,
                        "description": "Unstake the BPT from Aura and exit pool on Balancer with proportional exit (Not for recovery mode)",
                        "parameters": [
                            {
                                "name": "rewards_address",
                                "type": "constant",
                                "value": "0x750c5ED835d300d4ba5054cf2Fad946f0a0df0CD",
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
                        "function_name": "exit_2_2",
                        "label": "Unstake + Withdraw (Single Token)",
                        "test": True,
                        "stresstest": False,
                        "description": "Unstake BPT from gauge and withdraw a single token (specified by the user) by redeeming the BPT",
                        "parameters": [
                            {
                                "name": "rewards_address",
                                "type": "constant",
                                "value": "0x750c5ED835d300d4ba5054cf2Fad946f0a0df0CD",
                            },
                            {"name": "max_slippage", "type": "input", "rules": {"min": 0, "max": 100}},
                            {
                                "name": "token_out_address",
                                "label": "Token Out Address",
                                "type": "input",
                                "options": [
                                    {"value": "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1", "label": "WETH"},
                                    {"value": "0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6", "label": "wstETH"},
                                ],
                            },
                        ],
                    },
                    {
                        "function_name": "exit_2_3",
                        "label": "Unstake + withdraw (proportional) (Recovery mode)",
                        "test": True,
                        "stresstest": False,
                        "description": "Unstake the BPT from Aura and exit pool on Balancer with proportional exit. (Recovery mode)",
                        "parameters": [
                            {
                                "name": "rewards_address",
                                "type": "constant",
                                "value": "0x750c5ED835d300d4ba5054cf2Fad946f0a0df0CD",
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
        ]


# Load the contents of your test JSON file
with open(os.path.join(os.path.dirname(__file__), "test_balancer_template.json"), "r") as f:
    test_data = json.load(f)

# Convert the data to a string
test_data_str = json.dumps(test_data)


# Use patch to replace the open function
@patch("builtins.open", mock_open(read_data=test_data_str))
def test_build_balancer_positions(local_node_gc):
    with patch(
        "roles_royce.applications.execution_app.config.config_builder.get_tokens_from_bpt"
    ) as mock_get_tokens_from_bpt:
        dao = DAO.GnosisDAO
        blockchain = Chain.GNOSIS
        balancer_position = BalancerPosition(
            position_id="226", bpt_address="0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56", staked=False
        )
        w3 = local_node_gc.w3

        mock_get_tokens_from_bpt.return_value = [
            {"address": "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1", "symbol": "WETH"},
            {"address": "0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6", "symbol": "wstETH"},
        ]

        builder = DAOStrategiesBuilder(dao, blockchain, balancer=[balancer_position])
        result = builder.build_balancer_positions(w3, [balancer_position])

        assert (
            result
            == result
            == [
                {
                    "protocol": "Balancer",
                    "position_id": "226",
                    "position_id_tech": "0xF48f01DCB2CbB3ee1f6AaB0e742c2D3941039d56",
                    "position_id_human_readable": "gnosis_Balancer_WETH_wstETH",
                    "exec_config": [
                        {
                            "function_name": "exit_1_1",
                            "label": "Withdraw (proportional)",
                            "test": True,
                            "stresstest": False,
                            "description": "Exit pool on Balancer with proportional exit. (Not for recovery mode)",
                            "parameters": [
                                {
                                    "name": "bpt_address",
                                    "type": "constant",
                                    "value": "0xF48f01DCB2CbB3ee1f6AaB0e742c2D3941039d56",
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
                            "function_name": "exit_1_2",
                            "label": "Withdraw (Single Token)",
                            "test": True,
                            "stresstest": False,
                            "description": "Withdraw a single token (specified by the user) by redeeming the BPT",
                            "parameters": [
                                {
                                    "name": "bpt_address",
                                    "type": "constant",
                                    "value": "0xF48f01DCB2CbB3ee1f6AaB0e742c2D3941039d56",
                                },
                                {
                                    "name": "max_slippage",
                                    "label": "Max slippage",
                                    "type": "input",
                                    "rules": {"min": 0, "max": 100},
                                },
                                {
                                    "name": "token_out_address",
                                    "label": "Token out",
                                    "type": "input",
                                    "options": [
                                        {"value": "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1", "label": "WETH"},
                                        {"value": "0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6", "label": "wstETH"},
                                    ],
                                },
                            ],
                        },
                        {
                            "function_name": "exit_1_3",
                            "label": "Withdraw (proportional) (Recovery mode)",
                            "test": True,
                            "stresstest": False,
                            "description": "Exit pool on Balancer with proportional exit. (Recovery Mode)",
                            "parameters": [
                                {
                                    "name": "bpt_address",
                                    "type": "constant",
                                    "value": "0xF48f01DCB2CbB3ee1f6AaB0e742c2D3941039d56",
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
            ]
        )


with open(os.path.join(os.path.dirname(__file__), "test_swap_pool_template.json"), "r") as f:
    test_data = json.load(f)

test_data_str = json.dumps(test_data)


@patch("builtins.open", mock_open(read_data=test_data_str))
def test_build_swap_pool_positions(local_node_eth):
    dao = DAO.GnosisDAO
    blockchain = Chain.ETHEREUM
    wallet_position = WalletPosition(position_id="226", token_in_address="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")
    w3 = local_node_eth.w3

    builder = DAOStrategiesBuilder(dao, blockchain, wallet_tokens=[wallet_position])
    result = builder.build_wallet_positions(w3, [wallet_position])

    assert result == [
        {
            "protocol": "Wallet",
            "position_id": "226",
            "position_id_tech": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
            "position_id_human_readable": "ethereum_WalletPosition_stETH",
            "exec_config": [
                {
                    "function_name": "exit_2",
                    "label": "Exchange Wallet Token on Curve",
                    "test": True,
                    "stresstest": False,
                    "description": "Exchange a wallet token through Curve",
                    "parameters": [
                        {
                            "name": "token_in_address",
                            "label": "Token in",
                            "type": "input",
                            "options": [{"value": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84", "label": "stETH"}],
                        },
                        {
                            "name": "max_slippage",
                            "label": "Max slippage",
                            "type": "input",
                            "rules": {"min": 0.001, "max": 100},
                        },
                        {
                            "name": "token_out_address",
                            "label": "Token out",
                            "type": "input",
                            "options": [{"value": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "label": "ETH"}],
                        },
                    ],
                }
            ],
        }
    ]
