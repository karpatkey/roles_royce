from defabipedia.types import Chains
from roles_royce.protocols import balancer
from ...utils import local_node_eth

AVATAR = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
ROLES_MOD = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
REVOKER_ROLE = "0xf099e0f6604BDE0AA860B39F7da75770B34aC804"
LP80GNO20WETH = "0x32296969Ef14EB0c6d29669C550D4a0449130230"
REWARDS = "0x59D66C58E83A26d6a0E35114323f65c3945c89c1"


def test_stake_in_gauge():
    method = balancer.StakeInGauge(blockchain=Chains.Ethereum, gauge_address="0xCB664132622f29943f67FA56CCfD1e24CC8B4995", amount=100508265407679418)
    assert method.args_list == [100508265407679418]
    assert method.target_address == "0xCB664132622f29943f67FA56CCfD1e24CC8B4995"
    assert method.data == "0xb6b55f25000000000000000000000000000000000000000000000000016513bc209d8bba"