from pytest import approx
from roles_royce.protocols.eth import spark
from roles_royce.constants import ETHAddr
from tests.utils import local_node, accounts, get_balance, steal_token, create_simple_safe, local_node_set_block, \
    top_up_address, fork_unlock_account
from roles_royce.toolshed.anti_liquidation.spark.cdp import SparkCDPManager
from decimal import Decimal
from roles_royce import check, send, build
from roles_royce.toolshed.protocol_utils.spark.utils import SparkUtils
import time


def test_integration_spark_cdp(local_node, accounts):
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

    cdp_manager = SparkCDPManager(w3, safe.address)
    cdp = cdp_manager.get_cdp_data()

    # use approx as the protocol seems to depend on the timestamp of the blocks
    # and currently there is no way to fake the timestamps
    assert cdp.health_factor == approx(Decimal('3.584290325437631289'))
    target_health_factor = 5
    amount_to_repay = cdp_manager.get_delta_of_token_to_repay(spark_cdp=cdp,
                                                              target_health_factor=target_health_factor,
                                                              token_in_address=ETHAddr.DAI,
                                                              rate_model=spark.RateModel.VARIABLE)
    assert amount_to_repay == approx(283141934912473742122)
    safe.send([spark.ApproveToken(token=ETHAddr.DAI, amount=amount_to_repay),
               spark.Repay(token=ETHAddr.DAI, amount=amount_to_repay, rate_model=spark.RateModel.VARIABLE,
                           avatar=safe.address)])

    cdp = cdp_manager.get_cdp_data()
    assert cdp.health_factor == approx(Decimal('4.999999969705976845'))

    # Testing the 1% tolerance
    target_health_factor = 5
    amount_to_repay = cdp_manager.get_delta_of_token_to_repay(spark_cdp=cdp,
                                                              target_health_factor=target_health_factor,
                                                              token_in_address=ETHAddr.DAI,
                                                              rate_model=spark.RateModel.VARIABLE)
    assert amount_to_repay == 0


def test_integration_spark_cdp_roles(local_node):
    w3 = local_node
    block = 17837956
    local_node_set_block(w3, block)

    avatar_safe_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    roles_mod_address = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
    bot_address = "0xc2319f55e2Be3Ad3d9834234db1dB871A5cFacF7"

    top_up_address(w3, bot_address, 100)  # Sends 100 ETH to the bot address, block is increased by 1
    assert get_balance(w3, ETHAddr.ZERO, bot_address) == int(100e18)

    # Initial data
    initial_DAI_balance = get_balance(w3, ETHAddr.DAI, avatar_safe_address)
    assert initial_DAI_balance == 94798898237423007706087

    cdp_manager = SparkCDPManager(w3, avatar_safe_address)
    cdp = cdp_manager.get_cdp_data()

    target_health_factor = 3
    amount_of_DAI_to_repay = cdp_manager.get_delta_of_token_to_repay(spark_cdp=cdp,
                                                                     target_health_factor=target_health_factor,
                                                                     token_in_address=ETHAddr.DAI,
                                                                     rate_model=spark.RateModel.VARIABLE)
    assert amount_of_DAI_to_repay == approx(182246746503552964110971)

    chi = SparkUtils.get_chi(w3)
    assert chi == approx(1027669482862671731432655317)
    amount_of_sDAI_to_redeem = int(Decimal(amount_of_DAI_to_repay) / (Decimal(chi) / Decimal(1e27)))
    assert amount_of_sDAI_to_redeem == approx(177339831130276946729207)

    redeem_sDAI = spark.RedeemSDAIforDAI(amount=amount_of_sDAI_to_redeem, avatar=avatar_safe_address)
    status_simulation = check([redeem_sDAI], role=5, account=bot_address, roles_mod_address=roles_mod_address,
                              web3=w3)
    assert status_simulation

    fork_unlock_account(w3, bot_address)

    #With the "real" private keys we would execute the command below instead of the next two lines
    #send([redeem_sDAI], role=5, private_key=private_key, roles_mod_address=roles_mod_address,web3=w3)
    redeem_sDAI_tx = build([redeem_sDAI], role=5, account=bot_address, roles_mod_address=roles_mod_address,
                           web3=w3)
    w3.eth.send_transaction(redeem_sDAI_tx)

    delta_in_DAI_balance = get_balance(w3, ETHAddr.DAI, avatar_safe_address) - initial_DAI_balance
    assert delta_in_DAI_balance == approx(amount_of_DAI_to_repay)

    # With the "real" private keys we would execute the command below instead of the next two lines
    #send([spark.ApproveToken(token=ETHAddr.DAI, amount=delta_in_DAI_balance),
    #              spark.Repay(token=ETHAddr.DAI, amount=delta_in_DAI_balance, rate_model=spark.RateModel.VARIABLE,
    #                          avatar=avatar_safe_address)], role=5, private_key=private_key,
    #             roles_mod_address=roles_mod_address,
    #             web3=w3)
    txns = build([spark.ApproveToken(token=ETHAddr.DAI, amount=delta_in_DAI_balance),
                  spark.Repay(token=ETHAddr.DAI, amount=delta_in_DAI_balance, rate_model=spark.RateModel.VARIABLE,
                              avatar=avatar_safe_address)], role=5, account=bot_address,
                 roles_mod_address=roles_mod_address,
                 web3=w3)
    tx_hash = w3.eth.send_transaction(txns)
    w3.eth.wait_for_transaction_receipt(tx_hash, timeout=5)
    cdp = cdp_manager.get_cdp_data()
    assert cdp.health_factor == approx(Decimal('3'))
