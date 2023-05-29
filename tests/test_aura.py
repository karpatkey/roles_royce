import pytest
from eth_abi import abi
from web3 import Web3
from roles_royce.roles_modifier import RolesMod
from roles_royce.constants import ETHAddr, GCAddr

from roles_royce.protocols.eth import aura
from .utils import web3_eth

AVATAR = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
ROLES_MOD = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
REVOKER_ROLE = "0xf099e0f6604BDE0AA860B39F7da75770B34aC804"
LP80GNO20WETH = "0x32296969Ef14EB0c6d29669C550D4a0449130230"

def test_approve_method():
    method = aura.ApproveForBooster(token=LP80GNO20WETH, amount=123)
    assert method.get_args_list() == [ETHAddr.AURABooster, 123]
    assert method.target_address == LP80GNO20WETH
    assert method.data == "0x095ea7b3000000000000000000000000a57b8d98dae62b26ec3bcc4a365338157060b234000000000000000000000000000000000000000000000000000000000000007b"

def test_withdraw_and_unwrap():
    method = aura.WithdrawAndUndwrapStakedBPT(amount=123)
    assert method.data == "0xc32e7202000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000001"

def test_approve_method_with_roles(web3_eth):
    method = aura.ApproveForBooster(token=LP80GNO20WETH, amount=1000)
    ROLE = 1
    roles_mod = RolesMod(role=ROLE, contract_address=ROLES_MOD, account=REVOKER_ROLE, web3=web3_eth)
    check_transaction = roles_mod.check(method.target_address, method.data)
    assert check_transaction