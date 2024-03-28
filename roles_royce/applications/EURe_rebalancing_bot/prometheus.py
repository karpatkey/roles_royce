from dataclasses import dataclass

from prometheus_client import Gauge
from swaps import decimalsEURe, decimalsWXDAI


@dataclass
class Gauges:
    EUR_price_feed = Gauge("EUR_price_feed", "EUR price from feed")
    EURe_price_curve = Gauge("EURe_price_curve", "EURe price from Curve")
    bot_xDAI_balance = Gauge("bot_ETH_balance", "ETH balance of the bot")
    safe_WXDAI_balance = Gauge("safe_WXDAI_balance", "WXDAI balance of the avatar safe")
    safe_EURe_balance = Gauge("safe_EURe_balance", "EURe balance of the avatar safe")
    amount_WXDAI = Gauge("amount_WXDAI", "Amount of WXDAI to swap")
    amount_EURe = Gauge("amount_EURe", "Amount of EURe to swap")
    drift_threshold = Gauge("drift_threshold", "Drift threshold")
    drift_EURe_to_WXDAI = Gauge("EURe_to_WXDAI_drift", "EURe to WXDAI drift")
    drift_WXDAI_to_EURe = Gauge("WXDAI_to_EURe_drift", "WXDAI to EURe drift")
    last_updated = Gauge("last_updated", "Last updated time and date")

    def update(
        self,
        EUR_price_feed: float,
        EURe_price_curve: float,
        bot_xDAI_balance: int,
        safe_WXDAI_balance: int,
        safe_EURe_balance: int,
        amount_WXDAI: float,
        amount_EURe: float,
        drift_threshold: float,
        drift_EURe_to_WXDAI: float,
        drift_WXDAI_to_EURe: float,
    ):
        self.EUR_price_feed.set(EUR_price_feed)
        self.EURe_price_curve.set(EURe_price_curve)
        self.bot_xDAI_balance.set(bot_xDAI_balance / (10**18))
        self.safe_WXDAI_balance.set(safe_WXDAI_balance / (10**decimalsWXDAI))
        self.safe_EURe_balance.set(safe_EURe_balance / (10**decimalsEURe))
        self.amount_WXDAI.set(amount_WXDAI)
        self.amount_EURe.set(amount_EURe)
        self.drift_threshold.set(drift_threshold)
        self.drift_EURe_to_WXDAI.set(drift_EURe_to_WXDAI)
        self.drift_WXDAI_to_EURe.set(drift_WXDAI_to_EURe)
        self.last_updated.set_to_current_time()
