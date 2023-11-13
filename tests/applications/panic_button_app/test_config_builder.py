balancer_template = {
  "position_id": "FllMeWithPositionId",
  "protocol": "Balancer",
  "position_exec_config": [
    {
      "function_name": "exit_1_1",
      "label": "Exit_1_1",
      "description": "Withdraw funds from the Balancer pool withdrawing all assets in proportional way (not used for pools in recovery mode!)",
      "parameters": [
        {
          "name": "bpt_address",
          "type": "constant",
          "value": "FillMeWithBptAddress"
        },
        {
          "name": "max_slippage",
          "label": "Max slippage",
          "type": "input",
          "rules": {"min": 0,"max": 100}
        }
      ]
    },
    {
      "function_name": "exit_1_2",
      "label": "Exit_1_2",
      "description": "Withdraw funds from the Balancer pool withdrawing a single asset specified by the token index.",
      "parameters": [
        {
          "name": "bpt_address",
          "type": "constant",
          "value": "FillMeWithBptAddress"
        },
        {
          "name": "max_slippage",
          "label": "Max slippage",
          "type": "input",
          "rules": {"min": 0,"max": 100}
        },
        { "name": "token_out_address", 
        "label": "Token out",
        "type": "input", 
        "options": [            
            {
              "value": "FillMewithTokenAddress",
              "label": "FillMeWithTokenSymbol"
            }
            ] 
        }
      ]
    },
    {
      "function_name": "exit_1_3",
      "label": "Exit_1_3",
      "description":  "Withdraw funds from the Balancer pool withdrawing all assets in proportional way for pools in recovery mode.",
      "parameters": [
        {
          "name": "bpt_address",
          "type": "constant",
          "value": "FillMeWithBptAddress"
        },
        {
          "name": "max_slippage",
          "label": "Max slippage",
          "type": "input",
          "rules": {"min": 0,"max": 100}
        }
      ]
    }
  ]
}

aura_template = {
  "position_id": "FillMeWIthPositionId",
  "protocol": "Aura",
  "position_exec_config": [
    {
      "function_name": "exit_1",
      "label": "Exit_1",
      "description": "Withdraw from Aura",
      "parameters": [
        {
          "name": "rewards_address",
          "type": "constant",
          "value": "FillMeWithRewardsAddress"
        },
        {
          "name": "max_slippage",
          "label": "Max Slippage",
          "type": "input",
          "rules": {
            "min": 0,
            "max": 100
          }
        }
      ]
    },
    {
      "function_name": "exit_2_1",
      "label": "Exit_2_1",
      "description": "Withdraw funds from Aura and then from the Balancer pool withdrawing all assets in proportional way (not used for pools in recovery mode!)",
      "parameters": [
        {
          "name": "rewards_address",
          "type": "constant",
          "value": "FillMeWithRewardsAddress"
        },
        {
          "name": "max_slippage",
          "type": "input",
          "label": "Max Slippage",
          "rules": {
            "min": 0,
            "max": 100
          }
        }
      ]
    },
    {
      "function_name": "exit_2_2",
      "label": "Exit_2_2",
      "description": "Withdraw funds from Aura and then from the Balancer pool withdrawing a single asset.",
      "parameters": [
        {
          "name": "rewards_address",
          "type": "constant",
          "value": "FillMeWithRewardsAddress"
        },
        {
          "name": "max_slippage",
          "type": "input",
          "scale": {
            "min": 0,
            "max": 100,
            "step": 0.5
          }
        },
        {
          "name": "token_out_address",
          "label": "Token Out Address",
          "type": "input",
          "options": [
            {
              "value": "FillMewithTokenAddress",
              "label": "FillMeWithTokenSymbol"
            }
          ]
        }
      ]
    },
    {
      "function_name": "exit_2_3",
      "description": "Withdraw funds from Aura and then from the Balancer pool withdrawing all assets in proportional way when pool is in recovery mode",
      "parameters": [
        {
          "name": "rewards_address",
          "type": "constant",
          "value": "FillMeWithRewardsAddress"
        },
        {
          "name": "max_slippage",
          "type": "input",
          "scale": {
            "min": 0,
            "max": 100,
            "step": 0.5
          }
        }
      ]
    }
  ]
}

'''
def test_get_bpt_from_aura(local_node_gc):
    w3 = local_node_gc.w3
    block = 30698007
    local_node_gc.set_block(block)
    result = get_bpt_from_aura(w3)
    assert result[0]['aura_address'] == "0x026d163C28cC7dbf57d6ED57f14208Ee412CA526"

def test_add_balancer_positions(local_node_gc):
    BPT_ADDRESSES = ['0x0c1b9ce6bf6c01f587c2ee98b0ef4b20c6648753', '0x4cdabe9e07ca393943acfb9286bbbd0d0a310ff6']
    POSITION_IDS = ["249", "251" ]
    W3 = local_node_gc.w3
    block = 30699065
    local_node_gc.set_block(block)

    result = add_balancer_positions(W3, balancer_template, POSITION_IDS, BPT_ADDRESSES)

    assert result[0]['position_id'] == '249'
    assert result[0]['protocol'] == 'Balancer'

def test_add_aura_positions(local_node_gc):
    DB = [{'blockchain': 'gnosis', 'bpt_address': '0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56', 'aura_address': '0x1204f5060bE8b716F5A62b4Df4cE32acD01a69f5'}, {'blockchain': 'gnosis', 'bpt_address': '0xb973ca96a3f0d61045f53255e319aedb6ed49240', 'aura_address': '0x89D3D732da8bf0f88659Cf3738E5E44e553f9ED7'}]
    BPT_ADDRESSES = ['0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56', '0xb973ca96a3f0d61045f53255e319aedb6ed49240']
    POSITION_IDS = ["226", "227" ]

    W3 = local_node_gc.w3
    block = 30699345
    local_node_gc.set_block(block)

    result = add_aura_positions(W3, aura_template, POSITION_IDS, BPT_ADDRESSES)

    assert result[1]['protocol'] == 'Aura'
    assert result[1]['position_id'] == '227'

'''
from tests.utils import local_node_gc
import pytest
from unittest.mock import patch, mock_open
from web3 import Web3
from roles_royce.applications.panic_button_app.config.config_builder import DAO, Blockchain, AuraPosition, DAOStrategiesBuilder, BalancerPosition
import json

# Load the contents of your test JSON file
with open('tests/applications/panic_button_app/test_aura_template.json', 'r') as f:
    test_data = json.load(f)

# Convert the data to a string
test_data_str = json.dumps(test_data)

# Use patch to replace the open function
@patch('builtins.open', mock_open(read_data=test_data_str))
def test_build_aura_positions(local_node_gc):
    with patch('roles_royce.applications.panic_button_app.config.config_builder.get_bpt_from_aura') as mock_get_bpt_from_aura, \
         patch('roles_royce.applications.panic_button_app.config.config_builder.get_tokens_from_bpt') as mock_get_tokens_from_bpt:
        dao = DAO.GnosisDAO
        blockchain = Blockchain.Gnosis
        aura_position = AuraPosition(position_id='226', bpt_address='0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56')
        w3 = local_node_gc.w3

        mock_get_bpt_from_aura.return_value = [{'blockchain': 'gnosis', 'bpt_address': '0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56', 'aura_address': '0x1204f5060bE8b716F5A62b4Df4cE32acD01a69f5'}, {'blockchain': 'gnosis', 'bpt_address': '0xb973ca96a3f0d61045f53255e319aedb6ed49240', 'aura_address': '0x89D3D732da8bf0f88659Cf3738E5E44e553f9ED7'}]
        mock_get_tokens_from_bpt.return_value = [{'address': '0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1', 'symbol': 'WETH'}, {'address': '0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6', 'symbol': 'wstETH'}]

        builder = DAOStrategiesBuilder(dao, blockchain, aura=[aura_position])
        result = builder.build_aura_positions(w3, [aura_position])

        assert len(result) == 1
        assert result[0]['position_id'] == aura_position.position_id
        assert len(result[0]['exec_config']) == 4


# Load the contents of your test JSON file
with open('tests/applications/panic_button_app/test_balancer_template.json', 'r') as f:
    test_data = json.load(f)

# Convert the data to a string
test_data_str = json.dumps(test_data)

# Use patch to replace the open function
@patch('builtins.open', mock_open(read_data=test_data_str))
def test_build_balancer_positions(local_node_gc):
    with patch('roles_royce.applications.panic_button_app.config.config_builder.get_tokens_from_bpt') as mock_get_tokens_from_bpt:
        dao = DAO.GnosisDAO
        blockchain = Blockchain.Gnosis
        balancer_position = BalancerPosition(position_id='226', bpt_address='0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56')
        w3 = local_node_gc.w3

        mock_get_tokens_from_bpt.return_value = [{'address': '0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1', 'symbol': 'WETH'}, {'address': '0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6', 'symbol': 'wstETH'}]

        builder = DAOStrategiesBuilder(dao, blockchain, balancer=[balancer_position])
        result = builder.build_balancer_positions(w3, [balancer_position])

        assert len(result) == 1
        assert result[0]['position_id'] == balancer_position.position_id
        assert len(result[0]['exec_config']) == 3

