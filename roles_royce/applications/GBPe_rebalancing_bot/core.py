import json
from dataclasses import dataclass, field
from decimal import Decimal

import requests
from defabipedia.chainlink import ContractSpecs as ChainlinkContractSpecs
from defabipedia.curve import ContractSpecs as CurveContractSpecs
from defabipedia.tokens import Addresses, erc20_contract
from defabipedia.types import Chain
from web3 import Web3
from web3.types import TxReceipt

from roles_royce import roles
from roles_royce.applications.GBPe_rebalancing_bot.env import ENV
from roles_royce.applications.utils import to_dict
from roles_royce.protocols.base import Address, ContractMethod


@dataclass
class StaticData:
    env: ENV
    decimals_GBPe: int = 18
    decimals_x3CRV = 18

    def __str__(self):
        return json.dumps(to_dict(self, exclude_key="PRIVATE_KEY"), indent=4)


@dataclass
class DynamicData:
    amount_x3CRV: float
    amount_GBPe: float
    GBPe_to_x3CRV: float
    x3CRV_to_GBPe: float
    GBP_price: float
    x3CRV_price: float
    x3CRV_balance: int
    GBPe_balance: int
    bot_xDAI_balance: int
    drift_GBPe_to_USD: float = field(init=False)
    drift_USD_to_GBPe: float = field(init=False)

    def __post_init__(self):
        self.drift_GBPe_to_x3CRV = self.GBPe_to_x3CRV * self.x3CRV_price / (self.GBP_price * self.amount_GBPe) - 1
        self.drift_x3CRV_to_GBPe = self.x3CRV_to_GBPe * self.GBP_price / (self.amount_x3CRV * self.x3CRV_price) - 1

    def get_GBPe_price_curve(self) -> float:
        return self.GBPe_to_x3CRV * self.x3CRV_price / self.amount_GBPe

    def __str__(self):
        return json.dumps(to_dict(self, exclude_key="PRIVATE_KEY"), indent=4)


class Swapx3CRVforGBPe(ContractMethod):
    name = "exchange"
    in_signature = [("i", "uint256"), ("j", "uint256"), ("dx", "uint256"), ("min_dy", "uint256")]
    target_address = CurveContractSpecs[Chain.GNOSIS].GBPe_x3RCV_pool.address
    fixed_arguments = {"i": 1, "j": 0}

    def __init__(self, avatar: Address, amount: int, min_amount_out: int):
        super().__init__(avatar=avatar)
        self.args.dx = amount
        self.args.min_dy = min_amount_out


class SwapGBPeForx3CRV(ContractMethod):
    name = "exchange"
    in_signature = [("i", "uint256"), ("j", "uint256"), ("dx", "uint256"), ("min_dy", "uint256")]
    target_address = CurveContractSpecs[Chain.GNOSIS].GBPe_x3RCV_pool.address
    fixed_arguments = {"i": 0, "j": 1}

    def __init__(self, avatar: Address, amount: int, min_amount_out):
        super().__init__(avatar=avatar)
        self.args.dx = amount
        self.args.min_dy = min_amount_out


class DynamicDataManager:
    def __init__(self, w3: Web3, w3_eth: Web3, static_data: StaticData):
        self.w3 = w3
        self.fixer_api_key = static_data.env.FIXER_API_ACCESS_KEY
        self.w3_eth = w3_eth
        self.static_data = static_data

    def get_GBPe_to_x3CRV_curve(self, amount_in: float) -> float:
        """
        Returns the amount of x3CRV that would be received in a swap for the given amount of GBPe.

        Args:
            amount_in: Amount of GBPe to swap.

        Returns:
            Amount of x3CRV that would be received in a swap for the given amount of GBPe.
        """
        contract = CurveContractSpecs[Chain.GNOSIS].GBPe_x3RCV_pool.contract(self.w3)
        amount_int = int(amount_in * (10**self.static_data.decimals_GBPe))
        if amount_int == 0:
            raise ValueError(
                "Amount of GBPe too small. Amount of GBPe: %f." % (amount_in * (10**self.static_data.decimals_GBPe))
            )
        rate = contract.functions.get_dy(0, 1, amount_int).call()
        return float(Decimal(rate) / Decimal(10**self.static_data.decimals_x3CRV))

    def get_x3CRV_to_GBPe_curve(self, amount_in: float) -> float:
        """
        Returns the amount of GBPe that would be received in a swap for the given amount of x3CRV.

        Args:
            amount_in: Amount of x3CRV to swap.

        Returns:
            Amount of GBPe that would be received in a swap for the given amount of x3CRV.
        """
        contract = CurveContractSpecs[Chain.GNOSIS].GBPe_x3RCV_pool.contract(self.w3)
        amount_int = int(Decimal(amount_in) * Decimal(10**self.static_data.decimals_x3CRV))
        if amount_int == 0:
            raise ValueError(
                "Amount of x3CRV too small. Amount of x3CRV: %f."
                % (amount_in * (10**self.static_data.decimals_x3CRV))
            )
        rate = contract.functions.get_dy(1, 0, amount_int).call()
        return float(Decimal(rate) / Decimal(10**self.static_data.decimals_GBPe))

    def get_GBP_oracle_price(self) -> float:
        """
        Returns the GBP price in USD. If a Fixer api key is set, it will get the price from the Fixer API. Otherwise,
        it will get the price from the Chainlink price feed.

        Args:

        Returns:
            GBP price in USD.
        """
        if self.fixer_api_key != "":
            data_from_api = requests.get(
                "https://data.fixer.io/api/latest?access_key=%s&base=GBP&symbols=USD" % self.fixer_api_key
            )
            if data_from_api.status_code == 200:
                response = json.loads(data_from_api.content.decode("utf-8"))
                if response["success"]:
                    return response["rates"]["USD"]
        contract = ChainlinkContractSpecs[Chain.ETHEREUM].GbpPriceFeed.contract(self.w3_eth)
        chainlink_price = float(Decimal(contract.functions.latestAnswer().call()) / Decimal((10**8)))
        return chainlink_price

    def get_x3CRV_price(self) -> float:
        contract = CurveContractSpecs[Chain.GNOSIS].x3Pool.contract(self.w3)
        WXDAI_amount = contract.functions.calc_withdraw_one_coin(int(1e18), 0).call()
        USDC_amount = contract.functions.calc_withdraw_one_coin(int(1e18), 1).call()
        USDT_amount = contract.functions.calc_withdraw_one_coin(int(1e18), 2).call()
        WXDAI_balance = contract.functions.balances(0).call()
        USDC_balance = contract.functions.balances(1).call()
        USDT_balance = contract.functions.balances(2).call()
        WXDAI_share = (WXDAI_balance / 1e18) / (WXDAI_balance / 1e18 + USDC_balance / 1e6 + USDT_balance / 1e6)
        USDC_share = (USDC_balance / 1e6) / (WXDAI_balance / 1e18 + USDC_balance / 1e6 + USDT_balance / 1e6)
        USDT_share = (USDT_balance / 1e6) / (WXDAI_balance / 1e18 + USDC_balance / 1e6 + USDT_balance / 1e6)
        return WXDAI_amount / 1e18 * WXDAI_share + USDC_amount / 1e6 * USDC_share + USDT_amount / 1e6 * USDT_share

    def get_data(self, amount_x3CRV: float, amount_GBPe: float) -> DynamicData:
        GBPe_price = self.get_GBP_oracle_price()
        x3CRV_price = self.get_x3CRV_price()
        x3CRV_to_GBPe = self.get_x3CRV_to_GBPe_curve(amount_x3CRV)
        GBPe_to_x3CRV = self.get_GBPe_to_x3CRV_curve(amount_GBPe)
        x3CRV_balance = (
            erc20_contract(self.w3, Addresses[Chain.GNOSIS].x3CRV)
            .functions.balanceOf(self.static_data.env.AVATAR_SAFE_ADDRESS)
            .call()
        )
        GBPe_balance = (
            erc20_contract(self.w3, Addresses[Chain.GNOSIS].GBPe)
            .functions.balanceOf(self.static_data.env.AVATAR_SAFE_ADDRESS)
            .call()
        )
        bot_xDAI_balance = self.w3.eth.get_balance(self.static_data.env.BOT_ADDRESS)
        return DynamicData(
            amount_x3CRV=amount_x3CRV,
            amount_GBPe=amount_GBPe,
            GBPe_to_x3CRV=GBPe_to_x3CRV,
            x3CRV_to_GBPe=x3CRV_to_GBPe,
            GBP_price=GBPe_price,
            x3CRV_price=x3CRV_price,
            x3CRV_balance=x3CRV_balance,
            GBPe_balance=GBPe_balance,
            bot_xDAI_balance=bot_xDAI_balance,
        )


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
        self.avatar_safe_address = Web3.to_checksum_address(avatar_safe_address)
        self.roles_mod_address = Web3.to_checksum_address(roles_mod_address)
        self.role = role
        self.private_keys = private_keys
        self.max_slippage = max_slippage

    def swap_GBPe_for_x3CRV(self, static_data: StaticData, dynamic_data: DynamicData) -> TxReceipt:
        min_amount_out = int(
            Decimal(1 - self.max_slippage)
            * Decimal(dynamic_data.GBPe_to_x3CRV)
            * Decimal(10**static_data.decimals_x3CRV)
        )
        amount = int(Decimal(dynamic_data.amount_GBPe) * Decimal(10**static_data.decimals_GBPe))
        return roles.send(
            [SwapGBPeForx3CRV(amount=amount, min_amount_out=min_amount_out, avatar=self.avatar_safe_address)],
            role=self.role,
            private_key=self.private_keys,
            roles_mod_address=self.roles_mod_address,
            web3=self.w3,
        )

    def swap_x3CRV_for_GBPe(self, static_data: StaticData, dynamic_data: DynamicData) -> TxReceipt:
        min_amount_out = int(
            Decimal(1 - self.max_slippage)
            * Decimal(dynamic_data.x3CRV_to_GBPe)
            * Decimal(10**static_data.decimals_GBPe)
        )
        amount = int(Decimal(dynamic_data.amount_x3CRV) * Decimal(10**static_data.decimals_x3CRV))
        return roles.send(
            [Swapx3CRVforGBPe(amount=amount, min_amount_out=min_amount_out, avatar=self.avatar_safe_address)],
            role=self.role,
            private_key=self.private_keys,
            roles_mod_address=self.roles_mod_address,
            web3=self.w3,
        )
