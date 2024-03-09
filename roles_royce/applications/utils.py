from decouple import config
from typing import Any
from web3 import Web3
from roles_royce.toolshed.alerting import Messenger, LoggingLevel
import time
import sys
from web3.middleware import geth_poa_middleware


def custom_config(variable: str, default: Any, cast: type):
    """
    This function is a wrapper around the decouple.config function. It allows to leave variables unfilled in the .env
    file.

    Args:
        variable (str): The name of the environment variable
        default : The default value of the variable
        cast (type): The type of the variable

    Returns:
        The value of the variable if it is not empty, otherwise the default value is returned.
    """
    value = config(variable) if default is None else config(variable, default=default)
    return default if (value == "" or value is None) else config(variable, default=default, cast=cast)


def to_dict(obj: Any, exclude_key: str = None) -> dict:
    """
    This function converts an object to a dictionary. It is used to log the initial data of the bot. It removes key
    and value at any level of the dictionary if exclude_key is provided.

    Args:
        obj (Any): The object to be converted to a dictionary
        exclude_key (str): The key to be excluded from the dictionary at any lebel of the dictionary.

    Returns:
        dict: The dictionary representation of the object.
    """
    if hasattr(obj, '__dict__'):
        return {key: to_dict(value, exclude_key) for key, value in obj.__dict__.items() if key != exclude_key}
    elif isinstance(obj, list):
        return [to_dict(item, exclude_key) for item in obj]
    else:
        return obj


def web3_connection_check(rpc_endpoint_url: str,
                          messenger: Messenger,
                          rpc_endpoint_failure_counter: int,
                          fallback_rpc_endpoint_url: str = '',
                          rpc_endpoint_MEV: str = '',
                          max_rpc_endpoint_failures: int = 5) -> (Web3, Web3, int):
    """Checks if the RPC endpoint is working, and if not, tries to connect to a fallback RPC endpoint.

    Args:
        rpc_endpoint_url: RPC endpoint URL to check.
        messenger: Messenger object.
        rpc_endpoint_failure_counter: Counter of RPC endpoint failures.
        fallback_rpc_endpoint_url: Fallback RPC endpoint URL to check.
        max_rpc_endpoint_failures: Maximum number of RPC endpoint failures before exiting.

    Returns:
        w3: Web3 object.
        rpc_endpoint_failure_counter: Updated counter of RPC endpoint failures.
    """
    w3 = Web3(Web3.HTTPProvider(rpc_endpoint_url))
    if not w3.is_connected(show_traceback=True):
        time.sleep(5)
        # Second attempt
        if not w3.is_connected(show_traceback=True):
            # Case where a fallback RPC endpoint is provided
            if fallback_rpc_endpoint_url != '':
                messenger.log_and_alert(LoggingLevel.Warning, title='Warning',
                                        message=f'  RPC endpoint {rpc_endpoint_url} is not working.')
                w3 = Web3(Web3.HTTPProvider(fallback_rpc_endpoint_url))
                if not w3.is_connected(show_traceback=True):
                    time.sleep(5)
                    # Second attempt with fallback RPC endpoint
                    if not w3.is_connected(show_traceback=True):
                        messenger.log_and_alert(LoggingLevel.Error, title='Error',
                                                message=f'  RPC endpoint {rpc_endpoint_url} and fallback RPC '
                                                        f'endpoint {fallback_rpc_endpoint_url} are both not '
                                                        f'working.')
                        rpc_endpoint_failure_counter += 1
                    else:
                        rpc_endpoint_failure_counter = 0
                else:
                    rpc_endpoint_failure_counter = 0
            # Case where no fallback RPC endpoint is provided
            else:
                messenger.log_and_alert(LoggingLevel.Error, title='Error',
                                        message=f'  RPC endpoint {rpc_endpoint_url} is not working.')
                rpc_endpoint_failure_counter += 1
        else:
            rpc_endpoint_failure_counter = 0
    else:
        rpc_endpoint_failure_counter = 0

    if rpc_endpoint_failure_counter == max_rpc_endpoint_failures:
        messenger.log_and_alert(LoggingLevel.Error, title='Too many RPC endpoint failures, exiting...',
                                message='')
        time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
        sys.exit(1)

    else:
        if w3.eth.chain_id == 137:
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3, rpc_endpoint_failure_counter