import json
from time import time

import pytest
import requests
from defabipedia.types import Chain

from roles_royce import roles
from roles_royce.protocols.cowswap.contract_methods import SignOrder
from roles_royce.protocols.cowswap.utils import QuoteOrderCowSwap
from tests.roles import apply_presets, deploy_roles, setup_common_roles
from tests.utils import accounts, create_simple_safe, local_node_eth


def test_quote_order_cowswap():
    avatar_safe = "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f"
    sell_token = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    buy_token = "0x6810e776880C02933D47DB1b9fc05908e5386b96"
    sell_amount = 999749122606373987000
    kind = "sell"

    signer_tx = QuoteOrderCowSwap(
        blockchain=Chain.ETHEREUM,
        sell_token=sell_token,
        buy_token=buy_token,
        receiver=avatar_safe,
        kind=kind,
        sell_amount=sell_amount,
    )

    assert len(signer_tx.response) == 5


def test_cowswap_signer_v1():
    avatar_safe = "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f"

    sell_token = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    buy_token = "0x6810e776880C02933D47DB1b9fc05908e5386b96"
    buy_amount = 1000000000000000000
    sell_amount = 999749122606373987000
    kind = "sell"
    valid_to = 1707000000

    signer_tx = SignOrder(
        blockchain=Chain.ETHEREUM,
        avatar=avatar_safe,
        sell_token=sell_token,
        buy_token=buy_token,
        sell_amount=sell_amount,
        buy_amount=buy_amount,
        valid_to=valid_to,
        kind=kind,
    )

    assert (
        signer_tx.data
        == "0x569d34890000000000000000000000006b175474e89094c44da98b954eedeac495271d0f0000000000000000000000006810e776880c02933d47db1b9fc05908e5386b96000000000000000000000000458cd345b4c05e8df39d0a07220feb4ec19f5e6f000000000000000000000000000000000000000000000036324e621cd55ee2b80000000000000000000000000000000000000000000000000de0b6b3a76400000000000000000000000000000000000000000000000000000000000065bec0c0970eb15ab11f171c843c2d1fa326b7f8f6bf06ac7f84bb1affcc86511c783f120000000000000000000000000000000000000000000000000000000000000000f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee34677500000000000000000000000000000000000000000000000000000000000000005a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc95a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc900000000000000000000000000000000000000000000000000000000000007080000000000000000000000000000000000000000000000000000000000000000"
    )


# FIXME: This has to be fixed with a mock"
@pytest.mark.skip(reason="FIXME: This has to be fixed with a mock")
def test_cowswap_signer(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = w3.eth.default_block
    local_node_eth.set_block(block)
    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    # steal_token(w3,"0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6", "0x4D8027E6e6e3E1Caa9AC23267D10Fb7d20f85A37", avatar_safe.address, 100)
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    presets = """{
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
                "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000ae7ab96520DE3A18E5e111B5EaAb095312D7fE84095ea7b3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002",
                "value": "0"
                }
            ]
            }"""

    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=presets,
        replaces=[("E522f854b978650Dc838Ade0e39FbC1417A2FfB0", "23dA9AdE38E4477b23770DeD512fD37b12381FAB")],
    )

    blockchain = Chain.get_blockchain_from_web3(w3)

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    sell_token = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    buy_token = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    sell_amount = 4499999999999499999
    kind = "sell"
    valid_to = int(int(time()) + 600)

    quote_tx = QuoteOrderCowSwap(
        blockchain=blockchain,
        sell_token=sell_token,
        buy_token=buy_token,
        receiver=avatar_safe_address,
        kind=kind,
        sell_amount=sell_amount,
    )

    buy_amount = quote_tx.buy_amount
    fee_amount = quote_tx.fee_amount

    signer_tx = SignOrder(
        blockchain=blockchain,
        avatar=avatar_safe_address,
        sell_token=sell_token,
        buy_token=buy_token,
        sell_amount=sell_amount,
        buy_amount=buy_amount,
        valid_to=valid_to,
        kind=kind,
    )

    checking = roles.send(
        [signer_tx], role=role, private_key=private_key, roles_mod_address=roles_contract.address, web3=w3
    )

    assert checking

    cow_api_address = "https://api.cow.fi/mainnet/api/v1/orders"
    send_order_api = {
        "sellToken": signer_tx.args_list[0][0],
        "buyToken": signer_tx.args_list[0][1],
        "receiver": signer_tx.args_list[0][2],
        "sellAmount": str(signer_tx.args_list[0][3]),
        "buyAmount": str(signer_tx.args_list[0][4]),
        "validTo": signer_tx.args_list[0][5],
        "feeAmount": str(signer_tx.args_list[0][7]),
        "kind": kind,
        "partiallyFillable": False,
        "sellTokenBalance": "erc20",
        "buyTokenBalance": "erc20",
        "signingScheme": "presign",
        "signature": "0x",
        "from": signer_tx.args_list[0][2],
        "appData": json.dumps({"appCode": "santi_the_best"}),
        "appDataHash": "0x970eb15ab11f171c843c2d1fa326b7f8f6bf06ac7f84bb1affcc86511c783f12",
    }

    send_order = requests.post(cow_api_address, json=send_order_api)
    assert send_order.status_code == 201
