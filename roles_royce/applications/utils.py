from decouple import config


def custom_config(variable, default, cast):
    """
    This function is a wrapper around the decouple.config function. It allows to leave variables unfilled in the .env
    file.

    Args:
        variable (str): The name of the environment variable
        default (str): The default value of the variable
        cast (type): The type of the variable

    Returns:
        The value of the variable if it is not empty, otherwise the default value is returned.
    """
    value = config(variable, default=default)
    return default if (value == "" or value is None) else config(variable, default=default, cast=cast)