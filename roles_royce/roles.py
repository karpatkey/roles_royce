import logging
from typing import List

from web3 import Web3
from web3.types import TxReceipt
from .roles_modifier import RolesMod
from .constants import Chain
from .generic_method import Transactable
from .utils import multi_or_one

logger = logging.getLogger(__name__)


def build(txs: List[Transactable],
          role: int,
          account: str,
          roles_mod_address: str,
          web3: Web3,
          tx_kwargs: dict | None = None
          ):
    """
    Create a transaction to later be sent to the blockchain or other uses
    such as studying it or composing it with other contracts.

    :param txs: List of transactable items, usually :class:`~roles_royce.protocols.base.ContractMethod` instances.
    :param role: Role number of the execution.
    :param account: Account that wants to execute.
    :param roles_mod_address: Address to call execTransactionWithRole.
    :param web3: Web3 object.
    :param tx_kwargs: Kwargs for the transaction, for example ``max_priority_fee``.
    :return:
    """
    tx_data = multi_or_one(txs, Chain.get_blockchain_from_web3(web3))
    roles_mod = RolesMod(
        role=role,
        contract_address=roles_mod_address,
        account=account,
        operation=tx_data.operation,
        web3=web3,
        value=tx_data.value
    )
    tx_kwargs = tx_kwargs or {}
    tx = roles_mod.build(tx_data.contract_address, tx_data.data, **tx_kwargs)
    tx['from'] = account
    return tx


def check(txs: List[Transactable],
          role: int,
          account: str,
          roles_mod_address: str,
          web3: Web3,
          block: int | str = 'latest',
          ) -> bool:
    """Test the transaction with static call.

    :param txs: List of transactions.
    :param role: Role that wants to execute.
    :param account: Account that wants to execute.
    :param roles_mod_address: Address to call execTransactionWithRole.
    :param web3: Web3 object.
    :param block: Block number or 'latest'.
    :return: Status.
    """
    tx_data = multi_or_one(txs, Chain.get_blockchain_from_web3(web3))
    roles_mod = RolesMod(
        role=role,
        contract_address=roles_mod_address,
        account=account,
        operation=tx_data.operation,
        web3=web3,
        value=tx_data.value
    )
    return roles_mod.check(tx_data.contract_address, tx_data.data, block=block)


def send(txs: List[Transactable],
         role: int,
         private_key: str,
         roles_mod_address: str,
         web3: Web3,
         tx_kwargs: dict | None = None
         ) -> TxReceipt:
    """Send Transactables to the blockchain.

    :param txs: List of transactables.
    :param role: Role that wants to execute.
    :param private_key: The private key.
    :param roles_mod_address: Address to call execTransactionWithRole.
    :param web3: Web3 object.
    :param tx_kwargs: Kwargs for the transaction, for example ``max_priority_fee``.
    :return: Tx receipt.
    """
    tx_data = multi_or_one(txs, Chain.get_blockchain_from_web3(web3))
    roles_mod = RolesMod(
        role=role,
        contract_address=roles_mod_address,
        private_key=private_key,
        operation=tx_data.operation,
        web3=web3,
        value=tx_data.value
    )
    tx_kwargs = tx_kwargs or {}
    roles_mod_execute = roles_mod.execute(tx_data.contract_address, tx_data.data, **tx_kwargs)
    logger.info('building receipt....')
    roles_mod_tx1 = roles_mod.get_tx_receipt(roles_mod_execute)
    logger.info(roles_mod_tx1)
    return roles_mod_tx1
  