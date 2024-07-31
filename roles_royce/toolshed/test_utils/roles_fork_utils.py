import json

from defabipedia.types import Chain
from karpatkit.test_utils.fork import TEST_ACCOUNTS, top_up_address
from karpatkit.test_utils.simple_safe import SimpleSafe
from web3 import Web3

from roles_royce.evm_utils import roles_abi, roles_bytecode
from roles_royce.generic_method import TxData
from roles_royce.utils import MULTISENDS, to_checksum_address
from roles_royce.protocols.roles_modifier.contract_methods import EnableModule, AssignRoles
from roles_royce.protocols.safe.contract_methods import EnableModule as SafeEnableModule


def deploy_roles(w3: Web3, avatar):
    # Deploy a Roles contrat without using the ProxyFactory (to simplify things)
    role_constructor_bytes = "000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001"
    bytecode_without_default_constructor = roles_bytecode[: -len(role_constructor_bytes)]

    ctract = w3.eth.contract(abi=roles_abi, bytecode=bytecode_without_default_constructor)

    owner = avatar = target = to_checksum_address(avatar)
    tx_hash = ctract.constructor(owner, avatar, target).transact({"from": avatar})  # deploy!
    roles_ctract_address = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=5)["contractAddress"]

    ctract = w3.eth.contract(roles_ctract_address, abi=roles_abi)
    ctract.functions.setMultisend(MULTISENDS[Chain.ETHEREUM]).transact({"from": avatar})
    return ctract


def setup_common_roles(safe: SimpleSafe, roles_ctract):
    # set roles_mod as module of safe
    safe.send(txs=[SafeEnableModule(safe.address, module=roles_ctract.address)])

    # enable an asign roles to the test EOAs
    # EOA           | ROLE N | ROLE NAME
    # accounts[1]   |  1     | Manager
    # accounts[2]   |  2     | revoker
    # accounts[3]   |  3     | harvester
    # accounts[4]   |  4     | disassembler
    # accounts[5]   |  5     | swapper

    txns = []
    for role_number in range(1, 6):
        account = TEST_ACCOUNTS[role_number]
        txns.extend(
            [
                EnableModule(roles_mod_address=roles_ctract.address, module=account.address),
                AssignRoles(roles_mod_address=roles_ctract.address, module=account.address, assign_list=[role_number]),
            ]
        )
    safe.send(txs=txns)


def apply_roles_presets(safe: SimpleSafe, roles_ctract, json_data, replaces=None):
    presets_data = json.loads(json_data)
    for tx in presets_data["transactions"]:
        data: str = tx["data"]
        for replacer in replaces:
            data = data.replace(replacer[0], replacer[1])
        safe.send(txs=[TxData(contract_address=roles_ctract.address, data=data)])


def assign_role(local_node, avatar_safe_address: str, roles_mod_address: str, role: int, asignee: str):
    local_node.unlock_account(avatar_safe_address)
    # The amount of ETH of the Avatar address is increased
    top_up_address(local_node.w3, address=avatar_safe_address, amount=1)
    AssignRoles(roles_mod_address=roles_mod_address, module=asignee, assign_list=[role]).transact(local_node.w3,
                                                                                                  txparams={"from": avatar_safe_address})
