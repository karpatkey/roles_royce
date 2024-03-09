from decouple import config
from typing import Any


def custom_config(variable: str, default, cast: type):
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
