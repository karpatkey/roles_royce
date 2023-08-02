from pytest import approx
from roles_royce.protocols.eth import spark
from roles_royce.constants import ETHAddr
from tests.utils import local_node, accounts, get_balance, steal_token, create_simple_safe
from roles_royce.toolshed.anti_liquidation.spark import SparkCDP
from decimal import Decimal
from math import ceil


def test_integration(local_node, accounts):
    w3 = local_node

    safe = create_simple_safe(w3, accounts[0])

    ADDRESS_WITH_LOTS_OF_GNO = "0x849D52316331967b6fF1198e5E32A0eB168D039d"

    steal_token(w3, ETHAddr.GNO, holder=ADDRESS_WITH_LOTS_OF_GNO, to=safe.address, amount=int(123e18))
    assert get_balance(w3, ETHAddr.GNO, safe.address) == int(123e18)

    # Deposit GNO, receive spGNO
    safe.send([spark.ApproveToken(token=ETHAddr.GNO, amount=int(123e18)),
               spark.DepositToken(token=ETHAddr.GNO, avatar=safe.address,
                                  amount=int(123e18)),
               spark.ApproveToken(token=ETHAddr.GNO, amount=0)])
    assert get_balance(w3, ETHAddr.GNO, safe.address) == 0
    assert get_balance(w3, ETHAddr.spGNO, safe.address) == int(123e18)

    # Borrow DAI using GNO as collateral
    safe.send([spark.SetUserUseReserveAsCollateral(asset=ETHAddr.GNO, use=True)])
    assert get_balance(w3, ETHAddr.DAI, safe.address) == 0
    safe.send([spark.Borrow(token=ETHAddr.DAI, amount=int(1_000e18),
                            rate_model=spark.RateModel.VARIABLE,
                            avatar=safe.address)])
    assert get_balance(w3, ETHAddr.DAI, safe.address) == int(1_000e18)

    cdp = SparkCDP(w3, safe.address)

    # use approx as the protocol seems to depend on the timestamp of the blocks
    # and currently there is no way to fake the timestamps
    assert cdp.health_factor == approx(Decimal('3.584290325437631289'))
    target_health_factor = 5
    delta = cdp.get_delta_of_token_to_repay(target_health_factor, ETHAddr.DAI, rate_model=spark.RateModel.VARIABLE)
    assert delta == approx(Decimal('283.1419349124737421226367910'))
    amount_to_repay = ceil(delta * Decimal(1e18))
    safe.send([spark.ApproveToken(token=ETHAddr.DAI, amount=amount_to_repay),
               spark.Repay(token=ETHAddr.DAI, amount=amount_to_repay, rate_model=spark.RateModel.VARIABLE, avatar=safe.address)])

    cdp.update_data()
    assert cdp.health_factor == approx(Decimal('4.999999969705976845'))

    # Testing the 1% tolerance
    target_health_factor = 5
    amount_to_repay = ceil(cdp.get_delta_of_token_to_repay(target_health_factor, ETHAddr.DAI,
                                                           rate_model=spark.RateModel.VARIABLE) * Decimal(1e18))
    assert amount_to_repay == 0
