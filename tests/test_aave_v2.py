from roles_royce.constants import ETHAddr, GCAddr
from roles_royce.protocols.eth import aave_v2 as aave
from roles_royce.roles_modifier import RolesMod

from .utils import local_node_eth

AVATAR = "0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89"
ROLES_MOD_ADDRESS = "0xd8dd9164E765bEF903E429c9462E51F0Ea8514F9"
MANAGER_SAFE_ADDRESS = "0x60716991aCDA9E990bFB3b1224f1f0fB81538267"


def test_approve_method():
    method = aave.ApproveForAaveLendingPoolV2(token=GCAddr.USDT, amount=123)
    assert method.args_list == [ETHAddr.AAVE_V2_LendingPool, 123]
    assert method.target_address == GCAddr.USDT
    assert (
        method.data
        == "0x095ea7b30000000000000000000000007d2768de32b0b80b7a3454c06bdac94a69ddc7a9000000000000000000000000000000000000000000000000000000000000007b"
    )

    amount = 10000
    method = aave.ApproveForStkAAVE(amount=amount)
    assert method.args_list == [ETHAddr.stkAAVE, amount]
    assert (
        method.data
        == "0x095ea7b30000000000000000000000004da27a545c0c5b758a6ba100e3a049001de870f50000000000000000000000000000000000000000000000000000000000002710"
    )


def test_approve_method_with_roles(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(17683159)
    method = aave.ApproveForStkAAVE(amount=1000)
    ROLE = 1
    ROLES_MOD_ADDRESS = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
    REVOKER_ADDRESS = "0xf099e0f6604BDE0AA860B39F7da75770B34aC804"
    roles_mod = RolesMod(role=ROLE, contract_address=ROLES_MOD_ADDRESS, account=REVOKER_ADDRESS, web3=w3)
    check_transaction = roles_mod.check(method.target_address, method.data, block=17603159)
    assert check_transaction


def test_approve_for_stkaave():
    method = aave.ApproveForStkAAVE(amount=123)
    assert (
        method.data
        == "0x095ea7b30000000000000000000000004da27a545c0c5b758a6ba100e3a049001de870f5000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_approve_for_paraswap_liquidity():
    aDAI = "0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d"
    method = aave.ApproveForParaSwapLiquidity(token=aDAI, amount=123)
    assert (
        method.data
        == "0x095ea7b3000000000000000000000000135896de8421be2ec868e0b811006171d9df802a000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_deposit_method():
    method = aave.DepositToken(asset=GCAddr.USDT, amount=100, avatar=AVATAR)
    referral_code = 0
    assert method.args_list == [GCAddr.USDT, 100, AVATAR, referral_code]
    assert method.target_address == ETHAddr.AAVE_V2_LendingPool


def test_deposit_eth():
    method = aave.DepositETH(eth_amount=123, avatar=AVATAR)
    referral_code = 0
    assert method.args_list == [ETHAddr.AAVE_V2_LendingPool, AVATAR, referral_code]
    assert method.target_address == ETHAddr.AAVE_V2_WrappedTokenGateway
    assert method.value == 123


def test_borrow():
    method = aave.Borrow(asset=GCAddr.USDT, amount=123, interest_rate_mode=aave.InterestRateMode.STABLE, avatar=AVATAR)
    referral_code = 0
    assert method.args_list == [GCAddr.USDT, 123, 1, referral_code, AVATAR]
    assert method.target_address == ETHAddr.AAVE_V2_LendingPool


def test_borrow_with_bad_interest_rate():
    method = aave.Borrow(asset=GCAddr.USDT, amount=123, interest_rate_mode=aave.InterestRateMode.STABLE, avatar=AVATAR)
    referral_code = 0
    assert method.args_list == [GCAddr.USDT, 123, 1, referral_code, AVATAR]
    assert method.target_address == ETHAddr.AAVE_V2_LendingPool


def test_borrow_eth():
    method = aave.BorrowETH(amount=123, interest_rate_mode=aave.InterestRateMode.VARIABLE)
    referral_code = 0
    assert method.args_list == [ETHAddr.AAVE_V2_LendingPool, 123, 2, referral_code]
    assert method.target_address == ETHAddr.AAVE_V2_WrappedTokenGateway


def test_swap_borrow_rate_mode():
    method = aave.SwapBorrowRateMode(asset=ETHAddr.DAI, interest_rate_mode=aave.InterestRateMode.STABLE)
    assert (
        method.data
        == "0x94ba89a20000000000000000000000006b175474e89094c44da98b954eedeac495271d0f0000000000000000000000000000000000000000000000000000000000000001"
    )


def test_repay_eth():
    method = aave.RepayETH(eth_amount=10, interest_rate_mode=aave.InterestRateMode.VARIABLE, avatar=AVATAR)
    assert method.args.amount == 10
    assert method.value == 10


def test_cooldown(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(17683159)
    method = aave.CooldownStkAAVE()
    roles_mod = RolesMod(role=1, contract_address=ROLES_MOD_ADDRESS, account=MANAGER_SAFE_ADDRESS, web3=w3)
    check_transaction = roles_mod.check(method.target_address, method.data, block=17603159)
    assert check_transaction


def test_claim(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(17683159)
    method = aave.ClaimAAVERewards(avatar=AVATAR, amount=10)

    roles_mod = RolesMod(role=1, contract_address=ROLES_MOD_ADDRESS, account=MANAGER_SAFE_ADDRESS, web3=w3)
    check_transaction = roles_mod.check(method.target_address, method.data, block=17603159)
    assert check_transaction


def test_unstake():
    method = aave.UnstakeAAVE(avatar=AVATAR, amount=10)
    assert (
        method.data
        == "0x1e9a69500000000000000000000000000efccbb9e2c09ea29551879bd9da32362b32fc89000000000000000000000000000000000000000000000000000000000000000a"
    )


def test_delegate():
    method = aave.DelegateAAVEByType(delegatee=AVATAR, delegation_type=aave.DelegationType.VOTING)
    assert (
        method.data
        == "0xdc937e1c0000000000000000000000000efccbb9e2c09ea29551879bd9da32362b32fc890000000000000000000000000000000000000000000000000000000000000000"
    )


def test_submit_vote():
    method = aave.SubmitVote(support=True, proposal_id=12345)
    assert (
        method.data
        == "0x612c56fa00000000000000000000000000000000000000000000000000000000000030390000000000000000000000000000000000000000000000000000000000000001"
    )
