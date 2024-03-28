import logging

from roles_royce.applications.GBPe_rebalancing_bot.core import DynamicData, StaticData
from roles_royce.toolshed.alerting.alerting import LoggingLevel, Messenger

logger = logging.getLogger(__name__)


def log_initial_data(static_data: StaticData, messenger: Messenger):
    title = "GBPe rebalancing bot started"
    message = (
        f"  Avatar safe address: {static_data.env.AVATAR_SAFE_ADDRESS}\n"
        f"  Roles mod address: {static_data.env.ROLES_MOD_ADDRESS}\n"
        f"  Bot address: {static_data.env.BOT_ADDRESS}\n"
        f"  Drift threshold: {static_data.env.DRIFT_THRESHOLD * 100}%\n"
        f"  Initial amount to swap: {static_data.env.AMOUNT:,.2f}\n"
        f"  Cooldown Minutes: {static_data.env.COOLDOWN_MINUTES}\n"
    )

    messenger.log_and_alert(LoggingLevel.Info, title, message)


def log_status_update(static_data: StaticData, dynamic_data: DynamicData):
    title = "Status update"
    message = (
        f"Status update:\n"
        f"  GBP price: {dynamic_data.GBP_price:,.5f}\n"
        f"  x3CRV price: {dynamic_data.x3CRV_price:,.5f}\n"
        f"\n"
        f"  GBP to USD oracle: {dynamic_data.amount_GBPe:,.3f} GBPe ---> {dynamic_data.amount_GBPe * dynamic_data.GBP_price:,.3f} USD.\n"
        f"  GBPe to USD Curve: {dynamic_data.amount_GBPe:,.3f} GBPe ---> {dynamic_data.GBPe_to_x3CRV * dynamic_data.x3CRV_price:,.3f} USD.\n"
        f"  GBPe to x3CRV drift: {dynamic_data.drift_GBPe_to_x3CRV:,.5f}.\n"
        f"\n"
        f"  USD to GBP oracle: {dynamic_data.amount_x3CRV:,.3f} USD ---> {dynamic_data.amount_x3CRV / dynamic_data.GBP_price:,.3f} GBPe.\n"
        f"  USD to GBPe Curve: {dynamic_data.amount_x3CRV:,.3f} USD ---> {dynamic_data.x3CRV_to_GBPe / dynamic_data.x3CRV_price:,.3f} GBPe.\n"
        f"  x3CRV to GBPe drift: {dynamic_data.drift_x3CRV_to_GBPe:,.5f}.\n"
        f"\n"
        f"  Drift threshold: {static_data.env.DRIFT_THRESHOLD:,.5f}.\n"
        f"\n"
        f'  Avatar safe"s x3CRV balance: {dynamic_data.x3CRV_balance / (10 ** static_data.decimals_x3CRV):,.5f}.\n'
        f'  Avatar safe"s GBPe balance: {dynamic_data.GBPe_balance / (10 ** static_data.decimals_GBPe):,.5f}.\n'
        f'  Bot"s xDAI balance: {dynamic_data.bot_xDAI_balance / (10 ** 18):,.5f}.\n'
    )

    logger.info(title + ".\n" + message)
