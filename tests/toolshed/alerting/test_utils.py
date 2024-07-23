from web3 import Web3
import defabipedia
from defabipedia.types import Chain

from roles_royce.toolshed.alerting.utils import (
    get_token_amounts_from_transfer_events,
    get_tx_executed_msg,
    get_tx_receipt_message_with_transfers,
    EventLogDecoder,
)
from tests.fork_fixtures import local_node_eth, local_node_gc


def test_get_token_transfers(local_node_eth, local_node_gc):
    local_node_eth.set_block(17877040)
    local_node_gc.set_block(35115012)
    w3_eth = local_node_eth.w3
    w3_gc = local_node_gc.w3

    tx_receipt = w3_eth.eth.get_transaction_receipt(
        "0xfe5e7f623deceea833e7300f1a9b637afcb253cebca0d3968e9190faf1c2cbc4"
    )
    transfers, message = get_token_amounts_from_transfer_events(
        tx_receipt, "0x65389F6FFe361C0C27Ea5D9691616a2060f8a167", w3_eth
    )
    assert transfers == [
        {
            "amount": 0.055,
            "from": "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD",
            "to": "0x65389F6FFe361C0C27Ea5D9691616a2060f8a167",
        },
        {
            "amount": 5992277071.011556,
            "from": "0x65389F6FFe361C0C27Ea5D9691616a2060f8a167",
            "to": "0xBa3B918D8663b9A872E89Fa24b96e2EC77778707",
        },
        {
            "amount": 60528051.22233895,
            "from": "0x65389F6FFe361C0C27Ea5D9691616a2060f8a167",
            "to": "0xff30a1cF914a4a4e3B5514cD167bD2E69607e173",
        },
    ]
    assert message == (
        "  0x65389F6FFe361C0C27Ea5D9691616a2060f8a167  <---- 0.055 WETH -----  "
        "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD.\n"
        "\n"
        "  0x65389F6FFe361C0C27Ea5D9691616a2060f8a167  ----- 5,992,277,071.012 X2.0 ---->  "
        "0xBa3B918D8663b9A872E89Fa24b96e2EC77778707.\n"
        "\n"
        "  0x65389F6FFe361C0C27Ea5D9691616a2060f8a167  ----- 60,528,051.222 X2.0 ---->  "
        "0xff30a1cF914a4a4e3B5514cD167bD2E69607e173.\n"
    )
    message, message_slack = get_tx_executed_msg(tx_receipt, Chain.ETHEREUM)
    assert message == (
        "  Txn hash (Success): "
        "https://etherscan.io/tx/0xfe5e7f623deceea833e7300f1a9b637afcb253cebca0d3968e9190faf1c2cbc4."
    )
    assert message_slack == (
        "  *Txn hash (Success):* "
        "<https://etherscan.io/tx"
        "/0xfe5e7f623deceea833e7300f1a9b637afcb253cebca0d3968e9190faf1c2cbc4"
        "|0xfe5e7f623deceea833e7300f1a9b637afcb253cebca0d3968e9190faf1c2cbc4>."
    )

    message, message_slack = get_tx_receipt_message_with_transfers(
        tx_receipt, "0x65389F6FFe361C0C27Ea5D9691616a2060f8a167", w3_eth
    )
    assert message == (
        "  Txn hash (Success): "
        "https://etherscan.io/tx/0xfe5e7f623deceea833e7300f1a9b637afcb253cebca0d3968e9190faf1c2cbc4.\n"
        "\n"
        "  0x65389F6FFe361C0C27Ea5D9691616a2060f8a167  <---- 0.055 WETH -----  "
        "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD.\n"
        "\n"
        "  0x65389F6FFe361C0C27Ea5D9691616a2060f8a167  ----- 5,992,277,071.012 X2.0 "
        "---->  0xBa3B918D8663b9A872E89Fa24b96e2EC77778707.\n"
        "\n"
        "  0x65389F6FFe361C0C27Ea5D9691616a2060f8a167  ----- 60,528,051.222 X2.0 ---->  "
        "0xff30a1cF914a4a4e3B5514cD167bD2E69607e173.\n"
    )
    assert message_slack == (
        "  *Txn hash (Success):* "
        "<https://etherscan.io/tx"
        "/0xfe5e7f623deceea833e7300f1a9b637afcb253cebca0d3968e9190faf1c2cbc4"
        "|0xfe5e7f623deceea833e7300f1a9b637afcb253cebca0d3968e9190faf1c2cbc4>.\n"
        "\n"
        "  0x65389F6FFe361C0C27Ea5D9691616a2060f8a167  <---- 0.055 WETH -----  "
        "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD.\n"
        "\n"
        "  0x65389F6FFe361C0C27Ea5D9691616a2060f8a167  ----- 5,992,277,071.012 X2.0 "
        "---->  0xBa3B918D8663b9A872E89Fa24b96e2EC77778707.\n"
        "\n"
        "  0x65389F6FFe361C0C27Ea5D9691616a2060f8a167  ----- 60,528,051.222 X2.0 ---->  "
        "0xff30a1cF914a4a4e3B5514cD167bD2E69607e173.\n"
    )

    # THis has to be fixed, we're getting the logs RPC endpoint error...
    tx_receipt = w3_gc.eth.get_transaction_receipt("0x48ac45965d26ef89bf22f0a7b5f7d66f64e6cefaab8e6b3ccf2eeaf3dce49f25")
    transfers, message = get_token_amounts_from_transfer_events(
        tx_receipt, "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f", w3_gc
    )
    assert transfers == [
        {
            "amount": 28623.229796554493,
            "from": "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f",
            "to": "0xD7b118271B1B7d26C9e044Fc927CA31DccB22a5a",
        },
        {
            "amount": 2839.9402939711113,
            "from": "0xE43e60736b1cb4a75ad25240E2f9a62Bff65c0C0",
            "to": "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f",
        },
    ]
    assert message == (
        "  0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f  ----- 28,623.230 DXS ---->  "
        "0xD7b118271B1B7d26C9e044Fc927CA31DccB22a5a.\n"
        "\n"
        "  0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f  <---- 2,839.940 GNO -----  "
        "0xE43e60736b1cb4a75ad25240E2f9a62Bff65c0C0.\n"
    )

    message, message_slack = get_tx_executed_msg(tx_receipt, Chain.GNOSIS)
    assert message == (
        "  Txn hash (Success): "
        "https://gnosisscan.io/tx/0x48ac45965d26ef89bf22f0a7b5f7d66f64e6cefaab8e6b3ccf2eeaf3dce49f25."
    )
    assert message_slack == (
        "  *Txn hash (Success):* "
        "<https://gnosisscan.io/tx"
        "/0x48ac45965d26ef89bf22f0a7b5f7d66f64e6cefaab8e6b3ccf2eeaf3dce49f25"
        "|0x48ac45965d26ef89bf22f0a7b5f7d66f64e6cefaab8e6b3ccf2eeaf3dce49f25>."
    )


def test_decoder(local_node_eth):
    local_node_eth.set_block(19882187)
    w3_eth = local_node_eth.w3
    abi = defabipedia.balancer.ContractSpecs['ethereum'].Vault.abi
    decoder = EventLogDecoder(Web3().eth.contract(abi=abi))

    tx_receipt = w3_eth.eth.get_transaction_receipt("0xf06ca527de1a62ba96d67335bc09b961504aec5db78f83a86576546d7e48f775")

    event = decoder.decode_log(tx_receipt['logs'][4])
    assert event.name == 'PoolBalanceChanged'
    assert event.values == {
        'poolId': b'\xf4\xc0\xdd\x9b\x82\xda6\xc0v\x05\xdf\x83\xc8\xa4\x16\xf1\x17$\xd8\x8b\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00&',
        'liquidityProvider': '0x849D52316331967b6fF1198e5E32A0eB168D039d',
        'tokens': ['0x6810e776880C02933D47DB1b9fc05908e5386b96', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'],
        'deltas': [-18960441620315391058848, -283825508617941472088], 'protocolFeeAmounts': [923065361645970665, 0]
    }
