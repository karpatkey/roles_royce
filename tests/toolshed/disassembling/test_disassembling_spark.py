from decimal import Decimal
import json

from roles_royce.constants import ETHAddr
from roles_royce.protocols.eth import spark
from roles_royce.toolshed.protocol_utils.spark.utils import SparkUtils
from roles_royce.toolshed.disassembling import SparkDisassembler
from roles_royce.roles_modifier import GasStrategies, set_gas_strategy

from defabipedia.types import Chain
from defabipedia.spark import ContractSpecs

from tests.roles import apply_presets, deploy_roles, setup_common_roles
from tests.utils import create_simple_safe, get_balance, steal_token, top_up_address
from tests.fork_fixtures import accounts
from tests.fork_fixtures import local_node_eth_replay as local_node_eth, local_node_gc



def test_integration_1(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = 19917381
    local_node_eth.set_block(block)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    blockchain = Chain.get_blockchain_from_web3(w3)
    presets = """{"version": "1.0","chainId": "1","meta":{ "description": "","txBuilderVersion": "1.8.0"},"createdAt": 1695904723785,"transactions": [
        {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
        "data": "0x5e826695000000000000000000000000000000000000000000000000000000000000000400000000000000000000000083F20F44975D03b1b09e64809B757c47f942BEeA",
        "value": "0"},
        {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
        "data": "0x2fcf52d1000000000000000000000000000000000000000000000000000000000000000400000000000000000000000083F20F44975D03b1b09e64809B757c47f942BEeAba087652000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "value": "0"}
    ]}"""

    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=presets,
        replaces=[
            ("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])
        ],
    )
    DAIER = "0xfE9fE2eF61faF6E291b06903dFf85DF25a989498"
    steal_token(w3, ETHAddr.DAI, holder=DAIER, to=avatar_safe.address, amount=1_000)
    # Deposit DAI, get sDAI
    avatar_safe.send(
        [
            spark.ApproveDAIforSDAI(amount=1_000),
            spark.DepositDAIforSDAI(blockchain=blockchain, amount=1_000, avatar=avatar_safe.address)
        ]
    )
    assert get_balance(w3, ETHAddr.DAI, avatar_safe.address) == 0
    chi = SparkUtils.get_chi(w3)
    assert get_balance(w3, ETHAddr.sDAI, avatar_safe.address) == int(Decimal(1_000) / (Decimal(chi) / Decimal(1e27)))  # 976

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    dsr_disassembler = SparkDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    txn_transactable = dsr_disassembler.exit_1(percentage=50)
    dsr_disassembler.send(txn_transactable, private_key=private_key)

    assert get_balance(w3, ETHAddr.sDAI, avatar_safe.address) == 461

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
                "data": "0x5e826695000000000000000000000000000000000000000000000000000000000000000400000000000000000000000083F20F44975D03b1b09e64809B757c47f942BEeA",
                "value": "0"
                },
                {
                "to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
                "data": "0x2fcf52d1000000000000000000000000000000000000000000000000000000000000000400000000000000000000000083F20F44975D03b1b09e64809B757c47f942BEeA095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002",
                "value": "0"
                }
            ]
            }"""

def test_integration_exit_2(local_node_eth, accounts, requests_mock):
    requests_mock.real_http = True
    requests_mock.post("https://api.cow.fi/mainnet/api/v1/quote",
                       text=json.dumps({"quote": {"sellToken": "0x83F20F44975D03b1b09e64809B757c47f942BEeA",
                                                  "buyToken": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
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
    local_node_eth.set_block(20045539)
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
        token=ContractSpecs[blockchain].sDAI.address,
        holder="0x7d3dF6DC59992463F4776214F93bD70EF6ed11EE",
        to=avatar_safe.address,
        amount=8_999_999_999_999_000_000,
    )

    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    spark_disassembler = SparkDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe.address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    txn_transactable = spark_disassembler.exit_2(percentage=50, exit_arguments=[{'max_slippage': 1}])
    tx_receipt = spark_disassembler.send(txn_transactable, private_key=private_key)

    assert tx_receipt.status == 1
    for log in tx_receipt.logs:
        if log.address == '0x9008D19f58AAbD9eD0D60971565AA8510560ab41':
            uid_from_tx_log = '0x' + log.data.hex()[194:len(log.data.hex()) - 16]
            break

    assert uid_from_tx_log == '0xbf949c5371467eae17cc6a1a33fd9a0e670e43f71da22c65886b0f1f89a7bce86fa4080e06fdbd826426746d0121f9947fe7893f66640913'

