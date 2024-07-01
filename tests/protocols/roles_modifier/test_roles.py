from roles_royce.protocols.roles_modifier.contract_methods import ExecTransactionWithRoleV1, ExecTransactionWithRoleV2, get_exec_transaction_with_role_method


def test_exect_transaction_with_role():
    roles_mod_address = "0x8C33ee6E439C874713a9912f3D3debfF1Efb90Da"
    to = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
    data = "0x095ea7b3000000000000000000000000c92e8bdf79f0507f65a392b0ab4667716bfe01100000000000000000000000000000000000000000000000000000000000000064"
    method_v1 = ExecTransactionWithRoleV1(
        data=data, role=1, to=to, operation=0, value=0, roles_mod_address=roles_mod_address
    )
    assert method_v1.target_address == roles_mod_address
    assert method_v1.inputs == {'to': '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0', 'value': 0,
                             'data': b'\t^\xa7\xb3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc9.\x8b\xdfy\xf0P\x7fe\xa3\x92\xb0\xabFgqk\xfe\x01\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00d',
                             'operation': 0, 'role': 1, 'should_revert': True}

    method_v2 = ExecTransactionWithRoleV2(
        data=data, role="MY-ROLE", to=to, operation=0, value=0, roles_mod_address=roles_mod_address
    )
    assert method_v2.inputs == {'to': '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0', 'value': 0,
                             'data': b'\t^\xa7\xb3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc9.\x8b\xdfy\xf0P\x7fe\xa3\x92\xb0\xabFgqk\xfe\x01\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00d',
                             'operation': 0,
                             'role_key': b'MY-ROLE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                             'should_revert': True}

def test_get_exec_transaction_with_role_method():
    roles_mod_address = "0x8C33ee6E439C874713a9912f3D3debfF1Efb90Da"
    to = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
    data = "0x095ea7b3000000000000000000000000c92e8bdf79f0507f65a392b0ab4667716bfe01100000000000000000000000000000000000000000000000000000000000000064"

    method = get_exec_transaction_with_role_method(data=data, role=1, to=to, operation=0, value=0, roles_mod_address=roles_mod_address)
    isinstance(method, ExecTransactionWithRoleV1)

    method = get_exec_transaction_with_role_method(data=data, role="FOO", to=to, operation=0, value=0, roles_mod_address=roles_mod_address)
    isinstance(method, ExecTransactionWithRoleV2)
