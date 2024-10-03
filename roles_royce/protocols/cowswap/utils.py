import json
from dataclasses import dataclass

import requests
from defabipedia.types import Blockchain, Chain, StrEnum
from web3 import Web3
from web3.types import Address


class SwapKind(StrEnum):
    SELL = "sell"
    BUY = "buy"


COW_ORDER_API_URL = {
    Chain.ETHEREUM: "https://api.cow.fi/mainnet/api/v1/orders",
    Chain.GNOSIS: "https://api.cow.fi/xdai/api/v1/orders"}

COW_QUOTE_API_URL = {
    Chain.ETHEREUM: "https://api.cow.fi/mainnet/api/v1/quote",
    Chain.GNOSIS: "https://api.cow.fi/xdai/api/v1/quote",
}


class CONSTANTS(StrEnum):
    APP_DATA = json.dumps({"appCode": "karpatkey_swap"}, separators=(',', ':'))
    APP_DATA_HASH = Web3.keccak(text=json.dumps({"appCode": "karpatkey_swap"}, separators=(',', ':'))).hex()
    # APP_DATA_HASH is '0xec4d31696be1272dc6f998e7119a6776e55100c5f8a225ca4ff9529a9eef8e26'
    ERC20_HASH = Web3.keccak(text="erc20").hex()
    # ERC20_HASH is '0x5a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc9'
    SELL_HASH = Web3.keccak(text="sell").hex()
    # SELL_HASH is '0xf3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee346775'
    BUY_HASH = Web3.keccak(text="buy").hex()
    # BUY_HASH is '0x6ed88e868af0a1983e3886d5f3e95a2fafbd6c3450bc229e27342283dc429ccc'


@dataclass
class Order:
    sell_token: Address
    buy_token: Address
    receiver: Address
    sell_amount: int
    buy_amount: int
    fee_amount: int
    valid_to: int
    fee_amount: int
    kind: SwapKind
    partially_fillable: bool
    sell_token_balance: str
    buy_token_balance: str
    from_address: Address

    def get_order_dict(self):
        return {
            "sellToken": self.sell_token,
            "buyToken": self.buy_token,
            "receiver": self.receiver,
            "sellAmount": str(self.sell_amount),
            "buyAmount": str(self.buy_amount),
            "validTo": self.valid_to,
            "feeAmount": str(self.fee_amount),
            "kind": self.kind,
            "partiallyFillable": False,
            "sellTokenBalance": "erc20",
            "buyTokenBalance": "erc20",
            "signingScheme": "presign",
            "signature": "0x",
            "from": self.from_address,
            "appData": CONSTANTS.APP_DATA_HASH,
        }


def create_order(sell_token: Address,
                 buy_token: Address,
                 receiver: Address,
                 sell_amount: int,
                 buy_amount: int,
                 from_address: Address,
                 kind: SwapKind,
                 valid_to: int) -> Order:
    """
    Creates an Order object.

    Args:
        sell_token (Address): The token to sell
        buy_token (Address): The token to buy
        receiver (Address): The address of the receiver
        sell_amount (int): The amount to sell
        buy_amount (int): The amount to buy
        from_address (Address): The address of the sender
        kind (SwapKind): The kind of the order ("buy" or "sell")
        valid_to (int): The expiration time of the order in unix timestamp in seconds

    Returns:
        Order: The Order object
    """

    return Order(sell_token=sell_token,
                 buy_token=buy_token,
                 receiver=receiver,
                 sell_amount=sell_amount,
                 buy_amount=buy_amount,
                 fee_amount=0,
                 valid_to=valid_to,
                 kind=kind,
                 partially_fillable=False,
                 sell_token_balance="erc20",
                 buy_token_balance="erc20",
                 from_address=from_address)


def quote_order_api(blockchain: Blockchain,
                    sell_token: Address,
                    buy_token: Address,
                    receiver: Address,
                    from_address: Address,
                    kind: SwapKind,
                    amount: int,
                    valid_to: int | None = None) -> Order:
    """
    Quotes an order using the Cow API and returns the corresponding Order object

    Args:
        blockchain (Blockchain): The blockchain to use
        sell_token (Address): The token to sell
        buy_token (Address): The token to buy
        receiver (Address): The address of the receiver
        from_address (Address): The address of the sender
        kind (SwapKind): The kind of the order ("buy" or "sell")
        amount (int): The amount to sell or buy
        valid_to (int, optional): The expiration time of the order in unix timestamp in seconds. Defaults to None. If
            None, the order object returned has valid_to=0

    Returns:
        Order: The corresponding Order object
    """

    quote_order = {
        "sellToken": sell_token,
        "buyToken": buy_token,
        "receiver": receiver,
        "appData": CONSTANTS.APP_DATA,
        "appDataHash": CONSTANTS.APP_DATA_HASH,
        "partiallyFillable": False,
        "sellTokenBalance": "erc20",
        "buyTokenBalance": "erc20",
        "from": from_address,
        "priceQuality": "verified",
        "signingScheme": "presign",
        "onchainOrder": False,
        "kind": kind,
    }
    if kind == SwapKind.SELL:
        quote_order["sellAmountBeforeFee"] = str(amount)
    else:
        quote_order["buyAmountAfterFee"] = str(amount)

    response = requests.post(
        COW_QUOTE_API_URL[blockchain], data=json.dumps(quote_order)
    ).json()

    def cow_error(error):
        raise ValueError(f"[CowswapError]: {error}")

    if not response:
        if response.status_code == 400:
            cow_error(f"{response["errorType"]}: {response["description"]}")
        if response.status_code == 404:
            cow_error("No route was found for the specified order.")
        if response.status_code == 429:
            cow_error("Too many order quotes.")
        if response.status_code == 500:
            cow_error("Unexpected error quoting an order.")

        cow_error("Unknown error")

    return Order(sell_token=sell_token,
                 buy_token=buy_token,
                 receiver=receiver,
                 sell_amount=int(response["quote"]["sellAmount"]) + int(response["quote"]["feeAmount"]),
                 buy_amount=int(response["quote"]["buyAmount"]),
                 fee_amount=0,
                 valid_to=0 if valid_to is None else valid_to,
                 kind=kind,
                 partially_fillable=False,
                 sell_token_balance="erc20",
                 buy_token_balance="erc20",
                 from_address=from_address)


def create_order_api(blockchain: Blockchain,
                     sell_token: Address,
                     buy_token: Address,
                     receiver: Address,
                     from_address: Address,
                     kind: SwapKind,
                     amount: int,
                     valid_to: int,
                     order: Order | None = None,
                     fork: bool = False) -> dict:
    """
    Creates an order using the Cow API.

    Args:
        blockchain (Blockchain): The blockchain to use
        sell_token (Address): The token to sell
        buy_token (Address): The token to buy
        receiver (Address): The address of the receiver
        from_address (Address): The address of the sender
        kind (SwapKind): The kind of the order ("buy" or "sell")
        amount (int): The amount to sell or buy
        valid_to (int): The expiration time of the order in unix timestamp in seconds
        order (Order): The order to create. If None, it will be created from the other arguments

    Returns:
        dict: A dictionary with the order and the UID
    """

    if order is None:
        order = quote_order_api(
            blockchain=blockchain,
            sell_token=sell_token,
            buy_token=buy_token,
            receiver=receiver,
            from_address=from_address,
            kind=kind,
            amount=amount,
            valid_to=valid_to,
        )
    else:
        order.valid_to = valid_to  # In case the order was already created with valid_to=0 with quote_order_api

    response = requests.post(COW_ORDER_API_URL[blockchain], data=json.dumps(order.get_order_dict()))
    if response.status_code != 201:
        return {"order": order, "UID": None, "error": response.text}
    else:
        return {"order": order, "UID": response.json()}
