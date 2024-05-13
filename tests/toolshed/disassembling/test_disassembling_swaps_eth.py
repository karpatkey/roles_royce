import json
from web3 import Web3
import pytest

from defabipedia.rocket_pool import ContractSpecs
from defabipedia.swap_pools import EthereumSwapPools
from defabipedia.tokens import Abis
from defabipedia.types import Chain

from artemis.roles_modifier import set_gas_strategy, GasStrategies
from artemis.toolshed.disassembling import SwapDisassembler
from tests.roles import apply_presets, deploy_roles, setup_common_roles
from tests.utils import create_simple_safe, steal_token
from tests.fork_fixtures import accounts
from tests.fork_fixtures import local_node_eth_replay as local_node_eth, local_node_gc

ROLE = 4
AVATAR = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
ROLES_MOD = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
BLOCK = 19620486

presets_balancer = """{
  "version": "1.0",
  "chainId": "1",
  "meta": {
    "name": null,
    "description": "",
    "txBuilderVersion": "1.8.0"
  },
  "createdAt": 1701637793776,
  "transactions": [
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2d0e30db0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000ba12222222228d8ba445958a75a0704d566bf2c8",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000ba12222222228d8ba445958a75a0704d566bf2c852bbbe29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "value": "0"
    }
]
}"""

def test_integration_exit_1(local_node_eth, accounts):
    w3 = local_node_eth.w3
    local_node_eth.set_block(BLOCK)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=presets_balancer,
        replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])],
    )
    w3.eth.send_transaction({
        'to': avatar_safe.address,
        'from': "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc", #5th fork account
        'value': Web3.to_wei(6000, "ether")
    })

    blockchain = Chain.get_blockchain_from_web3(w3)

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    token_out = EthereumSwapPools.bal_rETH_WETH.tokens[0]
    token_in = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

    amount_in = 500_000_000_000_000_000

    swap_balancer_disassembler = SwapDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    eth_balance = w3.eth.get_balance(avatar_safe_address)
    assert eth_balance > amount_in

    weth_contract = w3.eth.contract(address=EthereumSwapPools.bal_rETH_WETH.tokens[1], abi=Abis.ERC20.abi)
    weth_balance = weth_contract.functions.balanceOf(avatar_safe_address).call()
    assert weth_balance == 0

    txn_transactable = swap_balancer_disassembler.exit_2(
        percentage=50,
        exit_arguments=[{"token_in_address": token_in, "max_slippage": 1, "token_out_address": token_out}],
        amount_to_redeem=amount_in,
    )
    send_it = swap_balancer_disassembler.send(txn_transactable, private_key)

    assert send_it

    weth_balance = weth_contract.functions.balanceOf(avatar_safe_address).call()
    assert weth_balance == 0

    reth_contract = ContractSpecs[blockchain].rETH.contract(w3)
    reth_balance = reth_contract.functions.balanceOf(avatar_safe_address).call()
    assert reth_balance > 0

def test_integration_exit_1_not_enough_eth(local_node_eth, accounts):
    w3 = local_node_eth.w3
    local_node_eth.set_block(BLOCK)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=presets_balancer,
        replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])],
    )

    blockchain = Chain.get_blockchain_from_web3(w3)

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    token_out = EthereumSwapPools.bal_rETH_WETH.tokens[0]
    token_in = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

    amount_in = 500_000_000_000_000_000

    swap_balancer_disassembler = SwapDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    eth_balance = w3.eth.get_balance(avatar_safe_address)
    assert (eth_balance - amount_in) < 3_000_000_000_000_000_000

    weth_contract = w3.eth.contract(address=EthereumSwapPools.bal_rETH_WETH.tokens[1], abi=Abis.ERC20.abi)
    weth_balance = weth_contract.functions.balanceOf(avatar_safe_address).call()
    assert weth_balance == 0

    with pytest.raises(ValueError) as exc_info:
        swap_balancer_disassembler.exit_2(
            percentage=50,
            exit_arguments=[{"token_in_address": token_in, "max_slippage": 1, "token_out_address": token_out}],
            amount_to_redeem=amount_in,
        )
    
    expected_error_message = "Must keep at least a balance of 3 of native token"
    assert str(exc_info.value) == expected_error_message

presets_curve = """{
  "version": "1.0",
  "chainId": "1",
  "meta": {
    "name": null,
    "description": "",
    "txBuilderVersion": "1.8.0"
  },
  "createdAt": 1701637793776,
  "transactions": [
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000dc24316b9ae028f1497c275eb9192a3ea0f67022",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000dc24316b9ae028f1497c275eb9192a3ea0f670223df02124000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "value": "0"
    },
        {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e826695000000000000000000000000000000000000000000000000000000000000000400000000000000000000000021E27a5E5513D6e65C4f830167390997aA84843a",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d1000000000000000000000000000000000000000000000000000000000000000400000000000000000000000021E27a5E5513D6e65C4f830167390997aA84843a3df02124000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "value": "0"
    }
]
}"""

def test_integration_exit_2(local_node_eth, accounts):
    w3 = local_node_eth.w3
    local_node_eth.set_block(BLOCK)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=presets_curve,
        replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])],
    )
    w3.eth.send_transaction({
        'to': avatar_safe.address,
        'from': "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc", #5th fork account
        'value': Web3.to_wei(6000, "ether")
    })

    blockchain = Chain.get_blockchain_from_web3(w3)

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    token_in = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    token_out = EthereumSwapPools.Curve_stETH_ETH.tokens[1]

    amount_in = 500_000_000_000_000_000

    swap_curve_disassembler = SwapDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    eth_balance = w3.eth.get_balance(avatar_safe_address)
    assert eth_balance >0

    steth_contract = w3.eth.contract(address=EthereumSwapPools.Curve_stETH_ETH.tokens[1], abi=Abis.ERC20.abi)
    steth_balance = steth_contract.functions.balanceOf(avatar_safe_address).call()
    assert steth_balance == 0

    txn_transactable = swap_curve_disassembler.exit_3(
        percentage=50,
        exit_arguments=[{"token_in_address": token_in, "max_slippage": 1, "token_out_address": token_out}],
        amount_to_redeem=amount_in
    )
    send_it = swap_curve_disassembler.send(txn_transactable, private_key)

    assert send_it

    steth_contract = w3.eth.contract(address=EthereumSwapPools.Curve_stETH_ETH.tokens[1], abi=Abis.ERC20.abi)
    steth_balance = steth_contract.functions.balanceOf(avatar_safe_address).call()
    assert steth_balance > 0


preset_uniswapv3 = """{
  "version": "1.0",
  "chainId": "1",
  "meta": {
    "name": null,
    "description": "",
    "txBuilderVersion": "1.8.0"
  },
  "createdAt": 1710944277151,
  "transactions": [
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2d0e30db0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x5e826695000000000000000000000000000000000000000000000000000000000000000400000000000000000000000068b3465833fb72a70ecdf485e0e4c7bd8665fc45",
      "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x2fcf52d1000000000000000000000000000000000000000000000000000000000000000400000000000000000000000068b3465833fb72a70ecdf485e0e4c7bd8665fc4504e45aaf000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
      "value": "0"
    }
  ]
}"""
preset_uniswapv3_v2 = """{
  "version": "1.0",
  "chainId": "1",
  "meta": {
    "name": null,
    "description": "",
    "txBuilderVersion": "1.8.0"
  },
  "createdAt": 1710944277151,
  "transactions": [
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2d0e30db0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001",
    "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x5e826695000000000000000000000000000000000000000000000000000000000000000400000000000000000000000068b3465833fb72a70ecdf485e0e4c7bd8665fc45",
      "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x33a0480c000000000000000000000000000000000000000000000000000000000000000400000000000000000000000068b3465833fb72a70ecdf485e0e4c7bd8665fc4504e45aaf00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000024000000000000000000000000000000000000000000000000000000000000002e000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000000000200000000000000000000000007f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000c01318bab7ee1f5ba734172bf7718b5dc6ec90e1",
      "value": "0"
    }
  ]
}"""


def test_integration_exit_3(local_node_eth, accounts):
    w3 = local_node_eth.w3
    local_node_eth.set_block(BLOCK)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=preset_uniswapv3,
        replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])],
    )

    w3.eth.send_transaction({
        'to': avatar_safe.address,
        'from': "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc", #5th fork account
        'value': Web3.to_wei(6000, "ether")
    })

    blockchain = Chain.get_blockchain_from_web3(w3)

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    token_in = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    token_out = EthereumSwapPools.UniV3_wstETH_ETH.tokens[0]

    amount_in = 500_000_000_000_000_000

    swap_uniswapv3_disassembler = SwapDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    eth_balance = w3.eth.get_balance(avatar_safe_address)
    assert eth_balance > 0

    wsteth_contract = w3.eth.contract(address=EthereumSwapPools.UniV3_wstETH_ETH.tokens[0], abi=Abis.ERC20.abi)
    wsteth_balance = wsteth_contract.functions.balanceOf(avatar_safe_address).call()
    assert wsteth_balance == 0

    txn_transactable = swap_uniswapv3_disassembler.exit_4(
        percentage=50,
        exit_arguments=[{"token_in_address": token_in, "max_slippage": 1, "token_out_address": token_out}],
        amount_to_redeem=amount_in
    )
    send_it = swap_uniswapv3_disassembler.send(txn_transactable, private_key)

    assert send_it

    wsteth_balance = wsteth_contract.functions.balanceOf(avatar_safe_address).call()
    assert wsteth_balance > 0
