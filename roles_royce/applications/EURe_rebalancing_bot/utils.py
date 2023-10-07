from dataclasses import dataclass, field
from decouple import config
from web3.types import Address, ChecksumAddress
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
from roles_royce.constants import Chain
import logging
from roles_royce.protocols.base import ContractMethod, InvalidArgument, AvatarAddress, Address
from roles_royce.applications.EURe_rebalancing_bot.addresses_and_abis import AddressesAndAbis
from decimal import Decimal
import threading
import requests
import json
import schedule
import time
from web3.types import TxReceipt
from roles_royce import roles


# The next helper function allows to leave variables unfilled in the .env file
def custom_config(variable, default, cast):
    value = config(variable, default=default)
    return default if value == '' else config(variable, default=default, cast=cast)


@dataclass
class ENV:
    RPC_ENDPOINT: str = config('RPC_ENDPOINT')
    FALLBACK_RPC_ENDPOINT: str = config('FALLBACK_RPC_ENDPOINT', default='')
    AVATAR_SAFE_ADDRESS: Address | ChecksumAddress | str = config('AVATAR_SAFE_ADDRESS')
    ROLES_MOD_ADDRESS: Address | ChecksumAddress | str = config('ROLES_MOD_ADDRESS')
    ROLE: int = config('ROLE', cast=int)
    PRIVATE_KEY: str = config('PRIVATE_KEY')
    FIXER_API_ACCESS_KEY: float = config('FIXER_API_ACCESS_KEY', cast=str)
    MAX_SLIPPAGE: float = custom_config('MAX_SLIPPAGE', default=0.01, cast=float)
    DRIFT_THRESHOLD: float = config('DRIFT_THRESHOLD', cast=float)
    AMOUNT: float = config('AMOUNT', cast=float)
    COOLDOWN_MINUTES: int = custom_config('COOLDOWN_MINUTES', default=5, cast=int)
    SLACK_WEBHOOK_URL: str = config('SLACK_WEBHOOK_URL', default='')
    TELEGRAM_BOT_TOKEN: str = config('TELEGRAM_BOT_TOKEN', default='')
    TELEGRAM_CHAT_ID: int = custom_config('TELEGRAM_CHAT_ID', default='', cast=int)
    PROMETHEUS_PORT: int = custom_config('PROMETHEUS_PORT', default=8000, cast=int)
    TEST_MODE: bool = config('TEST_MODE', default=False, cast=bool)
    LOCAL_FORK_PORT: int = custom_config('LOCAL_FORK_PORT', default=8545, cast=int)
    STATUS_NOTIFICATION_HOUR: int = custom_config('STATUS_NOTIFICATION_HOUR', default=12, cast=int)

    BOT_ADDRESS: Address | ChecksumAddress | str = field(init=False)

    def __post_init__(self):
        self.AVATAR_SAFE_ADDRESS = Web3.to_checksum_address(self.AVATAR_SAFE_ADDRESS)
        self.ROLES_MOD_ADDRESS = Web3.to_checksum_address(self.ROLES_MOD_ADDRESS)
        if not Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).is_connected():
            raise ValueError(f"RPC_ENDPOINT is not valid or not active: {self.RPC_ENDPOINT}.")
        self.BOT_ADDRESS = Web3(Web3.HTTPProvider(self.RPC_ENDPOINT)).eth.account.from_key(self.PRIVATE_KEY).address

    def __repr__(self):
        return 'Environment variables'


logger = logging.getLogger(__name__)

decimalsEURe = 18
decimalsWXDAI = 18


class SwapWXDAIforEURe(ContractMethod):
    name = "exchange_underlying"
    in_signature = [("i", "uint256"), ("j", "uint256"), ("_dx", "uint256"), ("_min_dy", "uint256")]
    target_address = AddressesAndAbis[Chain.GnosisChain].DepositZap.address
    fixed_arguments = {"i": 1, "j": 0}

    def __init__(self, avatar: Address, amount: int, min_amount_out: int):
        super().__init__(avatar=avatar)
        self.args._dx = amount
        self.args._min_dy = min_amount_out


class SwapEUReForWXDAI(ContractMethod):
    name = "exchange_underlying"
    in_signature = [("i", "uint256"), ("j", "uint256"), ("_dx", "uint256"), ("_min_dy", "uint256")]
    target_address = AddressesAndAbis[Chain.GnosisChain].DepositZap.address
    fixed_arguments = {"i": 0, "j": 1}

    def __init__(self, avatar: Address, amount: int, min_amount_out):
        super().__init__(avatar=avatar)
        self.args._dx = amount
        self.args._min_dy = min_amount_out


@dataclass
class SwapsData:
    amount_WXDAI: float
    amount_EURe: float
    EURe_to_WXDAI: float
    WXDAI_to_EURe: float
    EUR_price: float

    def get_EURe_to_WXDAI_drift(self) -> float:
        return self.EURe_to_WXDAI / (self.EUR_price * self.amount_EURe) - 1

    def get_WXDAI_to_EURe_drift(self) -> float:
        return self.EURe_to_WXDAI / (self.amount_WXDAI / self.EUR_price) - 1


class SwapsDataManager:
    w3: Web3

    def __init__(self, w3: Web3):
        self.w3 = w3

    def get_EURe_to_WXDAI_curve(self, amount: float) -> float:
        contract = self.w3.eth.contract(address=AddressesAndAbis[Chain.GnosisChain].DepositZap.address,
                                        abi=AddressesAndAbis[Chain.GnosisChain].DepositZap.abi)
        amount_int = int(amount * (10 ** decimalsEURe))
        if amount_int == 0:
            raise ValueError('Amount of EURe too small. Amount of EURe: %f.' % (amount * (10 ** decimalsEURe)))
        rate = contract.functions.get_dy_underlying(0, 1, amount_int).call()
        return float(Decimal(rate) / Decimal(10 ** decimalsEURe))

    def get_WXDAI_to_EURe_curve(self, amount: float) -> float:
        contract = self.w3.eth.contract(address=AddressesAndAbis[Chain.GnosisChain].DepositZap.address,
                                        abi=AddressesAndAbis[Chain.GnosisChain].DepositZap.abi)
        amount_int = int(Decimal(amount) * Decimal(10 ** decimalsWXDAI))
        if amount_int == 0:
            raise ValueError('Amount of WXDAI too small. Amount of WXDAI: %f.' % (amount * (10 ** decimalsWXDAI)))
        rate = contract.functions.get_dy_underlying(1, 0, amount_int).call()
        return float(Decimal(rate) / Decimal(10 ** decimalsWXDAI))

    def get_EUR_oracle_price(self):
        data_from_api = requests.get(
            'https://data.fixer.io/api/latest?access_key=%s&base=EUR&symbols=USD' % ENV.FIXER_API_ACCESS_KEY)
        if data_from_api.status_code == 200:
            response = json.loads(data_from_api.content.decode('utf-8'))
            if response['success']:
                return response['rates']['USD']
        contract = self.w3.eth.contract(address=AddressesAndAbis[Chain.GnosisChain].ChainlinkFeed.address,
                                        abi=AddressesAndAbis[Chain.GnosisChain].ChainlinkFeed.abi)
        chainlink_price = float(Decimal(contract.functions.latestAnswer().call()) / Decimal((10 ** 8)))
        return chainlink_price

    def get_data(self, amount_WXDAI: float, amount_EURe: float) -> SwapsData:
        EURe_price = self.get_EUR_oracle_price()
        WXDAI_to_EURe = self.get_WXDAI_to_EURe_curve(amount_WXDAI)
        EURe_to_WXDAI = self.get_EURe_to_WXDAI_curve(amount_EURe)
        return SwapsData(amount_WXDAI, amount_EURe, EURe_to_WXDAI, WXDAI_to_EURe, EURe_price)


class Swapper:
    w3: Web3
    avatar_safe_address: str
    roles_mod_address: str
    role: int
    private_keys: str
    max_slippage: float

    def __init__(self, w3: Web3, avatar_safe_address: str, roles_mod_address: str, role: int, private_keys: str,
                 max_slippage: float):
        self.w3 = w3
        self.avatar_safe_address = Web3.to_checksum_address(avatar_safe_address)
        self.roles_mod_address = Web3.to_checksum_address(roles_mod_address)
        self.role = role
        self.private_keys = private_keys
        self.max_slippage = max_slippage

    def swap_EURe_for_WXDAI(self, swaps_data: SwapsData) -> TxReceipt:
        min_amount_out = int(
            Decimal(1 - self.max_slippage) * Decimal(swaps_data.EURe_to_WXDAI) * Decimal(10 ** decimalsWXDAI))
        amount = int(Decimal(swaps_data.amount_EURe) * Decimal(10 ** decimalsEURe))
        return roles.send(
            [SwapEUReForWXDAI(amount=amount, min_amount_out=min_amount_out,
                              avatar=self.avatar_safe_address)],
            role=self.role, private_key=self.private_keys, roles_mod_address=self.roles_mod_address, web3=self.w3)

    def swap_WXDAI_for_EURe(self, swaps_data: SwapsData) -> TxReceipt:
        min_amount_out = int(
            Decimal(1 - self.max_slippage) * Decimal(swaps_data.WXDAI_to_EURe) * Decimal(10 ** decimalsEURe))
        amount = int(Decimal(swaps_data.amount_WXDAI) * Decimal(10 ** decimalsWXDAI))
        return roles.send(
            [SwapWXDAIforEURe(amount=amount, min_amount_out=min_amount_out,
                              avatar=self.avatar_safe_address)],
            role=self.role, private_key=self.private_keys, roles_mod_address=self.roles_mod_address, web3=self.w3)


def log_initial_data(env: ENV, messenger: Messenger):
    title = "EURe rebalancing bot started"
    message = (f"  Avatar safe address: {env.AVATAR_SAFE_ADDRESS}\n"
               f"  Roles mod address: {env.ROLES_MOD_ADDRESS}\n"
               f"  Bot address: {env.BOT_ADDRESS}\n"
               f"  Drift threshold: {env.DRIFT_THRESHOLD*100}%%\n"
               f"  Initial amount to swap: {env.AMOUNT}\n"
               f"  Cooldown Minutes: {env.COOLDOWN_MINUTES}\n")

    messenger.log_and_alert(LoggingLevel.Info, title, message)


class SchedulerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True

    def run(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.running = False
