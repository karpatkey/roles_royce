import json
import logging
import time
from dataclasses import dataclass, field

from decouple import config
from defabipedia.aura import Abis as AuraAbis
from defabipedia.balancer import Abis as BalancerAbis
from defabipedia.types import Chain
from eth_account import Account
from web3 import Web3
from web3.exceptions import ContractLogicError
from web3.types import Address

from roles_royce.constants import StrEnum
from roles_royce.generic_method import Transactable
from roles_royce.protocols.base import Address, ContractMethod
from roles_royce.toolshed.disassembling import (
    AuraDisassembler,
    BalancerDisassembler,
    Disassembler,
    LidoDisassembler,
    SwapDisassembler,
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


@dataclass
class ENV:
    DAO: str
    BLOCKCHAIN: str

    TENDERLY_ACCOUNT_ID: str = field(init=False)
    TENDERLY_PROJECT: str = field(init=False)
    TENDERLY_API_TOKEN: str = field(init=False)

    RPC_ENDPOINT: str = field(init=False)
    RPC_ENDPOINT_FALLBACK: str = field(init=False)
    RPC_ENDPOINT_MEV: str = field(init=False)

    AVATAR_SAFE_ADDRESS: Address = field(init=False)
    ROLES_MOD_ADDRESS: Address = field(init=False)
    ROLE: int = field(init=False)
    PRIVATE_KEY: str = field(init=False)
    DISASSEMBLER_ADDRESS: Address = field(init=False)

    MODE: Modes = field(init=False)
    LOCAL_FORK_PORT: int | None = field(init=False)
    LOCAL_FORK_HOST: str = field(init=False)

    local_fork_url: str | None = field(init=True, default=None)
    LOCAL_FORK_URL: str = field(init=False)

    SLACK_WEBHOOK_URL: str = field(init=False)

    def __post_init__(self):
        # Tenderly credentials
        self.TENDERLY_ACCOUNT_ID: str = config("TENDERLY_ACCOUNT_ID", default="")
        self.TENDERLY_PROJECT: str = config("TENDERLY_PROJECT", default="")
        self.TENDERLY_API_TOKEN: str = config("TENDERLY_API_TOKEN", default="")

        # DAO and blockchain
        if self.DAO not in [
            "GnosisDAO",
            "GnosisLtd",
            "karpatkey",
            "ENS",
            "BalancerDAO",
        ]:
            raise ValueError(f"DAO is not valid: {self.DAO}.")
        if self.BLOCKCHAIN.lower() not in ["mainnet", "ethereum", "gnosis"]:
            raise ValueError(f"BLOCKCHAIN is not valid: {self.BLOCKCHAIN}. Options are either 'ethereum' or 'gnosis'.")
        elif self.BLOCKCHAIN.lower() == "mainnet":
            self.BLOCKCHAIN = "ethereum"
        self.BLOCKCHAIN = self.BLOCKCHAIN.lower()

        # RPC endpoints
        self.RPC_ENDPOINT: str = config(self.BLOCKCHAIN.upper() + "_RPC_ENDPOINT", default="")
        self.RPC_ENDPOINT_FALLBACK: str = config(self.BLOCKCHAIN.upper() + "_RPC_ENDPOINT_FALLBACK", default="")
        self.RPC_ENDPOINT_MEV: str = config(self.BLOCKCHAIN.upper() + "_RPC_ENDPOINT_MEV", default="")

        # Configuration addresses and key
        self.AVATAR_SAFE_ADDRESS: Address = config(
            self.DAO.upper() + "_" + self.BLOCKCHAIN.upper() + "_AVATAR_SAFE_ADDRESS",
            default="",
        )
        self.ROLES_MOD_ADDRESS: Address = config(
            self.DAO.upper() + "_" + self.BLOCKCHAIN.upper() + "_ROLES_MOD_ADDRESS",
            default="",
        )
        self.ROLE: int = config(
            self.DAO.upper() + "_" + self.BLOCKCHAIN.upper() + "_ROLE",
            cast=int,
            default=0,
        )
        self.PRIVATE_KEY: str = config(
            self.DAO.upper() + "_" + self.BLOCKCHAIN.upper() + "_PRIVATE_KEY",
            default="",
        )
        self.AVATAR_SAFE_ADDRESS = to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = to_checksum_address(self.ROLES_MOD_ADDRESS)
        if self.PRIVATE_KEY != "":
            self.DISASSEMBLER_ADDRESS = Account.from_key(self.PRIVATE_KEY).address
        else:
            self.DISASSEMBLER_ADDRESS = config(
                self.DAO.upper() + "_" + self.BLOCKCHAIN.upper() + "_DISASSEMBLER_ADDRESS",
                default="",
            )

        # Environment mode: development or production
        self.MODE: Modes = custom_config("ENVIRONMENT", cast=Modes, default=Modes.DEVELOPMENT)
        if self.MODE.lower() not in ["development", "production"]:
            raise ValueError(
                f"ENVIRONMENT is not valid: {self.MODE}. Options are either 'development' or 'production'."
            )
        else:
            self.MODE = self.MODE.lower()
        if self.MODE == Modes.DEVELOPMENT:
            if self.BLOCKCHAIN == "ethereum":
                self.LOCAL_FORK_PORT = custom_config("LOCAL_FORK_PORT_ETHEREUM", cast=int, default=8546)
            else:
                self.LOCAL_FORK_PORT = custom_config("LOCAL_FORK_PORT_GNOSIS", cast=int, default=8547)
        else:
            self.LOCAL_FORK_PORT = None
        self.LOCAL_FORK_HOST: str = custom_config(
            "LOCAL_FORK_HOST" + "_" + self.BLOCKCHAIN.upper(),
            default="localhost",
            cast=str,
        )

        self.LOCAL_FORK_URL = self.local_fork_url or config("LOCAL_FORK_URL", default="")

        self.SLACK_WEBHOOK_URL: str = config("SLACK_WEBHOOK_URL", default="")

    def __repr__(self):
        return "Environment variables"


@dataclass
class ExecConfig:
    percentage: float
    dao: str
    blockchain: str
    protocol: str
    exit_strategy: str
    exit_arguments: list[dict]


# -----------------------------------------------------------------------------------------------------------------------


def start_the_engine(env: ENV) -> tuple[Web3, Web3]:
    if env.MODE == Modes.DEVELOPMENT:
        w3 = Web3(Web3.HTTPProvider(env.LOCAL_FORK_URL or f"http://{env.LOCAL_FORK_HOST}:{env.LOCAL_FORK_PORT}"))
        fork_unlock_account(w3, env.DISASSEMBLER_ADDRESS)
        top_up_address(w3, env.DISASSEMBLER_ADDRESS, 1)
        w3_MEV = w3
    else:
        w3 = Web3(Web3.HTTPProvider(env.RPC_ENDPOINT))
        if not w3.is_connected():
            w3 = Web3(Web3.HTTPProvider(env.RPC_ENDPOINT_FALLBACK))
            if not w3.is_connected():
                time.sleep(2)
                w3 = Web3(Web3.HTTPProvider(env.RPC_ENDPOINT))
                if not w3.is_connected():
                    w3 = Web3(Web3.HTTPProvider(env.RPC_ENDPOINT_FALLBACK))
                    if not w3.is_connected():
                        raise Exception("No connection to RPC endpoint")
        w3_MEV = Web3(Web3.HTTPProvider(env.RPC_ENDPOINT_MEV))
        if not w3_MEV.is_connected():
            w3_MEV = Web3(Web3.HTTPProvider(env.RPC_ENDPOINT))
            if not w3_MEV.is_connected():
                w3_MEV = Web3(Web3.HTTPProvider(env.RPC_ENDPOINT_FALLBACK))
                if not w3_MEV.is_connected():
                    raise Exception("No connection to RPC endpoint")

    return w3, w3_MEV


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
        tx["from_address"] = env.DISASSEMBLER_ADDRESS
        result.append(tx)
    return result


def gear_up(w3: Web3, env: ENV, exec_config: ExecConfig) -> (Disassembler, list[Transactable]):
    if exec_config.protocol == "Aura":
        disassembler = AuraDisassembler(
            w3=w3,
            avatar_safe_address=env.AVATAR_SAFE_ADDRESS,
            roles_mod_address=env.ROLES_MOD_ADDRESS,
            role=env.ROLE,
            signer_address=env.DISASSEMBLER_ADDRESS,
        )

    elif exec_config.protocol == "Balancer":
        disassembler = BalancerDisassembler(
            w3=w3,
            avatar_safe_address=env.AVATAR_SAFE_ADDRESS,
            roles_mod_address=env.ROLES_MOD_ADDRESS,
            role=env.ROLE,
            signer_address=env.DISASSEMBLER_ADDRESS,
        )
    elif exec_config.protocol == "Lido":
        disassembler = LidoDisassembler(
            w3=w3,
            avatar_safe_address=env.AVATAR_SAFE_ADDRESS,
            roles_mod_address=env.ROLES_MOD_ADDRESS,
            role=env.ROLE,
            signer_address=env.DISASSEMBLER_ADDRESS,
        )
    elif exec_config.protocol == "Wallet":
        disassembler = SwapDisassembler(
            w3=w3,
            avatar_safe_address=env.AVATAR_SAFE_ADDRESS,
            roles_mod_address=env.ROLES_MOD_ADDRESS,
            role=env.ROLE,
            signer_address=env.DISASSEMBLER_ADDRESS,
        )
    else:
        raise Exception("Status 422: Invalid protocol")

    exit_strategy = getattr(disassembler, exec_config.exit_strategy)

    txn_transactables = exit_strategy(percentage=exec_config.percentage, exit_arguments=exec_config.exit_arguments)

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
