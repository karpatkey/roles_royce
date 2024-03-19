import pytest

from roles_royce.protocols.balancer.types_and_enums import PoolKind
from roles_royce.protocols.balancer.utils import Pool

from ...utils import local_node_eth

stable_pool_pid = "0x3dd0843a028c86e0b760b1a76929d1c5ef93a2dd000200000000000000000249"
metastable_pool_pid = "0x1e19cf2d73a72ef1332c882f20534b6519be0276000200000000000000000112"
composable_stable_pool_pid = "0x42ed016f826165c2e5976fe5bc3df540c5ad0af700000000000000000000058b"
weighted_pool_pid = "0x5c6ee304399dbdb9c8ef030ab642b10820db8f56000200000000000000000014"

block = 18238491


def test_pool_kind(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(block)
    assert Pool(w3=w3, pool_id=stable_pool_pid).pool_kind() == PoolKind.StablePool
    assert Pool(w3=w3, pool_id=metastable_pool_pid).pool_kind() == PoolKind.MetaStablePool
    assert Pool(w3=w3, pool_id=composable_stable_pool_pid).pool_kind() == PoolKind.ComposableStablePool
    assert Pool(w3=w3, pool_id=weighted_pool_pid).pool_kind() == PoolKind.WeightedPool


def test_pool_assets(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(block)
    assert Pool(w3=w3, pool_id=stable_pool_pid).assets() == [
        "0x5c6Ee304399DBdB9C8Ef030aB642B10820DB8F56",
        "0x616e8BfA43F920657B3497DBf40D6b1A02D4608d",
    ]
    assert Pool(w3=w3, pool_id=metastable_pool_pid).assets() == [
        "0xae78736Cd615f374D3085123A210448E74Fc6393",
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    ]
    assert Pool(w3=w3, pool_id=composable_stable_pool_pid).assets() == [
        "0x42ED016F826165C2e5976fe5bC3df540C5aD0Af7",
        "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
        "0xac3E018457B222d93114458476f3E3416Abbe38F",
        "0xae78736Cd615f374D3085123A210448E74Fc6393",
    ]
    assert Pool(w3=w3, pool_id=weighted_pool_pid).assets() == [
        "0xba100000625a3754423978a60c9317c58a424e3D",
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    ]


def test_pool_balances(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(block)
    assert Pool(w3=w3, pool_id=stable_pool_pid).pool_balances() == [467684439524360032246916, 540428513700953351612562]
    assert Pool(w3=w3, pool_id=metastable_pool_pid).pool_balances() == [
        13048741861807843211830,
        15052548197564559927733,
    ]
    assert Pool(w3=w3, pool_id=composable_stable_pool_pid).pool_balances() == [
        2596148429267366902437064758664548,
        2173159551320492025528,
        9456532002425029275963,
        1585529541763709958508,
    ]
    assert Pool(w3=w3, pool_id=weighted_pool_pid).pool_balances() == [
        33299690445499735620931136,
        16666117772307088233735,
    ]


def test_bpt_index_from_composable(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(block)
    assert Pool(w3=w3, pool_id=composable_stable_pool_pid).bpt_index_from_composable() == 0
    with pytest.raises(ValueError):
        Pool(w3=w3, pool_id=stable_pool_pid).bpt_index_from_composable()


def test_bpt_balance(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(block)
    holder = "0xA57b8d98dAE62B26Ec3bcC4a365338157060B234"
    assert Pool(w3=w3, pool_id=stable_pool_pid).bpt_balance(holder) == 2804191539804194198545
