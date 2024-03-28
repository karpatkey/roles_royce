import copy
import json
import os
from dataclasses import dataclass

from defabipedia.lido import ContractSpecs
from defabipedia.swap_pools import SwapPoolInstances
from defabipedia.tokens import erc20_contract
from defabipedia.types import Blockchain, Chain, SwapPools
from web3 import Web3
from web3.types import Address

from roles_royce.constants import StrEnum

from .utils import get_aura_gauge_from_bpt, get_gauge_address_from_bpt, get_tokens_from_bpt

# -----------------------------------------------------------------------------------------------------------------------
blacklist_token = ["GNO", "ENS", "BAL", "AURA", "COW", "AGVE"]
whitelist_pairs = ["WETH", "stETH", "wstETH", "ETH", "WBTC", "USDC", "USDT", "DAI", "WXDAI", "rETH", "EURe"]
wallet_tokens_swap = [
    {
        "ethereum": [
            {
                "token_in": [
                    "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",  # stETH
                    "0xae78736Cd615f374D3085123A210448E74Fc6393",  # rETH
                    "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
                ],  # wstETH
                "token_out": [
                    "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # ETH
                    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
                    "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                ],  # DAI
            },
            {
                "token_in": ["0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"],  # ETH
                "token_out": [
                    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
                    "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                ],  # DAI
            },
            {
                "token_in": ["0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"],  # USDC
                "token_out": ["0x6B175474E89094C44Da98b954EedeAC495271d0F"],  # DAI
            },
            {
                "token_in": ["0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"],  # USDC
                "token_out": [
                    "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
                    "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                ],  # USDT
            },
            {
                "token_in": ["0xdAC17F958D2ee523a2206206994597C13D831ec7"],  # USDT
                "token_out": [
                    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
                    "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                ],  # DAI
            },
            {
                "token_in": ["0x6B175474E89094C44Da98b954EedeAC495271d0F"],  # DAI
                "token_out": [
                    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
                    "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                ],  # USDT
            },
        ]
    },
    {
        "gnosis": [
            {
                "token_in": ["0xcB444e90D8198415266c6a2724b7900fb12FC56E"],  # EURe
                "token_out": [
                    "0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83",  # USDC
                    "0x4ECaBa5870353805a9F068101A40E0f32ed605C6",  # USDT
                    "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d",
                ],  # WXDAI
            }
        ]
    },
]


# -----------------------------------------------------------------------------------------------------------------------
# StrEnums
# -----------------------------------------------------------------------------------------------------------------------


class DAO(StrEnum):
    GnosisDAO = "GnosisDAO"
    GnosisLtd = "GnosisLtd"
    karpatkey = "karpatkey"
    ENS = "ENS"
    BalancerDAO = "BalancerDAO"

    def __str__(self):
        return self.name


class Protocol(StrEnum):
    Balancer = "Balancer"
    Aura = "Aura"
    Lido = "Lido"
    Wallet = "Wallet"

    def __str__(self):
        return self.name


# -----------------------------------------------------------------------------------------------------------------------
# General
# -----------------------------------------------------------------------------------------------------------------------


def seed_file(dao: DAO, blockchain: Blockchain) -> None:
    file = os.path.join(os.path.dirname(__file__), "strategies", f"{dao}-{blockchain}.json")
    with open(file, "w") as f:
        data = {
            "dao": dao,
            "blockchain": f"{blockchain}",
            "general_parameters": [
                {"name": "percentage", "label": "Percentage", "type": "input", "rules": {"min": 0, "max": 100}}
            ],
            "positions": [],
        }
        json.dump(data, f)


def seed_dict(dao: DAO, blockchain: Blockchain, positions: list) -> dict:
    data = {
        "dao": dao,
        "blockchain": f"{blockchain}",
        "general_parameters": [
            {"name": "percentage", "label": "Percentage", "type": "input", "rules": {"min": 0, "max": 100}}
        ],
        "positions": positions,
    }
    return data


# -----------------------------------------------------------------------------------------------------------------------
# Position classes
# -----------------------------------------------------------------------------------------------------------------------


@dataclass
class BalancerPosition:
    position_id: str
    bpt_address: Address
    staked: bool

    def __post_init__(self):
        self.bpt_address = Web3.to_checksum_address(self.bpt_address)

    def position_id_tech(self, w3: Web3) -> Address:
        """Returns the address of the BPT if staked is False, otherwise the address of the BPT gauge token

        Args:
            w3: Web3 instance

        Returns:
            Address of the BPT is stake is False, or BPT gauge token if stake is True
        """
        if self.staked:
            gauge_address = get_gauge_address_from_bpt(w3, self.bpt_address)
            position_id_tech = gauge_address
        else:
            position_id_tech = self.bpt_address
        return position_id_tech

    def position_id_human_readable(self, w3: Web3, pool_tokens: list[dict] = None) -> str:
        """Returns a string with the name of the protocol and the symbols of the tokens in the pool, specifying if the
        BPT is staked in the gauge or not, e.g. Balancer_DAI_WETH_staked or Balancer_DAI_WETH.

        Args:
            w3: Web3 instance
            pool_tokens: List of dictionaries with the token address and symbol for each token in the pool

        Returns:
            String with the name of the protocol and the symbols of the tokens in the pool, adding _staked if the BPT
            is staked in the gauge.

        """
        if pool_tokens is None:
            pool_tokens = get_tokens_from_bpt(w3, self.bpt_address)
        result = f"{Chain.get_blockchain_from_web3(w3)}_Balancer"
        for token in pool_tokens:
            result = result + f"_{token['symbol']}"
        if self.staked:
            result = result + "_staked"
        return result


@dataclass
class AuraPosition:
    position_id: str
    bpt_address: Address

    def __post_init__(self):
        self.bpt_address = Web3.to_checksum_address(self.bpt_address)

    def position_id_tech(self, w3: Web3) -> Address:
        """Returns the address of the Aura gauge token"""
        return get_aura_gauge_from_bpt(w3, self.bpt_address)

    def position_id_human_readable(self, w3: Web3, pool_tokens: list[dict] = None) -> str:
        if pool_tokens is None:
            pool_tokens = get_tokens_from_bpt(w3, self.bpt_address)
        result = f"{Chain.get_blockchain_from_web3(w3)}_Aura"
        for token in pool_tokens:
            result = result + f"_{token['symbol']}"
        return result


@dataclass
class LidoPosition:
    position_id: str
    lido_address: Address

    def __post_init__(self):
        self.lido_address = Web3.to_checksum_address(self.lido_address)

    def position_id_tech(self) -> Address:
        """Returns either stETH or wstETH address"""
        return self.lido_address

    def position_id_human_readable(self, w3: Web3) -> str:
        blockchain = Chain.get_blockchain_from_web3(w3)
        if self.lido_address == ContractSpecs[blockchain].wstETH.address:
            return f"{blockchain}_Lido_wstETH"
        else:
            return f"{blockchain}_Lido_stETH"


@dataclass
class WalletPosition:
    position_id: str
    token_in_address: Address

    def __post_init__(self):
        self.token_in_address = Web3.to_checksum_address(self.token_in_address)

    def position_id_tech(self) -> Address:
        """The token address that will be swapped"""
        return self.token_in_address

    def position_id_human_readable(self, w3: Web3) -> str:
        blockchain = Chain.get_blockchain_from_web3(w3)
        if self.token_in_address == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            return f"{blockchain}_WalletPosition_ETH"
        else:
            token_contract = erc20_contract(w3, self.token_in_address)
            token_symbol = token_contract.functions.symbol().call()
            return f"{blockchain}_WalletPosition_{token_symbol}"


# -----------------------------------------------------------------------------------------------------------------------
# Json builder
# -----------------------------------------------------------------------------------------------------------------------
@dataclass
class DAOStrategiesBuilder:
    dao: DAO
    blockchain: Blockchain
    balancer: list[BalancerPosition] | None = None
    aura: list[AuraPosition] | None = None
    lido: list[LidoPosition] | None = None
    wallet_tokens: list[WalletPosition] | None = None

    def build_dict(self, w3: Web3) -> dict:
        positions = []
        print(f"Building dict for {self.dao}-{self.blockchain}")
        print(f"    Adding Balancer positions")
        if self.balancer:
            positions.extend(self.build_balancer_positions(w3, self.balancer))
        print(f"    Adding Aura positions")
        if self.aura:
            positions.extend(self.build_aura_positions(w3, self.aura))
        print(f"    Adding Lido positions")
        if self.lido:
            positions.extend(self.build_lido_positions(w3, self.lido))
        print(f"    Adding Wallet positions")
        if self.wallet_tokens:
            positions.extend(self.build_wallet_positions(w3, self.wallet_tokens))
        return seed_dict(self.dao, self.blockchain, positions)

    def build_json(self, w3: Web3):
        print(f"Building json for {self.dao}-{self.blockchain}")
        print(f"    Adding Balancer positions")
        if self.balancer:
            self.add_to_json(self.build_balancer_positions(w3, self.balancer))
        print(f"    Adding Aura positions")
        if self.aura:
            self.add_to_json(self.build_aura_positions(w3, self.aura))
        print(f"    Adding Lido positions")
        if self.lido:
            self.add_to_json(self.build_lido_positions(w3, self.lido))
        print(f"    Adding Wallet positions")
        if self.wallet_tokens:
            self.add_to_json(self.build_wallet_positions(w3, self.wallet_tokens))

    def add_to_json(self, positions: list[dict]):
        file = os.path.join(os.path.dirname(__file__), "strategies", f"{self.dao}-{self.blockchain}.json")

        if not os.path.isfile(file):
            seed_file(self.dao, self.blockchain)

        with open(file, "r") as f:
            strategies = json.load(f)

        for position in positions:
            if position["position_id_tech"] in [
                position_element["position_id_tech"] for position_element in strategies["positions"]
            ]:
                continue
            strategies["positions"].append(position)

        with open(file, "w") as f:
            json.dump(strategies, f, indent=4)

    @staticmethod
    def build_balancer_positions(w3: Web3, positions: list[BalancerPosition]) -> list[dict]:
        with open(os.path.join(os.path.dirname(__file__), "templates", "balancer_template.json"), "r") as f:
            balancer_template = json.load(f)

        result = []
        for balancer_position in positions:
            print("        Adding: ", balancer_position)

            bpt_address = balancer_position.bpt_address

            position = copy.deepcopy(balancer_template)

            if balancer_position.staked:
                for item in range(3):
                    position["exec_config"].pop(0)
                    gauge_address = balancer_position.position_id_tech(w3)
                for i in range(3):
                    position["exec_config"][i]["parameters"][0]["value"] = gauge_address
                    print(
                        "                Adding: ",
                        position["exec_config"][i]["function_name"],
                        position["exec_config"][i]["label"],
                    )
            else:
                for item in range(3):
                    position["exec_config"].pop(-1)
                for i in range(3):
                    position["exec_config"][i]["parameters"][0]["value"] = bpt_address
                    print(
                        "                Adding: ",
                        position["exec_config"][i]["function_name"],
                        position["exec_config"][i]["label"],
                    )

            del position["exec_config"][1]["parameters"][2]["options"][0]  # Remove the dummy element in template

            position["position_id"] = balancer_position.position_id

            try:
                pool_tokens = get_tokens_from_bpt(w3, bpt_address)
                position["position_id_tech"] = gauge_address if balancer_position.staked else bpt_address
                position["position_id_human_readable"] = balancer_position.position_id_human_readable(
                    w3, pool_tokens=pool_tokens
                )
                if all(token["symbol"] in whitelist_pairs for token in pool_tokens):
                    for token in pool_tokens:
                        position["exec_config"][1]["parameters"][2]["options"].append(
                            {"value": token["address"], "label": token["symbol"]}
                        )
                else:
                    del position["exec_config"][
                        1
                    ]  # Remove the single token exit strategy if all tokens are not in whitelist pairs
                    print(
                        f"        Removing because of no whitelisted tokens: Balancer position",
                        position["position_id"],
                        position["position_id_human_readable"],
                    )

            except Exception as e:
                position["position_id_human_readable"] = f"AddressGivesError: {e}"

            result.append(position)
            print(
                f"        Done adding: Balancer position",
                position["position_id"],
                position["position_id_human_readable"],
            )
        return result

    @staticmethod
    def build_aura_positions(w3: Web3, positions: list[AuraPosition]) -> list[dict]:
        with open(os.path.join(os.path.dirname(__file__), "templates", "aura_template.json"), "r") as f:
            aura_template = json.load(f)

        result = []
        for aura_position in positions:
            print("        Adding: ", aura_position)
            bpt_address = aura_position.bpt_address
            position = copy.deepcopy(aura_template)
            try:
                aura_address = aura_position.position_id_tech(w3)

                del position["exec_config"][2]["parameters"][2]["options"][0]  # Remove the dummy element in template

                position["position_id"] = aura_position.position_id
                position["position_id_tech"] = aura_address

                for i in range(4):
                    position["exec_config"][i]["parameters"][0]["value"] = aura_address
                    print(
                        "                Adding: ",
                        position["exec_config"][i]["function_name"],
                        position["exec_config"][i]["label"],
                    )
                pool_tokens = get_tokens_from_bpt(w3, bpt_address)
                position["position_id_human_readable"] = aura_position.position_id_human_readable(
                    w3, pool_tokens=pool_tokens
                )
                if all(token["symbol"] in whitelist_pairs for token in pool_tokens):
                    for token in pool_tokens:
                        position["exec_config"][2]["parameters"][2]["options"].append(
                            {"value": token["address"], "label": token["symbol"]}
                        )
                else:
                    del position["exec_config"][
                        2
                    ]  # Remove the single token exit strategy if all tokens are not in whitelist pairs
                    print("                Removing because no whitelisted tokens: ")

            except Exception as e:
                position["position_id_human_readable"] = f"AddressGivesError: {e}"

            result.append(position)
            print(
                f"        Done adding: Aura position", position["position_id"], position["position_id_human_readable"]
            )
        return result

    @staticmethod
    def build_lido_positions(w3: Web3, positions: list[LidoPosition]) -> list[dict]:
        with open(os.path.join(os.path.dirname(__file__), "templates", "lido_template.json"), "r") as f:
            lido_template = json.load(f)

        result = []
        for lido_position in positions:
            print("        Adding: ", lido_position)
            position = copy.deepcopy(lido_template)
            blockchain = Chain.get_blockchain_from_web3(w3)
            if lido_position.lido_address == ContractSpecs[blockchain].wstETH.address:
                if blockchain == Chain.GNOSIS:
                    position["exec_config"] = list(
                        filter(
                            lambda x: x["function_name"] not in ["exit_1", "exit_2", "exit_3"], position["exec_config"]
                        )
                    )
                else:
                    position["exec_config"] = list(
                        filter(lambda x: x["function_name"] not in ["exit_1", "exit_3"], position["exec_config"])
                    )
            else:
                position["exec_config"] = list(
                    filter(lambda x: x["function_name"] not in ["exit_2", "exit_4"], position["exec_config"])
                )
            position["position_id"] = lido_position.position_id
            position["position_id_tech"] = lido_position.position_id_tech()
            position["position_id_human_readable"] = lido_position.position_id_human_readable(w3)
            for i in range(len(position["exec_config"])):
                print(
                    "                Adding: ",
                    position["exec_config"][i]["function_name"],
                    position["exec_config"][i]["label"],
                )

            print(
                f"        Done adding: Lido position", position["position_id"], position["position_id_human_readable"]
            )

            result.append(position)
        return result

    @staticmethod
    def build_wallet_positions(w3: Web3, positions: list[WalletPosition]) -> list[dict]:
        with open(os.path.join(os.path.dirname(__file__), "templates", "swap_pool_template.json"), "r") as f:
            wallet_template = json.load(f)

        result = []
        for wallet_position in positions:
            blockchain = Chain.get_blockchain_from_web3(w3)
            for blockchain_entry in wallet_tokens_swap:
                if blockchain in blockchain_entry:
                    for swap_entry in blockchain_entry[blockchain]:
                        token_in_address = wallet_position.position_id_tech()
                        if token_in_address in swap_entry["token_in"]:
                            print("        Adding: ", wallet_position)
                            position = copy.deepcopy(wallet_template)

                            position["position_id"] = wallet_position.position_id
                            position["position_id_tech"] = wallet_position.position_id_tech()
                            position["position_id_human_readable"] = wallet_position.position_id_human_readable(w3)

                            token_pairs = []
                            for token_out in swap_entry["token_out"]:
                                token_pairs.append([token_in_address, token_out])

                            pools_class = SwapPoolInstances[blockchain]
                            instances = []
                            for token_pair in token_pairs:
                                token_in = token_pair[0]
                                token_out = token_pair[1]

                                for attr_name in dir(pools_class):
                                    attr_value = getattr(pools_class, attr_name)
                                    if isinstance(attr_value, SwapPools):
                                        if token_in in attr_value.tokens and token_out in attr_value.tokens:
                                            instances.append({"pair": token_pair, "pool": attr_value})

                            for instance in instances:
                                if instance["pool"].protocol == "Balancer":
                                    i = 0
                                elif instance["pool"].protocol == "Curve":
                                    i = 1
                                elif instance["pool"].protocol == "UniswapV3":
                                    i = 2
                                if instance["pair"][0] == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                                    token_in_symbol = "ETH"
                                    token_out_contract = erc20_contract(w3, instance["pair"][1])
                                    token_out_symbol = token_out_contract.functions.symbol().call()
                                elif instance["pair"][1] == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                                    token_out_symbol = "ETH"
                                    token_in_contract = erc20_contract(w3, instance["pair"][0])
                                    token_in_symbol = token_in_contract.functions.symbol().call()
                                else:
                                    token_in_contract = erc20_contract(w3, instance["pair"][0])
                                    token_in_symbol = token_in_contract.functions.symbol().call()
                                    token_out_contract = erc20_contract(w3, instance["pair"][1])
                                    token_out_symbol = token_out_contract.functions.symbol().call()
                                if (
                                    position["exec_config"][i]["parameters"][0]["options"][0]["value"]
                                    == "FillMewithTokenAddress"
                                ):
                                    del position["exec_config"][i]["parameters"][0]["options"][
                                        0
                                    ]  # Remove the dummy token_in element in template
                                    del position["exec_config"][i]["parameters"][2]["options"][
                                        0
                                    ]  # Remove the dummy token_out element in template
                                    position["exec_config"][i]["parameters"][0]["options"].append(
                                        {"value": instance["pair"][0], "label": token_in_symbol}
                                    )
                                    position["exec_config"][i]["parameters"][2]["options"].append(
                                        {"value": instance["pair"][1], "label": token_out_symbol}
                                    )
                                else:
                                    if not any(
                                        option["value"] == instance["pair"][1]
                                        for option in position["exec_config"][i]["parameters"][2]["options"]
                                    ):
                                        position["exec_config"][i]["parameters"][2]["options"].append(
                                            {"value": instance["pair"][1], "label": token_out_symbol}
                                        )
                            for i in range(len(position["exec_config"]) - 1, -1, -1):
                                if (
                                    position["exec_config"][i]["parameters"][0]["options"][0]["value"]
                                    == "FillMewithTokenAddress"
                                ):
                                    del position["exec_config"][i]

                            if len(position["exec_config"]) > 0:
                                result.append(position)
                            print(
                                f"        Done adding: Wallet position",
                                position["position_id"],
                                position["position_id_human_readable"],
                            )
                else:
                    print("        Not adding: ", wallet_position)
        return result
