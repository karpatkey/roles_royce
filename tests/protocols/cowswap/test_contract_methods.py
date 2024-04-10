from defabipedia.types import Chain
from roles_royce import roles
from roles_royce.protocols.cowswap.contract_methods import SignOrder
from roles_royce.protocols.cowswap.utils import create_order_api, quote_order_api
from tests.roles import apply_presets, deploy_roles, setup_common_roles
from tests.utils import accounts, create_simple_safe, local_node_eth


def test_sign_order():
    avatar_safe = "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f"

    sell_token = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    buy_token = "0x6810e776880C02933D47DB1b9fc05908e5386b96"
    buy_amount = 1000000000000000000
    sell_amount = 999749122606373987000
    fee_amount = 7639801273
    kind = "sell"
    valid_to = 1712696625 + 10 * 60

    signer_tx = SignOrder(
        blockchain=Chain.ETHEREUM,
        avatar=avatar_safe,
        sell_token=sell_token,
        buy_token=buy_token,
        sell_amount=sell_amount,
        buy_amount=buy_amount,
        fee_amount=fee_amount,
        valid_to=valid_to,
        valid_duration=10 * 60,
        kind=kind,
    )

    assert (
            signer_tx.data
            == "0x569d34890000000000000000000000006b175474e89094c44da98b954eedeac495271d0f0000000000000000000000006810e776880c02933d47db1b9fc05908e5386b96000000000000000000000000458cd345b4c05e8df39d0a07220feb4ec19f5e6f000000000000000000000000000000000000000000000036324e621e9cbd00710000000000000000000000000000000000000000000000000de0b6b3a7640000000000000000000000000000000000000000000000000000000000006615af89ec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e260000000000000000000000000000000000000000000000000000000000000000f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee34677500000000000000000000000000000000000000000000000000000000000000005a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc95a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc900000000000000000000000000000000000000000000000000000000000002580000000000000000000000000000000000000000000000000000000000000000"
    )


def test_integration_sign_order(local_node_eth, accounts):
    w3 = local_node_eth.w3
    local_node_eth.set_block(19622768)
    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
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
    private_key = accounts[4].key
    role = 4

    sell_token = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    buy_token = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    sell_amount = 4499999999999499999
    kind = "sell"

    order = quote_order_api(
        blockchain=blockchain,
        sell_token=sell_token,
        buy_token=buy_token,
        receiver=avatar_safe_address,
        from_address=avatar_safe_address,
        kind=kind,
        amount=sell_amount,
    )

    valid_duration = 1 * 60 * 60
    # require(block.timestamp + validDuration > order.validTo,"Dishonest valid duration");
    valid_to = w3.eth.get_block('latest').timestamp + valid_duration - 1

    response_create_order = create_order_api(
        blockchain=blockchain,
        sell_token=order.sell_token,
        buy_token=order.buy_token,
        receiver=order.receiver,
        from_address=order.from_address,
        kind=order.kind,
        amount=order.sell_amount,
        valid_to=valid_to)

    sign_order_transactable = SignOrder(
        blockchain=blockchain,
        avatar=avatar_safe_address,
        sell_token=sell_token,
        buy_token=buy_token,
        sell_amount=sell_amount,
        buy_amount=order.buy_amount,
        fee_amount=order.fee_amount,
        valid_to=valid_to,
        valid_duration=valid_duration,
        kind=kind,
    )

    tx_receipt = roles.send(
        [sign_order_transactable], role=role, private_key=private_key, roles_mod_address=roles_contract.address, web3=w3
    )

    assert tx_receipt.status == 1
    uid_from_tx_log = '0x' + tx_receipt.logs[1].data.hex()[192:len(tx_receipt.logs[1].data.hex())-16]

    assert uid_from_tx_log == response_create_order["UID"]

    1 + 1
