import json

import pytest
import requests
from defabipedia.lido import ContractSpecs
from defabipedia.types import Chain

from roles_royce.protocols.eth import lido
from roles_royce.roles_modifier import GasStrategies, set_gas_strategy
from roles_royce.toolshed.disassembling import LidoDisassembler
from tests.roles import apply_presets, deploy_roles, setup_common_roles
from tests.utils import create_simple_safe, steal_token
from tests.fork_fixtures import accounts
from tests.fork_fixtures import local_node_eth_replay as local_node_eth
presets = """{
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
      "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84",
      "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x33a0480c0000000000000000000000000000000000000000000000000000000000000004000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84095ea7b300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001200000000000000000000000000000000000000000000000000000000000000140000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
      "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x939337720000000000000000000000000000000000000000000000000000000000000004000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000200000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b1",
      "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x5e82669500000000000000000000000000000000000000000000000000000000000000040000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",
      "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x33a0480c00000000000000000000000000000000000000000000000000000000000000040000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca0095ea7b30000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000140000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000001c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000020000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b1",
      "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b1",
      "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x33a0480c0000000000000000000000000000000000000000000000000000000000000004000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b1d6681042000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000001c00000000000000000000000000000000000000000000000000000000000000220000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000c01318bab7ee1f5ba734172bf7718b5dc6ec90e1",
      "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x33a0480c0000000000000000000000000000000000000000000000000000000000000004000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b119aa6257000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000001c00000000000000000000000000000000000000000000000000000000000000220000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000c01318bab7ee1f5ba734172bf7718b5dc6ec90e1",
      "value": "0"
    },
    {
      "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
      "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b1e3afe0a3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
      "value": "0"
    }
  ]
}"""


def test_integration_exit_1(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = 18421437
    local_node_eth.set_block(block)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=presets,
        replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])],
    )

    blockchain = Chain.get_blockchain_from_web3(w3)
    steal_token(
        w3=w3,
        token=ContractSpecs[blockchain].stETH.address,
        holder="0xE53FFF67f9f384d20Ebea36F43b93DC49Ed22753",
        to=avatar_safe.address,
        amount=8_999_999_999_999_000_000,
    )

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    lido_disassembler = LidoDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe.address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    steth_contract = ContractSpecs[blockchain].stETH.contract(w3)
    steth_balance = steth_contract.functions.balanceOf(avatar_safe_address).call()
    assert steth_balance == 8999999999998999998

    txn_transactable = lido_disassembler.exit_1(percentage=50)
    lido_disassembler.send(txn_transactable, private_key=private_key)
    nft_ids = lido.GetWithdrawalRequests(owner=avatar_safe_address).call(w3)
    assert len(nft_ids) == 1

    steth_balance = steth_contract.functions.balanceOf(avatar_safe_address).call()
    assert steth_balance == 4499999999999500000


def test_integration_exit_2(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = 18710862
    local_node_eth.set_block(block)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)

    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=presets,
        replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])],
    )

    blockchain = Chain.get_blockchain_from_web3(w3)
    steal_token(
        w3=w3,
        token=ContractSpecs[blockchain].wstETH.address,
        holder="0x4dCbB1fE5983ad5b44DC661273a4f11CA812f8B8",
        to=avatar_safe.address,
        amount=8_999_999_999_999_000_000,
    )

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    lido_disassembler = LidoDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe.address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    wsteth_contract = ContractSpecs[blockchain].wstETH.contract(w3)
    wsteth_balance = wsteth_contract.functions.balanceOf(avatar_safe_address).call()
    assert wsteth_balance == 8999999999999000000

    txn_transactable = lido_disassembler.exit_2(percentage=50)
    lido_disassembler.send(txn_transactable, private_key=private_key)
    nft_ids = lido.GetWithdrawalRequests(owner=avatar_safe_address).call(w3)
    assert len(nft_ids) == 1

    wsteth_balance = wsteth_contract.functions.balanceOf(avatar_safe_address).call()
    assert wsteth_balance == 4499999999999500000


preset_cowswap = """{
            "version": "1.0",
            "chainId": "1",
            "meta": {
                "description": "",
                "txBuilderVersion": "1.8.0"
            },
            "createdAt": 1700857590822,
            "transactions": [
                {
                "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
                "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000E522f854b978650Dc838Ade0e39FbC1417A2FfB0",
                "value": "0"
                },
                {
                "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
                "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000E522f854b978650Dc838Ade0e39FbC1417A2FfB0569d3489000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002",
                "value": "0"
                },
                {
                "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
                "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000ae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
                "value": "0"
                },
                {
                "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
                "data": "0x5e82669500000000000000000000000000000000000000000000000000000000000000040000000000000000000000007f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
                "value": "0"
                },
                {
                "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
                "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000ae7ab96520DE3A18E5e111B5EaAb095312D7fE84095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002",
                "value": "0"
                },
                {
                "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
                "data": "0x2fcf52d100000000000000000000000000000000000000000000000000000000000000040000000000000000000000007f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002",
                "value": "0"
                }
            ]
            }"""


def test_integration_exit_3(local_node_eth, accounts, requests_mock):
    requests_mock.real_http = True
    requests_mock.post("https://api.cow.fi/mainnet/api/v1/quote",
                       text=json.dumps({"quote": {"sellToken": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
                                                  "buyToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                                                  "receiver": "0x63972026c0662accd024ab732f8362110031f387",
                                                  "sellAmount": "4496482906023644820",
                                                  "buyAmount": "4489669017177514999", "validTo": 1712883572,
                                                  "appData": "{\"appCode\":\"karpatkey_swap\"}",
                                                  "appDataHash": "0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26",
                                                  "feeAmount": "3517093975855179", "kind": "sell",
                                                  "partiallyFillable": False, "sellTokenBalance": "erc20",
                                                  "buyTokenBalance": "erc20", "signingScheme": "presign"},
                                        "from": "0x63972026c0662accd024ab732f8362110031f387",
                                        "expiration": "2024-04-12T00:31:32.753094749Z", "id": 482551545,
                                        "verified": False}),
                       status_code=200)
    requests_mock.post("https://api.cow.fi/mainnet/api/v1/orders",
                       text='"0x1d49609e1f36a65f7b0993728ef5661dffd89a1ac2dbfbe7a8641a95a504d32a17efb5661e7582f247fbce3693b1f7158acb98146618876d"',
                       status_code=201)
    w3 = local_node_eth.w3
    local_node_eth.set_block(19636004)
    set_gas_strategy(GasStrategies.AGGRESIVE)
    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=preset_cowswap,
        replaces=[("E522f854b978650Dc838Ade0e39FbC1417A2FfB0", "23dA9AdE38E4477b23770DeD512fD37b12381FAB")],
    )

    blockchain = Chain.get_blockchain_from_web3(w3)
    steal_token(
        w3=w3,
        token=ContractSpecs[blockchain].stETH.address,
        holder="0xE53FFF67f9f384d20Ebea36F43b93DC49Ed22753",
        to=avatar_safe.address,
        amount=8_999_999_999_999_000_000,
    )

    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    lido_disassembler = LidoDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe.address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    txn_transactable = lido_disassembler.exit_3(percentage=50, exit_arguments=[{'max_slippage': 1}])
    tx_receipt = lido_disassembler.send(txn_transactable, private_key=private_key)

    assert tx_receipt.status == 1
    for log in tx_receipt.logs:
        if log.address == '0x9008D19f58AAbD9eD0D60971565AA8510560ab41':
            uid_from_tx_log = '0x' + log.data.hex()[194:len(log.data.hex()) - 16]
            break

    assert uid_from_tx_log == '0x1d49609e1f36a65f7b0993728ef5661dffd89a1ac2dbfbe7a8641a95a504d32a17efb5661e7582f247fbce3693b1f7158acb98146618876d'


def test_integration_exit_4(local_node_eth, accounts, requests_mock):
    requests_mock.real_http = True
    requests_mock.post("https://api.cow.fi/mainnet/api/v1/quote",
                       text=json.dumps({"quote": {"sellToken": "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",
                                                  "buyToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                                                  "receiver": "0x3e83a898fcbe5d4a0d3e886b287a8359034a5952",
                                                  "sellAmount": "4498223604396024865",
                                                  "buyAmount": "5225511848017673212", "validTo": 1712885566,
                                                  "appData": "{\"appCode\":\"karpatkey_swap\"}",
                                                  "appDataHash": "0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26",
                                                  "feeAmount": "1776395603475135", "kind": "sell",
                                                  "partiallyFillable": False, "sellTokenBalance": "erc20",
                                                  "buyTokenBalance": "erc20", "signingScheme": "presign"},
                                        "from": "0x3e83a898fcbe5d4a0d3e886b287a8359034a5952",
                                        "expiration": "2024-04-12T01:04:46.868693450Z", "id": 482569777,
                                        "verified": False}),
                       status_code=200)
    requests_mock.post("https://api.cow.fi/mainnet/api/v1/orders",
                       text='"0x59dadaec2dd2b84fc499cc62cf95b244701685c9f58491f4f0dd60cfdb9305733e83a898fcbe5d4a0d3e886b287a8359034a595266188cb7"',
                       status_code=201)
    w3 = local_node_eth.w3
    local_node_eth.set_block(19636004)
    set_gas_strategy(GasStrategies.AGGRESIVE)
    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=preset_cowswap,
        replaces=[("E522f854b978650Dc838Ade0e39FbC1417A2FfB0", "23dA9AdE38E4477b23770DeD512fD37b12381FAB")],
    )

    blockchain = Chain.get_blockchain_from_web3(w3)
    steal_token(
        w3=w3,
        token=ContractSpecs[blockchain].wstETH.address,
        holder="0x5fEC2f34D80ED82370F733043B6A536d7e9D7f8d",
        to=avatar_safe.address,
        amount=8_999_999_999_999_000_000,
    )

    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    lido_disassembler = LidoDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe.address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    txn_transactable = lido_disassembler.exit_4(percentage=50, exit_arguments=[{'max_slippage': 1}])
    tx_receipt = lido_disassembler.send(txn_transactable, private_key=private_key)

    assert tx_receipt.status == 1
    for log in tx_receipt.logs:
        if log.address == '0x9008D19f58AAbD9eD0D60971565AA8510560ab41':
            uid_from_tx_log = '0x' + log.data.hex()[194:len(log.data.hex()) - 16]
            break

    assert uid_from_tx_log == '0x1dee5a48ba7ee0d0603785740bb98969e29619da43977081925f3d9d6ecee17e3e83a898fcbe5d4a0d3e886b287a8359034a595266188cb9'
