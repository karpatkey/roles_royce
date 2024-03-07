from decimal import Decimal
from roles_royce.protocols import uniswap_v3
from roles_royce.protocols.uniswap_v3.types_and_enums import FeeAmount
from tests.utils import local_node_eth
from defabipedia.tokens import EthereumTokenAddr as ETHAddr
import pytest


def test_validate_tokens():
    address_1 = ETHAddr.USDC
    address_2 = ETHAddr.WETH

    assert uniswap_v3.validate_tokens(address_1, address_2) is True

    with pytest.raises(ValueError, match="token0 and token1 must be different"):
        assert uniswap_v3.validate_tokens(address_1, address_1)


def test_validate_amounts():
    amount_0 = 100
    amount_1 = 200

    assert uniswap_v3.validate_amounts(amount_0, None) is True
    assert uniswap_v3.validate_amounts(None, amount_1) is True

    with pytest.raises(ValueError, match="Either amount0_desired or amount1_desired must be provided"):
        assert uniswap_v3.validate_amounts(None, None)

    with pytest.raises(ValueError, match="Only one amount can be provided"):
        assert uniswap_v3.validate_amounts(amount_0, amount_1)

    with pytest.raises(ValueError, match="amount0_desired must be greater than 0"):
        assert uniswap_v3.validate_amounts(-amount_0, None)

    with pytest.raises(ValueError, match="amount1_desired must be greater than 0"):
        assert uniswap_v3.validate_amounts(None, -amount_1)


def validate_price_range():
    assert uniswap_v3.validate_price_range(1, 4, 2) is True
    with pytest.raises(ValueError, match="token0_min_price must be greater than 0"):
        assert uniswap_v3.validate_price_range(-1, 4, 2)
    with pytest.raises(ValueError, match="token1_min_price must be greater than 0"):
        assert uniswap_v3.validate_price_range(1, -4, 2)
    with pytest.raises(ValueError, match="pool_price out of range"):
        assert uniswap_v3.validate_price_range(1, 4, 5)


def test_validate_slippage():
    assert uniswap_v3.validate_slippage(3, 4) is True
    with pytest.raises(ValueError, match="amount0_min_slippage must be between 0 and 100"):
        assert uniswap_v3.validate_slippage(-1, 4)
    with pytest.raises(ValueError, match="amount1_min_slippage must be between 0 and 100"):
        assert uniswap_v3.validate_slippage(1, -4)


def test_validate_removed_liquidity_percentage():
    assert uniswap_v3.validate_removed_liquidity_percentage(3) is True
    with pytest.raises(ValueError, match="removed_liquidity_percentage must be between 0 and 100"):
        assert uniswap_v3.validate_removed_liquidity_percentage(-1)
    with pytest.raises(ValueError, match="removed_liquidity_percentage must be between 0 and 100"):
        assert uniswap_v3.validate_removed_liquidity_percentage(101)


def test_check_allowance(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(19169130)

    token = ETHAddr.USDC
    spender = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"
    owner = "0x849D52316331967b6fF1198e5E32A0eB168D039d"

    assert uniswap_v3.check_allowance(w3, owner, spender, token, 100) is False

    token = '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2'
    spender = '0x447db3e7Cf4b4Dcf7cADE7bDBc375018408B8098'
    owner = '0x4971DD016127F390a3EF6b956Ff944d0E2e1e462'
    assert uniswap_v3.check_allowance(w3, owner, spender, token, 100) is True


def test_pool(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(19368932)

    pool = uniswap_v3.Pool(w3, ETHAddr.USDC, ETHAddr.WETH, FeeAmount.MEDIUM)

    assert pool.addr == "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"
    assert pool.ic == 194016
    assert pool.sqrt_price_x96 == 1293227242398819784334550154076475
    assert pool.sqrt_price == Decimal("16322.82260952329333843603752")
    assert pool.price == Decimal("0.0002664345379419648155527995198")
    assert pool.tick_spacing == 60


def test_nft_position(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(19368932)

    nft_position = uniswap_v3.NFTPosition(w3, 424810)

    assert nft_position.liquidity == 5701094127890312119
    assert nft_position.tick_lower == 0
    assert nft_position.tick_upper == 60
    assert nft_position.price_min == Decimal("1")
    assert nft_position.price_max == Decimal("1.006017734268817500507686164")
    assert nft_position.fr0 == 6653063644654570505260907049128192
    assert nft_position.fr1 == 3604572511083265637921001177185617
