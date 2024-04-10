import json
from defabipedia.types import Chain
from roles_royce import roles
from roles_royce.protocols.cowswap.contract_methods import SignOrder
from roles_royce.protocols.cowswap.utils import QuoteOrderCowSwap
from roles_royce.protocols.cowswap.methods_swap import CowSwap
from tests.roles import apply_presets, deploy_roles, setup_common_roles
from tests.utils import accounts, create_simple_safe, local_node_eth, steal_token
from unittest import mock


@mock.patch('time.time', mock.MagicMock(return_value=1712696625))
def test_cowswap(local_node_eth, requests_mock):
    w3 = local_node_eth.w3
    requests_mock.real_http = True

    avatar_safe = "0x849D52316331967b6fF1198e5E32A0eB168D039d"

    sell_token = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    buy_token = "0x6810e776880C02933D47DB1b9fc05908e5386b96"
    sell_amount = 999749122606373987000
    kind = "sell"
    valid_duration = 10 * 60

    requests_mock.post("https://api.cow.fi/mainnet/api/v1/quote",
                       text=json.dumps({
                           "expiration": "2024-04-09T19:25:13.178481047Z",
                           "from": "0x458cd345b4c05e8df39d0a07220feb4ec19f5e6f",
                           "id": 480076131,
                           "quote": {
                               "appData": "{\" appCode \":\"karpatkey_swap \"}",
                               "appDataHash": "0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26",
                               "buyAmount": "2675007315318953013",
                               "buyToken": "0x6810e776880c02933d47db1b9fc05908e5386b96",
                               "buyTokenBalance": "erc20",
                               "feeAmount": "25500869445527609344",
                               "kind": "sell",
                               "partiallyFillable": False,
                               "receiver": "0x458cd345b4c05e8df39d0a07220feb4ec19f5e6f",
                               "sellAmount": "974248253160846377656",
                               "sellToken": "0x6b175474e89094c44da98b954eedeac495271d0f",
                               "sellTokenBalance": "erc20",
                               "signingScheme": "eip712",
                               "validTo": 1712692393
                           },
                           "verified": False
                       }),
                       status_code=200)

    transactables = CowSwap(w3=w3,
                            avatar=avatar_safe,
                            sell_token=sell_token,
                            buy_token=buy_token,
                            amount=sell_amount,
                            receiver=avatar_safe,
                            kind=kind,
                            max_slippage=0.1,
                            valid_duration=valid_duration)

    assert transactables[0].data == '0x095ea7b3000000000000000000000000c92e8bdf79f0507f65a392b0ab4667716bfe0110000000000000000000000000000000000000000000000036324e621cd55ee2b8'
    assert transactables[1].data == '0x569d34890000000000000000000000006b175474e89094c44da98b954eedeac495271d0f0000000000000000000000006810e776880c02933d47db1b9fc05908e5386b96000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000036324e621cd55ee2b800000000000000000000000000000000000000000000000021692e7b810ab200000000000000000000000000000000000000000000000000000000006615af89ec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e260000000000000000000000000000000000000000000000000000000000000000f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee34677500000000000000000000000000000000000000000000000000000000000000005a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc95a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc900000000000000000000000000000000000000000000000000000000000002580000000000000000000000000000000000000000000000000000000000000000'


@mock.patch('time.time', mock.MagicMock(return_value=1712707533))
def test_cow(local_node_eth, accounts):
    w3 = local_node_eth.w3
    local_node_eth.set_block(19621518)
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

    avatar_safe = avatar_safe.address
    private_key = accounts[4].key
    role = 4

    sell_token = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    buy_token = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    sell_amount = 4499999999999499999
    kind = "sell"

    ADDRESS_WITH_LOTS_OF_STETH ='0x18709E89BD403F470088aBDAcEbE86CC60dda12e'

    steal_token(w3, sell_token, ADDRESS_WITH_LOTS_OF_STETH, avatar_safe, 4499999999999499999)

    transactables = CowSwap(w3=w3,
                            avatar=avatar_safe,
                            sell_token=sell_token,
                            buy_token=buy_token,
                            amount=sell_amount,
                            receiver=avatar_safe,
                            kind=kind,
                            max_slippage=0.1)

    checking = roles.send(
        transactables, role=role, private_key=private_key, roles_mod_address=roles_contract.address, web3=w3
    )

    assert checking.status == 1
