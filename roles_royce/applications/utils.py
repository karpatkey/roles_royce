import sys
import time
from typing import Any

from decouple import config
from web3 import Web3
from web3.middleware import geth_poa_middleware

from roles_royce.toolshed.alerting import LoggingLevel, Messenger


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
    if hasattr(obj, "__dict__"):
        return {key: to_dict(value, exclude_key) for key, value in obj.__dict__.items() if key != exclude_key}
    elif isinstance(obj, list):
        return [to_dict(item, exclude_key) for item in obj]
    elif isinstance(obj, int):
        return str(obj)  # Convert int to string explicitly
    else:
        return obj


def web3_connection_check(
    rpc_endpoint_url: str,
    messenger: Messenger,
    rpc_endpoint_failure_counter: int,
    rpc_endpoint_fallback_url: str = "",
    rpc_endpoint_execution_url: str = "",
    max_rpc_endpoint_failures: int = 5,
) -> (Web3, Web3, int):
    """
    This function checks the connection to the RPC endpoint and the MEV RPC endpoint intended to be used for execution.
    If the connection fails, it tries to connect to the fallback RPC endpoint if this one was specified. If
    the connection(s) fail it increments the rpc_endpoint_failure_counter. If the counter reaches the maximum number of
    failures, the program exits.

    Args:
        rpc_endpoint_url (str): The RPC endpoint URL
        messenger (Messenger): The messenger object
        rpc_endpoint_failure_counter (int): The counter of the RPC endpoint failures
        rpc_endpoint_fallback_url (str): The fallback RPC endpoint URL- Can be empty
        rpc_endpoint_execution_url (str): Execution dedicated RPC endpoint, e.g. MEV blocker. Can be empty, and in that
            case the same Web3 object is used for both RPC and MEV RPC endpoints
        max_rpc_endpoint_failures (int): The maximum number of RPC endpoint failures before the program exits

    Returns:
        (Web3, Web3, int): The Web3 object for the RPC endpoint, the Web3 object for the MEV RPC endpoint, and the updated
        RPC endpoint failure counter if there was any connection error. If no rpc_endpoint_mev_url is provided both Web3
        objects are the same. If the maximum number of RPC endpoint failures is reached, the program exits.
    """
    w3 = Web3(Web3.HTTPProvider(rpc_endpoint_url))
    if not w3.is_connected(show_traceback=True):
        time.sleep(5)
        # Second attempt
        if not w3.is_connected(show_traceback=True):
            # Case where a fallback RPC endpoint is provided
            if rpc_endpoint_fallback_url != "":
                messenger.log_and_alert(
                    LoggingLevel.Warning, title="Warning", message=f"  RPC endpoint {rpc_endpoint_url} is not working."
                )
                w3 = Web3(Web3.HTTPProvider(rpc_endpoint_fallback_url))
                if not w3.is_connected(show_traceback=True):
                    time.sleep(5)
                    # Second attempt with fallback RPC endpoint
                    if not w3.is_connected(show_traceback=True):
                        messenger.log_and_alert(
                            LoggingLevel.Warning,
                            title="Warning",
                            message=f"  RPC endpoint {rpc_endpoint_url} and fallback RPC "
                            f"endpoint {rpc_endpoint_fallback_url} are both not "
                            f"working.",
                        )
                        rpc_endpoint_failure_counter += 1
                    else:
                        rpc_endpoint_failure_counter = 0
                else:
                    rpc_endpoint_failure_counter = 0
            # Case where no fallback RPC endpoint is provided
            else:
                messenger.log_and_alert(
                    LoggingLevel.Warning, title="Warning", message=f"  RPC endpoint {rpc_endpoint_url} is not working."
                )
                rpc_endpoint_failure_counter += 1
        else:
            rpc_endpoint_failure_counter = 0
    else:
        rpc_endpoint_failure_counter = 0

    if rpc_endpoint_execution_url != "":
        w3_execution = Web3(Web3.HTTPProvider(rpc_endpoint_execution_url))
        if not w3_execution.is_connected(show_traceback=True):
            messenger.log_and_alert(
                LoggingLevel.Warning,
                title="Warning",
                message=f"  Execution RPC endpoint {rpc_endpoint_url} is not working.",
            )
            w3_execution = w3
    else:
        w3_execution = w3

    if rpc_endpoint_failure_counter == max_rpc_endpoint_failures:
        messenger.log_and_alert(LoggingLevel.Error, title="Too many RPC endpoint failures, exiting...", message="")
        time.sleep(5)  # Cooldown time for the messenger system to send messages in queue
        sys.exit(1)

    else:
        if "anvil" in w3.client_version and w3.eth.chain_id == 137:
            # When trying to execute transactions on the Polygon network using Anvil the following error is raised:
            # The field extraData is 97 bytes, but should be 32. It is quite likely that you are connected to a POA chain
            # See https://stackoverflow.com/questions/70812529/the-field-extradata-is-97-bytes-but-should-be-32-it-is-quite-likely-that-you-a
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            w3_execution.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3, w3_execution, rpc_endpoint_failure_counter


def check_env_endpoints(endpoints: list[(str, str)]) -> None:
    """
    This function checks if the RPC endpoints are valid and active. If not, it raises a ValueError. It is meant to
    receive one tuple per chain, where the first element is the RPC endpoint and the second element is the fallback RPC
    endpoint.

    Args:
        endpoints (list[(str, str)]): The list of RPC endpoints URLs TUPLES where each tuple is
        (RPC_ENDPOINT_URL,RPC_ENDPOINT_FALLBACK_URL).

    Returns:
        None

    Raises:
        ValueError: If either the RPC endpoint or fallback RPC endpoint is not valid or not active in any of the tuples.
        ValueError: If the RPC endpoint and fallback RPC endpoint are not for the same chain in any of the tuples.
    """
    for item in endpoints:
        if not Web3(Web3.HTTPProvider(item[0])).is_connected():
            raise ValueError(f"RPC_ENDPOINT: {item[0]} is not valid or not active.")
        if not Web3(Web3.HTTPProvider(item[1])).is_connected():
            raise ValueError(f"RPC_ENDPOINT_FALLBACK: {item[1]} is not valid or not active: {item[1]}.")
        if Web3(Web3.HTTPProvider(item[0])).eth.chain_id != Web3(Web3.HTTPProvider(item[1])).eth.chain_id:
            raise ValueError(
                f"RPC_ENDPOINT: {item[0]} and RPC_ENDPOINT_FALLBACK: {item[1]} are not for the same chain."
            )
