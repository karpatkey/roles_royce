from decimal import Decimal

from defabipedia.types import Chain
from karpatkit.helpers import get_balance
from karpatkit.test_utils.fork import create_simple_safe
from karpatkit.test_utils.fork import local_node_eth_replay as local_node_eth
from karpatkit.test_utils.fork import steal_token

from roles_royce.constants import ETHAddr
from roles_royce.protocols.eth import spark
from roles_royce.toolshed.protocol_utils.spark.utils import SparkUtils


def test_integration(local_node_eth, accounts):
    w3 = local_node_eth.w3
    safe = create_simple_safe(w3, accounts[0])

    ADDRESS_WITH_LOTS_OF_GNO = "0x849D52316331967b6fF1198e5E32A0eB168D039d"

    steal_token(w3, ETHAddr.GNO, holder=ADDRESS_WITH_LOTS_OF_GNO, to=safe.address, amount=123_000_000)
    assert get_balance(w3, ETHAddr.GNO, safe.address) == 123_000_000
    blockchain = Chain.get_blockchain_from_web3(w3)
    # Deposit GNO, receive spGNO
    safe.send(
        [
            spark.ApproveToken(blockchain=blockchain, token=ETHAddr.GNO, amount=123_000_000),
            spark.DepositToken(blockchain=blockchain, token=ETHAddr.GNO, avatar=safe.address, amount=123_000_000),
            spark.ApproveToken(blockchain=blockchain, token=ETHAddr.GNO, amount=0),
        ]
    )
    assert get_balance(w3, ETHAddr.GNO, safe.address) == 0
    assert get_balance(w3, ETHAddr.spGNO, safe.address) == 123_000_000

    # Borrow DAI using GNO as collateral
    res = safe.send([spark.Collateralize(blockchain=blockchain, asset=ETHAddr.GNO, use_as_collateral=True)])
    assert get_balance(w3, ETHAddr.DAI, safe.address) == 0
    res = safe.send(
        [
            spark.Borrow(
                blockchain=blockchain,
                token=ETHAddr.DAI,
                amount=1_000,
                rate_mode=spark.RateMode.VARIABLE,
                avatar=safe.address,
            )
        ]
    )
    assert get_balance(w3, ETHAddr.DAI, safe.address) == 1_000

    # Deposit DAI, get sDAI
    safe.send(
        [
            spark.ApproveDAIforSDAI(amount=1_000),
            spark.DepositDAIforSDAI(blockchain=blockchain, amount=1_000, avatar=safe.address),
            spark.ApproveDAIforSDAI(amount=0),
        ]
    )
    assert get_balance(w3, ETHAddr.DAI, safe.address) == 0
    chi = SparkUtils.get_chi(w3)
    assert get_balance(w3, ETHAddr.sDAI, safe.address) == int(Decimal(1_000) / (Decimal(chi) / Decimal(1e27)))  # 976

    # Repay sDAI to get DAI
    safe.send([spark.RedeemSDAIforDAI(blockchain=blockchain, amount=976, avatar=safe.address)])
    assert get_balance(w3, ETHAddr.DAI, safe.address) == int(Decimal(chi * 976) / Decimal(1e27))  # 999
    assert get_balance(w3, ETHAddr.sDAI, safe.address) == 0

    # Get back the original amount of GNO
    safe.send([spark.WithdrawToken(blockchain=blockchain, token=ETHAddr.GNO, amount=123_000_000, avatar=safe.address)])
    assert get_balance(w3, ETHAddr.GNO, safe.address) == 123_000_000
    assert get_balance(w3, ETHAddr.spGNO, safe.address) == 0
