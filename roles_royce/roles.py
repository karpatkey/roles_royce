import logging
from typing import List

from defabipedia.types import Chain
from defabipedia.multisend import ContractSpecs
from web3 import Web3
from web3.types import TxReceipt

from .generic_method import Transactable
from .roles_modifier import RolesMod
from .utils import multi_or_one
from roles_royce.evm_utils import roles_abi

logger = logging.getLogger(__name__)

# FIXME, the following function should be removed when roles v1 is no longer supported by Roles Royce. This function is
#  only used in this script
def use_old_multisend_if_needed(w3: Web3, roles_mod_address: str, address: str)-> str:
    """Returns the roles modifier contract's multisend address if the roles modifier contract is v1 and the address
    is the (new) multisend contract. To be used as a hacky patch in the 'build', 'check' and 'send' functions for roles
    v1 contract instances that use the old multisend contract, not the one in defabipedia."""
    if address == ContractSpecs[Chain.GNOSIS].MultiSend.address:
        try:
            return w3.eth.contract(roles_mod_address, abi=roles_abi).functions.multisend().call()
        except:
            pass
    else:
        return address

def build(
    txs: List[Transactable],
    role: int | str,
    account: str,
    roles_mod_address: str,
    web3: Web3,
    tx_kwargs: dict | None = None,
) -> dict:
    """Create a transaction to later be sent to the blockchain or other uses
    such as studying it or composing it with other contracts.

    Args:
        txs: List of transactable items, usually :class:`~roles_royce.protocols.base.ContractMethod` instances.
        role: Role of the execution. A str for roles v2 or an int for the legacy roles contracts.
        account: Account that wants to execute.
        roles_mod_address: Address to call execTransactionWithRole.
        web3: Web3 object.
        tx_kwargs: Kwargs for the transaction, for example ``max_priority_fee``.

    Returns:
        Transaction dict.
    """
    tx_data = multi_or_one(txs, Chain.get_blockchain_from_web3(web3))
    roles_mod = RolesMod(
        role=role,
        contract_address=roles_mod_address,
        account=account,
        operation=tx_data.operation,
        w3=web3,
        value=tx_data.value,
    )
    tx_kwargs = tx_kwargs or {}
    tx = roles_mod.build(use_old_multisend_if_needed(web3, roles_mod_address, tx_data.contract_address), tx_data.data, **tx_kwargs)
    tx["from"] = account
    return tx



def check(
    txs: List[Transactable],
    role: int | str,
    account: str,
    roles_mod_address: str,
    web3: Web3,
    block: int | str = "latest",
) -> bool:
    """Test the transaction with static call.

    Args:
        txs: List of transactions.
        role: Role of the execution. A str for roles v2 or an int for the legacy roles contracts.
        account: Account that wants to execute.
        roles_mod_address: Address to call execTransactionWithRole.
        web3: Web3 object.
        block: Block number or 'latest'.

    Returns:
        Status.
    """
    tx_data = multi_or_one(txs, Chain.get_blockchain_from_web3(web3))
    roles_mod = RolesMod(
        role=role,
        contract_address=roles_mod_address,
        account=account,
        operation=tx_data.operation,
        w3=web3,
        value=tx_data.value,
    )

    return roles_mod.check(use_old_multisend_if_needed(web3, roles_mod_address, tx_data.contract_address), tx_data.data, block=block)


def send(
    txs: List[Transactable],
    role: int | str,
    private_key: str,
    roles_mod_address: str,
    web3: Web3,
    tx_kwargs: dict | None = None,
) -> TxReceipt:
    """Send Transactables to the blockchain.

    Args:
        txs: List of transactables.
        role: Role of the execution. A str for roles v2 or an int for the legacy roles contracts.
        private_key: The private key.
        roles_mod_address: Address to call execTransactionWithRole.
        web3: Web3 object.
        tx_kwargs: Kwargs for the transaction, for example ``max_priority_fee``.

    Returns:
        Tx receipt.
    """
    tx_data = multi_or_one(txs, Chain.get_blockchain_from_web3(web3))
    roles_mod = RolesMod(
        role=role,
        contract_address=roles_mod_address,
        private_key=private_key,
        operation=tx_data.operation,
        w3=web3,
        value=tx_data.value,
    )
    tx_kwargs = tx_kwargs or {}
    roles_mod_execute = roles_mod.execute(use_old_multisend_if_needed(web3, roles_mod_address, tx_data.contract_address), tx_data.data, **tx_kwargs)
    roles_mod_tx1 = roles_mod.get_tx_receipt(roles_mod_execute)
    return roles_mod_tx1
