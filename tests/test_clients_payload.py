from tests.test_roles_modifier import RolesModTester
from roles_royce.protocols.eth import aave_v3
from roles_royce.constants import ETHAddr


def test_roles_v2_ens(local_node_eth):
    test_block = 20314887
    w3 = local_node_eth.w3
    local_node_eth.set_block(test_block)

    original_safe = "0x4F2083f5fBede34C2714aFfb3105539775f7FE64"
    manager_safe_address = "0xb423e0f6E7430fa29500c5cC9bd83D28c8BD8978"

    test_account0_addr = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    test_account0_private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

    # user = "0x51dEc19Aa2CD414EB982B6D9811081FFcfEe839d"

    role = RolesModTester(
        role="MANAGER",
        contract_address="0x703806E61847984346d2D7DDd853049627e50A40",
        w3=w3,
        account=test_account0_addr,
    )

    method = aave_v3.ApproveToken(ETHAddr.USDC, 1000)
    assert role.check(contract_address=method.contract_address, data=method.data, block=test_block)
