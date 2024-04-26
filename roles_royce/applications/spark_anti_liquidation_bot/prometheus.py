import logging
import threading
import time
from dataclasses import dataclass, field
from decimal import Decimal

import schedule
from decouple import config
from prometheus_client import Gauge
from web3 import Web3
from web3.types import Address, ChecksumAddress

from roles_royce.toolshed.alerting.alerting import LoggingLevel, Messenger
from roles_royce.toolshed.anti_liquidation.spark import SparkCDP


@dataclass
class Gauges:
    health_factor = Gauge("health_factor", "Spark CDP health factor")
    # TODO: This should be generalized for any Spark CDP with any tokens
    wstETH_deposited = Gauge("wstETH_balance", "wstETH deposited balance of the Spark CDP")
    DAI_borrowed = Gauge("DAI_borrowed", "DAI borrowed balance of the Spark CDP")
    wstETH_price = Gauge("wstETH_price", "wstETH price")
    DAI_price = Gauge("DAI_price", "DAI price")
    bot_ETH_balance = Gauge("bot_ETH_balance", "ETH balance of the bot")
    alerting_health_factor = Gauge("alerting_health_factor", "Alerting health factor")
    health_factor_threshold = Gauge("health_factor_threshold", "Health factor threshold")
    sDAI_balance = Gauge("sDAI_balance", "sDAI balance of the avatar safe")
    last_updated = Gauge("last_updated", "Last updated time and date")
    DAI_equivalent = Gauge("DAI_equivalent", "DAI that would be obtained by redeeming the total of the sDAI")
    DAI_balance = Gauge("DAI_balance", "DAI balance of the avatar safe")

    def update(
        self,
        health_factor: float,
        bot_ETH_balance: float,
        DAI_balance: float,
        sDAI_balance: float,
        wstETH_deposited: float,
        wstETH_spark_price: float,
        DAI_borrowed: float,
        DAI_spark_price: float,
        DAI_equivalent: float,
    ):
        self.bot_ETH_balance.set(bot_ETH_balance / 1e18)
        self.health_factor.set(float(health_factor))
        self.sDAI_balance.set(float(Decimal(sDAI_balance) / Decimal(1e18)))
        self.DAI_equivalent.set(DAI_equivalent)
        self.DAI_balance.set(float(Decimal(DAI_balance) / Decimal(1e18)))
        self.wstETH_deposited.set(wstETH_deposited)
        self.wstETH_price.set(wstETH_spark_price)
        self.DAI_borrowed.set(DAI_borrowed)
        self.DAI_price.set(DAI_spark_price)
        self.last_updated.set_to_current_time()
