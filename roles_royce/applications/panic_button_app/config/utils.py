from web3.types import Address
from web3 import Web3
from defabipedia import balancer, aura
from defabipedia.types import Chains
from roles_royce.protocols.balancer.utils import Pool, PoolKind


def get_bpt_from_aura(w3: Web3) -> list[dict]:
    """
    Fetches all the Aura gauge token addresses with their corresponding BPT addresses

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
    blockchain = Chains.get_blockchain_from_web3(w3)
    booster_ctr = aura.ContractSpecs[blockchain].Booster.contract(w3)
    pool_length = booster_ctr.functions.poolLength().call()
    result = []
    for i in range(0, pool_length, 1):
        info = booster_ctr.functions.poolInfo(i).call()
        info_dict = {"blockchain": blockchain, "bpt_address": info[0], "aura_address": info[3]}
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


def get_tokens_from_bpt(w3: Web3, bpt_address: Address) -> list[dict]:
    """
    Fetches all the token addresses with their symbols from the BPT address

    Args:
        w3: Web3 instance
        bpt_address: BPT address of the pool

    Returns:
        List of dictionaries with the token address and symbol for each token in the pool
            e.g. [{
                    "address": token_address,
                    "symbol": token_symbol
                }]
    """
    bpt_contract = w3.eth.contract(address=bpt_address,
                                   abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].UniversalBPT.abi)
    pool_id = bpt_contract.functions.getPoolId().call()
    vault_contract = balancer.ContractSpecs[Chains.get_blockchain_from_web3(w3)].Vault.contract(w3)
    pool_tokens = vault_contract.functions.getPoolTokens(pool_id).call()[0]
    pool = Pool(w3=w3, pool_id=pool_id)
    if pool.pool_kind() == PoolKind.ComposableStablePool:
        del pool_tokens[pool.bpt_index_from_composable()]  # Remove the BPT if it is a composable stable
    result = []
    for token_address in pool_tokens:
        token_contract = w3.eth.contract(address=token_address,
                                         abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].ERC20.abi)
        token_symbol = token_contract.functions.symbol().call()
        result.append({
            "address": token_address,
            "symbol": token_symbol
        })
    return result
