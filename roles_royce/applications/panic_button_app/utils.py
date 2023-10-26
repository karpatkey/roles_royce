from dataclasses import dataclass, field
from decouple import config
from web3.types import Address
from web3 import Web3
from roles_royce.protocols.base import Address
from roles_royce.constants import Blockchain


# The next helper function allows to leave variables unfilled in the .env file
def custom_config(variable, default, cast):
    value = config(variable, default=default)
    return default if value == '' else config(variable, default=default, cast=cast)


@dataclass
class ENV:
    DAO: str
    BLOCKCHAIN: str

    TENDERLY_ACCOUNT_ID: str = config('TENDERLY_ACCOUNT_ID')
    TENDERLY_PROJECT: str = config('TENDERLY_PROJECT')
    TENDERLY_API_TOKEN: str = config('TENDERLY_API_TOKEN')

    RPC_ENDPOINT: str = field(init=False)
    FALLBACK_RPC_ENDPOINT: str = field(init=False)
    AVATAR_SAFE_ADDRESS: Address = field(init=False)
    ROLES_MOD_ADDRESS: Address = field(init=False)
    ROLE: int = field(init=False)
    PRIVATE_KEY: str = field(init=False)
    SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
    BOT_ADDRESS: Address = field(init=False)

    def __post_init__(self):
        if self.DAO not in ['GnosisDAO', 'GnosisLTD']:
            raise ValueError(f"DAO is not valid: {self.DAO}.")
        if self.BLOCKCHAIN not in ['mainnet', 'gnosis']:
            raise ValueError(f"BLOCKCHAIN is not valid: {self.BLOCKCHAIN}.")
        self.RPC_ENDPOINT: str = config(self.BLOCKCHAIN.upper() + 'RPC_ENDPOINT')
        self.FALLBACK_RPC_ENDPOINT: str = config(self.BLOCKCHAIN.upper() + 'FALLBACK_RPC_ENDPOINT')
        self.AVATAR_SAFE_ADDRESS: Address = config(self.DAO.upper() + self.BLOCKCHAIN.upper() + 'AVATAR_SAFE_ADDRESS')
        self.ROLES_MOD_ADDRESS: Address = config(self.DAO.upper() + self.BLOCKCHAIN.upper() + 'ROLES_MOD_ADDRESS')
        self.ROLE: int = config(self.DAO.upper() + self.BLOCKCHAIN.upper() + 'ROLE', cast=int)
        self.PRIVATE_KEYS: str = config(self.DAO.upper() + self.BLOCKCHAIN.upper() + 'PRIVATE_KEYS')
        self.SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)

    def __repr__(self):
        return 'Environment variables'


@dataclass
class ExecConfig:
    percentage: int
    simulate: bool
    dao: str
    blockchain: str
    protocol: str
    exit_strategy: str
    exit_arguments: list[dict]
