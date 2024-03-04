import json
import requests

from defabipedia.types import Chain
from roles_royce.protocols.eth import lido
from roles_royce.toolshed.disassembling import SwapDisassembler
from roles_royce.roles_modifier import GasStrategies, set_gas_strategy

from tests.utils import (local_node_eth, accounts, create_simple_safe, steal_token)
from tests.roles import setup_common_roles, deploy_roles, apply_presets

ROLE = 4
AVATAR = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
ROLES_MOD = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"

def test_find_pools_with_tokens(local_node_eth):
    w3 = local_node_eth.w3
    disassembler = SwapDisassembler(w3, AVATAR, ROLES_MOD, ROLE,)
    pools = disassembler.find_pools_with_tokens("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
                                                "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
    assert len(pools) == 2