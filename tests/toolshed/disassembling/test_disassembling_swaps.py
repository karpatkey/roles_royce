import json
import requests

from defabipedia.types import Chain
from defabipedia.rocket_pool import ContractSpecs
from defabipedia.swap_pools import EthereumSwapPools
from defabipedia.tokens import Abis
from roles_royce.protocols.eth import lido
from roles_royce.toolshed.disassembling import SwapDisassembler
from roles_royce.roles_modifier import GasStrategies, set_gas_strategy

from tests.utils import (local_node_eth, accounts, create_simple_safe, steal_token)
from tests.roles import setup_common_roles, deploy_roles, apply_presets

ROLE = 4
AVATAR = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
ROLES_MOD = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"

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
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000ae78736Cd615f374D3085123A210448E74Fc6393",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000ae78736Cd615f374D3085123A210448E74Fc6393095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
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

#TODO: add tests for exit strategies

def test_integration_exit_1(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = w3.eth.default_block
    local_node_eth.set_block(block)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    apply_presets(avatar_safe, roles_contract, json_data=presets_balancer,
                  replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])])
    
    blockchain = Chain.get_blockchain_from_web3(w3)
    steal_token(w3=w3, token=EthereumSwapPools.bal_rETH_WETH.tokens[0], holder="0xB3668730E4a8ABe282a6d471c75Baf75557FfFf3",
                to=avatar_safe.address, amount=8_999_999_999_999_000_000)
    
    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    token_in = EthereumSwapPools.bal_rETH_WETH.tokens[0]
    token_out = EthereumSwapPools.bal_rETH_WETH.tokens[1]

    amount_in = 1_000_000_000_000_000_000

    swap_balancer_disassembler = SwapDisassembler(w3=w3,
                                                  avatar_safe_address=avatar_safe_address,
                                                  roles_mod_address=roles_contract.address,
                                                  role=role,
                                                  signer_address=disassembler_address)

    reth_contract = ContractSpecs[blockchain].rETH.contract(w3)
    reth_balance = reth_contract.functions.balanceOf(avatar_safe_address).call()
    assert reth_balance == 8_999_999_999_999_000_000

    weth_contract = w3.eth.contract(address=EthereumSwapPools.bal_rETH_WETH.tokens[1], abi=Abis.ERC20.abi)
    weth_balance = weth_contract.functions.balanceOf(avatar_safe_address).call()
    assert weth_balance == 0

    txn_transactable = swap_balancer_disassembler.exit_1(percentage=50,
                                                         exit_arguments=[{"token_in_address": token_in,
                                                                         "max_slippage": 1,
                                                                         "token_out_address": token_out}])
    send_it = swap_balancer_disassembler.send(txn_transactable, private_key)

    assert send_it   

    weth_balance = weth_contract.functions.balanceOf(avatar_safe_address).call()
    assert weth_balance > 0


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
    "data": "0x5e82669500000000000000000000000000000000000000000000000000000000000000040000000000000000000000006b175474e89094c44da98b954eedeac495271d0f",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d100000000000000000000000000000000000000000000000000000000000000040000000000000000000000006b175474e89094c44da98b954eedeac495271d0f095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000bebc44782c7db0a1a60cb6fe97d0b483032ff1c7",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000bebc44782c7db0a1a60cb6fe97d0b483032ff1c73df02124000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "value": "0"
    }
]
}"""

#TODO: add tests for exit strategies

def test_integration_exit_2(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = w3.eth.default_block
    local_node_eth.set_block(block)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    apply_presets(avatar_safe, roles_contract, json_data=presets_curve,
                  replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])])
    
    blockchain = Chain.get_blockchain_from_web3(w3)
    steal_token(w3=w3, token=EthereumSwapPools.TriPool.tokens[0], holder="0xfE175398f22f267Ea8f5718e5848ef1e0047bF32",
                to=avatar_safe.address, amount=8_999_999_999_999_000_000)
    
    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    token_in = EthereumSwapPools.TriPool.tokens[0]
    token_out = EthereumSwapPools.TriPool.tokens[1]

    amount_in = 1_000_000_000_000_000_000

    swap_curve_disassembler = SwapDisassembler(w3=w3,
                                                  avatar_safe_address=avatar_safe_address,
                                                  roles_mod_address=roles_contract.address,
                                                  role=role,
                                                  signer_address=disassembler_address)

    dai_contract = w3.eth.contract(address=EthereumSwapPools.TriPool.tokens[0], abi=Abis.ERC20.abi)
    dai_balance = dai_contract.functions.balanceOf(avatar_safe_address).call()
    assert dai_balance == 8_999_999_999_999_000_000

    usdc_contract = w3.eth.contract(address=EthereumSwapPools.TriPool.tokens[1], abi=Abis.ERC20.abi)
    usdc_balance = usdc_contract.functions.balanceOf(avatar_safe_address).call()
    assert usdc_balance == 0

    txn_transactable = swap_curve_disassembler.exit_2(percentage=50,
                                                         exit_arguments=[{"token_in_address": token_in,
                                                                         "max_slippage": 1,
                                                                         "token_out_address": token_out}])
    send_it = swap_curve_disassembler.send(txn_transactable, private_key)

    assert send_it   

    usdc_balance = usdc_contract.functions.balanceOf(avatar_safe_address).call()
    assert usdc_balance > 0

presets_uniswapv3 = """{
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
    "data": "0x5e82669500000000000000000000000000000000000000000000000000000000000000040000000000000000000000006b175474e89094c44da98b954eedeac495271d0f",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d100000000000000000000000000000000000000000000000000000000000000040000000000000000000000006b175474e89094c44da98b954eedeac495271d0f095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e82669500000000000000000000000000000000000000000000000000000000000000040000000000000000000000006c6Bc977E13Df9b0de53b251522280BB72383700",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d100000000000000000000000000000000000000000000000000000000000000040000000000000000000000006c6Bc977E13Df9b0de53b251522280BB72383700128acb08000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000e592427a0aece92de3edee1f18e0157c05861564",
    "value": "0"
    },
    {
    "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
    "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000e592427a0aece92de3edee1f18e0157c05861564414bf389000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002",
    "value": "0"
    }
]
}"""

#TODO: add tests for exit strategies

def test_integration_exit_3(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = w3.eth.default_block
    local_node_eth.set_block(block)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    apply_presets(avatar_safe, roles_contract, json_data=presets_uniswapv3,
                  replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])])
    
    blockchain = Chain.get_blockchain_from_web3(w3)
    steal_token(w3=w3, token=EthereumSwapPools.UniV3_DAI_USDC.tokens[0], holder="0xfE175398f22f267Ea8f5718e5848ef1e0047bF32",
                to=avatar_safe.address, amount=8_999_999_999_999_000_000)
    
    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    token_in = EthereumSwapPools.UniV3_DAI_USDC.tokens[0]
    token_out = EthereumSwapPools.UniV3_DAI_USDC.tokens[1]

    amount_in = 1_000_000_000_000_000_000

    swap_uniswapv3_disassembler = SwapDisassembler(w3=w3,
                                                  avatar_safe_address=avatar_safe_address,
                                                  roles_mod_address=roles_contract.address,
                                                  role=role,
                                                  signer_address=disassembler_address)

    dai_contract = w3.eth.contract(address=EthereumSwapPools.UniV3_DAI_USDC.tokens[0], abi=Abis.ERC20.abi)
    dai_balance = dai_contract.functions.balanceOf(avatar_safe_address).call()
    assert dai_balance == 8_999_999_999_999_000_000

    usdc_contract = w3.eth.contract(address=EthereumSwapPools.UniV3_DAI_USDC.tokens[1], abi=Abis.ERC20.abi)
    usdc_balance = usdc_contract.functions.balanceOf(avatar_safe_address).call()
    assert usdc_balance == 0

    txn_transactable = swap_uniswapv3_disassembler.exit_3(percentage=50,
                                                         exit_arguments=[{"token_in_address": token_in,
                                                                         "max_slippage": 1,
                                                                         "token_out_address": token_out}])
    send_it = swap_uniswapv3_disassembler.send(txn_transactable, private_key)

    assert send_it   

    usdc_balance = usdc_contract.functions.balanceOf(avatar_safe_address).call()
    assert usdc_balance > 0