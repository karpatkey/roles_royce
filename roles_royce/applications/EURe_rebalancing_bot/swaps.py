import json
from dataclasses import dataclass, field
from decimal import Decimal

import requests
from defabipedia.chainlink import ContractSpecs as ChainlinkContractSpecs
from defabipedia.curve import ContractSpecs as CurveContractSpecs
from defabipedia.types import Chain
from web3 import Web3
from web3.types import TxReceipt

from roles_royce import roles
from roles_royce.protocols.base import Address, ContractMethod
from roles_royce.utils import to_checksum_address

decimalsEURe = 18
decimalsWXDAI = 18


class SwapWXDAIforEURe(ContractMethod):
    name = "exchange_underlying"
    in_signature = [("i", "uint256"), ("j", "uint256"), ("_dx", "uint256"), ("_min_dy", "uint256")]
    target_address = CurveContractSpecs[Chain.GNOSIS].EURe_x3RCV_deposit_zap.address
    fixed_arguments = {"i": 1, "j": 0}

    def __init__(self, avatar: Address, amount: int, min_amount_out: int):
        super().__init__(avatar=avatar)
        self.args._dx = amount
        self.args._min_dy = min_amount_out


class SwapEUReForWXDAI(ContractMethod):
    name = "exchange_underlying"
    in_signature = [("i", "uint256"), ("j", "uint256"), ("_dx", "uint256"), ("_min_dy", "uint256")]
    target_address = CurveContractSpecs[Chain.GNOSIS].EURe_x3RCV_deposit_zap.address
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
    drift_EURe_to_WXDAI: float = field(init=False)
    drift_WXDAI_to_EURe: float = field(init=False)

    def __post_init__(self):
        self.drift_EURe_to_WXDAI = self.EURe_to_WXDAI / (self.EUR_price * self.amount_EURe) - 1
        self.drift_WXDAI_to_EURe = self.WXDAI_to_EURe / (self.amount_WXDAI / self.EUR_price) - 1


class SwapsDataManager:
    def __init__(self, w3: Web3, fixer_api_key: str = ""):
        self.w3 = w3
        self.fixer_api_key = fixer_api_key

    def get_EURe_to_WXDAI_curve(self, amount: float) -> float:
        """
        Returns the amount of WXDAI that would be received in a swap for the given amount of EURe.

        Args:
            amount: Amount of EURe to swap.

        Returns:
            Amount of WXDAI that would be received in a swap for the given amount of EURe.
        """
        contract = CurveContractSpecs[Chain.GNOSIS].EURe_x3RCV_deposit_zap.contract(self.w3)

        amount_int = int(amount * (10**decimalsEURe))
        if amount_int == 0:
            raise ValueError("Amount of EURe too small. Amount of EURe: %f." % (amount * (10**decimalsEURe)))
        rate = contract.functions.get_dy_underlying(0, 1, amount_int).call()
        return float(Decimal(rate) / Decimal(10**decimalsEURe))

    def get_WXDAI_to_EURe_curve(self, amount: float) -> float:
        """
        Returns the amount of EURe that would be received in a swap for the given amount of WXDAI.

        Args:
            amount: Amount of WXDAI to swap.

        Returns:
            Amount of EURe that would be received in a swap for the given amount of WXDAI.
        """

        contract = CurveContractSpecs[Chain.GNOSIS].EURe_x3RCV_deposit_zap.contract(self.w3)
        amount_int = int(Decimal(amount) * Decimal(10**decimalsWXDAI))
        if amount_int == 0:
            raise ValueError("Amount of WXDAI too small. Amount of WXDAI: %f." % (amount * (10**decimalsWXDAI)))
        rate = contract.functions.get_dy_underlying(1, 0, amount_int).call()
        return float(Decimal(rate) / Decimal(10**decimalsWXDAI))

    def get_EUR_oracle_price(self):
        """
        Returns the EUR price in USD. If a Fixer api key is set, it will get the price from the Fixer API. Otherwise,
        it will get the price from the Chainlink price feed.

        Args:

        Returns:
            EUR price in USD.
        """
        if self.fixer_api_key != "":
            data_from_api = requests.get(
                "https://data.fixer.io/api/latest?access_key=%s&base=EUR&symbols=USD" % self.fixer_api_key
            )
            if data_from_api.status_code == 200:
                response = json.loads(data_from_api.content.decode("utf-8"))
                if response["success"]:
                    return response["rates"]["USD"]
        contract = ChainlinkContractSpecs[Chain.GNOSIS].EurPriceFeed.contract(self.w3)
        chainlink_price = float(Decimal(contract.functions.latestAnswer().call()) / Decimal((10**8)))
        return chainlink_price

    def get_data(self, amount_WXDAI: float, amount_EURe: float) -> SwapsData:
        EURe_price = self.get_EUR_oracle_price()
        WXDAI_to_EURe = self.get_WXDAI_to_EURe_curve(amount_WXDAI)
        EURe_to_WXDAI = self.get_EURe_to_WXDAI_curve(amount_EURe)
        return SwapsData(amount_WXDAI, amount_EURe, EURe_to_WXDAI, WXDAI_to_EURe, EURe_price)


class Swapper:
    def __init__(
        self,
        w3: Web3,
        avatar_safe_address: str,
        roles_mod_address: str,
        role: int,
        private_keys: str,
        max_slippage: float,
    ):
        self.w3 = w3
        self.avatar_safe_address = to_checksum_address(avatar_safe_address)
        self.roles_mod_address = to_checksum_address(roles_mod_address)
        self.role = role
        self.private_keys = private_keys
        self.max_slippage = max_slippage

    def swap_EURe_for_WXDAI(self, swaps_data: SwapsData) -> TxReceipt:
        min_amount_out = int(
            Decimal(1 - self.max_slippage) * Decimal(swaps_data.EURe_to_WXDAI) * Decimal(10**decimalsWXDAI)
        )
        amount = int(Decimal(swaps_data.amount_EURe) * Decimal(10**decimalsEURe))
        return roles.send(
            [SwapEUReForWXDAI(amount=amount, min_amount_out=min_amount_out, avatar=self.avatar_safe_address)],
            role=self.role,
            private_key=self.private_keys,
            roles_mod_address=self.roles_mod_address,
            web3=self.w3,
        )

    def swap_WXDAI_for_EURe(self, swaps_data: SwapsData) -> TxReceipt:
        min_amount_out = int(
            Decimal(1 - self.max_slippage) * Decimal(swaps_data.WXDAI_to_EURe) * Decimal(10**decimalsEURe)
        )
        amount = int(Decimal(swaps_data.amount_WXDAI) * Decimal(10**decimalsWXDAI))
        return roles.send(
            [SwapWXDAIforEURe(amount=amount, min_amount_out=min_amount_out, avatar=self.avatar_safe_address)],
            role=self.role,
            private_key=self.private_keys,
            roles_mod_address=self.roles_mod_address,
            web3=self.w3,
        )
