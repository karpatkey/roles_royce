import json
from dataclasses import dataclass
from defabipedia.types import StrEnum
from web3.types import Address
import requests
from defabipedia.types import Blockchain, Chain
from web3 import Web3
import time


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
            "sellAmount": str(self.sell_amount) + str(self.fee_amount),
            "buyAmount": str(self.buy_amount),
            "validTo": self.valid_to,
            "feeAmount": str(0),
            "kind": self.kind,
            "partiallyFillable": False,
            "sellTokenBalance": "erc20",
            "buyTokenBalance": "erc20",
            "signingScheme": "presign",
            "signature": "0x",
            "from": self.from_address,
            "appData": json.dumps({"appCode": "karpatkey_swap"}, separators=(',', ':')),
            "appDataHash": Web3.keccak(text=json.dumps({"appCode": "karpatkey_swap"}, separators=(',', ':'))).hex(),
        }

def quote_order_api(blockchain: Blockchain,
                    sell_token: Address,
                    buy_token: Address,
                    receiver: Address,
                    from_address: Address,
                    kind: SwapKind,
                    amount: int) -> Order:
    quote_order = {
        "sellToken": sell_token,
        "buyToken": buy_token,
        "receiver": receiver,
        "appData": json.dumps({"appCode": "karpatkey_swap"}, separators=(',', ':')),
        "appDataHash": Web3.keccak(text=json.dumps({"appCode": "karpatkey_swap"}, separators=(',', ':'))).hex(),
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

    return Order(sell_token=sell_token,
                 buy_token=buy_token,
                 receiver=receiver,
                 sell_amount=int(response["quote"]["sellAmount"]) + int(response["quote"]["feeAmount"]),
                 buy_amount=int(response["quote"]["buyAmount"]),
                 fee_amount=0,
                 valid_to=0,
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
                     order: Order | None = None) -> dict:
    """
    Creates an order in the COW API.

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
        dict: A dictionary with the order, the response and the UID
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
        )
        order.valid_to = valid_to

    response = requests.post(COW_ORDER_API_URL[blockchain], json=order.get_order_dict())
    if response.status_code != 201:
        return {"order": order, "response": response, "UID": None}
    else:
        return {"order": order, "response": response,
                "UID": response.text[1:len(response.text) - 1]}
