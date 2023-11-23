from tests.utils import local_node_gc
import pytest
from unittest.mock import patch, mock_open
from web3 import Web3
from roles_royce.applications.panic_button_app.config.config_builder import DAO, Blockchain, AuraPosition, \
    DAOStrategiesBuilder, BalancerPosition
import json
from defabipedia.types import Chains
import os

# Load the contents of your test JSON file
with open(os.path.join(os.path.dirname(__file__), 'test_aura_template.json'), 'r') as f:
    test_data = json.load(f)

# Convert the data to a string
test_data_str = json.dumps(test_data)


# Use patch to replace the open function
@patch('builtins.open', mock_open(read_data=test_data_str))
def test_build_aura_positions(local_node_gc):
    with patch(
            'roles_royce.applications.panic_button_app.config.config_builder.get_bpt_from_aura') as mock_get_bpt_from_aura, \
            patch(
                'roles_royce.applications.panic_button_app.config.config_builder.get_tokens_from_bpt') as mock_get_tokens_from_bpt:
        dao = DAO.GnosisDAO
        blockchain = Chains.Gnosis
        aura_position = AuraPosition(position_id='226', bpt_address='0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56')
        w3 = local_node_gc.w3

        mock_get_bpt_from_aura.return_value = [
            {
                'blockchain': 'gnosis',
                'bpt_address': '0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56',
                'aura_address': '0x1204f5060bE8b716F5A62b4Df4cE32acD01a69f5'
            },
            {
                'blockchain': 'gnosis',
                'bpt_address': '0xb973ca96a3f0d61045f53255e319aedb6ed49240',
                'aura_address': '0x89D3D732da8bf0f88659Cf3738E5E44e553f9ED7'
            }
        ]
        mock_get_tokens_from_bpt.return_value = [
            {
                'address': '0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1',
                'symbol': 'WETH'
            },
            {
                'address': '0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6',
                'symbol': 'wstETH'
            }
        ]

        builder = DAOStrategiesBuilder(dao, blockchain, aura=[aura_position])
        result = builder.build_aura_positions(w3, [aura_position])

        assert len(result) == 1
        assert result[0]['position_id'] == aura_position.position_id
        assert len(result[0]['exec_config']) == 4


# Load the contents of your test JSON file
with open(os.path.join(os.path.dirname(__file__), 'test_balancer_template.json'), 'r') as f:
    test_data = json.load(f)

# Convert the data to a string
test_data_str = json.dumps(test_data)


# Use patch to replace the open function
@patch('builtins.open', mock_open(read_data=test_data_str))
def test_build_balancer_positions(local_node_gc):
    with patch(
            'roles_royce.applications.panic_button_app.config.config_builder.get_tokens_from_bpt') as mock_get_tokens_from_bpt:
        dao = DAO.GnosisDAO
        blockchain = Chains.Gnosis
        balancer_position = BalancerPosition(position_id='226',
                                             bpt_address='0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56')
        w3 = local_node_gc.w3

        mock_get_tokens_from_bpt.return_value = [
            {
                'address': '0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1',
                'symbol': 'WETH'
            },
            {
                'address': '0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6',
                'symbol': 'wstETH'
            }
        ]

        builder = DAOStrategiesBuilder(dao, blockchain, balancer=[balancer_position])
        result = builder.build_balancer_positions(w3, [balancer_position])

        assert len(result) == 1
        assert result[0]['position_id'] == balancer_position.position_id
        assert len(result[0]['exec_config']) == 3
