from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
import logging
from core import StaticData, DynamicData

logger = logging.getLogger(__name__)


def log_initial_data(static_data: StaticData, messenger: Messenger):
    title = "Uniswap v3 keeper started"
    message = f"{static_data}"
    messenger.log_and_alert(LoggingLevel.Info, title, message)


def log_status_update(static_data: StaticData, dynamic_data: DynamicData):
    title = "Status update"
    message = f"{static_data}\n{dynamic_data}"
    logger.info(title + ".\n" + message)
