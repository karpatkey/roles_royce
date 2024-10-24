from defabipedia.balancer import Chain
from karpatkit.test_utils.fork import local_node_eth_replay as local_node_eth

from roles_royce.protocols import balancer

# --------------------------------------------------------------------------------------------------------------------
# Staking and unstaking in gauge
# --------------------------------------------------------------------------------------------------------------------


def test_stake_in_gauge(local_node_eth):
    m = balancer.Stake(
        blockchain=Chain.ETHEREUM, gauge_address="0xb812249d60b80c7cbc9398e382ed6dfdf82e23d2", amount=100508265407679418
    )
    assert m.data == "0xb6b55f25000000000000000000000000000000000000000000000000016513bc209d8bba"


def test_unstake_in_gauge(local_node_eth):
    m = balancer.Unstake(
        blockchain=Chain.ETHEREUM,
        gauge_address="0xb812249d60b80c7cbc9398e382ed6dfdf82e23d2",
        amount=35072783119882834679,
    )
    assert m.data == "0x2e1a7d4d000000000000000000000000000000000000000000000001e6bb8e6c88eed2f7"
