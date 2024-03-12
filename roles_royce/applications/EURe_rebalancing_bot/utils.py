from dataclasses import dataclass, field
from decouple import config
from web3.types import ChecksumAddress
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
import logging
from roles_royce.protocols.base import Address
import threading
import schedule
import time
from prometheus_client import Gauge
from swaps import decimalsWXDAI, decimalsEURe
from roles_royce.applications.EURe_rebalancing_bot.env import ENV

logger = logging.getLogger(__name__)


def log_initial_data(env: ENV, messenger: Messenger):
    title = "EURe rebalancing bot started"
    message = (f"  Avatar safe address: {env.AVATAR_SAFE_ADDRESS}\n"
               f"  Roles mod address: {env.ROLES_MOD_ADDRESS}\n"
               f"  Bot address: {env.BOT_ADDRESS}\n"
               f"  Drift threshold: {env.DRIFT_THRESHOLD * 100}%\n"
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
