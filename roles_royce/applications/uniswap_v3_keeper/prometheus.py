from dataclasses import dataclass
from prometheus_client import Gauge
from core import DynamicData, StaticData


@dataclass
class Gauges:
    nft_id = Gauge("nft_id", "NFT Id")
    bot_ETH_balance = Gauge("bot_ETH_balance", "ETH balance of the bot")
    safe_token0_balance = Gauge("safe_token0_balance", "Safe token0 balance")
    safe_token1_balance = Gauge("safe_token1_balance", "Safe token1 balance")
    token0_balance = Gauge("token0_balance", "Position token0 balance")
    token1_balance = Gauge("token1_balance", "Position token1 balance")
    price_min = Gauge("price_min", "Minimum range range price of token0 vs token1")
    price_max = Gauge("price_max", "Maximum range range price of token0 vs token1")
    price = Gauge("price", "Current price of token0 vs token1")
    price_range_threshold = Gauge("price_range_threshold", "Price range threshold")
    minimum_min_price = Gauge("minimum_min_price", "Minimum min price")

    def update(self, dynamic_data: DynamicData, static_data: StaticData) -> None:
        self.nft_id.set(dynamic_data.nft_id)
        self.bot_ETH_balance.set(dynamic_data.bot_ETH_balance / (10 ** 18))
        self.safe_token0_balance.set(dynamic_data.safe_token0_balance / (10 ** static_data.token0_decimals))
        self.safe_token1_balance.set(dynamic_data.safe_token1_balance / (10 ** static_data.token1_decimals))
        self.token0_balance.set(dynamic_data.token0_balance / (10 ** static_data.token0_decimals))
        self.token1_balance.set(dynamic_data.token1_balance / (10 ** static_data.token1_decimals))
        self.price_min.set(dynamic_data.price_min)
        self.price_max.set(dynamic_data.price_max)
        self.price.set(dynamic_data.price)
        self.price_range_threshold.set(
            float(static_data.env.PRICE_RANGE_THRESHOLD * (
                    dynamic_data.price_max - dynamic_data.price_min) + dynamic_data.price_min
                  )
        )
        self.minimum_min_price.set(static_data.env.MINIMUM_MIN_PRICE)