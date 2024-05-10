import json
import os
from unittest.mock import mock_open, patch

import pytest
from defabipedia.types import Chain

from artemis.applications.execution_app.config.config_builder import (
    DAO,
    AuraPosition,
    BalancerPosition,
    DAOStrategiesBuilder,
    WalletPosition,
    LidoPosition,
)
from tests.fork_fixtures import local_node_eth, local_node_gc

# Load the contents of your test JSON file
with open(os.path.join(os.path.dirname(__file__), "test_aura_template.json"), "r") as f:
    test_data = json.load(f)

# Convert the data to a string
test_data_str = json.dumps(test_data)


# Use patch to replace the open function
@patch("builtins.open", mock_open(read_data=test_data_str))
def test_build_aura_positions(local_node_gc):
    with patch(
        "artemis.applications.execution_app.config.config_builder.get_bpt_from_aura_address"
    ) as mock_get_bpt_from_aura_address, patch(
        "artemis.applications.execution_app.config.config_builder.get_tokens_from_bpt"
    ) as mock_get_tokens_from_bpt, patch(
        "artemis.applications.execution_app.config.config_builder.get_pool_id_from_bpt"
    ) as mock_get_pool_id_from_bpt:
        dao = DAO.GnosisDAO
        blockchain = Chain.GNOSIS
        aura_position = AuraPosition(position_id="226", reward_address="0x750c5ED835d300d4ba5054cf2Fad946f0a0df0CD")
        w3 = local_node_gc.w3
        block = 32101684
        local_node_gc.set_block(block)

        mock_get_pool_id_from_bpt.return_value = "0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56000200000000000000000012"
        mock_get_bpt_from_aura_address.return_value = "0xF48f01DCB2CbB3ee1f6AaB0e742c2D3941039d56"
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
                        "stresstest_error": "None",
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
                        "stresstest_error": "None",
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
                        "function_name": "exit_2_3",
                        "label": "Unstake + withdraw (proportional) (Recovery mode)",
                        "test": True,
                        "stresstest": False,
                        "stresstest_error": "None",
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
        "artemis.applications.execution_app.config.config_builder.get_tokens_from_bpt"
    ) as mock_get_tokens_from_bpt, patch(
        "artemis.applications.execution_app.config.config_builder.get_pool_id_from_bpt"
    ) as mock_get_pool_id_from_bpt:
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
        mock_get_pool_id_from_bpt.return_value = "0xbad20c15a773bf03ab973302f61fabcea5101f0a000000000000000000000034"

        builder = DAOStrategiesBuilder(dao, blockchain, balancer=[balancer_position])
        result = builder.build_balancer_positions(w3, [balancer_position])

        assert result == [
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
                        "stresstest_error": "None",
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
                        "stresstest_error": "None",
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
                        "stresstest_error": "None",
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


with open(os.path.join(os.path.dirname(__file__), "test_lido_template.json"), "r") as f:
    test_data = json.load(f)

test_data_str = json.dumps(test_data)


@patch("builtins.open", mock_open(read_data=test_data_str))
def test_build_lido_positions(local_node_eth):
    dao = DAO.GnosisDAO
    blockchain = Chain.ETHEREUM

    lido_position = LidoPosition(position_id="226", lido_address="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")
    w3 = local_node_eth.w3
    block = 19663216
    local_node_eth.set_block(block)

    builder = DAOStrategiesBuilder(dao, blockchain, lido=[lido_position])
    result = builder.build_lido_positions(w3, [lido_position])

    assert result == [
        {
            "protocol": "Lido",
            "position_id": "226",
            "position_id_tech": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
            "position_id_human_readable": "ethereum_Lido_stETH",
            "exec_config": [
                {
                    "function_name": "exit_1",
                    "label": "Unstake stETH",
                    "test": True,
                    "stresstest": False,
                    "stresstest_error": "None",
                    "description": "Unstake stETH for ETH",
                    "parameters": [],
                },
                {
                    "function_name": "exit_3",
                    "label": "Swap stETH",
                    "test": True,
                    "stresstest": False,
                    "stresstest_error": "None",
                    "description": "Swap stETH for ETH",
                    "parameters": [
                        {
                            "name": "max_slippage",
                            "type": "input",
                            "label": "Max slippage",
                            "rules": {"min": 0.001, "max": 100},
                        }
                    ],
                },
                {
                    "function_name": "exit_5",
                    "label": "Exchange Wallet Token on Balancer",
                    "test": True,
                    "stresstest": False,
                    "stresstest_error": "None",
                    "description": "Exchange a wallet token through Balancer",
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
                },
                {
                    "function_name": "exit_6",
                    "label": "Exchange Wallet Token on Curve",
                    "test": True,
                    "stresstest": False,
                    "stresstest_error": "None",
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
                },
            ],
        }
    ]


with open(os.path.join(os.path.dirname(__file__), "test_swap_pool_template.json"), "r") as f:
    test_data = json.load(f)

test_data_str = json.dumps(test_data)


@patch("builtins.open", mock_open(read_data=test_data_str))
def test_build_swap_pool_positions(local_node_eth):
    dao = DAO.GnosisDAO
    blockchain = Chain.ETHEREUM
    wallet_position = WalletPosition(position_id="226", token_in_address="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")
    w3 = local_node_eth.w3
    block = 19663216
    local_node_eth.set_block(block)

    builder = DAOStrategiesBuilder(dao, blockchain, wallet_tokens=[wallet_position])
    result = builder.build_wallet_positions(w3, [wallet_position])

    assert result == [
        {
            "protocol": "Wallet",
            "position_id": "226",
            "position_id_tech": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
            "position_id_human_readable": "ethereum_WalletPosition_stETH_to_ETH_in_CowSwap_to_WETH_in_CowSwap_to_ETH_in_Curve",
            "exec_config": [
                {
                    "function_name": "exit_1",
                    "label": "Exchange Wallet Token on Cowswap",
                    "test": True,
                    "stresstest": False,
                    "stresstest_error": "None",
                    "description": "Exchange a wallet token through Cowswap",
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
                            "options": [
                                {"value": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "label": "ETH"},
                                {"value": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "label": "WETH"},
                            ],
                        },
                    ],
                },
                {
                    "function_name": "exit_3",
                    "label": "Exchange Wallet Token on Curve",
                    "test": True,
                    "stresstest": False,
                    "stresstest_error": "None",
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
                },
            ],
        },
        {
            "protocol": "Wallet",
            "position_id": "226",
            "position_id_tech": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
            "position_id_human_readable": "ethereum_WalletPosition_stETH_to_DAI_in_CowSwap_to_USDT_in_CowSwap_to_USDC_in_CowSwap",
            "exec_config": [
                {
                    "function_name": "exit_1",
                    "label": "Exchange Wallet Token on Cowswap",
                    "test": True,
                    "stresstest": False,
                    "stresstest_error": "None",
                    "description": "Exchange a wallet token through Cowswap",
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
                            "options": [
                                {"value": "0x6B175474E89094C44Da98b954EedeAC495271d0F", "label": "DAI"},
                                {"value": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "label": "USDT"},
                                {"value": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "label": "USDC"},
                            ],
                        },
                    ],
                }
            ],
        },
    ]
