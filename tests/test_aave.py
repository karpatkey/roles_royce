import pytest
from eth_abi import abi
from rolling_roles.roles_modifier import RolesMod
from rolling_roles.constants import ETHAddr

from rolling_roles.protocols.eth import aave
from .utils import web3_eth

USDT_CONTRACT = '0x4ECaBa5870353805a9F068101A40E0f32ed605C6'
AVATAR = "0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89"
ROLES_MOD_ADDRESS = "0xd8dd9164E765bEF903E429c9462E51F0Ea8514F9"
MANAGER_SAFE_ADDRESS = "0x60716991aCDA9E990bFB3b1224f1f0fB81538267"

def decode_data_input(arg_types, data_input):
    return abi.decode(arg_types, bytes.fromhex(data_input[10:]))


def test_approve_method():
    method = aave.ApproveForAaveLendingPoolV2(token=USDT_CONTRACT, amount=123)
    assert method.get_args_list() == [ETHAddr.AaveLendingPoolV2, 123]
    assert method.target_address == USDT_CONTRACT
    assert method.data == "0x095ea7b30000000000000000000000007d2768de32b0b80b7a3454c06bdac94a69ddc7a9000000000000000000000000000000000000000000000000000000000000007b"

    amount = 10000
    method = aave.ApproveForStkAAVE(amount=amount)
    assert method.get_args_list() == [ETHAddr.stkAAVE, amount]
    assert method.data == '0x095ea7b30000000000000000000000004da27a545c0c5b758a6ba100e3a049001de870f50000000000000000000000000000000000000000000000000000000000002710'
    decoded = decode_data_input(method.arg_types, method.data)
    assert decoded == (ETHAddr.stkAAVE.lower(), amount)


@pytest.mark.xfail(reason="Mainnet role contract not properly configured")
def test_approve_method_with_roles(web3_eth):
    method = aave.ApproveForStkAAVE(amount=1000)
    ROLE = 2
    ROLES_MOD_ADDRESS = '0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503'
    roles_mod = RolesMod(role=ROLE, contract_address=ROLES_MOD_ADDRESS, account=AVATAR, web3=web3_eth)
    check_transaction = roles_mod.check(method.target_address, method.data)
    assert check_transaction


def test_deposit_method():
    method = aave.DepositToken(asset=USDT_CONTRACT, amount=100, avatar=AVATAR)
    referral_code = 0
    assert method.get_args_list() == [USDT_CONTRACT, 100, AVATAR, referral_code]
    assert method.target_address == ETHAddr.AaveLendingPoolV2


def test_deposit_eth():
    method = aave.DepositETH(eth_amount=123, avatar=AVATAR)
    referral_code = 0
    assert method.get_args_list() == [ETHAddr.AaveLendingPoolV2, AVATAR, referral_code]
    assert method.target_address == ETHAddr.WrappedTokenGatewayV2
    assert method.eth_amount == 123


def test_borrow():
    method = aave.Borrow(asset=USDT_CONTRACT, amount=123, interest_rate_model=aave.InterestRateModel.STABLE,
                    avatar=AVATAR)
    referral_code = 0
    assert method.get_args_list() == [USDT_CONTRACT, 123, 1, referral_code, AVATAR]
    assert method.target_address == ETHAddr.AaveLendingPoolV2


def test_borrow_with_bad_interest_rate():
    method = aave.Borrow(asset=USDT_CONTRACT, amount=123, interest_rate_model=aave.InterestRateModel.STABLE,
                    avatar=AVATAR)
    referral_code = 0
    assert method.get_args_list() == [USDT_CONTRACT, 123, 1, referral_code, AVATAR]
    assert method.target_address == ETHAddr.AaveLendingPoolV2


def test_borrow_eth():
    method = aave.BorrowETH(amount=123, interest_rate_model=aave.InterestRateModel.VARIABLE)
    referral_code = 0
    assert method.get_args_list() == [ETHAddr.AaveLendingPoolV2, 123, 2, referral_code]
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


