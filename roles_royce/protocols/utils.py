import binascii

from defabipedia.tokens import Abis
from web3 import Web3
from web3.types import Address

from roles_royce.generic_method import Transactable
from roles_royce.protocols.base import ApproveForToken, AvatarAddress


def check_allowance_and_approve(
    w3: Web3, avatar: AvatarAddress, token: Address, spender: Address, amount: int
) -> Transactable | None:
    """
    Checks if the allowance of the token is enough for the spender to spend the amount and if not, returns an
    approve transactable to approve the spender to spend the amount

    Args:
        w3: Web3 instance
        avatar: Avatar address
        token: Token address
        spender: Spender address
        amount: Amount to approve

    Returns:
        Transactable | None: ApproveForToken if allowance is not enough, None otherwise
    """
    allowance = w3.eth.contract(address=token, abi=Abis.ERC20.abi).functions.allowance(avatar, spender).call()

    if allowance < amount:
        return ApproveForToken(amount=amount, token=token, spender=spender)
    else:
        return None


def format_bytes32_string(input_string):
    # Convert the string to bytes
    input_bytes = input_string.encode("utf-8")
    # Pad or truncate the bytes to 32 bytes
    padded_bytes = input_bytes.ljust(32, b"\0")[:32]
    # Convert the bytes to hexadecimal representation
    hex_string = binascii.hexlify(padded_bytes).decode("utf-8")
    return "0x" + hex_string
