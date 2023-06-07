import pytest
from eth_abi import abi
from web3 import Web3
from roles_royce.roles_modifier import RolesMod
from roles_royce.constants import ETHAddr, GCAddr

from roles_royce.protocols.eth import balancer
from .utils import web3_eth


def test_exit_pool_exact_for_all_tokensapprove_method():
    bb_a_USD_pid = "0xfebb0bbf162e64fb9d0dfe186e517d84c395f016000000000000000000000502"
    avatar_address = '0x4F2083f5fBede34C2714aFfb3105539775f7FE64'
    roles_mod_address = '0xf20325cf84b72e8BBF8D8984B8f0059B984B390B'
    bb_a_USD = "0xfeBb0bbf162E64fb9D0dfe186E517d84C395f016"
    bb_a_DAI = "0x6667c6fa9f2b3Fc1Cc8D85320b62703d938E4385"
    bb_a_USDT = "0xA1697F9Af0875B63DdC472d6EeBADa8C1fAB8568"
    bb_a_USDC = "0xcbFA4532D8B2ade2C261D3DD5ef2A2284f792692"

    assets = [bb_a_DAI, bb_a_USDT, bb_a_USDC, bb_a_USD]
    m = balancer.ExitPoolExactBPTInForAllTokensOut(pool_id=bb_a_USD_pid,
                                                   avatar=avatar_address,
                                                   assets=assets,
                                                   min_amounts_out=[0, 0, 0, 0],
                                                   bpt_amount_in=10)
    assert True, print(m.get_args_list())
    assert m.data == None
