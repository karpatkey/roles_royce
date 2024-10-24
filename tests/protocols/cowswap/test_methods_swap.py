import json

from defabipedia.types import Chain
from karpatkit.test_utils.fork import accounts, create_simple_safe
from karpatkit.test_utils.fork import local_node_eth_replay as local_node_eth

from roles_royce import roles
from roles_royce.protocols.cowswap.methods_swap import create_order_and_swap, swap
from roles_royce.protocols.cowswap.utils import Order, SwapKind, quote_order_api
from roles_royce.toolshed.test_utils.roles_fork_utils import apply_roles_presets, deploy_roles, setup_common_roles


def test_create_order_and_swap(local_node_eth, requests_mock):
    requests_mock.real_http = True
    w3 = local_node_eth.w3
    local_node_eth.set_block(19627789)

    avatar_safe = "0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C"

    valid_duration = 10 * 60

    sell_token = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    buy_token = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    sell_amount = 784999999999994999997
    kind = "sell"

    requests_mock.post(
        "https://api.cow.fi/mainnet/api/v1/quote",
        text=json.dumps(
            {
                "quote": {
                    "sellToken": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
                    "buyToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                    "receiver": "0x58e6c7ab55aa9012eacca16d1ed4c15795669e1c",
                    "sellAmount": "784979836180084865665",
                    "buyAmount": "784194345945024902508",
                    "validTo": 1712784934,
                    "appData": '{"appCode":"karpatkey_swap"}',
                    "appDataHash": "0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26",
                    "feeAmount": "20163819910134332",
                    "kind": "sell",
                    "partiallyFillable": False,
                    "sellTokenBalance": "erc20",
                    "buyTokenBalance": "erc20",
                    "signingScheme": "presign",
                },
                "from": "0x58e6c7ab55aa9012eacca16d1ed4c15795669e1c",
                "expiration": "2024-04-10T21:07:34.875627713Z",
                "id": 481408144,
                "verified": False,
            }
        ),
        status_code=200,
    )

    requests_mock.post(
        "https://api.cow.fi/mainnet/api/v1/orders",
        text='"0x529ed6e1ec9ba395c58fca9f20eb2e0a16a4e484082b8a7b824a901142c5d94258e6c7ab55aa9012eacca16d1ed4c15795669e1c66178747"',
        status_code=201,
    )

    transactables = create_order_and_swap(
        blockchain=Chain.ETHEREUM,
        avatar=avatar_safe,
        sell_token=sell_token,
        buy_token=buy_token,
        amount=sell_amount,
        kind=kind,
        max_slippage=0.1,
        valid_duration=valid_duration,
    )

    assert (
        transactables[0].data
        == "0x095ea7b3000000000000000000000000c92e8bdf79f0507f65a392b0ab4667716bfe011000000000000000000000000000000000000000000000002a8e103ce44957b4bd"
    )
    assert (
        transactables[1].data
        == "0x569d3489000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee00000000000000000000000058e6c7ab55aa9012eacca16d1ed4c15795669e1c00000000000000000000000000000000000000000000002a8e103ce44957b4bd00000000000000000000000000000000000000000000002642982e847eb4000000000000000000000000000000000000000000000000000000000000661700e7ec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e260000000000000000000000000000000000000000000000000000000000000000f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee34677500000000000000000000000000000000000000000000000000000000000000005a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc95a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc900000000000000000000000000000000000000000000000000000000000004b00000000000000000000000000000000000000000000000000000000000000000"
    )


def test_swap(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(19627789)
    order = Order(
        sell_token="0x6B175474E89094C44Da98b954EedeAC495271d0F",
        buy_token="0x6810e776880C02933D47DB1b9fc05908e5386b96",
        receiver="0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f",
        from_address="0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f",
        sell_amount=985693283370526960312,
        buy_amount=2731745328645699409,
        fee_amount=0,
        valid_to=1712697525,
        kind=SwapKind.SELL,
        partially_fillable=False,
        sell_token_balance="erc20",
        buy_token_balance="erc20",
    )

    transactables = swap(w3=w3, order=order)
    assert (
        transactables[0].data
        == "0x095ea7b3000000000000000000000000c92e8bdf79f0507f65a392b0ab4667716bfe01100000000000000000000000000000000000000000000000356f3e02cc74b5eab8"
    )
    assert (
        transactables[1].data
        == "0x569d34890000000000000000000000006b175474e89094c44da98b954eedeac495271d0f0000000000000000000000006810e776880c02933d47db1b9fc05908e5386b96000000000000000000000000458cd345b4c05e8df39d0a07220feb4ec19f5e6f0000000000000000000000000000000000000000000000356f3e02cc74b5eab800000000000000000000000000000000000000000000000025e91be72ac27751000000000000000000000000000000000000000000000000000000006615b0b5ec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e260000000000000000000000000000000000000000000000000000000000000000f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee34677500000000000000000000000000000000000000000000000000000000000000005a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc95a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc900000000000000000000000000000000000000000000000000000000000002580000000000000000000000000000000000000000000000000000000000000000"
    )


def test_integration_create_order_and_swap(local_node_eth, accounts, requests_mock):
    requests_mock.real_http = True
    w3 = local_node_eth.w3
    local_node_eth.set_block(19627933)
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

    apply_roles_presets(
        avatar_safe,
        roles_contract,
        json_data=presets,
        replaces=[("E522f854b978650Dc838Ade0e39FbC1417A2FfB0", "23dA9AdE38E4477b23770DeD512fD37b12381FAB")],
    )

    avatar_safe_address = avatar_safe.address
    private_key = accounts[4].key
    role = 4

    sell_token = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    buy_token = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    sell_amount = 4499999999999499999
    kind = "sell"

    requests_mock.post(
        "https://api.cow.fi/mainnet/api/v1/quote",
        text=json.dumps(
            {
                "quote": {
                    "sellToken": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
                    "buyToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                    "receiver": "0x01b1214ecf83ff63b12e18b05b3db84cae375635",
                    "sellAmount": "4494365075127968832",
                    "buyAmount": "4490141191271109775",
                    "validTo": 1712786610,
                    "appData": '{"appCode":"karpatkey_swap"}',
                    "appDataHash": "0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26",
                    "feeAmount": "5634924871531167",
                    "kind": "sell",
                    "partiallyFillable": False,
                    "sellTokenBalance": "erc20",
                    "buyTokenBalance": "erc20",
                    "signingScheme": "presign",
                },
                "from": "0x01b1214ecf83ff63b12e18b05b3db84cae375635",
                "expiration": "2024-04-10T21:35:30.813459830Z",
                "id": 481431436,
                "verified": False,
            }
        ),
        status_code=200,
    )
    requests_mock.post(
        "https://api.cow.fi/mainnet/api/v1/orders",
        text='"0xf356250a165178a8128d943f1df212f696c17f4b4d306dd9891a1f66197157b601b1214ecf83ff63b12e18b05b3db84cae375635661791f9"',
        status_code=201,
    )

    valid_duration = 10 * 60 * 60
    max_slippage = 0.1

    transactables = create_order_and_swap(
        blockchain=Chain.ETHEREUM,
        avatar=avatar_safe_address,
        sell_token=sell_token,
        buy_token=buy_token,
        amount=sell_amount,
        kind=kind,
        max_slippage=max_slippage,
        valid_duration=valid_duration,
    )

    tx_receipt = roles.send(
        txs=transactables, role=role, private_key=private_key, roles_mod_address=roles_contract.address, web3=w3
    )

    assert tx_receipt.status == 1
    for log in tx_receipt.logs:
        if log.address == "0x9008D19f58AAbD9eD0D60971565AA8510560ab41":
            uid_from_tx_log = "0x" + log.data.hex()[194 : len(log.data.hex()) - 16]
            break
    assert (
        uid_from_tx_log
        == "0xf9524f70c501fa1d356de72d3b75c9aafb5eeebb771f1b01e04dfdbe8144a53501b1214ecf83ff63b12e18b05b3db84cae375635661791fa"
        or "0xf356250a165178a8128d943f1df212f696c17f4b4d306dd9891a1f66197157b601b1214ecf83ff63b12e18b05b3db84cae375635661791f9"
    )
    # w3.eth.get_block('latest').timestamp may return different things on run time


def test_integration_swap(local_node_eth, accounts, requests_mock):
    requests_mock.real_http = True
    w3 = local_node_eth.w3
    local_node_eth.set_block(19627933)
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

    apply_roles_presets(
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

    requests_mock.post(
        "https://api.cow.fi/mainnet/api/v1/quote",
        text=json.dumps(
            {
                "quote": {
                    "sellToken": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
                    "buyToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                    "receiver": "0x01b1214ecf83ff63b12e18b05b3db84cae375635",
                    "sellAmount": "4494365075127968832",
                    "buyAmount": "4490141191271109775",
                    "validTo": 1712786610,
                    "appData": '{"appCode":"karpatkey_swap"}',
                    "appDataHash": "0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26",
                    "feeAmount": "5634924871531167",
                    "kind": "sell",
                    "partiallyFillable": False,
                    "sellTokenBalance": "erc20",
                    "buyTokenBalance": "erc20",
                    "signingScheme": "presign",
                },
                "from": "0x01b1214ecf83ff63b12e18b05b3db84cae375635",
                "expiration": "2024-04-10T21:35:30.813459830Z",
                "id": 481431436,
                "verified": False,
            }
        ),
        status_code=200,
    )
    order = quote_order_api(
        blockchain=blockchain,
        sell_token=sell_token,
        buy_token=buy_token,
        receiver=avatar_safe_address,
        from_address=avatar_safe_address,
        kind=kind,
        amount=sell_amount,
    )

    valid_duration = 10 * 60 * 60
    # In the order signer contract: require(block.timestamp + validDuration > order.validTo,"Dishonest valid duration");
    # and w3.eth.get_block('latest').timestamp is approximately 1712784730 (sometimes it is 1712784731, etc.)
    valid_to = 1712784730 + valid_duration - 1000
    order.valid_to = valid_to  # quote_order_api returns an Order with valid_to=0

    sign_order_transactables = swap(w3, order, valid_duration)

    tx_receipt = roles.send(
        txs=sign_order_transactables,
        role=role,
        private_key=private_key,
        roles_mod_address=roles_contract.address,
        web3=w3,
    )

    assert tx_receipt.status == 1
    for log in tx_receipt.logs:
        if log.address == "0x9008D19f58AAbD9eD0D60971565AA8510560ab41":
            uid_from_tx_log = "0x" + log.data.hex()[194 : len(log.data.hex()) - 16]
            break
    assert (
        uid_from_tx_log
        == "0x6c9fbbe347d133956af1e2fcf0b1adede666faec6198cfecb96d9f292de2e60e01b1214ecf83ff63b12e18b05b3db84cae37563566178e12"
    )
