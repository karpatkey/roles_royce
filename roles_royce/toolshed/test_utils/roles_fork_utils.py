import json

from defabipedia.types import Chain
from karpatkit.test_utils.fork import TEST_ACCOUNTS, top_up_address
from karpatkit.test_utils.simple_safe import SimpleSafe
from web3 import Web3
from defabipedia.multisend import ContractSpecs as MultiSendContractSpecs
from roles_royce.evm_utils import roles_v1_abi, roles_v2_abi, roles_v1_bytecode, roles_v2_bytecode
from roles_royce.generic_method import TxData
from roles_royce.protocols.roles_modifier import AssignRolesV1, EnableModule, SetTransactionUnwrapper
from roles_royce.protocols.safe.contract_methods import EnableModule as SafeEnableModule
from roles_royce.utils import to_checksum_address


def _deploy_roles(w3: Web3, owner, avatar, target, abi, bytecode):
    # constructor: owner(address), avatar(address), target(address)
    role_constructor_bytes = "000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001"
    bytecode_without_default_constructor = bytecode[: -len(role_constructor_bytes)]

    ctract = w3.eth.contract(abi=abi, bytecode=bytecode_without_default_constructor)

    owner, avatar, target = to_checksum_address(owner), to_checksum_address(avatar), to_checksum_address(target)
    tx_hash = ctract.constructor(owner, avatar, target).transact({"from": avatar})  # deploy!
    roles_ctract_address = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=5)["contractAddress"]

    ctract = w3.eth.contract(roles_ctract_address, abi=abi)

    return ctract


def deploy_roles(w3: Web3, avatar, owner=None, target=None):
    """Deploy a Roles Modifier V1 contract"""
    owner, target = owner or avatar, target or avatar
    ctract = _deploy_roles(w3, owner, avatar, target, roles_v1_abi, roles_v1_bytecode)
    ctract.functions.setMultisend(MultiSendContractSpecs[Chain.ETHEREUM].MultiSend.address).transact({"from": avatar})
    return ctract


def deploy_roles_v2(w3: Web3, avatar, owner=None, target=None):
    """Deploy a Roles Modifier V2 contract"""
    owner, target = owner or avatar, target or avatar
    ctract = _deploy_roles(w3, owner, avatar, target, roles_v2_abi, roles_v2_bytecode)

    SetTransactionUnwrapper(
        roles_mod_address=ctract.address,
        to="0x38869bf66a61cF6bDB996A6aE40D5853Fd43B526",  # multisend
        selector="0x8d80ff0a",
        adapter="0x93B7fCbc63ED8a3a24B59e1C3e6649D50B7427c0",
    ).transact(w3, txparams={"from": avatar})
    SetTransactionUnwrapper(
        roles_mod_address=ctract.address,
        to="0x9641d764fc13c8B624c04430C7356C1C7C8102e2",  # MultiSendCallOnly
        selector="0x8d80ff0a",
        adapter="0x93B7fCbc63ED8a3a24B59e1C3e6649D50B7427c0",
    ).transact(w3, txparams={"from": avatar})
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
                EnableModule(roles_mod_address=roles_ctract.address, module=account.address),  # FIXME: this is not needed!
                AssignRolesV1(roles_mod_address=roles_ctract.address, module=account.address, assign_list=[role_number]),
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
    AssignRolesV1(roles_mod_address=roles_mod_address, module=asignee, assign_list=[role]).transact(
        local_node.w3, txparams={"from": avatar_safe_address}
    )
