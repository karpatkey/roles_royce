from dataclasses import dataclass, field
from decouple import config
from web3.types import Address
from web3 import Web3
from roles_royce.protocols.base import Address
from defabipedia.types import Blockchain
from eth_account import Account


# The next helper function allows to leave variables unfilled in the .env file
def custom_config(variable, default, cast):
    value = config(variable, default=default)
    return default if value == '' else config(variable, default=default, cast=cast)


@dataclass
class ENV:
    DAO: str
    BLOCKCHAIN: str

    TENDERLY_ACCOUNT_ID: str = config('TENDERLY_ACCOUNT_ID', default='')
    TENDERLY_PROJECT: str = config('TENDERLY_PROJECT', default='')
    TENDERLY_API_TOKEN: str = config('TENDERLY_API_TOKEN', default='')

    RPC_ENDPOINT: str = field(init=False)
    FALLBACK_RPC_ENDPOINT: str = field(init=False)
    AVATAR_SAFE_ADDRESS: Address = field(init=False)
    ROLES_MOD_ADDRESS: Address = field(init=False)
    ROLE: int = field(init=False)
    PRIVATE_KEY: str = field(init=False)
    SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
    DISASSEMBLER_ADDRESS: Address = field(init=False)
    ENVIRONMENT: str = custom_config('ENVIRONMENT', cast=str, default='development')
    LOCAL_FORK_PORT: int | None = custom_config('LOCAL_FORK_PORT', cast=int, default=None)

    def __post_init__(self):
        if self.DAO not in ['GnosisDAO', 'GnosisLTD']:
            raise ValueError(f"DAO is not valid: {self.DAO}.")
        if self.BLOCKCHAIN.lower() not in ['mainnet', 'ethereum', 'gnosis']:
            raise ValueError(f"BLOCKCHAIN is not valid: {self.BLOCKCHAIN}. Options are either 'ethereum' or 'gnosis'.")
        elif self.BLOCKCHAIN.lower() == 'mainnet':
            self.BLOCKCHAIN = 'ethereum'
        self.BLOCKCHAIN = self.BLOCKCHAIN.lower()
        self.RPC_ENDPOINT: str = config(self.BLOCKCHAIN.upper() + '_RPC_ENDPOINT', default='')
        self.FALLBACK_RPC_ENDPOINT: str = config(self.BLOCKCHAIN.upper() + '_FALLBACK_RPC_ENDPOINT', default='')
        self.AVATAR_SAFE_ADDRESS: Address = config(self.DAO.upper() + '_' + self.BLOCKCHAIN.upper() + '_AVATAR_SAFE_ADDRESS', default='')
        self.ROLES_MOD_ADDRESS: Address = config(self.DAO.upper() + '_' + self.BLOCKCHAIN.upper() + '_ROLES_MOD_ADDRESS', default='')
        self.ROLE: int = config(self.DAO.upper() + '_' + self.BLOCKCHAIN.upper() + '_ROLE', cast=int, default=0)
        self.PRIVATE_KEY: str = config(self.DAO.upper() + '_' + self.BLOCKCHAIN.upper() + '_PRIVATE_KEY', default='')
        self.SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        if self.PRIVATE_KEY != '':
            self.DISASSEMBLER_ADDRESS = Account.from_key(self.PRIVATE_KEY).address
        else:
            self.DISASSEMBLER_ADDRESS = config(self.DAO.upper() + '_' + self.BLOCKCHAIN.upper() + '_DISASSEMBLER_ADDRESS', default='')
        if self.ENVIRONMENT.lower() not in ['development', 'production']:
            raise ValueError(f"ENVIRONMENT is not valid: {self.ENVIRONMENT}. Options are either 'development' or 'production'.")
        else:
            self.ENVIRONMENT = self.ENVIRONMENT.lower()
        if self.BLOCKCHAIN == 'ethereum':
            self.LOCAL_FORK_PORT = custom_config('LOCAL_FORK_PORT_ETHEREUM', cast=int, default=8546)
        else:
            self.LOCAL_FORK_PORT = custom_config('LOCAL_FORK_PORT_GNOSIS', cast=int, default=8547)

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
