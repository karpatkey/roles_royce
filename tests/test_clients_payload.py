from defabipedia.types import Chain
from karpatkit.test_utils.fork import steal_safe

from roles_royce.constants import ETHAddr
from roles_royce.protocols.eth import aave_v3
from tests.test_roles_modifier import RolesModTester


def test_roles_v2_ens(local_node_eth, accounts):
    test_block = 20335968
    w3 = local_node_eth.w3
    local_node_eth.set_block(test_block)

    avatar_safe_address = "0x4F2083f5fBede34C2714aFfb3105539775f7FE64"
    manager_safe_address = "0xb423e0f6E7430fa29500c5cC9bd83D28c8BD8978"

    role_contract_address = "0x703806E61847984346d2D7DDd853049627e50A40"

    avatar_safe = steal_safe(w3, safe_address=avatar_safe_address, new_owner_address=accounts[0].address)

    avatar_safe.contract.functions.enableModule(role_contract_address).transact({"from": avatar_safe.address})
    assert avatar_safe.contract.functions.isModuleEnabled(role_contract_address).call()

    role = RolesModTester(
        role="MANAGER",
        contract_address=role_contract_address,
        w3=w3,
        account=manager_safe_address,
    )

    method = aave_v3.ApproveToken(Chain.ETHEREUM, ETHAddr.USDC, 1000)
    assert role.check(contract_address=method.contract_address, data=method.data)
