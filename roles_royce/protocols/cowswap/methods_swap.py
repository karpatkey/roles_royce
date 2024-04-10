from roles_royce.protocols.cowswap.contract_methods import SignOrder
from roles_royce.protocols.cowswap.utils import QuoteOrderCowSwap, SwapKind
from roles_royce.protocols.utils import check_allowance_and_approve
from roles_royce.protocols.base import AvatarAddress
from web3 import Web3
from roles_royce.generic_method import Transactable
from defabipedia.types import Chain
from defabipedia.cowswap_signer import ContractSpecs
from web3.types import Address


def CowSwap(w3: Web3,
            avatar: AvatarAddress,
            sell_token: Address,
            buy_token: Address,
            amount: int,
            receiver: Address,
            kind: SwapKind,
            max_slippage: float,
            valid_duration: int = 20 * 60) -> list[Transactable]:
    quote = QuoteOrderCowSwap(
        blockchain=Chain.get_blockchain_from_web3(w3),
        sell_token=sell_token,
        buy_token=buy_token,
        receiver=receiver,
        kind=kind,
        amount=amount,
    )

    fee_amount = quote.fee_amount
    buy_amount = quote.buy_amount if kind == SwapKind.BUY else int(quote.buy_amount * (1 - max_slippage))
    sell_amount = quote.sell_amount if kind == SwapKind.SELL else int(quote.sell_amount * (1 + max_slippage))

    result = []
    approve_transactable = check_allowance_and_approve(w3=w3,
                                                       avatar=avatar,
                                                       token=sell_token,
                                                       spender=ContractSpecs[Chain.get_blockchain_from_web3(w3)].CowswapRelayer.address,
                                                       amount=sell_amount + fee_amount)
    if approve_transactable:
        result.append(approve_transactable)

    sign_order_transactable = SignOrder(
        blockchain=Chain.get_blockchain_from_web3(w3),
        avatar=avatar,
        sell_token=sell_token,
        buy_token=buy_token,
        sell_amount=sell_amount,
        buy_amount=buy_amount,
        fee_amount=fee_amount,
        valid_duration=valid_duration,
        kind="sell",
    )
    result.append(sign_order_transactable)
    return result
