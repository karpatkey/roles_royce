import roles_royce.protocols.eth.compound_v2 as compound
from roles_royce.constants import ETHAddr


def test_approve():
    m = compound.Approve(token=ETHAddr.USDC, ctoken=compound.Ctoken.cUSDC, amount=123)
    assert (
        m.data
        == "0x095ea7b300000000000000000000000039aa39c021dfbae8fac545936693ac917d5e7563000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_mint():
    m = compound.Mint(ctoken=compound.Ctoken.cDAI, amount=12300)
    assert m.data == "0xa0712d68000000000000000000000000000000000000000000000000000000000000300c"


def test_redeem():
    m = compound.Redeem(ctoken=compound.Ctoken.cETH, amount=12300)
    assert m.data == "0xdb006a75000000000000000000000000000000000000000000000000000000000000300c"


def test_redeem_underlying():
    m = compound.RedeemUnderlying(ctoken=compound.Ctoken.cETH, amount=2300)
    assert m.data == "0x852a12e300000000000000000000000000000000000000000000000000000000000008fc"


def test_enter_markets():
    m = compound.EnterMarkets(ctokens=[compound.Ctoken.cDAI, compound.Ctoken.cETH])
    assert (
        m.data
        == "0xc2998238000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000020000000000000000000000005d3a536e4d6dbd6114cc1ead35777bab948e36430000000000000000000000004ddc2d193948926d02f9b1fe9e1daa0718270ed5"
    )


def test_exit_market():
    m = compound.ExitMarket(ctoken=compound.Ctoken.cDAI)
    assert m.data == "0x057b6c8b0000000000000000000000005d3a536e4d6dbd6114cc1ead35777bab948e3643"


def test_borrow():
    m = compound.Borrow(ctoken=compound.Ctoken.cDAI, amount=123)
    assert m.data == "0xc5ebeaec000000000000000000000000000000000000000000000000000000000000007b"


def test_repay():
    m = compound.Repay(ctoken=compound.Ctoken.cDAI, amount=123)
    assert m.data == "0x0e752702000000000000000000000000000000000000000000000000000000000000007b"


def test_repay_eth():
    m = compound.RepayETH(avatar="0x24Dd242c3c4061b1fCaA5119af608B56afBaEA95", amount=123)
    assert m.data == "0x9f35c3d500000000000000000000000024dd242c3c4061b1fcaa5119af608b56afbaea95"
    assert m.value == 123


def test_claim_comp():
    m = compound.ClaimCOMP(
        avatar="0x24Dd242c3c4061b1fCaA5119af608B56afBaEA95", ctokens=[compound.Ctoken.cSUSHI, compound.Ctoken.cETH]
    )
    assert (
        m.data
        == "0x1c3db2e000000000000000000000000024dd242c3c4061b1fcaa5119af608b56afbaea95000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000020000000000000000000000004b0181102a0112a2ef11abee5563bb4a3176c9d70000000000000000000000004ddc2d193948926d02f9b1fe9e1daa0718270ed5"
    )
