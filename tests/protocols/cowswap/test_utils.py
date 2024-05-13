from defabipedia.types import Chain
from artemis.protocols.cowswap.utils import SwapKind, create_order_api, quote_order_api, Order, create_order
import json


def test_order():
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

    assert order.get_order_dict() == {'appData': '0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26',
                                      'buyAmount': '2731745328645699409',
                                      'buyToken': '0x6810e776880C02933D47DB1b9fc05908e5386b96',
                                      'buyTokenBalance': 'erc20',
                                      'feeAmount': '0',
                                      'from': '0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f',
                                      'kind': 'sell',
                                      'partiallyFillable': False,
                                      'receiver': '0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f',
                                      'sellAmount': '985693283370526960312',
                                      'sellToken': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
                                      'sellTokenBalance': 'erc20',
                                      'signature': '0x',
                                      'signingScheme': 'presign',
                                      'validTo': 1712697525}


def test_create_order():
    order = create_order(sell_token='0x6B175474E89094C44Da98b954EedeAC495271d0F',
                         buy_token='0x6810e776880C02933D47DB1b9fc05908e5386b96',
                         receiver='0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f',
                         from_address='0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f',
                         sell_amount=985693283370526960312,
                         buy_amount=2731745328645699409,
                         valid_to=1712697525,
                         kind=SwapKind.SELL)
    assert order == Order(sell_token='0x6B175474E89094C44Da98b954EedeAC495271d0F',
                          buy_token='0x6810e776880C02933D47DB1b9fc05908e5386b96',
                          receiver='0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f',
                          from_address='0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f',
                          sell_amount=985693283370526960312,
                          buy_amount=2731745328645699409,
                          fee_amount=0,
                          valid_to=1712697525,
                          kind=SwapKind.SELL,
                          partially_fillable=False, sell_token_balance='erc20', buy_token_balance='erc20')


def test_quote_order_sell_buy(requests_mock):
    avatar_safe = "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f"
    sell_token = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    buy_token = "0x6810e776880C02933D47DB1b9fc05908e5386b96"
    sell_amount = 999749122606373987000

    requests_mock.real_http = True
    requests_mock.post("https://api.cow.fi/mainnet/api/v1/quote",
                       text=json.dumps({"quote": {"sellToken": "0x6b175474e89094c44da98b954eedeac495271d0f",
                                                  "buyToken": "0x6810e776880c02933d47db1b9fc05908e5386b96",
                                                  "receiver": "0x458cd345b4c05e8df39d0a07220feb4ec19f5e6f",
                                                  "sellAmount": "986076688216997817016",
                                                  "buyAmount": "2715461014656166690", "validTo": 1712725390,
                                                  "appData": "{\"appCode\":\"karpatkey_swap\"}",
                                                  "appDataHash": "0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26",
                                                  "feeAmount": "13672434389376169984", "kind": "sell",
                                                  "partiallyFillable": False, "sellTokenBalance": "erc20",
                                                  "buyTokenBalance": "erc20", "signingScheme": "presign"},
                                        "from": "0x458cd345b4c05e8df39d0a07220feb4ec19f5e6f",
                                        "expiration": "2024-04-10T04:35:10.557295381Z", "id": 480554155,
                                        "verified": False}),
                       status_code=200)

    order = quote_order_api(
        blockchain=Chain.ETHEREUM,
        sell_token=sell_token,
        buy_token=buy_token,
        receiver=avatar_safe,
        from_address=avatar_safe,
        kind=SwapKind.SELL,
        amount=sell_amount,
    )
    assert order.buy_amount == 2715461014656166690
    assert order.sell_amount == 999749122606373987000
    assert requests_mock.request_history[
               0].text == ('{"sellToken": "0x6B175474E89094C44Da98b954EedeAC495271d0F", "buyToken": '
                           '"0x6810e776880C02933D47DB1b9fc05908e5386b96", "receiver": '
                           '"0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f", "appData": '
                           '"{\\"appCode\\":\\"karpatkey_swap\\"}", "appDataHash": '
                           '"0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26", '
                           '"partiallyFillable": false, "sellTokenBalance": "erc20", "buyTokenBalance": '
                           '"erc20", "from": "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f", '
                           '"priceQuality": "verified", "signingScheme": "presign", "onchainOrder": '
                           'false, "kind": "sell", "sellAmountBeforeFee": "999749122606373987000"}')


def test_quote_order_api_buy(requests_mock):
    avatar_safe = "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f"
    sell_token = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    buy_token = "0x6810e776880C02933D47DB1b9fc05908e5386b96"
    buy_amount = 999749122606373987000

    requests_mock.real_http = True
    requests_mock.post("https://api.cow.fi/mainnet/api/v1/quote",
                       text='{"quote":{"sellToken":"0x6b175474e89094c44da98b954eedeac495271d0f","buyToken":"0x6810e776880c02933d47db1b9fc05908e5386b96","receiver":"0x458cd345b4c05e8df39d0a07220feb4ec19f5e6f","sellAmount":"392983913649705259647909","buyAmount":"999749122606373987000","validTo":1712693430,"appData":"{\\"appCode\\":\\"karpatkey_swap\\"}","appDataHash":"0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26","feeAmount":"54546202693328093184","kind":"buy","partiallyFillable":false,"sellTokenBalance":"erc20","buyTokenBalance":"erc20","signingScheme":"eip712"},"from":"0x458cd345b4c05e8df39d0a07220feb4ec19f5e6f","expiration":"2024-04-09T19:42:30.458409786Z","id":480090898,"verified":false}',
                       status_code=200)

    order = quote_order_api(
        blockchain=Chain.ETHEREUM,
        sell_token=sell_token,
        buy_token=buy_token,
        receiver=avatar_safe,
        from_address=avatar_safe,
        kind=SwapKind.BUY,
        amount=buy_amount,
    )
    assert order.sell_amount == 393038459852398587741093
    assert requests_mock.request_history[
               0].text == ('{"sellToken": "0x6B175474E89094C44Da98b954EedeAC495271d0F", "buyToken": '
                           '"0x6810e776880C02933D47DB1b9fc05908e5386b96", "receiver": '
                           '"0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f", "appData": '
                           '"{\\"appCode\\":\\"karpatkey_swap\\"}", "appDataHash": '
                           '"0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26", '
                           '"partiallyFillable": false, "sellTokenBalance": "erc20", "buyTokenBalance": '
                           '"erc20", "from": "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f", '
                           '"priceQuality": "verified", "signingScheme": "presign", "onchainOrder": '
                           'false, "kind": "buy", "buyAmountAfterFee": "999749122606373987000"}')


def test_create_order_api(requests_mock):
    receiver = "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f"
    sell_token = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    buy_token = "0x6810e776880C02933D47DB1b9fc05908e5386b96"
    sell_amount = 999749122606373987000
    requests_mock.real_http = True
    requests_mock.post("https://api.cow.fi/mainnet/api/v1/quote",
                       text=json.dumps({"quote": {"sellToken": "0x6b175474e89094c44da98b954eedeac495271d0f",
                                                  "buyToken": "0x6810e776880c02933d47db1b9fc05908e5386b96",
                                                  "receiver": "0x458cd345b4c05e8df39d0a07220feb4ec19f5e6f",
                                                  "sellAmount": "988385325151045149368",
                                                  "buyAmount": "2935522110450512046",
                                                  "validTo": 1713213810,
                                                  "appData": "{\"appCode\":\"karpatkey_swap\"}",
                                                  "appDataHash": "0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26",
                                                  "feeAmount": "11363797455328837632",
                                                  "kind": "sell", "partiallyFillable": False,
                                                  "sellTokenBalance": "erc20",
                                                  "buyTokenBalance": "erc20", "signingScheme": "presign"},
                                        "from": "0x458cd345b4c05e8df39d0a07220feb4ec19f5e6f",
                                        "expiration": "2024-04-15T20:15:30.948835184Z",
                                        "id": 486728243,
                                        "verified": False}),
                       status_code=200)
    requests_mock.post("https://api.cow.fi/mainnet/api/v1/orders",
                       text='"0x1121a6e7fb9f3c50f962a996db730930d76b2c47af87c8c67dfde0ddb1ac5381458cd345b4c05e8df39d0a07220feb4ec19f5e6f6615c043"',
                       status_code=201)
    response = create_order_api(blockchain=Chain.ETHEREUM,
                                sell_token=sell_token,
                                buy_token=buy_token,
                                receiver=receiver,
                                from_address=receiver,
                                kind=SwapKind.SELL,
                                amount=sell_amount,
                                valid_to=1712696625 + 60 * 15)

    assert response[
               "UID"] == '0x1121a6e7fb9f3c50f962a996db730930d76b2c47af87c8c67dfde0ddb1ac5381458cd345b4c05e8df39d0a07220feb4ec19f5e6f6615c043'
    assert requests_mock.request_history[
               0].text == ('{"sellToken": "0x6B175474E89094C44Da98b954EedeAC495271d0F", "buyToken": '
                           '"0x6810e776880C02933D47DB1b9fc05908e5386b96", "receiver": '
                           '"0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f", "appData": '
                           '"{\\"appCode\\":\\"karpatkey_swap\\"}", "appDataHash": '
                           '"0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26", '
                           '"partiallyFillable": false, "sellTokenBalance": "erc20", "buyTokenBalance": '
                           '"erc20", "from": "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f", '
                           '"priceQuality": "verified", "signingScheme": "presign", "onchainOrder": '
                           'false, "kind": "sell", "sellAmountBeforeFee": "999749122606373987000"}')

    order = Order(sell_token='0x6B175474E89094C44Da98b954EedeAC495271d0F',
                  buy_token='0x6810e776880C02933D47DB1b9fc05908e5386b96',
                  receiver='0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f',
                  from_address='0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f',
                  sell_amount=985693283370526960312,
                  buy_amount=2731745328645699409,
                  fee_amount=14055839235847026688,
                  valid_to=1712697525,
                  kind=SwapKind.SELL,
                  partially_fillable=False, sell_token_balance='erc20', buy_token_balance='erc20')

    response = create_order_api(blockchain=Chain.ETHEREUM,
                                sell_token=sell_token,
                                buy_token=buy_token,
                                receiver=receiver,
                                from_address=receiver,
                                kind=SwapKind.SELL,
                                amount=sell_amount,
                                valid_to=1712696625 + 60 * 15,
                                order=order)

    assert response[
               "UID"] == '0x1121a6e7fb9f3c50f962a996db730930d76b2c47af87c8c67dfde0ddb1ac5381458cd345b4c05e8df39d0a07220feb4ec19f5e6f6615c043'
    assert requests_mock.request_history[
               0].text == ('{"sellToken": "0x6B175474E89094C44Da98b954EedeAC495271d0F", "buyToken": '
                           '"0x6810e776880C02933D47DB1b9fc05908e5386b96", "receiver": '
                           '"0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f", "appData": '
                           '"{\\"appCode\\":\\"karpatkey_swap\\"}", "appDataHash": '
                           '"0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26", '
                           '"partiallyFillable": false, "sellTokenBalance": "erc20", "buyTokenBalance": '
                           '"erc20", "from": "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f", '
                           '"priceQuality": "verified", "signingScheme": "presign", "onchainOrder": '
                           'false, "kind": "sell", "sellAmountBeforeFee": "999749122606373987000"}')
