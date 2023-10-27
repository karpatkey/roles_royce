import json
from web3.types import Address
from web3 import Web3
from defabipedia import balancer
from defabipedia.types import Chains
from roles_royce.protocols.balancer.utils import Pool, PoolKind


def seed_file(file: str, dao: str, blockchain: str) -> None:
    with open(file, "w") as f:
        data = {
            "dao": dao,
            "blockchain": blockchain,
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
            "positions": []
        }
        json.dump(data, f)


def add_balancer_positions(w3: Web3, file: str, position_ids: list[str], bpt_addresses: list[Address]):
    with open(file, "r") as f:
        data = json.load(f)

    with open('balancer_template.json', 'r') as f:
        balancer_template = json.load(f)

    for bpt_address in bpt_addresses:
        position = balancer_template.copy()
        position["position_id"] = position_ids[bpt_addresses.index(bpt_address)]
        bpt_address = Web3.to_checksum_address(bpt_address)
        for i in range(3):
            position["exec_config"][i]["parameters"][0]["value"] = bpt_address

        bpt_contract = w3.eth.contract(address=bpt_address, abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].UniversalBPT.abi)
        pool_id = bpt_contract.functions.getPoolId().call()
        vault_contract = balancer.ContractSpecs[Chains.get_blockchain_from_web3(w3)].Vault.contract(w3)
        pool_tokens = vault_contract.functions.getPoolTokens(pool_id).call()[0]
        pool = Pool(w3=w3, pool_id=pool_id.hex())
        if pool.pool_kind() == PoolKind.ComposableStablePool:
            del pool_tokens[pool.bpt_index_from_composable()] # Remove the BPT if it is a composable stable
        del position["exec_config"][1]["parameters"][2]["options"][0]  # Remove the dummy element in template
        for token_address in pool_tokens:
            token_contract = w3.eth.contract(address=token_address, abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].ERC20.abi)
            token_symbol = token_contract.functions.symbol().call()
            position["exec_config"][1]["parameters"][2]["options"].append({
                "value": token_address,
                "label": token_symbol
            })
        data["positions"].append(position)

    with open(file, "w") as f:
        json.dump(data, f)


