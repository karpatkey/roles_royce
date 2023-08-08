import logging
from typing import List

from web3 import Web3
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
          ) -> bool:
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
    """Test the transaction with static call

    Args:
        txs (List[GenericMethodTransaction]): list of transactions
        role (int): role that wants to execute
        account (str): account that wants to execute
        roles_mod_address (str): address to call execTransactionWithRole
        web3 (Web3)
        block (int | str): block number or 'latest'

    Returns:
        bool: status
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
         ) -> bool:
    """Send transactions to the blockchain.

    Args:
        txs (List[TxData]): list of transactions
        role (int): role that wants to execute
        private_key (str): to access the EOA
        roles_mod_address (str): address to call execTransactionWithRole
        web3 (Web3)
        tx_kwargs (dict): kwargs for the transaction

    Returns:
        (obj) tx_receipt
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
  