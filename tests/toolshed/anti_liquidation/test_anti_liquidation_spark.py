from decimal import Decimal

from pytest import approx

from roles_royce import roles
from roles_royce.constants import ETHAddr
from roles_royce.protocols.eth import spark
from roles_royce.toolshed.anti_liquidation.spark import CDPData, SparkCDPManager
from roles_royce.toolshed.protocol_utils.spark.utils import SparkToken, SparkUtils
from tests.utils import (
    accounts,
    assign_role,
    create_simple_safe,
    get_allowance,
    get_balance,
    local_node_eth,
    steal_token,
    top_up_address,
)


def test_spark_cdp_manager_token_addresses(local_node_eth):
    w3 = local_node_eth.w3
    block = 17837956
    local_node_eth.set_block(block)
    owner_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    cdp_manager = SparkCDPManager(w3, owner_address, token_addresses_block=block)
    assert cdp_manager.token_addresses == [
        {
            SparkToken.VARIABLE_DEBT: "0xf705d2B7e92B3F38e6ae7afaDAA2fEE110fE5914",
            SparkToken.STABLE_DEBT: "0xfe2B7a7F4cC0Fb76f7Fc1C6518D586F1e4559176",
            SparkToken.INTEREST_BEARING: "0x4DEDf26112B3Ec8eC46e7E31EA5e123490B05B8B",
            SparkToken.UNDERLYING: "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        },
        {
            SparkToken.VARIABLE_DEBT: "0xaBc57081C04D921388240393ec4088Aa47c6832B",
            SparkToken.STABLE_DEBT: "0xEc6C6aBEd4DC03299EFf82Ac8A0A83643d3cB335",
            SparkToken.INTEREST_BEARING: "0x78f897F0fE2d3B5690EbAe7f19862DEacedF10a7",
            SparkToken.UNDERLYING: "0x83F20F44975D03b1b09e64809B757c47f942BEeA",
        },
        {
            SparkToken.VARIABLE_DEBT: "0x7B70D04099CB9cfb1Db7B6820baDAfB4C5C70A67",
            SparkToken.STABLE_DEBT: "0x887Ac022983Ff083AEb623923789052A955C6798",
            SparkToken.INTEREST_BEARING: "0x377C3bd93f2a2984E1E7bE6A5C22c525eD4A4815",
            SparkToken.UNDERLYING: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        },
        {
            SparkToken.VARIABLE_DEBT: "0x2e7576042566f8D6990e07A1B61Ad1efd86Ae70d",
            SparkToken.STABLE_DEBT: "0x3c6b93D38ffA15ea995D1BC950d5D0Fa6b22bD05",
            SparkToken.INTEREST_BEARING: "0x59cD1C87501baa753d0B5B5Ab5D8416A45cD71DB",
            SparkToken.UNDERLYING: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        },
        {
            SparkToken.VARIABLE_DEBT: "0xd5c3E3B566a42A6110513Ac7670C1a86D76E13E6",
            SparkToken.STABLE_DEBT: "0x9832D969a0c8662D98fFf334A4ba7FeE62b109C2",
            SparkToken.INTEREST_BEARING: "0x12B54025C112Aa61fAce2CDB7118740875A566E9",
            SparkToken.UNDERLYING: "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
        },
        {
            SparkToken.VARIABLE_DEBT: "0xf6fEe3A8aC8040C3d6d81d9A4a168516Ec9B51D2",
            SparkToken.STABLE_DEBT: "0x4b29e6cBeE62935CfC92efcB3839eD2c2F35C1d9",
            SparkToken.INTEREST_BEARING: "0x4197ba364AE6698015AE5c1468f54087602715b2",
            SparkToken.UNDERLYING: "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        },
        {
            SparkToken.VARIABLE_DEBT: "0x57a2957651DA467fCD4104D749f2F3684784c25a",
            SparkToken.STABLE_DEBT: "0xbf13910620722D4D4F8A03962894EB3335Bf4FaE",
            SparkToken.INTEREST_BEARING: "0x7b481aCC9fDADDc9af2cBEA1Ff2342CB1733E50F",
            SparkToken.UNDERLYING: "0x6810e776880C02933D47DB1b9fc05908e5386b96",
        },
        {
            SparkToken.VARIABLE_DEBT: "0xBa2C8F2eA5B56690bFb8b709438F049e5Dd76B96",
            SparkToken.STABLE_DEBT: "0xa9a4037295Ea3a168DC3F65fE69FdA524d52b3e1",
            SparkToken.INTEREST_BEARING: "0x9985dF20D7e9103ECBCeb16a84956434B6f06ae8",
            SparkToken.UNDERLYING: "0xae78736Cd615f374D3085123A210448E74Fc6393",
        },
    ]


def test_spark_cdp_manager_balances_data(local_node_eth):
    w3 = local_node_eth.w3
    block = 17837956
    local_node_eth.set_block(block)
    owner_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    cdp_manager = SparkCDPManager(w3, owner_address, token_addresses_block=block)
    cdp = cdp_manager.get_cdp_data(block=block)
    assert cdp.balances_data == [
        {
            CDPData.LiquidationThreshold: Decimal("0.76"),
            CDPData.VariableDebtBalance: Decimal("1000824.038165527779863585"),
            CDPData.UnderlyingPriceUSD: Decimal("1.00106418"),
            CDPData.CollateralEnabled: False,
            CDPData.StableDebtBalance: Decimal(0),
            CDPData.UnderlyingAddress: "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            CDPData.InterestBearingBalance: Decimal(0),
        },
        {
            CDPData.LiquidationThreshold: Decimal("0.25"),
            CDPData.VariableDebtBalance: Decimal(0),
            CDPData.UnderlyingPriceUSD: Decimal("111.74296612"),
            CDPData.CollateralEnabled: True,
            CDPData.StableDebtBalance: Decimal(0),
            CDPData.UnderlyingAddress: "0x6810e776880C02933D47DB1b9fc05908e5386b96",
            CDPData.InterestBearingBalance: Decimal("88000"),
        },
    ]


def test_spark_cdp_manager_health_factor(local_node_eth):
    w3 = local_node_eth.w3
    block = 17837956
    local_node_eth.set_block(block)
    owner_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    cdp_manager = SparkCDPManager(w3, owner_address, token_addresses_block=block)
    cdp = cdp_manager.get_cdp_data(block=block)
    assert cdp.health_factor == Decimal("2.45370996319511532")


def test_spark_cdp_manager_get_delta(local_node_eth):
    w3 = local_node_eth.w3
    block = 17837956
    local_node_eth.set_block(block)
    owner_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    cdp_manager = SparkCDPManager(w3, owner_address, token_addresses_block=block)
    cdp = cdp_manager.get_cdp_data(block=block)
    target_health_factor = 5
    amount_to_repay = cdp_manager.get_delta_of_token_to_repay(
        spark_cdp=cdp,
        target_health_factor=target_health_factor,
        token_in_address=ETHAddr.DAI,
        rate_model=spark.RateModel.VARIABLE,
    )
    assert amount_to_repay == 509677655395144366484434


def test_integration_spark_cdp(local_node_eth, accounts):
    local_node_eth.reset_state()  # Back to block ETH_LOCAL_NODE_DEFAULT_BLOCK = 17565000
    w3 = local_node_eth.w3

    safe = create_simple_safe(w3, accounts[0])

    ADDRESS_WITH_LOTS_OF_GNO = "0x849D52316331967b6fF1198e5E32A0eB168D039d"

    steal_token(w3, ETHAddr.GNO, holder=ADDRESS_WITH_LOTS_OF_GNO, to=safe.address, amount=int(123e18))
    assert get_balance(w3, ETHAddr.GNO, safe.address) == int(123e18)

    # Deposit GNO, receive spGNO
    safe.send(
        [
            spark.ApproveToken(token=ETHAddr.GNO, amount=int(123e18)),
            spark.DepositToken(token=ETHAddr.GNO, avatar=safe.address, amount=int(123e18)),
            spark.ApproveToken(token=ETHAddr.GNO, amount=0),
        ]
    )
    assert get_balance(w3, ETHAddr.GNO, safe.address) == 0
    assert get_balance(w3, ETHAddr.spGNO, safe.address) == int(123e18)

    # Borrow DAI using GNO as collateral
    safe.send([spark.SetUserUseReserveAsCollateral(asset=ETHAddr.GNO, use=True)])
    assert get_balance(w3, ETHAddr.DAI, safe.address) == 0
    safe.send(
        [
            spark.Borrow(
                token=ETHAddr.DAI, amount=int(1_000e18), rate_model=spark.RateModel.VARIABLE, avatar=safe.address
            )
        ]
    )
    assert get_balance(w3, ETHAddr.DAI, safe.address) == int(1_000e18)

    cdp_manager = SparkCDPManager(w3, safe.address)

    cdp = cdp_manager.get_cdp_data()

    # use approx as the protocol seems to depend on the timestamp of the blocks
    # and currently there is no way to fake the timestamps

    assert cdp.health_factor == approx(Decimal("3.584290325437631289"))
    target_health_factor = 5
    amount_to_repay = cdp_manager.get_delta_of_token_to_repay(
        spark_cdp=cdp,
        target_health_factor=target_health_factor,
        token_in_address=ETHAddr.DAI,
        rate_model=spark.RateModel.VARIABLE,
    )
    assert amount_to_repay == approx(283141934912473742122)
    safe.send(
        [
            spark.ApproveToken(token=ETHAddr.DAI, amount=amount_to_repay),
            spark.Repay(
                token=ETHAddr.DAI, amount=amount_to_repay, rate_model=spark.RateModel.VARIABLE, avatar=safe.address
            ),
        ]
    )

    cdp = cdp_manager.get_cdp_data()

    assert cdp.health_factor == approx(Decimal("4.999999969705976845"))

    # Testing the 1% tolerance
    target_health_factor = 5
    amount_to_repay = cdp_manager.get_delta_of_token_to_repay(
        spark_cdp=cdp,
        target_health_factor=target_health_factor,
        token_in_address=ETHAddr.DAI,
        rate_model=spark.RateModel.VARIABLE,
    )
    assert amount_to_repay == 0


def test_integration_spark_cdp_roles_1(local_node_eth):
    w3 = local_node_eth.w3
    block = 17837956
    local_node_eth.set_block(block)

    avatar_safe_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    roles_mod_address = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
    bot_address = "0xc2319f55e2Be3Ad3d9834234db1dB871A5cFacF7"
    # Role 5 already has the correct preset applied
    role = 5

    top_up_address(w3, bot_address, 100)  # Sends 100 ETH to the bot address, block is increased by 1
    assert get_balance(w3, ETHAddr.ZERO, bot_address) == int(100e18)

    # Initial data
    initial_DAI_balance = get_balance(w3, ETHAddr.DAI, avatar_safe_address)
    assert initial_DAI_balance == 94798898237423007706087

    cdp_manager = SparkCDPManager(w3, avatar_safe_address)
    cdp = cdp_manager.get_cdp_data()

    target_health_factor = 3
    amount_of_DAI_to_repay = cdp_manager.get_delta_of_token_to_repay(
        spark_cdp=cdp,
        target_health_factor=target_health_factor,
        token_in_address=ETHAddr.DAI,
        rate_model=spark.RateModel.VARIABLE,
    )
    assert amount_of_DAI_to_repay == approx(182246746503552964110971)

    chi = SparkUtils.get_chi(w3)
    assert chi == approx(1027669482862671731432655317)
    amount_of_sDAI_to_redeem = int(Decimal(amount_of_DAI_to_repay) / (Decimal(chi) / Decimal(1e27)))
    assert amount_of_sDAI_to_redeem == approx(177339831130276946729207)

    redeem_sDAI = spark.RedeemSDAIforDAI(amount=amount_of_sDAI_to_redeem, avatar=avatar_safe_address)
    status_simulation = roles.check(
        [redeem_sDAI], role=role, account=bot_address, roles_mod_address=roles_mod_address, web3=w3
    )
    assert status_simulation

    local_node_eth.unlock_account(bot_address)

    redeem_sDAI_tx = roles.build(
        [redeem_sDAI], role=role, account=bot_address, roles_mod_address=roles_mod_address, web3=w3
    )
    w3.eth.send_transaction(redeem_sDAI_tx)

    delta_in_DAI_balance = get_balance(w3, ETHAddr.DAI, avatar_safe_address) - initial_DAI_balance
    assert delta_in_DAI_balance == approx(amount_of_DAI_to_repay)

    txns = roles.build(
        [
            spark.ApproveToken(token=ETHAddr.DAI, amount=delta_in_DAI_balance),
            spark.Repay(
                token=ETHAddr.DAI,
                amount=delta_in_DAI_balance,
                rate_model=spark.RateModel.VARIABLE,
                avatar=avatar_safe_address,
            ),
        ],
        role=role,
        account=bot_address,
        roles_mod_address=roles_mod_address,
        web3=w3,
    )
    tx_hash = w3.eth.send_transaction(txns)
    w3.eth.wait_for_transaction_receipt(tx_hash, timeout=5)
    cdp = cdp_manager.get_cdp_data()
    assert cdp.health_factor == approx(Decimal("3"))


def test_integration_spark_cdp_roles_2(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = 17837956
    local_node_eth.set_block(block)

    avatar_safe_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    roles_mod_address = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
    # Role 5 already has the correct preset applied
    role = 5
    assign_role(local_node_eth, avatar_safe_address, roles_mod_address, role, accounts[0].address)

    bot_address = accounts[0].address
    private_key = accounts[0].key.hex()

    # Initial data
    initial_DAI_balance = get_balance(w3, ETHAddr.DAI, avatar_safe_address)
    assert initial_DAI_balance == 94798898237423007706087

    cdp_manager = SparkCDPManager(w3, avatar_safe_address)
    cdp = cdp_manager.get_cdp_data()

    target_health_factor = 3
    amount_of_DAI_to_repay = cdp_manager.get_delta_of_token_to_repay(
        spark_cdp=cdp,
        target_health_factor=target_health_factor,
        token_in_address=ETHAddr.DAI,
        rate_model=spark.RateModel.VARIABLE,
    )
    assert amount_of_DAI_to_repay == approx(182246746503552964110971)

    chi = SparkUtils.get_chi(w3)
    assert chi == approx(1027669482862671731432655317)
    amount_of_sDAI_to_redeem = int(Decimal(amount_of_DAI_to_repay) / (Decimal(chi) / Decimal(1e27)))
    assert amount_of_sDAI_to_redeem == approx(177339831130276946729207)

    redeem_sDAI = spark.RedeemSDAIforDAI(amount=amount_of_sDAI_to_redeem, avatar=avatar_safe_address)
    status_simulation = roles.check(
        [redeem_sDAI], role=role, account=bot_address, roles_mod_address=roles_mod_address, web3=w3
    )
    assert status_simulation

    roles.send([redeem_sDAI], role=role, private_key=private_key, roles_mod_address=roles_mod_address, web3=w3)

    DAI_balance = get_balance(w3, ETHAddr.DAI, avatar_safe_address)
    delta_in_DAI_balance = DAI_balance - initial_DAI_balance
    assert delta_in_DAI_balance == approx(amount_of_DAI_to_repay)

    amount_of_DAI_to_repay = amount_of_DAI_to_repay if amount_of_DAI_to_repay < DAI_balance else DAI_balance
    pre_allowance = get_allowance(w3, ETHAddr.DAI, avatar_safe_address, "0xC13e21B648A5Ee794902342038FF3aDAB66BE987")
    assert pre_allowance == 0
    roles.send(
        [spark.ApproveToken(token=ETHAddr.DAI, amount=amount_of_DAI_to_repay + int(1000e18))],
        role=role,
        private_key=private_key,
        roles_mod_address=roles_mod_address,
        web3=w3,
    )
    cdp_manager.repay_single_token_debt(
        cdp,
        token_in_address=ETHAddr.DAI,
        rate_model=spark.RateModel.VARIABLE,
        token_in_amount=amount_of_DAI_to_repay,
        roles_mod_address=roles_mod_address,
        role=role,
        private_key=private_key,
    )

    post_allowance = get_allowance(w3, ETHAddr.DAI, avatar_safe_address, "0xC13e21B648A5Ee794902342038FF3aDAB66BE987")
    assert post_allowance == 0

    cdp = cdp_manager.get_cdp_data()
    assert cdp.health_factor == approx(Decimal("3"))


def test_integration_spark_cdp_roles_3(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = 17837956
    local_node_eth.set_block(block)

    avatar_safe_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    roles_mod_address = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
    # Role 5 already has the correct preset applied
    role = 5
    assign_role(local_node_eth, avatar_safe_address, roles_mod_address, role, accounts[0].address)
    private_key = accounts[0].key.hex()

    cdp_manager = SparkCDPManager(w3, avatar_safe_address)
    cdp = cdp_manager.get_cdp_data()

    target_health_factor = 3
    amount_of_DAI_to_repay = cdp_manager.get_delta_of_token_to_repay(
        spark_cdp=cdp,
        target_health_factor=target_health_factor,
        token_in_address=ETHAddr.DAI,
        rate_model=spark.RateModel.VARIABLE,
    )

    chi = SparkUtils.get_chi(w3)
    amount_of_sDAI_to_redeem = int(Decimal(amount_of_DAI_to_repay) / (Decimal(chi) / Decimal(1e27)))

    redeem_sDAI = spark.RedeemSDAIforDAI(amount=amount_of_sDAI_to_redeem, avatar=avatar_safe_address)
    roles.send([redeem_sDAI], role=role, private_key=private_key, roles_mod_address=roles_mod_address, web3=w3)

    DAI_balance = get_balance(w3, ETHAddr.DAI, avatar_safe_address)
    amount_of_DAI_to_repay = amount_of_DAI_to_repay if amount_of_DAI_to_repay < DAI_balance else DAI_balance
    roles.send(
        [spark.ApproveToken(token=ETHAddr.DAI, amount=amount_of_DAI_to_repay - int(1000e18))],
        role=role,
        private_key=private_key,
        roles_mod_address=roles_mod_address,
        web3=w3,
    )
    cdp_manager.repay_single_token_debt(
        cdp,
        token_in_address=ETHAddr.DAI,
        rate_model=spark.RateModel.VARIABLE,
        token_in_amount=amount_of_DAI_to_repay,
        roles_mod_address=roles_mod_address,
        role=role,
        private_key=private_key,
    )

    post_allowance = get_allowance(w3, ETHAddr.DAI, avatar_safe_address, "0xC13e21B648A5Ee794902342038FF3aDAB66BE987")
    assert post_allowance == 0
    cdp = cdp_manager.get_cdp_data()
    assert cdp.health_factor == approx(Decimal("3"))
