import pytest
from unittest.mock import patch
from rolling_roles.roles_modifier import RolesMod
from .utils import web3_eth

ROLE = 2
ROLES_MOD_ADDRESS = "0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503"
ACCOUNT = "0x7e19DE37A31E40eec58977CEA36ef7fB70e2c5CD"


def test_check(web3_eth):
    data = "0x095ea7b30000000000000000000000007f90122bf0700f9e7e1f688fe926940e8839f35300000000000000000000000000000000000000000000000000000000000003e8"
    roles = RolesMod(role=ROLE, contract_address="0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503", web3=web3, account=ACCOUNT)
    assert roles.check(contract_address="0x4ECaBa5870353805a9F068101A40E0f32ed605C6", data=data)

    with patch.object(RolesMod, "_send_raw_transaction", lambda x, y: bytes()):
        roles.private_key = '0xa60429f7d6b751ca19d52302826b4a611893fbb138f0059f354b79846f2ab125'
        roles.execute(contract_address="0x4ECaBa5870353805a9F068101A40E0f32ed605C6", data=data)
