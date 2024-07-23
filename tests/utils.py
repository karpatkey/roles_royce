from defabipedia.tokens import NATIVE, EthereumTokenAddr, erc20_contract
from web3 import Web3


def get_balance(w3, token, address):
    """Get the token or ETH balance of an address"""
    if token == NATIVE or token == EthereumTokenAddr.ZERO:  # Check allso with ZERO to maintain backwards compat
        return w3.eth.get_balance(address)
    else:
        ctract = erc20_contract(w3, token)
        return ctract.functions.balanceOf(address).call()


def get_allowance(w3, token, owner_address, spender_address):
    """Get the token allowance of an address"""
    ctract = erc20_contract(w3, token)
    return ctract.functions.allowance(owner_address, spender_address).call()


def to_hex_32_bytes(value: str | int) -> str:
    """Convert a value to a 32 bytes hex string"""
    if isinstance(value, str):
        if value.startswith("0x") and len(value) <= 66:
            return "0x" + value[2:].rjust(64, "0")
        else:
            raise ValueError("Invalid value. Value must be a hex string with or without 0x prefix and length <= 66")
    elif isinstance(value, int):
        return Web3.to_hex(Web3.to_bytes(value).rjust(32, b"\0"))
    else:
        raise ValueError("Invalid value. Value must be an int or a hex string with 0x prefix and length <= 66")


