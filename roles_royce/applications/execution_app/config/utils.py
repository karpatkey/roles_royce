import json
import os

from defabipedia import aura, balancer
from defabipedia.tokens import erc20_contract
from defabipedia.types import Chain
from web3 import Web3
from web3.types import Address

from roles_royce.protocols.balancer.utils import Pool, PoolKind
from roles_royce.utils import to_checksum_address


def get_bpt_from_aura_address(w3: Web3, aura_address: Address) -> Address:
    blockchain = Chain.get_blockchain_from_web3(w3)
    aura_contract = w3.eth.contract(address=aura_address, abi=aura.Abis[blockchain].BaseRewardPool.abi)
    bpt_address = aura_contract.functions.asset().call()
    return bpt_address


def get_aura_gauge_from_bpt(w3: Web3, bpt_address: Address) -> Address:
    """
    Fetches the Aura gauge address from the BPT address from the data in the aura_db_{blockchain}.json file in the
    db directory

    Args:
        w3: Web3 instance
        bpt_address: BPT address of the pool

    Returns:
        Address of the Aura gauge token
    """
    with open(
        os.path.join(os.path.dirname(__file__), "db", f"aura_db_{Chain.get_blockchain_from_web3(w3)}.json"), "r"
    ) as f:
        aura_db = json.load(f)
    for item in aura_db:
        if to_checksum_address(item.get("bpt_address")) == bpt_address:
            aura_address = item.get("aura_address")
            return aura_address


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
    bpt_contract = w3.eth.contract(
        address=bpt_address, abi=balancer.Abis[Chain.get_blockchain_from_web3(w3)].UniversalBPT.abi
    )
    pool_id = bpt_contract.functions.getPoolId().call()
    vault_contract = balancer.ContractSpecs[Chain.get_blockchain_from_web3(w3)].Vault.contract(w3)
    pool_tokens = vault_contract.functions.getPoolTokens(pool_id).call()[0]
    pool = Pool(w3=w3, pool_id=pool_id)
    if pool.pool_kind() == PoolKind.ComposableStablePool:
        del pool_tokens[pool.bpt_index_from_composable()]  # Remove the BPT if it is a composable stable
    result = []
    for token_address in pool_tokens:
        token_contract = erc20_contract(w3, token_address)
        token_symbol = token_contract.functions.symbol().call()
        result.append({"address": token_address, "symbol": token_symbol})
    return result


def get_gauge_address_from_bpt(w3: Web3, bpt_address: Address) -> Address:
    """get the gauge address from a bpt

    Args:
        w3 (Web3): Web3 instance
        bpt_address (Address): BPT address of the pool

    Returns:
        Address: The gauge address
    """

    blockchain = Chain.get_blockchain_from_web3(w3)
    get_gauge_contract = balancer.ContractSpecs[blockchain].LiquidityGaugeFactory.contract(w3)
    gauge_address = get_gauge_contract.functions.getPoolGauge(bpt_address).call()
    if gauge_address == "0x0000000000000000000000000000000000000000":
        with open(
            os.path.join(os.path.dirname(__file__), "db", f"gauge_db_{Chain.get_blockchain_from_web3(w3)}.json"), "r"
        ) as f:
            gauge_db = json.load(f)
        for item in gauge_db:
            if to_checksum_address(item.get("bpt_address")) == bpt_address:
                gauge_address = item.get("gauge_address")
                return gauge_address

    return gauge_address


def get_pool_id_from_bpt(w3: Web3, bpt_address: Address) -> int:
    bpt_contract = w3.eth.contract(
        address=bpt_address, abi=balancer.Abis[Chain.get_blockchain_from_web3(w3)].UniversalBPT.abi
    )
    pool_id = bpt_contract.functions.getPoolId().call()
    return pool_id
