import logging
import threading
import time

import schedule

from roles_royce.applications.spark_anti_liquidation_bot.env import ENV
from roles_royce.toolshed.alerting.alerting import LoggingLevel, Messenger
from roles_royce.toolshed.anti_liquidation.spark import SparkCDP

logger = logging.getLogger(__name__)


def log_initial_data(env: ENV, messenger: Messenger):
    title = "Spark Anti-Liquidation Bot started"
    message = (
        f"  Avatar safe address: {env.AVATAR_SAFE_ADDRESS}\n"
        f"  Roles mod address: {env.ROLES_MOD_ADDRESS}\n"
        f"  Bot address: {env.BOT_ADDRESS}\n"
        f"  Target health factor: {env.TARGET_HEALTH_FACTOR}\n"
    )
    if messenger.slack_messenger.webhook != "" or (
        messenger.telegram_messenger.bot_token != "" and messenger.telegram_messenger.chat_id != ""
    ):
        message = message + f"  Alerting health factor: {env.ALERTING_HEALTH_FACTOR}\n"
    message = message + (
        f"  Health Factor threshold: {env.THRESHOLD_HEALTH_FACTOR}\n"
        f"  Tolerance: {env.TOLERANCE}\n"
        f"  Cooldown Minutes: {env.COOLDOWN_MINUTES}\n"
    )
    messenger.log_and_alert(LoggingLevel.Info, title, message)


def send_status(messenger: Messenger, cdp: SparkCDP, bot_ETH_balance: float):
    title = "Spark CDP status update"
    message = f"  Current health factor: {cdp.health_factor}\n" f"{cdp}\n" f"Bot ETH balance: {bot_ETH_balance:,.5f}"
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
