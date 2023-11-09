import logging
from .generic_method import GenericMethodTransaction, Transactable
from .roles_modifier import Operation
from defabipedia.types import Chains

logging.getLogger(__name__).addHandler(logging.NullHandler())

def add_stderr_logger(level: int = logging.DEBUG) -> logging.StreamHandler:
    """Helper for quickly adding a StreamHandler to the logger. Useful for
    debugging.
    Returns the handler after adding it.
    """
    # This method needs to be in this __init__.py to get the __name__ correct
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug("Added a stderr logging handler to logger: %s", __name__)
    return handler
