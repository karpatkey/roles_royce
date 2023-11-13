import json
from web3.types import Address
from web3 import Web3
from defabipedia import balancer, aura
from defabipedia.types import Chains
from roles_royce.protocols.balancer.utils import Pool, PoolKind
from roles_royce.constants import StrEnum
from .utils import get_bpt_from_aura, get_tokens_from_bpt
import os
from dataclasses import dataclass, field


# -----------------------------------------------------------------------------------------------------------------------
# StrEnums
# -----------------------------------------------------------------------------------------------------------------------

class DAO(StrEnum):
    GnosisDAO = "GnosisDAO"
    GnosisLTD = "GnosisLTD"

    def __str__(self):
        return self.name


class Blockchain(StrEnum):
    Ethereum = "Ethereum"
    Gnosis = "Gnosis"

    def __str__(self):
        return self.name


class Protocol(StrEnum):
    Balancer = "Balancer"
    Aura = "Aura"
    Lido = "Lido"

    def __str__(self):
        return self.name


# -----------------------------------------------------------------------------------------------------------------------
# General
# -----------------------------------------------------------------------------------------------------------------------

def seed_file(dao: str, blockchain: str) -> None:
    file = f"strategies/{dao}{blockchain}.json"
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


# -----------------------------------------------------------------------------------------------------------------------
# Position classes
# -----------------------------------------------------------------------------------------------------------------------

@dataclass
class BalancerPosition:
    position_id: str
    bpt_address: Address
    position_id_tech: Address = field(init=False)

    def __post_init__(self):
        self.position_id_tech = self.bpt_address


@dataclass
class AuraPosition:
    position_id: str
    bpt_address: Address
    position_id_tech: Address = field(init=False)

    def __post_init__(self):
        self.position_id_tech = self.bpt_address


# -----------------------------------------------------------------------------------------------------------------------


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
            position["exec_config"][i]["parameters"][0]["value"] = aura_address

        bpt_contract = w3.eth.contract(address=bpt_address,
                                       abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].UniversalBPT.abi)
        pool_id = bpt_contract.functions.getPoolId().call()
        vault_contract = balancer.ContractSpecs[Chains.get_blockchain_from_web3(w3)].Vault.contract(w3)
        pool_tokens = vault_contract.functions.getPoolTokens(pool_id).call()[0]
        pool = Pool(w3=w3, pool_id=pool_id)
        if pool.pool_kind() == PoolKind.ComposableStablePool:
            del pool_tokens[pool.bpt_index_from_composable()]  # Remove the BPT if it is a composable stable
        del position["exec_config"][2]["parameters"][2]["options"][
            0]  # Remove the dummy element in template
        for token_address in pool_tokens:
            token_contract = w3.eth.contract(address=token_address,
                                             abi=balancer.Abis[Chains.get_blockchain_from_web3(w3)].ERC20.abi)
            token_symbol = token_contract.functions.symbol().call()
            position["exec_config"][2]["parameters"][2]["options"].append({
                "value": token_address,
                "label": token_symbol
            })
        result.append(position)
    return result


def add_lido_positions(protocol, template, position_id):
    template['position_id'] = f"{protocol}_{position_id}"
    return template


# -----------------------------------------------------------------------------------------------------------------------
# Json builder
# -----------------------------------------------------------------------------------------------------------------------
@dataclass
class DAOStrategiesBuilder:
    dao: DAO
    blockchain: Blockchain
    balancer: list[BalancerPosition] | None = None
    aura: list[AuraPosition] | None = None
    lido: bool = False  # We either have funds in Lido or we don't

    def build_json(self, w3: Web3):
        self.add_to_json(self.build_balancer_positions(w3, self.balancer))
        self.add_to_json(self.build_aura_positions(w3, self.aura))
        # TODO: add_lido_position

    def add_to_json(self, positions: list[dict]):
        file = f"strategies/{self.dao}{self.blockchain}.json"

        if not os.path.isfile(file):
            seed_file(self.dao, self.blockchain)

        with open(file, "r") as f:
            strategies = json.load(f)

        for position in positions:
            if position['position_id_tech'] in [item for position in strategies["positions"] for item in
                                                position['position_id_tech']]:
                continue
            strategies['positions'].append(position)

        with open(file, "w") as f:
            json.dump(strategies, f)

    @staticmethod
    def build_balancer_positions(w3: Web3, positions: list[BalancerPosition]) -> list[dict]:
        with open('templates/balancer_template.json', 'r') as f:
            balancer_template = json.load(f)

        result = []
        for balancer_position in positions:
            bpt_address = Web3.to_checksum_address(balancer_position.position_id_tech)

            position = balancer_template.copy()
            del position["exec_config"][1]["parameters"][2]["options"][0]  # Remove the dummy element in template

            position["position_id"] = balancer_position.position_id
            position["position_id_tech"] = bpt_address
            for i in range(3):
                position["exec_config"][i]["parameters"][0]["value"] = bpt_address
            pool_tokens = get_tokens_from_bpt(w3, bpt_address)

            position["position_id_human_readable"] = 'Balancer'
            for token in pool_tokens:
                position["exec_config"][1]["parameters"][2]["options"].append({
                    "value": token['address'],
                    "label": token['symbol']
                })
                position["position_id_human_readable"] = position[
                                                             "position_id_human_readable"] + f"_{token['symbol']}"
            result.append(position)

        return result

    @staticmethod
    def build_aura_positions(w3: Web3, positions: list[AuraPosition]) -> list[dict]:
        with open('templates/aura_template.json', 'r') as f:
            aura_template = json.load(f)
        
        aura_addresses = get_bpt_from_aura(w3)
        result = []
        for aura_position in positions:
            
            bpt_address = Web3.to_checksum_address(aura_position.position_id_tech)
            for item in aura_addresses:
                if Web3.to_checksum_address(item.get('bpt_address')) == bpt_address:
                    aura_address = item.get('aura_address')
                    break

            

            position = aura_template.copy()
            del position["exec_config"][2]["parameters"][2]["options"][0]  # Remove the dummy element in template

            position["position_id"] = aura_position.position_id
            position["position_id_tech"] = aura_address
            for i in range(4):
                position["exec_config"][i]["parameters"][0]["value"] = aura_address
            pool_tokens = get_tokens_from_bpt(w3, bpt_address)

            position["position_id_human_readable"] = 'Aura'
            for token in pool_tokens:
                position["exec_config"][2]["parameters"][2]["options"].append({
                    "value": token['address'],
                    "label": token['symbol']
                })
                position["position_id_human_readable"] = position[
                                                             "position_id_human_readable"] + f"_{token['symbol']}"
            result.append(position)

        return result        


        
        #TODO: add_lido_position
