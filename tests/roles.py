import json

from defabipedia.types import Chain
from web3 import Web3

from roles_royce.evm_utils import roles_abi, roles_bytecode
from roles_royce.generic_method import TxData
from roles_royce.utils import MULTISENDS, to_checksum_address

from .utils import TEST_ACCOUNTS, SimpleSafe


def deploy_roles(w3: Web3, avatar):
    # Deploy a Roles contrat without using the ProxyFactory (to simplify things)
    role_constructor_bytes = "000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001"
    bytecode_without_default_constructor = roles_bytecode[: -len(role_constructor_bytes)]

    ctract = w3.eth.contract(abi=roles_abi, bytecode=bytecode_without_default_constructor)

    owner = avatar = target = to_checksum_address(avatar)
    tx_hash = ctract.constructor(owner, avatar, target).transact({"from": avatar})  # deploy!
    roles_ctract_address = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=5).contractAddress

    ctract = w3.eth.contract(roles_ctract_address, abi=roles_abi)
    ctract.functions.setMultisend(MULTISENDS[Chain.ETHEREUM]).transact({"from": avatar})
    return ctract


def setup_common_roles(safe: SimpleSafe, roles_ctract):
    # set roles_mod as module of safe
    enable_module_roles = safe.contract.functions.enableModule(roles_ctract.address).build_transaction(
        {"from": safe.address}
    )["data"]
    safe.send(txs=[TxData(contract_address=safe.address, data=enable_module_roles)])

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
        enable_module = roles_ctract.functions.enableModule(account.address).build_transaction({"from": safe.address})[
            "data"
        ]
        assign_role = roles_ctract.functions.assignRoles(account.address, [role_number], [True]).build_transaction(
            {"from": safe.address}
        )["data"]
        txns.extend(
            [
                TxData(contract_address=roles_ctract.address, data=enable_module),
                TxData(contract_address=roles_ctract.address, data=assign_role),
            ]
        )
    safe.send(txs=txns)


def apply_presets(safe: SimpleSafe, roles_ctract, json_data, replaces=None):
    presets_data = json.loads(json_data)
    for tx in presets_data["transactions"]:
        data: str = tx["data"]
        for replacer in replaces:
            data = data.replace(replacer[0], replacer[1])
        safe.send(txs=[TxData(contract_address=roles_ctract.address, data=data)])
