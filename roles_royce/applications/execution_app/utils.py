import json
import logging
import time
from dataclasses import dataclass
from typing import Optional

from decouple import config
from defabipedia.aura import Abis as AuraAbis
from defabipedia.balancer import Abis as BalancerAbis
from defabipedia.types import Chain
from pydantic import BaseModel, ConfigDict
from web3 import Web3
from web3.exceptions import ContractLogicError

from roles_royce.applications.execution_app.pulley_fork import PulleyFork
from roles_royce.constants import StrEnum
from roles_royce.generic_method import Transactable
from roles_royce.protocols.base import Address, ContractMethod
from roles_royce.toolshed.disassembling import (
    AuraDisassembler,
    BalancerDisassembler,
    Disassembler,
    LidoDisassembler,
    SwapDisassembler,
    DSRDisassembler,
    SparkDisassembler,
)
from roles_royce.utils import to_checksum_address


class Modes(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


# The next helper function allows to leave env variables unfilled in the .env file
def custom_config(variable, default, cast):
    """Attempts to read variable from .env file, if not found or empty it returns 'default' cast as type 'cast'"""
    value = config(variable, default=default)

    return default if value == "" else config(variable, default=default, cast=cast)


class ENV(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    rpc_url: str
    rpc_fallback_url: str
    avatar_safe_address: Address
    disassembler_address: Address
    roles_mod_address: Address
    role: int
    mode: str
    web3: Optional[Web3] = None

    def __post_init__(self):
        self.avatar_safe_address = to_checksum_address(self.avatar_safe_address)
        self.roles_mod_address = to_checksum_address(self.roles_mod_address)

        if self.mode.lower() not in ["development", "production"]:
            raise ValueError(
                f"ENVIRONMENT is not valid: {self.mode}. Options are either 'development' or 'production'."
            )
        else:
            self.mode = self.mode.lower()

        if self.mode == Modes.PRODUCTION:
            self.web3 = start_the_engine(self)

    def __repr__(self):
        return "Environment variables"

    def with_fork(self, fork: PulleyFork):
        rpc_url = fork.url()
        return ENV(
            rpc_url=rpc_url,
            rpc_fallback_url=rpc_url,
            avatar_safe_address=self.avatar_safe_address,
            disassembler_address=self.disassembler_address,
            roles_mod_address=self.roles_mod_address,
            role=self.role,
            mode=self.mode,
            web3=None,
        )


@dataclass
class ExecConfig:
    percentage: float
    protocol: str
    exit_strategy: str
    exit_arguments: list[dict]


# -----------------------------------------------------------------------------------------------------------------------


def start_the_engine(env: ENV) -> Web3:
    if env.mode == Modes.DEVELOPMENT:
        w3 = Web3(Web3.HTTPProvider(env.rpc_url))
        fork_unlock_account(w3, env.disassembler_address)
        top_up_address(w3, env.disassembler_address, 1)
    else:
        w3 = Web3(Web3.HTTPProvider(env.rpc_url))
        if not w3.is_connected():
            w3 = Web3(Web3.HTTPProvider(env.rpc_fallback_url))
            if not w3.is_connected():
                time.sleep(2)
                w3 = Web3(Web3.HTTPProvider(env.rpc_url))
                if not w3.is_connected():
                    w3 = Web3(Web3.HTTPProvider(env.rpc_fallback_url))
                    if not w3.is_connected():
                        raise Exception("No connection to RPC endpoint")

    return w3


def bytes_to_hex_in_iterable(data):
    """Converts all atomic elements in nested lists or tuples from bytes to hex if they are bytes."""
    if isinstance(data, list):
        return [bytes_to_hex_in_iterable(element) for element in data]
    if isinstance(data, tuple):
        return tuple(bytes_to_hex_in_iterable(element) for element in data)
    elif isinstance(data, bytes):
        return "0x" + data.hex()
    else:
        return data


def decode_transaction(txns: list[ContractMethod], env: ENV) -> list[dict]:
    result = []
    for transactable in txns:
        tx = json.loads(transactable.abi)[0]
        for item, arg in zip(tx["inputs"], transactable.args_list):
            item["value"] = bytes_to_hex_in_iterable(arg)
        tx["to_address"] = transactable.contract_address
        tx["value"] = transactable.value
        tx["data"] = transactable.data
        tx["from_address"] = env.disassembler_address
        result.append(tx)
    return result


def disassembler_from_config(w3: Web3, env: ENV, protocol: str) -> Disassembler:
    disassembler_klass: Disassembler | None = {
        "Aura": AuraDisassembler,
        "Balancer": BalancerDisassembler,
        "Lido": LidoDisassembler,
        "Wallet": SwapDisassembler,
        "Maker": DSRDisassembler,
        "Spark": SparkDisassembler,
    }.get(protocol)

    if not disassembler_klass:
        raise Exception(f"Status 422: Invalid protocol: {protocol}")
    else:
        return disassembler_klass(
            w3=w3,
            avatar_safe_address=env.avatar_safe_address,
            roles_mod_address=env.roles_mod_address,
            role=env.role,
            signer_address=env.disassembler_address,
        )


def gear_up(w3: Web3, env: ENV, exec_config: ExecConfig) -> tuple[Disassembler, list[Transactable]]:
    disassembler = disassembler_from_config(w3, env, exec_config.protocol)

    strategy = getattr(disassembler, exec_config.exit_strategy)

    txn_transactables = strategy(percentage=exec_config.percentage, exit_arguments=exec_config.exit_arguments)

    return disassembler, txn_transactables


# -----------------------------------------------------------------------------------------------------------------------


# TODO: all tools for dev environment should be in roles_royce
def fork_unlock_account(w3, address):
    """Unlock the given address on the forked node."""
    return w3.provider.make_request("anvil_impersonateAccount", [address])


# These accounts are not guaranteed to hold tokens forever...
Holders = {
    Chain.ETHEREUM: "0x00000000219ab540356cBB839Cbe05303d7705Fa",  # BINANCE_ACCOUNT_WITH_LOTS_OF_ETH =
    Chain.GNOSIS: "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d",  # WXDAI_CONTRACT_WITH_LOTS_OF_XDAI =
}


def top_up_address(w3: Web3, address: str, amount: int) -> None:
    """Top up an address with ETH"""
    holder = Holders[Chain.get_blockchain_from_web3(w3)]
    if amount > (w3.eth.get_balance(holder) * 1e18) * 0.99:
        raise ValueError("Not enough ETH in the faucet account")
    fork_unlock_account(w3, holder)
    try:
        w3.eth.send_transaction({"to": address, "value": Web3.to_wei(amount, "ether"), "from": holder})
    except ContractLogicError:
        raise Exception("Address is a smart contract address with no payable function.")


def fork_reset_state(w3: Web3, url: str, block: int | str = "latest"):
    """Reset the state of the forked node to the state of the blockchain node at the given block.

    Args:
        w3: Web3 instance of the local node
        url: URL of the node from which to fork
        block: Block number at which to fork the blockchain, or "latest" to use the latest block
    """
    latest_block = Web3(Web3.HTTPProvider(url)).eth.block_number

    if isinstance(block, str):
        if block == "latest":
            block = latest_block
    else:
        if block > latest_block:
            raise ValueError(f"Block number {block} is greater than the latest block {latest_block}")
    return w3.provider.make_request("anvil_reset", [{"forking": {"jsonRpcUrl": url, "blockNumber": block}}])


# -----------------------------------------------------------------------------------------------------------------------


def recovery_mode_balancer(w3, bpt_address: str, exit_strategy: str, blockchain=None):
    blockchain = blockchain or Chain.get_blockchain_from_web3(w3)
    try:
        bpt_contract = w3.eth.contract(address=bpt_address, abi=BalancerAbis[blockchain].UniversalBPT.abi)
        bpt_pool_recovery_mode = bpt_contract.functions.inRecoveryMode().call()
    except ContractLogicError:
        logging.info("Balancer pool has no recovery mode")
        if exit_strategy == "exit_1_3" or exit_strategy == "exit_2_3":
            logging.info("Test will not execute")
            return True
        else:
            return False
    if bpt_pool_recovery_mode and (exit_strategy == "exit_1_1" or exit_strategy == "exit_2_1"):
        logging.info("Balancer pool is in recovery mode, not testing this exit_strategy")
        return True
    elif not bpt_pool_recovery_mode and (exit_strategy == "exit_1_3" or exit_strategy == "exit_2_3"):
        logging.info("Balancer pool is not in recovery mode, not testing this exit_strategy")
        return True
    else:
        return False
