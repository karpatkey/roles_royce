from roles_royce.constants import ETHAddr
from roles_royce.protocols import aura
from roles_royce.roles_modifier import RolesMod

from ...utils import local_node_eth

AVATAR = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
ROLES_MOD = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
REVOKER_ROLE = "0xf099e0f6604BDE0AA860B39F7da75770B34aC804"
LP80GNO20WETH = "0x32296969Ef14EB0c6d29669C550D4a0449130230"
REWARDS = "0x59D66C58E83A26d6a0E35114323f65c3945c89c1"


def test_approve_method():
    method = aura.ApproveForBooster(token=LP80GNO20WETH, amount=123)
    assert method.args_list == [ETHAddr.AURABooster, 123]
    assert method.target_address == LP80GNO20WETH
    assert (
        method.data
        == "0x095ea7b3000000000000000000000000a57b8d98dae62b26ec3bcc4a365338157060b234000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_approve_token_dep_wrapper():
    method = aura.ApproveTokenDepWrapper(token=LP80GNO20WETH, amount=123)
    assert (
        method.data
        == "0x095ea7b3000000000000000000000000b188b1cb84fb0ba13cb9ee1292769f903a9fec59000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_approve_aurabal():
    method = aura.ApproveAURABal(amount=123)
    assert (
        method.data
        == "0x095ea7b3000000000000000000000000616e8bfa43f920657b3497dbf40d6b1a02d4608d000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_approve_b80bal20weth():
    method = aura.ApproveB80Bal20WETH(amount=123)
    assert (
        method.data
        == "0x095ea7b3000000000000000000000000ead792b55340aa20181a80d6a16db6a0ecd1b827000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_approve_bal():
    method = aura.ApproveBAL(amount=123)
    assert (
        method.data
        == "0x095ea7b300000000000000000000000068655ad9852a99c87c0934c7290bb62cfa5d4123000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_approve_aurabal_stk():
    method = aura.ApproveAURABalStk(amount=123)
    assert (
        method.data
        == "0x095ea7b3000000000000000000000000faa2ed111b4f580fcb85c48e6dc6782dc5fcd7a6000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_approve_aura():
    method = aura.ApproveAURA(amount=123)
    assert (
        method.data
        == "0x095ea7b30000000000000000000000003fa73f1e5d8a792c80f426fc8f84fbf7ce9bbcac000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_withdraw_and_unwrap():
    method = aura.WithdrawAndUnwrap(reward_address=REWARDS, amount=123)
    assert (
        method.data
        == "0xc32e7202000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000001"
    )


def test_deposit_bpt():
    method = aura.DepositBPT(pool_id=122, amount=99768376997984391577003)
    assert (
        method.data
        == "0x43a0d066000000000000000000000000000000000000000000000000000000000000007a000000000000000000000000000000000000000000001520745dac26a092bdab"
        "0000000000000000000000000000000000000000000000000000000000000001"
    )


def test_stake_aurabal():
    method = aura.StakeAURABal(amount=123)
    assert method.data == "0xa694fc3a000000000000000000000000000000000000000000000000000000000000007b"


def test_deposit_80bal_20weth():
    method = aura.Deposit80BAL20WETH(amount=123, stake_address=AVATAR)
    assert (
        method.data
        == "0x80ed71e4000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000001"
        "000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
    )


def test_deposit_bal():
    method = aura.DepositBAL(amount=123, min_out=123, stake_address=AVATAR)
    assert (
        method.data
        == "0x2968f616000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000000000007b"
        "0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
    )


def test_withdraw_aura():
    method = aura.WithdrawAuraBAL(amount=123, claim=True)
    assert (
        method.data
        == "0x38d07436000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000001"
    )


def test_compounder_staking():
    method = aura.CompounderStaking(amount=123, avatar=AVATAR)
    assert (
        method.data
        == "0x6e553f65000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
    )


def test_compounder_unstaking():
    method = aura.CompounderWithdraw(amount=123, receiver=AVATAR, avatar=AVATAR)
    assert (
        method.data
        == "0xb460af94000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
        "000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
    )


def test_compounder_redeem():
    method = aura.CompounderRedeem(amount=123, avatar=AVATAR, receiver=AVATAR)
    assert (
        method.data
        == "0xba087652000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
        "000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
    )


def test_lock_aura():
    method = aura.LockAURA(amount=123, receiver=AVATAR)
    assert (
        method.data
        == "0x282d3fdf000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_process_expired_locks():
    method = aura.ProcessExpiredLocks(relock=True)
    assert method.data == "0x312ff8390000000000000000000000000000000000000000000000000000000000000001"


def test_approve_method_with_roles(local_node_eth):
    w3 = local_node_eth.w3
    method = aura.ApproveForBooster(token=LP80GNO20WETH, amount=1000)
    ROLE = 1
    roles_mod = RolesMod(role=ROLE, contract_address=ROLES_MOD, account=REVOKER_ROLE, web3=w3)
    check_transaction = roles_mod.check(method.target_address, method.data)
    assert check_transaction
