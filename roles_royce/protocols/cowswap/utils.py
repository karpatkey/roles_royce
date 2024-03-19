import json
from dataclasses import dataclass

import requests
from defabipedia.types import Blockchain, Chain


@dataclass
class QuoteOrderCowSwap:
    blockchain: Blockchain
    sell_token: str
    buy_token: str
    receiver: str
    kind: str
    sell_amount: int

    def __post_init__(self):
        self.quote_order = {
            "sellToken": self.sell_token,
            "buyToken": self.buy_token,
            "receiver": self.receiver,
            "appData": json.dumps({"appCode": "santi_the_best"}),
            "appDataHash": "0x970eb15ab11f171c843c2d1fa326b7f8f6bf06ac7f84bb1affcc86511c783f12",
            "partiallyFillable": False,
            "sellTokenBalance": "erc20",
            "buyTokenBalance": "erc20",
            "from": self.receiver,
            "priceQuality": "verified",
            "signingScheme": "eip712",
            "onchainOrder": False,
            "kind": self.kind,
            "sellAmountBeforeFee": str(self.sell_amount),
        }

        if self.blockchain == Chain.ETHEREUM:
            self.response = requests.post(
                "https://api.cow.fi/mainnet/api/v1/quote", data=json.dumps(self.quote_order)
            ).json()
        elif self.blockchain == Chain.GNOSIS:
            self.response = requests.post(
                "https://api.cow.fi/xdai/api/v1/quote", data=json.dumps(self.quote_order)
            ).json()
        else:
            raise ValueError("Unsupported blockchain %s" % self.blockchain)

        self.buy_amount = int(self.response["quote"]["buyAmount"])
        self.fee_amount = int(self.response["quote"]["feeAmount"])
