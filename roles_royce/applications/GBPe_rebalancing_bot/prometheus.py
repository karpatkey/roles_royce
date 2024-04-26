from dataclasses import dataclass

from core import DynamicData, StaticData
from prometheus_client import Gauge


@dataclass
class Gauges:
    GBP_price_feed = Gauge("GBP_price_feed", "GBP price from feed")
    x3CRV_price = Gauge("x3CRV_price", "x3CRV price from Curve")
    GBPe_price_curve = Gauge("GBPe_price_curve", "GBPe price from Curve")
    bot_xDAI_balance = Gauge("bot_ETH_balance", "ETH balance of the bot")
    safe_x3CRV_balance = Gauge("safe_x3CRV_balance", "x3CRV balance of the avatar safe")
    safe_GBPe_balance = Gauge("safe_GBPe_balance", "GBPe balance of the avatar safe")
    amount_x3CRV = Gauge("amount_x3CRV", "Amount of x3CRV to swap")
    amount_GBPe = Gauge("amount_GBPe", "Amount of GBPe to swap")
    drift_threshold = Gauge("drift_threshold", "Drift threshold")
    drift_GBPe_to_x3CRV = Gauge("GBPe_to_x3CRV_drift", "GBPe to x3CRV drift")
    drift_x3CRV_to_GBPe = Gauge("x3CRV_to_GBPe_drift", "x3CRV to GBPe drift")
    last_updated = Gauge("last_updated", "Last updated time and date")

    def update(self, static_data: StaticData, dynamic_data: DynamicData):
        self.GBP_price_feed.set(dynamic_data.GBP_price)
        self.x3CRV_price.set(dynamic_data.x3CRV_price)
        self.GBPe_price_curve.set(dynamic_data.get_GBPe_price_curve())
        self.bot_xDAI_balance.set(dynamic_data.bot_xDAI_balance / (10**18))
        self.safe_x3CRV_balance.set(dynamic_data.x3CRV_balance / (10**static_data.decimals_x3CRV))
        self.safe_GBPe_balance.set(dynamic_data.GBPe_balance / (10**static_data.decimals_GBPe))
        self.amount_x3CRV.set(dynamic_data.amount_x3CRV)
        self.amount_GBPe.set(dynamic_data.amount_GBPe)
        self.drift_threshold.set(static_data.env.DRIFT_THRESHOLD)
        self.drift_GBPe_to_x3CRV.set(dynamic_data.drift_GBPe_to_x3CRV)
        self.drift_x3CRV_to_GBPe.set(dynamic_data.drift_x3CRV_to_GBPe)
        self.last_updated.set_to_current_time()
