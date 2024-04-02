import time
from dataclasses import dataclass

from prometheus_client import Gauge

from roles_royce.applications.bridge_keeper.core import DynamicData, StaticData
from roles_royce.applications.bridge_keeper.utils import Flags


@dataclass
class Gauges:
    bridge_DAI_balance = Gauge("bridge_DAI_balance", 'Bridge"s DAI balance')
    bot_ETH_balance = Gauge("bot_ETH_balance", "ETH balance of the bot")
    next_claim_epoch = Gauge("next_claim_epoch", "Next claim epoch")
    refill_threshold = Gauge("refill_threshold", "Refill threshold")
    invest_threshold = Gauge("invest_threshold", "Invest threshold")
    min_cash_threshold = Gauge("min_cash_threshold", "Minimum amount of underlying tokens that are not invested")
    claimable = Gauge("claimable", "Claimable interest")
    min_interest_paid = Gauge("min_interest_paid", "Minimum amount of interest that can be paid in a single call")
    amount_of_interest_to_pay = Gauge("amount_of_interest_to_pay", "Amount of interest to pay")
    lack_of_gas_warning = Gauge("lack_of_gas_warning", "Lack of gas warning flag")
    interest_payed = Gauge("interest_payed", "Interest payed flag")
    tx_executed = Gauge("tx_executed", "Transaction executed flag")
    minutes_till_interest_payment = Gauge("minutes_till_interest_payment", "Minutes left till next interest payment")

    def update(self, static_data: StaticData, dynamic_data: DynamicData, flags: Flags):
        self.bot_ETH_balance.set(dynamic_data.bot_ETH_balance / (10**18))
        self.bridge_DAI_balance.set(dynamic_data.bridge_DAI_balance / (10**static_data.decimals_DAI))
        self.next_claim_epoch.set(dynamic_data.next_claim_epoch)
        self.invest_threshold.set(static_data.env.INVEST_THRESHOLD)
        self.refill_threshold.set(static_data.env.REFILL_THRESHOLD)
        self.min_cash_threshold.set(dynamic_data.min_cash_threshold / (10**static_data.decimals_DAI))
        self.claimable.set(dynamic_data.claimable / (10**static_data.decimals_DAI))
        self.min_interest_paid.set(dynamic_data.min_interest_paid / (10**static_data.decimals_DAI))
        self.amount_of_interest_to_pay.set(static_data.env.AMOUNT_OF_INTEREST_TO_PAY)
        self.lack_of_gas_warning.set(flags.lack_of_gas_warning.is_set())
        self.interest_payed.set(flags.interest_payed.is_set())
        self.tx_executed.set(flags.tx_executed.is_set())
        self.minutes_till_interest_payment.set(
            int((dynamic_data.next_claim_epoch - 60 * static_data.env.MINUTES_BEFORE_CLAIM_EPOCH - time.time()) / 60)
        )
