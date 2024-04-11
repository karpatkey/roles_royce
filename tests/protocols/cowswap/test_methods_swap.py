import json
from defabipedia.types import Chain
from roles_royce import roles
from roles_royce.protocols.cowswap.methods_swap import create_approve_sign, approve_and_sign
from roles_royce.protocols.cowswap.utils import SwapKind, Order
from tests.roles import apply_presets, deploy_roles, setup_common_roles
from tests.utils import accounts, create_simple_safe, local_node_eth, steal_token


def test_create_approve_sign(local_node_eth, requests_mock):
    requests_mock.real_http = True
    w3 = local_node_eth.w3
    local_node_eth.set_block(19627789)

    avatar_safe = "0x58e6c7ab55Aa9012eAccA16d1ED4c15795669E1C"

    valid_duration = 10 * 60

    sell_token = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    buy_token = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    sell_amount = 784999999999994999997
    kind = "sell"

    requests_mock.post("https://api.cow.fi/mainnet/api/v1/quote",
                       text=json.dumps({"quote": {"sellToken": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
                                                  "buyToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                                                  "receiver": "0x58e6c7ab55aa9012eacca16d1ed4c15795669e1c",
                                                  "sellAmount": "784979836180084865665",
                                                  "buyAmount": "784194345945024902508", "validTo": 1712784934,
                                                  "appData": "{\"appCode\":\"karpatkey_swap\"}",
                                                  "appDataHash": "0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26",
                                                  "feeAmount": "20163819910134332", "kind": "sell",
                                                  "partiallyFillable": False, "sellTokenBalance": "erc20",
                                                  "buyTokenBalance": "erc20", "signingScheme": "presign"},
                                        "from": "0x58e6c7ab55aa9012eacca16d1ed4c15795669e1c",
                                        "expiration": "2024-04-10T21:07:34.875627713Z", "id": 481408144,
                                        "verified": False}),
                       status_code=200)

    requests_mock.post("https://api.cow.fi/mainnet/api/v1/orders",
                       text='"0x529ed6e1ec9ba395c58fca9f20eb2e0a16a4e484082b8a7b824a901142c5d94258e6c7ab55aa9012eacca16d1ed4c15795669e1c66178747"',
                       status_code=201)

    transactables = create_approve_sign(w3=w3,
                                        avatar=avatar_safe,
                                        sell_token=sell_token,
                                        buy_token=buy_token,
                                        amount=sell_amount,
                                        kind=kind,
                                        max_slippage=0.1,
                                        valid_duration=valid_duration)

    assert transactables[
               0].data == '0x095ea7b3000000000000000000000000c92e8bdf79f0507f65a392b0ab4667716bfe011000000000000000000000000000000000000000000000002a8e103ce44957b4bd'
    assert transactables[
               1].data == '0x569d3489000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee00000000000000000000000058e6c7ab55aa9012eacca16d1ed4c15795669e1c00000000000000000000000000000000000000000000002a8e103ce44957b4bd00000000000000000000000000000000000000000000002642982e847eb4000000000000000000000000000000000000000000000000000000000000661700e7ec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e260000000000000000000000000000000000000000000000000000000000000000f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee34677500000000000000000000000000000000000000000000000000000000000000005a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc95a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc900000000000000000000000000000000000000000000000000000000000002580000000000000000000000000000000000000000000000000000000000000000'


def test_approve_and_sign(local_node_eth):
    w3 = local_node_eth.w3
    order = Order(sell_token='0x6B175474E89094C44Da98b954EedeAC495271d0F',
                  buy_token='0x6810e776880C02933D47DB1b9fc05908e5386b96',
                  receiver='0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f',
                  from_address='0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f',
                  sell_amount=985693283370526960312,
                  buy_amount=2731745328645699409,
                  fee_amount=0,
                  valid_to=1712697525,
                  kind=SwapKind.SELL,
                  partially_fillable=False, sell_token_balance='erc20', buy_token_balance='erc20')

    transactables = approve_and_sign(w3=w3, order=order)
    assert transactables[
               0].data == '0x095ea7b3000000000000000000000000c92e8bdf79f0507f65a392b0ab4667716bfe01100000000000000000000000000000000000000000000000356f3e02cc74b5eab8'
    assert transactables[1].data == '0x569d34890000000000000000000000006b175474e89094c44da98b954eedeac495271d0f0000000000000000000000006810e776880c02933d47db1b9fc05908e5386b96000000000000000000000000458cd345b4c05e8df39d0a07220feb4ec19f5e6f0000000000000000000000000000000000000000000000356f3e02cc74b5eab800000000000000000000000000000000000000000000000025e91be72ac27751000000000000000000000000000000000000000000000000000000006615b0b5ec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e260000000000000000000000000000000000000000000000000000000000000000f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee34677500000000000000000000000000000000000000000000000000000000000000005a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc95a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc900000000000000000000000000000000000000000000000000000000000002580000000000000000000000000000000000000000000000000000000000000000'

