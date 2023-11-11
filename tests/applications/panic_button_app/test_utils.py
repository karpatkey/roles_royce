from roles_royce.applications.panic_button_app.config.config_builder import get_bpt_from_aura
from tests.utils import local_node_gc


def test_get_bpt_from_aura(local_node_gc):
    w3 = local_node_gc.w3
    block = 30698007
    local_node_gc.set_block(block)
    result = get_bpt_from_aura(w3)
    assert result[0]['aura_address'] == "0x026d163C28cC7dbf57d6ED57f14208Ee412CA526"
