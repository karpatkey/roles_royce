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

#TODO: add tests for exit strategies