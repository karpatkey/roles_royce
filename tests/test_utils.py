from .utils import to_hex_32_bytes
from .utils import local_node_gc, accounts, assign_role


def test_to_hex_32_bytes():
    assert to_hex_32_bytes(15789) == '0x0000000000000000000000000000000000000000000000000000000000003dad'
    assert (to_hex_32_bytes('0x51D34416593a8acF4127dc4a40625A8eFAB9940c') ==
            '0x00000000000000000000000x51D34416593a8acF4127dc4a40625A8eFAB9940c')


def test_assign_role(local_node_gc, accounts):
    avatar_safe_address = "0x51D34416593a8acF4127dc4a40625A8eFAB9940c"
    roles_mod_address = "0x48f9Ce12d5cc2d3655aAA6D38c5Edc6ECfBE84D7"
    # Role 1 already has the correct preset applied
    role = 1
    tx_receipt = assign_role(local_node_gc, avatar_safe_address, roles_mod_address, role, accounts[0].address)
    assert tx_receipt['status'] == 1
