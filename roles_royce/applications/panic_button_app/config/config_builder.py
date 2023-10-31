import json
from web3.types import Address
from web3 import Web3
from defabipedia import balancer, aura
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

def get_bpt_from_aura(w3: Web3):
    booster_ctr = aura.ContractSpecs[Chains.get_blockchain_from_web3(w3)].Booster.contract(w3)
    blockchain = Chains.get_blockchain_from_web3(w3)
    pool_length = booster_ctr.functions.poolLength().call()
    result = []
    for i in range(0,pool_length,1):
        info = booster_ctr.functions.poolInfo(i).call()
        info_dict = {"blockchain":blockchain,"bpt_address":info[0],"aura_address":info[3]}
        if len(result) == 0:
            result.append(info_dict)
        if any(d['bpt_address'] == info_dict['bpt_address'] for d in result):
            for d in result:
                if d['bpt_address'] == info_dict['bpt_address']:
                    d['aura_address'] = info_dict['aura_address']
                    break
        else:
            result.append(info_dict)
    return result

def add_balancer_positions(w3: Web3, template: dict, position_ids: list[str], bpt_addresses: list[Address]):
    result = []
    for bpt_address in bpt_addresses:
        position = template.copy()
        position["position_id"] = position_ids[bpt_addresses.index(bpt_address)]
        bpt_address = Web3.to_checksum_address(bpt_address)
        for i in range(3):
            position["position_exec_config"][i]["parameters"][0]["value"] = bpt_address
        bpt_contract = w3.eth.contract(address=bpt_address, abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].UniversalBPT.abi)
        pool_id = bpt_contract.functions.getPoolId().call()
        vault_contract = balancer.ContractSpecs[Chains.get_blockchain_from_web3(w3)].Vault.contract(w3)
        pool_tokens = vault_contract.functions.getPoolTokens(pool_id).call()[0]
        pool = Pool(w3=w3, pool_id=pool_id)
        if pool.pool_kind() == PoolKind.ComposableStablePool:
            del pool_tokens[pool.bpt_index_from_composable()] # Remove the BPT if it is a composable stable
        del position["position_exec_config"][1]["parameters"][2]["options"][0]  # Remove the dummy element in template
        for token_address in pool_tokens:
            token_contract = w3.eth.contract(address=token_address, abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].ERC20.abi)
            token_symbol = token_contract.functions.symbol().call()
            position["position_exec_config"][1]["parameters"][2]["options"].append({
                "value": token_address,
                "label": token_symbol
            })
        result.append(position)
    return result

def add_aura_positions(w3: Web3, template: dict, position_ids: list[str], bpt_addresses: list[Address]):

    aura_balancer_list = get_bpt_from_aura(w3)
    result = []
    for bpt_address in bpt_addresses:
        position = template.copy()
        position["position_id"] = position_ids[bpt_addresses.index(bpt_address)]
        bpt_address = Web3.to_checksum_address(bpt_address)
        for item in aura_balancer_list:
            if item.get('bpt_address') == bpt_address:
                aura_address = item.get('aura_address')
                break
        for i in range(4):
            position["position_exec_config"][i]["parameters"][0]["value"] = aura_address
    
        bpt_contract = w3.eth.contract(address=bpt_address, abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].UniversalBPT.abi)
        pool_id = bpt_contract.functions.getPoolId().call()
        vault_contract = balancer.ContractSpecs[Chains.get_blockchain_from_web3(w3)].Vault.contract(w3)
        pool_tokens = vault_contract.functions.getPoolTokens(pool_id).call()[0]
        pool = Pool(w3=w3, pool_id=pool_id)
        if pool.pool_kind() == PoolKind.ComposableStablePool:
            del pool_tokens[pool.bpt_index_from_composable()] # Remove the BPT if it is a composable stable
        del position["position_exec_config"][2]["parameters"][2]["options"][0]  # Remove the dummy element in template        
        for token_address in pool_tokens:
            token_contract = w3.eth.contract(address=token_address, abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].ERC20.abi)
            token_symbol = token_contract.functions.symbol().call()
            position["position_exec_config"][2]["parameters"][2]["options"].append({
                "value": token_address,
                "label": token_symbol
            })
        result.append(position)
    return result


def add_lido_positions(protocol, template, position_id):
    template['position_id'] = f"{protocol}_{position_id}" 
    return template 


def add_positions(w3: Web3, file: str, protocol: str, position_ids: list[str], addresses: list[Address] = None):
    with open(file, "r") as f:
        data = json.load(f)

    if protocol == 'balancer':
        with open('balancer_template.json', 'r') as f:
            template = json.load(f)
        result = add_balancer_positions(w3, template, position_ids, addresses)
        
    elif protocol == 'aura':
        with open('aura_template.json', 'r') as f:
            template = json.load(f)
        result = add_aura_positions(w3, template, position_ids, addresses)

    elif protocol == 'lido':
        with open('lido_template.json', 'r') as f:
            template = json.load(f)
        result = add_lido_positions(w3, template, position_ids)

    data['positions'] = result
    with open(file, "w") as f:
        json.dump(data, f)
