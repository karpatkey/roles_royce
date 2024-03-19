import logging
import threading
import time
from dataclasses import dataclass, field

import schedule
from decouple import config
from prometheus_client import Gauge
from swaps import decimalsEURe, decimalsWXDAI
from web3 import Web3
from web3.types import ChecksumAddress

from roles_royce.applications.EURe_rebalancing_bot.env import ENV
from roles_royce.protocols.base import Address
from roles_royce.toolshed.alerting.alerting import LoggingLevel, Messenger

logger = logging.getLogger(__name__)


def log_initial_data(env: ENV, messenger: Messenger):
    title = "EURe rebalancing bot started"
    message = (
        f"  Avatar safe address: {env.AVATAR_SAFE_ADDRESS}\n"
        f"  Roles mod address: {env.ROLES_MOD_ADDRESS}\n"
        f"  Bot address: {env.BOT_ADDRESS}\n"
        f"  Drift threshold: {env.DRIFT_THRESHOLD * 100}%\n"
        f"  Initial amount to swap: {env.AMOUNT}\n"
        f"  Cooldown Minutes: {env.COOLDOWN_MINUTES}\n"
    )

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
