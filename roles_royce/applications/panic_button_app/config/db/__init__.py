import json
import os

from defabipedia import aura, balancer
from defabipedia.types import Chain
from web3 import Web3
from web3.types import Address

from roles_royce.utils import to_checksum_address


def update_aura_db(w3: Web3) -> list[dict]:
    """
    Fetches all the Aura gauge token addresses with their corresponding BPT addresses and saves them in a json file
    aura_db_{blockchain}.json in the same directory the call is made

    Args:
        w3: Web3 instance

    Returns:
        List of dictionaries with the BPT address and the Aura gauge address for each pool
         e.g. [{
                    "blockchain": "ethereum",
                    "aura_address": "0xAura_gauge_token_address",
                    "bpt_address": "0xBpt_address"
              }]
    """
    blockchain = Chain.get_blockchain_from_web3(w3)
    booster_ctr = aura.ContractSpecs[blockchain].Booster.contract(w3)
    pool_length = booster_ctr.functions.poolLength().call()
    result = []
    for i in range(0, pool_length, 1):
        info = booster_ctr.functions.poolInfo(i).call()
        info_dict = {"blockchain": f"{blockchain}", "bpt_address": info[0], "aura_address": info[3]}
        if len(result) == 0:
            result.append(info_dict)
        if any(d["bpt_address"] == info_dict["bpt_address"] for d in result):
            for d in result:
                if d["bpt_address"] == info_dict["bpt_address"]:
                    d["aura_address"] = info_dict["aura_address"]
                    break
        else:
            result.append(info_dict)
    with open(f"aura_db_{blockchain}.json", "w") as f:
        json.dump(result, f, indent=4)
    return result


# Only for eth
def update_gauge_db(w3: Web3) -> list[dict]:
    """
    Fetches all the Gauge token addresses with their corresponding BPT addresses and saves them in a json file
    gauge_db_{blockchain}.json in the same directory the call is made

    Args:
        w3: Web3 instance

    Returns:
        List of dictionaries with the BPT address and the Gauge token address for each pool
         e.g. [{
                    "blockchain": "ethereum",
                    "gauge_address": "0xGauge_token_address",
                    "bpt_address": "0xBpt_address"
              }]
    """
    blockchain = Chain.get_blockchain_from_web3(w3)
    # lgf2_addr = balancer.ContractSpecs[blockchain].LiquidityGaugeFactory2.address
    lgf2_addr = "0xf1665E19bc105BE4EDD3739F88315cC699cc5b65"
    event_filter = w3.eth.filter(
        {
            "fromBlock": 15399251,
            "toBlock": "latest",
            "address": lgf2_addr,
            "topics": [w3.keccak(text="GaugeCreated(address)").hex()],
        }
    )

    logs = event_filter.get_all_entries()
    result = []
    decoded_addresses = [to_checksum_address((f"0x{log['topics'][1].hex()[-40:]}")) for log in logs]

    for address in decoded_addresses:
        gauge_contr = w3.eth.contract(address=address, abi=balancer.Abis[blockchain].Gauge.abi)
        bpt_address = gauge_contr.functions.lp_token().call()
        result.append({"blockchain": blockchain, "gauge_address": address, "bpt_address": bpt_address})
    with open(f"gauge_db_{blockchain}.json", "w") as g:
        json.dump(result, g, indent=4)
    return result


def main():
    PUBLIC_ETH_NODE_URL = "https://rpc.mevblocker.io"
    PUBLIC_GC_NODE_URL = "https://rpc.ankr.com/gnosis"

    w3_eth = Web3(
        Web3.HTTPProvider(os.environ.get("RR_ETH_FORK_URL", PUBLIC_ETH_NODE_URL))
    )  # Will use the endpoint stored as github secret if possible
    w3_gc = Web3(
        Web3.HTTPProvider(os.environ.get("RR_GC_FORK_URL", PUBLIC_GC_NODE_URL))
    )  # Will use the endpoint stored as github secret if possible

    update_aura_db(w3_eth)
    update_aura_db(w3_gc)
    update_gauge_db(w3_eth)


if __name__ == "__main__":
    main()
