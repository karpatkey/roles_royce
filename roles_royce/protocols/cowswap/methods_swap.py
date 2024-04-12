from roles_royce.protocols.cowswap.contract_methods import SignOrder
from roles_royce.protocols.cowswap.utils import SwapKind, quote_order_api, create_order_api, Order
from roles_royce.protocols.utils import check_allowance_and_approve
from roles_royce.protocols.base import AvatarAddress
from web3 import Web3
from roles_royce.generic_method import Transactable
from defabipedia.types import Chain
from defabipedia.cowswap_signer import ContractSpecs
from web3.types import Address


def create_order_and_swap(w3: Web3,
                          avatar: AvatarAddress,
                          sell_token: Address,
                          buy_token: Address,
                          amount: int,
                          kind: SwapKind,
                          max_slippage: float,
                          valid_duration: int = 10 * 60) -> list[Transactable]:
    """
    Creates a swap order using the Cow API and returns the sign_order Transactable to execute to sign the order on-chain.

    Args:
        w3 (Web3): The web3 object
        avatar (AvatarAddress): The address of the avatar safe
        sell_token (Address): The token to sell
        buy_token (Address): The token to buy
        amount (int): The amount to sell
        kind (SwapKind): The kind of the order ("buy" or "sell")
        max_slippage (float): The maximum slippage allowed
        valid_duration (int): The duration the order is valid in seconds

    Returns:
        list[Transactable]: A list with one single Transactable element.

    Raises:
        ValueError: If the order creation using the API fails
    """

    order = quote_order_api(
        blockchain=Chain.get_blockchain_from_web3(w3),
        sell_token=sell_token,
        buy_token=buy_token,
        receiver=avatar,
        from_address=avatar,
        kind=kind,
        amount=amount,
        valid_to=w3.eth.get_block('latest').timestamp + valid_duration,
    )

    order.buy_amount = order.buy_amount if kind == SwapKind.BUY else int(order.buy_amount * (1 - max_slippage))
    order.sell_amount = order.sell_amount if kind == SwapKind.SELL else int(order.sell_amount * (1 + max_slippage))

    response_create_order = create_order_api(
        blockchain=Chain.get_blockchain_from_web3(w3),
        sell_token=order.sell_token,
        buy_token=order.buy_token,
        receiver=order.receiver,
        from_address=order.from_address,
        kind=order.kind,
        amount=order.sell_amount,
        valid_to=order.valid_to,
        order=order)

    if not response_create_order["UID"]:
        raise ValueError("Order creation failed")

    result = []
    approve_transactable = check_allowance_and_approve(w3=w3,
                                                       avatar=avatar,
                                                       token=sell_token,
                                                       spender=ContractSpecs[
                                                           Chain.get_blockchain_from_web3(w3)].CowswapRelayer.address,
                                                       amount=order.sell_amount)
    if approve_transactable:
        result.append(approve_transactable)

    sign_order_transactable = SignOrder(
        blockchain=Chain.get_blockchain_from_web3(w3),
        avatar=avatar,
        sell_token=order.sell_token,
        buy_token=order.buy_token,
        sell_amount=order.sell_amount,
        buy_amount=order.buy_amount,
        fee_amount=order.fee_amount,
        valid_to=order.valid_to,
        valid_duration=valid_duration + 10 * 60,
        # In the order signer contract:
        # require(block.timestamp + validDuration > order.validTo,"Dishonest valid duration");
        # 'valid_duration' is here both an argument SignOrderand and create_order_and_swap but they mean different things
        kind=order.kind,
    )
    result.append(sign_order_transactable)
    return result


def swap(w3: Web3, order: Order, valid_duration: int = 10 * 60) -> list[Transactable]:
    """
    Receives a swap Order object and returns the sign_order Transactable to execute to sign the order on-chain.

    Args:
        w3 (Web3): The web3 object
        order (Order): The order object
        valid_duration (int): The duration the order is valid in seconds

    Returns:
        list[Transactable]: A list with one single Transactable element.

    Raises:
        ValueError: If the receiver and the from address in the order are both not the same address.
        ValueError: If current timestamp + valid_duration is not greater than the parameter valid_to in the order.
    """

    if order.receiver != order.from_address:
        raise ValueError("Both the receiver and the from_address must be the avatar safe.")

    if order.valid_to >= w3.eth.get_block('latest').timestamp + valid_duration:
        raise ValueError("Invalid valid_duration: timestamp + valid_duration must be greater than valid_to")

    result = []
    approve_transactable = check_allowance_and_approve(w3=w3,
                                                       avatar=order.from_address,
                                                       token=order.sell_token,
                                                       spender=ContractSpecs[
                                                           Chain.get_blockchain_from_web3(w3)].CowswapRelayer.address,
                                                       amount=order.sell_amount)
    if approve_transactable:
        result.append(approve_transactable)

    sign_order_transactable = SignOrder(
        blockchain=Chain.get_blockchain_from_web3(w3),
        avatar=order.receiver,
        sell_token=order.sell_token,
        buy_token=order.buy_token,
        sell_amount=order.sell_amount,
        buy_amount=order.buy_amount,
        fee_amount=order.fee_amount,
        valid_to=order.valid_to,
        valid_duration=valid_duration,
        kind=order.kind,
    )
    result.append(sign_order_transactable)
    return result
