from decimal import Decimal
from roles_royce.protocols import uniswap_v3
from roles_royce.protocols.uniswap_v3.types_and_enums import FeeAmount
from tests.utils import local_node_eth
from defabipedia.tokens import EthereumTokenAddr as ETHAddr


def test_utils(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(19368932)

    pool = uniswap_v3.Pool(w3, ETHAddr.USDC, ETHAddr.WETH, FeeAmount.MEDIUM)

    assert pool.addr == "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"
    assert pool.ic == 194016
    assert pool.sqrt_price_x96 == 1293227242398819784334550154076475
    assert pool.sqrt_price == Decimal("16322.82260952329333843603752")
    assert pool.price == Decimal("0.0002664345379419648155527995198")
    assert pool.tick_spacing == 60

    nft_position = uniswap_v3.NFTPosition(w3, 424810)

    assert nft_position.liquidity == 5701094127890312119
    assert nft_position.tick_lower == 0
    assert nft_position.tick_upper == 60
    assert nft_position.price_min == Decimal("1")
    assert nft_position.price_max == Decimal("1.006017734268817500507686164")
    assert nft_position.fr0 == 6653063644654570505260907049128192
    assert nft_position.fr1 == 3604572511083265637921001177185617
