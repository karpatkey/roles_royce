import pytest

from roles_royce import check, Chain
from roles_royce.protocols.eth import balancer

from .utils import web3_eth

bb_a_USD_pid = "0xfebb0bbf162e64fb9d0dfe186e517d84c395f016000000000000000000000502"
avatar_address = '0x4F2083f5fBede34C2714aFfb3105539775f7FE64'
roles_mod_address = '0xf20325cf84b72e8BBF8D8984B8f0059B984B390B'
bb_a_USD = "0xfeBb0bbf162E64fb9D0dfe186E517d84C395f016"
bb_a_DAI = "0x6667c6fa9f2b3Fc1Cc8D85320b62703d938E4385"
bb_a_USDT = "0xA1697F9Af0875B63DdC472d6EeBADa8C1fAB8568"
bb_a_USDC = "0xcbFA4532D8B2ade2C261D3DD5ef2A2284f792692"

pytestmark = pytest.mark.skip("all tests still WIP")

def test_exit_pool_single(web3_eth):
    assets = [bb_a_DAI, bb_a_USDT, bb_a_USDC, bb_a_USD]
    query_exit = balancer.SingleAssetQueryExit(pool_id=bb_a_USD_pid,
                                               avatar=avatar_address,
                                               assets=assets,
                                               min_amounts_out=[0, 0, 0, 0],
                                               bpt_amount_in=100000,
                                               exit_token_index=2)

    amounts = query_exit.call(web3_eth, block_identifier=17065330)[1]
    assert amounts == [0, 0, 98698, 0]

    exit_pool = balancer.SingleAssetExit(pool_id=bb_a_USD_pid,
                                         avatar=avatar_address,
                                         assets=assets,
                                         min_amounts_out=amounts,
                                         bpt_amount_in=100000,
                                         exit_token_index=2)

    status = check(txs=[exit_pool], role=1, account=avatar_address, roles_mod_address=roles_mod_address,
                   web3=web3_eth, blockchain=Chain.ETHEREUM, block=17065330)
    assert status


def test_exit_pool_proportional():
    assets = [bb_a_DAI, bb_a_USDT, bb_a_USDC, bb_a_USD]
    m = balancer.ProportionalExit(pool_id=bb_a_USD_pid,
                                  avatar=avatar_address,
                                  assets=assets,
                                  min_amounts_out=[0, 0, 0, 0],
                                  bpt_amount_in=10)
    assert m.data == "0x8bdb3913febb0bbf162e64fb9d0dfe186e517d84c395f01600000000000000000000050200000000000000000000000" \
                     "04f2083f5fbede34c2714affb3105539775f7fe640000000000000000000000004f2083f5fbede34c2714affb31055397" \
                     "75f7fe6400000000000000000000000000000000000000000000000000000000000000800000000000000000000000000" \
                     "0000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000" \
                     "00012000000000000000000000000000000000000000000000000000000000000001c0000000000000000000000000000" \
                     "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                     "00040000000000000000000000006667c6fa9f2b3fc1cc8d85320b62703d938e4385000000000000000000000000a1697" \
                     "f9af0875b63ddc472d6eebada8c1fab8568000000000000000000000000cbfa4532d8b2ade2c261d3dd5ef2a2284f7926" \
                     "92000000000000000000000000febb0bbf162e64fb9d0dfe186e517d84c395f0160000000000000000000000000000000" \
                     "0000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000" \
                     "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                     "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                     "0000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000" \
                     "00000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a"


def test_exit_pool_custom():
    assets = [bb_a_DAI, bb_a_USDT, bb_a_USDC, bb_a_USD]
    m = balancer.CustomExit(pool_id=bb_a_USD_pid,
                            avatar=avatar_address,
                            assets=assets,
                            amounts_out=[123, 0, 321, 0],
                            max_bpt_amount_in=10)
