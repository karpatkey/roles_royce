from roles_royce.protocols.eth import aave_v3
from .utils import (local_node_eth, accounts, get_balance, steal_token, create_simple_safe, top_up_address)
from .roles import setup_common_roles, deploy_roles, apply_presets
from roles_royce import roles
from decimal import Decimal
from pytest import approx
from roles_royce.toolshed.protocol_utils.aave_v3.addresses_and_abis import AddressesAndAbis
from roles_royce.toolshed.protocol_utils.aave_v3.cdp import AaveV3CDPManager
from roles_royce.constants import Chain

USER = "0xDf3A7a27704196Af5149CD67D881279e32AF2C21"

# -----------------------------------------------------#
# Integration Tests

def test_integration_liquidation_call(local_node_eth):
    w3 = local_node_eth.w3
    block = 18430238
    local_node_eth.set_block(block)

    cdp = AaveV3CDPManager(w3=w3, owner_address=USER)

    balances = cdp.get_cdp_balances_data(block=block)
    health_factor = cdp.get_health_factor(block=block)
    cdp_data = cdp.get_cdp_data(block=block)

    print(health_factor)