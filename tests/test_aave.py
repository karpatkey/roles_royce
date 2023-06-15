import pytest
from eth_abi import abi
from roles_royce.roles_modifier import RolesMod
from roles_royce.constants import ETHAddr, GCAddr

from roles_royce.protocols.eth import aave
from .utils import web3_eth

AVATAR = "0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89"
ROLES_MOD_ADDRESS = "0xd8dd9164E765bEF903E429c9462E51F0Ea8514F9"
MANAGER_SAFE_ADDRESS = "0x60716991aCDA9E990bFB3b1224f1f0fB81538267"


def test_approve_method():
    method = aave.ApproveForAaveLendingPoolV2(token=GCAddr.USDT, amount=123)
    assert method.args_list == [ETHAddr.AaveLendingPoolV2, 123]
    assert method.target_address == GCAddr.USDT
    assert method.data == "0x095ea7b30000000000000000000000007d2768de32b0b80b7a3454c06bdac94a69ddc7a9000000000000000000000000000000000000000000000000000000000000007b"

    amount = 10000
    method = aave.ApproveForStkAAVE(amount=amount)
    assert method.args_list == [ETHAddr.stkAAVE, amount]
    assert method.data == '0x095ea7b30000000000000000000000004da27a545c0c5b758a6ba100e3a049001de870f50000000000000000000000000000000000000000000000000000000000002710'

def test_approve_method_with_roles(web3_eth):
    method = aave.ApproveForStkAAVE(amount=1000)
    ROLE = 1
    ROLES_MOD_ADDRESS = '0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc'
    REVOKER_ADDRESS = "0xf099e0f6604BDE0AA860B39F7da75770B34aC804"
    roles_mod = RolesMod(role=ROLE, contract_address=ROLES_MOD_ADDRESS, account=REVOKER_ADDRESS, web3=web3_eth)
    check_transaction = roles_mod.check(method.target_address, method.data)
    assert check_transaction


def test_deposit_method():
    method = aave.DepositToken(asset=GCAddr.USDT, amount=100, avatar=AVATAR)
    referral_code = 0
    assert method.args_list == [GCAddr.USDT, 100, AVATAR, referral_code]
    assert method.target_address == ETHAddr.AaveLendingPoolV2


def test_deposit_eth():
    method = aave.DepositETH(eth_amount=123, avatar=AVATAR)
    referral_code = 0
    assert method.args_list == [ETHAddr.AaveLendingPoolV2, AVATAR, referral_code]
    assert method.target_address == ETHAddr.WrappedTokenGatewayV2
    assert method.value == 123


def test_borrow():
    method = aave.Borrow(asset=GCAddr.USDT, amount=123, interest_rate_model=aave.InterestRateModel.STABLE,
                         avatar=AVATAR)
    referral_code = 0
    assert method.args_list == [GCAddr.USDT, 123, 1, referral_code, AVATAR]
    assert method.target_address == ETHAddr.AaveLendingPoolV2


def test_borrow_with_bad_interest_rate():
    method = aave.Borrow(asset=GCAddr.USDT, amount=123, interest_rate_model=aave.InterestRateModel.STABLE,
                         avatar=AVATAR)
    referral_code = 0
    assert method.args_list == [GCAddr.USDT, 123, 1, referral_code, AVATAR]
    assert method.target_address == ETHAddr.AaveLendingPoolV2


def test_borrow_eth():
    method = aave.BorrowETH(amount=123, interest_rate_model=aave.InterestRateModel.VARIABLE)
    referral_code = 0
    assert method.args_list == [ETHAddr.AaveLendingPoolV2, 123, 2, referral_code]
    assert method.target_address == ETHAddr.WrappedTokenGatewayV2


def test_cooldown(web3_eth):
    method = aave.CooldownStkAAVE()
    roles_mod = RolesMod(role=1, contract_address=ROLES_MOD_ADDRESS, account=MANAGER_SAFE_ADDRESS, web3=web3_eth)
    check_transaction = roles_mod.check(method.target_address, method.data)
    assert check_transaction

def test_claim(web3_eth):
    method = aave.ClaimAAVERewards(avatar=AVATAR, amount=10)

    roles_mod = RolesMod(role=1, contract_address=ROLES_MOD_ADDRESS, account=MANAGER_SAFE_ADDRESS, web3=web3_eth)
    check_transaction = roles_mod.check(method.target_address, method.data)
    assert check_transaction

def test_unstake(web3_eth):
    method = aave.UnstakeAAVE(avatar=AVATAR, amount=10)
    assert method.data == '0x1e9a69500000000000000000000000000efccbb9e2c09ea29551879bd9da32362b32fc89000000000000000000000000000000000000000000000000000000000000000a'


