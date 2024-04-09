from decimal import Decimal
from dataclasses import dataclass, field
import threading
from web3.types import Address, TxReceipt
from web3 import Web3
from defabipedia.uniswap_v3 import ContractSpecs
from defabipedia.types import Chain
from roles_royce.toolshed.alerting.utils import EventLogDecoder
from roles_royce.applications.uniswap_v3_keeper.env import ENV
from roles_royce.protocols.uniswap_v3.utils import NFTPosition, Pool
import os
import json


class MinimumPriceError(Exception):
    pass


@dataclass
class Flags:
    lack_of_gas_warning: threading.Event = field(default_factory=threading.Event)
    tx_executed: threading.Event = field(default_factory=threading.Event)


def check_initial_data(env: ENV, nft_id: int | None):
    if env.TEST_MODE:
        w3 = Web3(Web3.HTTPProvider(f"http://{env.LOCAL_FORK_HOST}:{env.LOCAL_FORK_PORT}"))
    else:
        w3 = Web3(Web3.HTTPProvider(env.RPC_ENDPOINT))
    pool = Pool(w3=w3,
                token0=env.TOKEN0_ADDRESS,
                token1=env.TOKEN1_ADDRESS,
                fee=env.FEE)

    if pool.price < env.MINIMUM_MIN_PRICE:
        raise MinimumPriceError(
            f"The current price is below the minimum min price.\n"
            f"Current price: {pool.price}.\n"
            f"Minimum min price: {env.MINIMUM_MIN_PRICE}")

    if nft_id is None:
        if env.INITIAL_MIN_PRICE is None or env.INITIAL_MAX_PRICE is None:
            raise ValueError(
                f"INITIAL_MIN_PRICE and INITIAL_MAX_PRICE must be provided. INITIAL_MIN_PRICE inputted: {env.INITIAL_MIN_PRICE}, INITIAL_MAX_PRICE inputted: {env.INITIAL_MAX_PRICE}."
            )
        if not (env.INITIAL_MIN_PRICE < env.INITIAL_MAX_PRICE):
            raise ValueError(
                f"INITIAL_MIN_PRICE must be smaller than INITIAL_MAX_PRICE. INITIAL_MIN_PRICE inputted: {env.INITIAL_MIN_PRICE}, INITIAL_MAX_PRICE inputted: {env.INITIAL_MAX_PRICE}."
            )
        if env.MINIMUM_MIN_PRICE >= env.INITIAL_MIN_PRICE:
            raise ValueError(
                f"MINIMUM_MIN_PRICE must be smaller than INITIAL_MIN_PRICE. MINIMUM_MIN_PRICE inputted: {env.MINIMUM_MIN_PRICE}, INITIAL_MIN_PRICE inputted: {env.INITIAL_MIN_PRICE}."
            )
        if env.INITIAL_AMOUNT0 is None and env.INITIAL_AMOUNT1 is None:
            raise ValueError(
                f"At least one of INITIAL_AMOUNT0 or INITIAL_AMOUNT1 must be provided. INITIAL_AMOUNT0 inputted: {env.INITIAL_AMOUNT0}, INITIAL_AMOUNT1 inputted: {env.INITIAL_AMOUNT1}."
            )
        if env.INITIAL_AMOUNT0 is not None and env.INITIAL_AMOUNT1 is not None:
            raise ValueError(
                f"Only one of INITIAL_AMOUNT0 or INITIAL_AMOUNT1 must be provided. INITIAL_AMOUNT0 inputted: {env.INITIAL_AMOUNT0}, INITIAL_AMOUNT1 inputted: {env.INITIAL_AMOUNT1}."
            )
        if env.INITIAL_AMOUNT0 is not None and env.INITIAL_AMOUNT0 <= 0:
            raise ValueError(
                f"INITIAL_AMOUNT0 must be greater than 0. INITIAL_AMOUNT0 inputted: {env.INITIAL_AMOUNT0}."
            )
        if env.INITIAL_AMOUNT1 is not None and env.INITIAL_AMOUNT1 <= 0:
            raise ValueError(
                f"INITIAL_AMOUNT1 must be greater than 0. INITIAL_AMOUNT1 inputted: {env.INITIAL_AMOUNT1}."
            )
        if (float(pool.price) - env.INITIAL_MIN_PRICE) / (
                env.INITIAL_MAX_PRICE - env.INITIAL_MAX_PRICE) < env.PRICE_RANGE_THRESHOLD / 100 or (
                env.INITIAL_MAX_PRICE - float(pool.price)) / (
                env.INITIAL_MAX_PRICE - env.INITIAL_MIN_PRICE) < env.PRICE_RANGE_THRESHOLD / 100:
            raise ValueError(f"The current price is already within the threshold near one of the edges of the price range."
                             f"Please adjust the initial price range.\n"
                             f"Current price: {pool.price}.\n"
                             f"Minimum price threshold: INITIAL_MIN_PRICE + PRICE_RANGE_THRESHOLD / 100 * (INITIAL_MAX_PRICE"
                             f" - INITIAL_MAX_PRICE)  = {env.INITIAL_MIN_PRICE + env.PRICE_RANGE_THRESHOLD / 100 * (env.INITIAL_MAX_PRICE - env.INITIAL_MAX_PRICE)}.\n"
                             f"Maximum price threshold: INITIAL_MAX_PRICE - PRICE_RANGE_THRESHOLD / 100 * (INITIAL_MAX_PRICE"
                             f" - INITIAL_MAX_PRICE)  = {env.INITIAL_MAX_PRICE - env.PRICE_RANGE_THRESHOLD / 100 * (env.INITIAL_MAX_PRICE - env.INITIAL_MAX_PRICE)}.\n"
                             f"Maximum price threshold: INITIAL_MAX_PRICE - PRICE_RANGE_THRESHOLD / 100 * ("
                             f"INITIAL_MAX_PRICE - INITIAL_MIN_PRICE)  = {env.PRICE_RANGE_THRESHOLD}\n")
        delta = (Decimal(env.PRICE_DELTA_MULTIPLIER) * Decimal(env.PRICE_RANGE_THRESHOLD / 100)
                 * Decimal(env.INITIAL_MAX_PRICE - env.INITIAL_MIN_PRICE))

        if delta > pool.price:
            raise ValueError(
                "With the current parameters, the price delta is greater than the current price. Please adjust"
                "the initial price range, the multiplier and the threshold\n"
                f"Current price: {pool.price}\n"
                f"Price delta: (PRICE_DELTA_MULTIPLIER * PRICE_RANGE_THRESHOLD / 100)  (INITIAL_MAX_PRICE - "
                f"INITIAL_MIN_PRICE) = {delta}\n")


def get_nft_id_from_mint_tx(w3: Web3, tx_receipt: TxReceipt, recipient: Address) -> int | None:
    """Returns the NFT Id of the minted NFT in the transaction.

    Args:
        w3 (Web3): Web3 instance.
        tx_receipt (TxReceipt): Transaction receipt.
        recipient (Address): Recipient address that receives the NFT.

    Returns:
        int | None: NFT Id of the minted NFT in the transaction. Returns None if no NFT was minted to the recipient
            in that transaction.
    """
    event_log_decoder = EventLogDecoder(
        Web3().eth.contract(abi=ContractSpecs[Chain.get_blockchain_from_web3(w3)].PositionsNFT.abi)
    )
    for element in tx_receipt.logs:
        if (
                element["address"]
                == ContractSpecs[Chain.get_blockchain_from_web3(w3)].PositionsNFT.address
        ):
            event = event_log_decoder.decode_log(element)
            if not event:
                continue
            if event.name == "Transfer" and event.values["to"] == recipient:
                return event.values["tokenId"]
    return None


def get_all_nfts(
        w3: Web3,
        owner: str,
        discarded_nfts: list[int] = [],
        active: bool = True,
        token0: Address | None = None,
        token1: Address | None = None,
        fee: int | None = None,
) -> list[int]:
    """Returns all NFT Ids owned by a wallet with liquidity>0. It a priori filters any NFT Ids that are passed in the
    discarded_nfts list (this allows for faster performance). If active=True, it will discard those with liquidity=0.
    It also filters by token0, token1 and fee if these are specified.

    Args:
        w3 (Web3): Web3 instance.
        owner (str): Owner address.
        discarded_nfts (list[int], optional): List of NFT Ids to be discarded. Defaults to [].
        active (bool, optional): If True, it will only return NFT Ids with liquidity>0. Defaults to True.
        token0 (Address | None, optional): Token0 address. Defaults to None. If specified it will only return NFT Ids
            having liquidity in a pool with token0 as token0.
        token1 (Address | None, optional): Token1 address. Defaults to None. If specified it will only return NFT Ids
            having liquidity in a pool with token1 as token1.
        fee (int | None, optional): Fee. Defaults to None. If specified it will only return NFT Ids having liquidity in
            a pool with the specified fee.

    Returns:
        a list where each element is the nft id with liquidity>0 that is owned by the wallet (open and closed nfts)
    """

    result = []

    nft_contract = ContractSpecs[
        Chain.get_blockchain_from_web3(w3)
    ].PositionsNFT.contract(w3)
    nfts = nft_contract.functions.balanceOf(owner).call()
    for nft_index in range(nfts):
        nft_id = nft_contract.functions.tokenOfOwnerByIndex(owner, nft_index).call()
        if nft_id in discarded_nfts:
            continue
        nft_position = NFTPosition(w3=w3, nft_id=nft_id)
        if active:
            if nft_position.liquidity == 0:
                continue
        if token0 is not None:
            if nft_position.pool.token0 != token0:
                continue
        if token1 is not None:
            if nft_position.pool.token1 != token1:
                continue
        if fee is not None:
            if nft_position.pool.fee != fee:
                continue
        result.append(nft_id)
    return result


def get_amounts_quotient_from_price_delta(pool: Pool, price_delta: Decimal) -> Decimal:
    """Returns the quotient of the amounts of token0 and token1 in a pool for a given symmetric price range.
    Specifically, returns the quotient amount1/amount0 corresponding to prices price_min=price-price_delta and
    price_max=price+price_delta.

    Args:
        pool (Pool): Pool instance.
        price_delta (Decimal): Half of the length of the new symmetric price range.

    Returns:
        Decimal: Quotient amount1/amount0.

    Raises:
        ValueError: If price_delta is greater than the current price.
    """
    if pool.price < price_delta:
        raise ValueError("Price delta has to be smaller than the pool's price.")
    decimals_factor = Decimal(10 ** (pool.token1_decimals - pool.token0_decimals))
    sqrt_price = pool.sqrt_price
    price = pool.price

    return (sqrt_price * ((price + price_delta) * decimals_factor).sqrt() * (
            sqrt_price - ((price - price_delta) * decimals_factor).sqrt())
            / (((price + price_delta) * decimals_factor).sqrt() - sqrt_price))


def get_active_nft() -> int | None:
    file = os.path.join(os.path.dirname(__file__), "active_nft.json")
    if not os.path.isfile(file):
        raise FileNotFoundError("nfts.json file not found")
    with open(file, "r") as f:
        nft_dict = json.load(f)
        if nft_dict["active_nft"] == "":
            return None
        else:
            return int(nft_dict["active_nft"])


def store_active_nft(nft_id: int) -> None:
    file = os.path.join(os.path.dirname(__file__), "active_nft.json")
    with open(file, "w") as f:
        json.dump({"active_nft": nft_id}, f)
