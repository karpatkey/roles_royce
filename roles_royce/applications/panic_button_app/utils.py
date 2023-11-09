from dataclasses import dataclass, field
from decouple import config
from web3.types import Address
from web3 import Web3
from roles_royce.protocols.base import Address
from defabipedia.types import Chains
from eth_account import Account
from roles_royce.constants import StrEnum
from web3.exceptions import ContractLogicError


class Modes(StrEnum):
    DEVELOPMENT = 'development'
    PRODUCTION = 'production'


# The next helper function allows to leave env variables unfilled in the .env file
def custom_config(variable, default, cast):
    """Attempts to read variable from .env file, if not found or empty it returns 'default' cast as type 'cast'"""
    value = config(variable, default=default)

    return default if value == '' else config(variable, default=default, cast=cast)


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

    SLACK_WEBHOOK_URL: str = field(init=False)


    def __post_init__(self):
        # Tenderly credentials
        self.TENDERLY_ACCOUNT_ID: str = config('TENDERLY_ACCOUNT_ID', default='')
        self.TENDERLY_PROJECT: str = config('TENDERLY_PROJECT', default='')
        self.TENDERLY_API_TOKEN: str = config('TENDERLY_API_TOKEN', default='')

        # DAO and blockchain
        if self.DAO not in ['GnosisDAO', 'GnosisLTD']:
            raise ValueError(f"DAO is not valid: {self.DAO}.")
        if self.BLOCKCHAIN.lower() not in ['mainnet', 'ethereum', 'gnosis']:
            raise ValueError(f"BLOCKCHAIN is not valid: {self.BLOCKCHAIN}. Options are either 'ethereum' or 'gnosis'.")
        elif self.BLOCKCHAIN.lower() == 'mainnet':
            self.BLOCKCHAIN = 'ethereum'
        self.BLOCKCHAIN = self.BLOCKCHAIN.lower()

        # RPC endpoints
        self.RPC_ENDPOINT: str = config(self.BLOCKCHAIN.upper() + '_RPC_ENDPOINT', default='')
        self.RPC_ENDPOINT_FALLBACK: str = config(self.BLOCKCHAIN.upper() + '_RPC_ENDPOINT_FALLBACK', default='')
        self.RPC_ENDPOINT_FALLBACK: str = config(self.BLOCKCHAIN.upper() + '_RPC_ENDPOINT_MEV', default='')


        # Configuration addresses and key
        self.AVATAR_SAFE_ADDRESS: Address = config(
            self.DAO.upper() + '_' + self.BLOCKCHAIN.upper() + '_AVATAR_SAFE_ADDRESS', default='')
        self.ROLES_MOD_ADDRESS: Address = config(
            self.DAO.upper() + '_' + self.BLOCKCHAIN.upper() + '_ROLES_MOD_ADDRESS', default='')
        self.ROLE: int = config(self.DAO.upper() + '_' + self.BLOCKCHAIN.upper() + '_ROLE', cast=int, default=0)
        self.PRIVATE_KEY: str = config(self.DAO.upper() + '_' + self.BLOCKCHAIN.upper() + '_PRIVATE_KEY', default='')
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        if self.PRIVATE_KEY != '':
            self.DISASSEMBLER_ADDRESS = Account.from_key(self.PRIVATE_KEY).address
        else:
            self.DISASSEMBLER_ADDRESS = config(
                self.DAO.upper() + '_' + self.BLOCKCHAIN.upper() + '_DISASSEMBLER_ADDRESS', default='')

        # Environment mode: development or production
        self.MODE: Modes = custom_config('ENVIRONMENT', cast=Modes, default=Modes.DEVELOPMENT)
        if self.MODE.lower() not in ['development', 'production']:
            raise ValueError(
                f"ENVIRONMENT is not valid: {self.MODE}. Options are either 'development' or 'production'.")
        else:
            self.MODE = self.MODE.lower()
        if self.MODE == Modes.DEVELOPMENT:
            if self.BLOCKCHAIN == 'ethereum':
                self.LOCAL_FORK_PORT = custom_config('LOCAL_FORK_PORT_ETHEREUM', cast=int, default=8546)
            else:
                self.LOCAL_FORK_PORT = custom_config('LOCAL_FORK_PORT_GNOSIS', cast=int, default=8547)
        else:
            self.LOCAL_FORK_PORT = None
        self.LOCAL_FORK_HOST: str = custom_config('LOCAL_FORK_HOST', default='localhost', cast=str)

        self.SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')

    def __repr__(self):
        return 'Environment variables'


@dataclass
class ExecConfig:
    percentage: float
    simulate: bool
    dao: str
    blockchain: str
    protocol: str
    exit_strategy: str
    exit_arguments: list[dict]


# -----------------------------------------------------------------------------------------------------------------------

# TODO: all tools for dev environment should be in roles_royce
def fork_unlock_account(w3, address):
    """Unlock the given address on the forked node."""
    return w3.provider.make_request("anvil_impersonateAccount", [address])

# This accounts are not guaranteed to hold tokens forever...
Holders = {
    Chains.Ethereum: '0x00000000219ab540356cBB839Cbe05303d7705Fa',  # BINANCE_ACCOUNT_WITH_LOTS_OF_ETH =
    Chains.Gnosis: '0xe91d153e0b41518a2ce8dd3d7944fa863463a97d'  # WXDAI_CONTRACT_WITH_LOTS_OF_XDAI =
}


def top_up_address(w3: Web3, address: str, amount: int) -> None:
    """Top up an address with ETH"""
    holder = Holders[Chains.get_blockchain_from_web3(w3)]
    if amount > (w3.eth.get_balance(holder) * 1e18) * 0.99:
        raise ValueError("Not enough ETH in the faucet account")
    fork_unlock_account(w3, holder)
    try:
        w3.eth.send_transaction(
            {"to": address, "value": Web3.to_wei(amount, "ether"), "from": holder})
    except ContractLogicError:
        raise Exception("Address is a smart contract address with no payable function.")

# -----------------------------------------------------------------------------------------------------------------------
