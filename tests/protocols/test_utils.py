from roles_royce.protocols.utils import check_allowance_and_approve
from tests.utils import local_node_eth
from roles_royce import roles


def test_check_allowance_and_approve(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(19620800)
    avatar_safe = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    token = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    spender = '0xC92E8bdf79f0507f65a392b0ab4667716BFE0110'
    amount = 2623982628288085982
    result = check_allowance_and_approve(w3, avatar_safe, token, spender, amount-100)
    assert result is None

    result = check_allowance_and_approve(w3, avatar_safe, token, spender, amount+100)
    assert result.data == '0x095ea7b3000000000000000000000000c92e8bdf79f0507f65a392b0ab4667716bfe0110000000000000000000000000000000000000000000000000246a424c47e84042'
    assert result.target_address == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
