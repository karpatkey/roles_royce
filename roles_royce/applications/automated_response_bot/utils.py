# REQUIRED 3rd PARTY PACKAGES - cryptography

import base64
import json
from datetime import datetime, timedelta

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA

received_webhook_msg = {
    "id": "125d5b5e-222a-4a5f-a325-28412ca8a771",
    "data": '{"riskInsight":{"id":"M0OFLUXEDDV4","chain":"bsc","name":"Ownership changed","category":"Governance","status":"Active","timestamp":"2023-09-05T04:55:53.000Z","severity":"Medium","details":"Ownership of contract <0xf7fce88ee8ca8f9fc3abc97e2ca8b2bb5ea9524d|0xf7fce88ee8ca8f9fc3abc97e2ca8b2bb5ea9524d> changed - new owner <Null: 0x000...000|0x0000000000000000000000000000000000000000>","involvedAssets":[{"address":"0x0000000000000000000000000000000000000000","alias":"Null: 0x000...000","type":"Contract","chain":"bsc","involvementType":"New Owner"},{"address":"0xf7fce88ee8ca8f9fc3abc97e2ca8b2bb5ea9524d","type":"Contract","chain":"bsc","involvementType":"Target"},{"address":"0xd7ed580f4587205454a4d2ef7c39d844d694de6a","type":"Wallet","chain":"bsc","involvementType":"Removed Owner"}],"riskTypeId":"A-29","riskTypeDescription":"Contract ownership transferred","txnHash":"0xb2264473af745cb4e238d521e002ef223df801031d04699c5bcc18851e75e492","context":[{"title":"To","value":"0xf7fce88ee8ca8f9fc3abc97e2ca8b2bb5ea9524d"},{"title":"From","value":"0xd7ed580f4587205454a4d2ef7c39d844d694de6a"},{"title":"Value","value":"0"},{"title":"Status","value":"Success"},{"title":"Txn Hash","value":"0xb2264473af745cb4e238d521e002ef223df801031d04699c5bcc18851e75e492"},{"title":"Timestamp","value":"2023-09-05T04:55:53Z"},{"title":"Is Reorged","value":"false"},{"title":"Block Number","value":"31467736"},{"title":"Transaction Fee","value":"0.00007047002901015"},{"title":"Full Involved Assets","value":"[\\n  {\\n    \\"type\\": \\"contract\\",\\n    \\"chain\\": \\"bsc\\",\\n    \\"address\\": \\"0x0000000000000000000000000000000000000000\\",\\n    \\"involvement\\": \\"new_owner\\",\\n    \\"system_labels\\": [\\n      \\"Reward Calculator (Binance smart chain)\\",\\n      \\"Null: 0x000...000\\",\\n      \\"Swap Factory (Binance smart chain)\\",\\n      \\"Notifier  (Binance smart chain)\\",\\n      \\"(Tetu): Tetu Token (BSC)\\",\\n      \\"Mint Helper (Binance smart chain)\\",\\n      \\"Swap Router  (Binance smart chain)\\",\\n      \\"Pawn Shop (Binance smart chain)\\",\\n      \\"PS Vault (Binance smart chain)\\",\\n      \\"Auto Rewarder (Binance smart chain)\\",\\n      \\"Tetu Token (BSC)\\",\\n      \\"Tetu Token (Binance smart chain)\\",\\n      \\"Burn\\",\\n      \\"burn\\",\\n      \\"genesis\\"\\n    ],\\n    \\"alias\\": \\"Null: 0x000...000\\"\\n  },\\n  {\\n    \\"type\\": \\"contract\\",\\n    \\"chain\\": \\"bsc\\",\\n    \\"address\\": \\"0xf7fce88ee8ca8f9fc3abc97e2ca8b2bb5ea9524d\\",\\n    \\"involvement\\": \\"destination, target\\",\\n    \\"system_labels\\": []\\n  },\\n  {\\n    \\"type\\": \\"wallet\\",\\n    \\"chain\\": \\"bsc\\",\\n    \\"address\\": \\"0xd7ed580f4587205454a4d2ef7c39d844d694de6a\\",\\n    \\"involvement\\": \\"origin, removed_owner\\",\\n    \\"system_labels\\": []\\n  }\\n]"}],"stage":"Undefined","parentRiId":"M0OFLUXEDDV4","threatIntelReview":"NotReviewed"},"watchlists":[{"id":632,"name":"Alert testש\'sdaweddfs","description":"awdeaw","createdAt":"2023-04-10T14:40:43.245Z","updatedAt":"2023-08-27T15:17:11.242Z","createdBy":"Ronen Badalov","createdByUserId":13,"assets":[{"chain":"ethereum","address":null,"name":"0xmons","type":"Protocol"},{"chain":"ethereum","address":"0x0000000000000000000000000000000000000000","name":null,"type":"Wallet"},{"chain":"ethereum","address":"0x036cec1a199234fc02f72d29e596a09440825f1c","name":null,"type":"Contract"},{"chain":"ethereum","address":null,"name":"0x core","type":"Protocol"},{"chain":"bsc","address":"0x0000000000000000000000000000000000000000","name":null,"type":"Contract"},{"chain":"ethereum","address":null,"name":"0xSplits","type":"Protocol"},{"chain":"ethereum","address":null,"name":"[Deprecated] StarkGate: DAI [Ethereum <> StarkNet] - Pegged Bridge","type":"Protocol"},{"chain":"ethereum","address":null,"name":"Gnosis xDai [Ethereum <> Gnosis] - Pegged Bridge","type":"Protocol"},{"chain":"ethereum","address":null,"name":"Polygon POS [Ethereum <> Polygon] - Pegged Bridge","type":"Protocol"},{"chain":"ethereum","address":null,"name":"StarkGate: USDC [Ethereum <> StarkNet] - Pegged Bridge","type":"Protocol"},{"chain":"ethereum","address":null,"name":"StarkGate: DAI [Ethereum <> StarkNet] - Pegged Bridge","type":"Protocol"},{"chain":"ethereum","address":null,"name":"1inch core","type":"Protocol"},{"chain":"arbitrum","address":"0x102be4bccc2696c35fd5f5bfe54c1dfba416a741","name":null,"type":"Wallet"}],"alertsTagsStats":[{"count":0,"name":"All"},{"count":0,"name":"Read"},{"count":0,"name":"Unread"},{"count":0,"name":"Important"},{"count":0,"name":"Dismissed"}]}],"customAgents":[],"triggeredAssets":[{"chain":"bsc","address":"0x0000000000000000000000000000000000000000","name":null,"type":"Contract"}],"securitySuits":[]}',
    "digitalSignature": "MEYCIQCkaaHML+7jTJJKmD7me8cj2yXr1cwii2t87eZ5g5KKIgIhANofGJuOyAH5+/eEg1bm66cUjGm3mgW0GtTuRVgSNASe",
}

PUBLIC_KEY = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBgZAJk+OuOzp3sO6B+44gqLDzz/X1KloIQYkqefTYMv+URMIvN97gsoLYrZ9K08uQR0XHLXbB0RCTAt6BNFhzQ=="

FRESHNESS_VALIDATION_THRESHOLD_MINUTES = 60

validator = serialization.load_der_public_key(base64.b64decode(PUBLIC_KEY.encode('ascii')))


def validate_webhook(received_webhook_msg, PUBLIC_KEY, FRESHNESS_VALIDATION_THRESHOLD_MINUTES) -> bool:
    validator = serialization.load_der_public_key(base64.b64decode(PUBLIC_KEY.encode('ascii')))

    try:
        validator.verify(
            signature=base64.b64decode(received_webhook_msg["digitalSignature"].encode('ascii')),
            data=received_webhook_msg["data"].encode(),
            signature_algorithm=ECDSA(hashes.SHA256()),
        )

        # Optional freshness validation
        parsed_msg = json.loads(received_webhook_msg["data"]) # parsing data back to JSON
        risk_insight = parsed_msg["riskInsight"]
        risk_insight["timestamp"] = datetime.strptime(risk_insight["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
        if risk_insight["timestamp"] < datetime.utcnow() - timedelta(minutes=FRESHNESS_VALIDATION_THRESHOLD_MINUTES):
            raise ValueError("Timestamp crossed the freshness threshold")
    except InvalidSignature:
        print("Received an InvalidSignature")
        return False
    return True

exit_strat = {
    "dao": "TestSafeDAO",
    "blockchain": "gnosis",
    "general_parameters": [
        {
            "name": "percentage",
            "label": "Percentage",
            "type": "input",
            "rules": {
                "min": 0,
                "max": 100
            }
        }
    ],
    "positions": [
        {
            "position_id": "142",
            "position_id_tech": "0x7513105D6cF9D18756D95DeD81D6d3F68dB4b8DA",
            "position_id_human_readable": "gnosis_Aura_USDT_sDAI_USDC",
            "protocol": "Aura",
            "exec_config": [
                {
                    "function_name": "exit_1",
                    "label": "Unstake",
                    "test": True,
                    "stresstest": True,
                    "stresstest_error": "None",
                    "description": "Unstake BPT from Aura gauge",
                    "parameters": [
                        {
                            "name": "rewards_address",
                            "type": "constant",
                            "value": "0x7513105D6cF9D18756D95DeD81D6d3F68dB4b8DA"
                        }
                    ]
                },
            ]
        }
    ]
}