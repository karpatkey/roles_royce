from artemis.applications.execution_app.config.utils import get_pool_id_from_bpt
from tests.fork_fixtures import local_node_gc_replay as local_node_gc

BPT = "0x06135A9Ae830476d3a941baE9010B63732a055F4"


def test_get_pool_id_from_bpt(local_node_gc):
    w3 = local_node_gc.w3
    result = get_pool_id_from_bpt(w3, BPT)
    assert result == "0x06135a9ae830476d3a941bae9010b63732a055f4000000000000000000000065"
