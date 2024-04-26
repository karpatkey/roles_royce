import logging
from typing import List

from defabipedia.types import Chain
from web3 import Web3
from web3.types import TxReceipt

from .generic_method import Transactable
from .roles_modifier import RolesMod
from .utils import multi_or_one

logger = logging.getLogger(__name__)


def build(
    txs: List[Transactable], role: int, account: str, roles_mod_address: str, web3: Web3, tx_kwargs: dict | None = None
) -> dict:
    """Create a transaction to later be sent to the blockchain or other uses
    such as studying it or composing it with other contracts.

    Args:
        txs: List of transactable items, usually :class:`~roles_royce.protocols.base.ContractMethod` instances.
        role: Role number of the execution.
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
        web3=web3,
        value=tx_data.value,
    )
    tx_kwargs = tx_kwargs or {}
    tx = roles_mod.build(tx_data.contract_address, tx_data.data, **tx_kwargs)
    tx["from"] = account
    return tx


def check(
    txs: List[Transactable],
    role: int,
    account: str,
    roles_mod_address: str,
    web3: Web3,
    block: int | str = "latest",
) -> bool:
    """Test the transaction with static call.

    Args:
        txs: List of transactions.
        role: Role that wants to execute.
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
        web3=web3,
        value=tx_data.value,
    )
    return roles_mod.check(tx_data.contract_address, tx_data.data, block=block)


def send(
    txs: List[Transactable],
    role: int,
    private_key: str,
    roles_mod_address: str,
    web3: Web3,
    tx_kwargs: dict | None = None,
) -> TxReceipt:
    """Send Transactables to the blockchain.

    Args:
        txs: List of transactables.
        role: Role that wants to execute.
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
        web3=web3,
        value=tx_data.value,
    )
    tx_kwargs = tx_kwargs or {}
    roles_mod_execute = roles_mod.execute(tx_data.contract_address, tx_data.data, **tx_kwargs)
    roles_mod_tx1 = roles_mod.get_tx_receipt(roles_mod_execute)
    return roles_mod_tx1
