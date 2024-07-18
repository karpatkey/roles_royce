from tests.test_roles_modifier import RolesModTester
from tests.safe import SimpleSafe
from roles_royce.protocols.eth import aave_v3
from roles_royce.constants import ETHAddr
from tests.utils import steal_safe


def test_roles_v2_ens(local_node_eth, accounts):
    test_block = 20335968
    w3 = local_node_eth.w3
    local_node_eth.set_block(test_block)

    original_safe = "0x4F2083f5fBede34C2714aFfb3105539775f7FE64"
    manager_safe_address = "0xb423e0f6E7430fa29500c5cC9bd83D28c8BD8978"

    role_contract = "0x703806E61847984346d2D7DDd853049627e50A40"

    manager_safe = steal_safe(w3, safe_address=manager_safe_address, new_owner_address=accounts[0].address)

    manager_safe.contract.functions.enableModule(role_contract).transact({"from": manager_safe.address})
    assert manager_safe.contract.functions.isModuleEnabled(role_contract).call()

    print(manager_safe.retrieve_all_info())

    # user = "0x51dEc19Aa2CD414EB982B6D9811081FFcfEe839d"

    role = RolesModTester(
        role="MANAGER",
        contract_address=role_contract,
        w3=w3,
        account=manager_safe,
    )

    method = aave_v3.ApproveToken(ETHAddr.USDC, 1000)
    role.check(contract_address=method.contract_address, data=method.data)
