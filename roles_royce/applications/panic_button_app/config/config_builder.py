import json
from web3.types import Address
from web3 import Web3
from defabipedia import balancer
from defabipedia.types import Chains
from roles_royce.protocols.balancer.utils import Pool, PoolKind

pool_address_eth = "0xA57b8d98dAE62B26Ec3bcC4a365338157060B234"
pool_address_gno = "0x98Ef32edd24e2c92525E59afc4475C1242a30184"
abiPoolInfo = '[{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"poolInfo","outputs":[{"internalType":"address","name":"lptoken","type":"address"},{"internalType":"address","name":"token","type":"address"},{"internalType":"address","name":"gauge","type":"address"},{"internalType":"address","name":"crvRewards","type":"address"},{"internalType":"address","name":"stash","type":"address"},{"internalType":"bool","name":"shutdown","type":"bool"}],"stateMutability":"view","type":"function"}]'
abiPoolLength = '[{"inputs":[],"name":"poolLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'


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

def get_bpt_from_aura(blockchain):
    if blockchain == "Ethereum":
        w3 = Web3(Web3.HTTPProvider("https://rpc.mevblocker.io"))
    elif blockchain == "Gnosis":
        w3 = Web3(Web3.HTTPProvider("https://rpc.gnosischain.com/"))
    pool_length_ctr = w3.eth.contract(address=pool_address_eth, abi=abiPoolLength)
    pool_length = pool_length_ctr.functions.poolLength().call()
    result = []
    print("eth aura pools: ",pool_length)
    for i in range(0,pool_length,1):
        info = w3.eth.contract(address=pool_address_eth, abi=abiPoolInfo).functions.poolInfo(i).call()
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

def add_aura_position(w3, lptoken_address, protocol, position_id, database):
    with open('aura_template.json', 'r') as f:
        template = json.load(f)
    bpt_address = w3.to_checksum_address(lptoken_address)
    for item in database:
        if item['bpt_address'] == bpt_address:
            contract_address = item['aura_address']
            break
        else:
            contract_address = bpt_address
    template['position_id'] = f"{protocol}_{position_id}"
    template['position_exec_config'][0]['parameters'][0]['value'] = contract_address
    template['position_exec_config'][1]['parameters'][0]['value'] = contract_address
    template['position_exec_config'][2]['parameters'][0]['value'] = contract_address
    template['position_exec_config'][3]['parameters'][0]['value'] = contract_address
    try:
        bpt_contract = w3.eth.contract(address=bpt_address, abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].UniversalBPT.abi)
        pool_id = bpt_contract.functions.getPoolId().call()
        vault_contract = balancer.ContractSpecs[Chains.get_blockchain_from_web3(w3)].Vault.contract(w3)
        pool_tokens = vault_contract.functions.getPoolTokens(pool_id).call()[0]
        pool = Pool(w3=w3, pool_id=pool_id.hex())
        if pool.pool_kind() == PoolKind.ComposableStablePool:
            del pool_tokens[pool.bpt_index_from_composable()] # Remove the BPT if it is a composable stable
        del template["exec_config"][1]["parameters"][2]["options"][0]  # Remove the dummy element in template
        for token_address in pool_tokens:
            token_contract = w3.eth.contract(address=token_address, abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].ERC20.abi)
            token_symbol = token_contract.functions.symbol().call()
            template["exec_config"][1]["parameters"][2]["options"].append({
                "value": token_address,
                "label": token_symbol
            })     
    except: 
        template = 'error'
    return template 

def add_lido_position(protocol, position_id):
    with open('lido_template.json', 'r') as f:
        template = json.load(f)
    template['position_id'] = f"{protocol}_{position_id}" 
    return template 

