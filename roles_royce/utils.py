import logging
from typing import List
from eth_abi import abi
from web3 import Web3
import requests
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from .roles_modifier import Operation
from .constants import Blockchain, Chain
from .generic_method import Transactable, TxData

API_URL = "https://api.tenderly.co/api/v1/"

logger = logging.getLogger(__name__)


def to_data_input(name, signature, args):
    encoded_signature = Web3.keccak(text=f"{name}{signature}").hex()[:10]
    encoded_args = abi.encode([signature], [args]).hex()
    return f"{encoded_signature}{encoded_args}"


MULTISENDS = {
    Chain.ETHEREUM: '0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761',
    Chain.GC: '0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761'
}


class MultiSendOffline(MultiSend):
    def __init__(self, address, chain_id: int):
        self.chain_id = chain_id
        super().__init__(ethereum_client=None, address=address)

    def build_tx_data(self, multi_send_txs: List[MultiSendTx]) -> bytes:
        multisend_contract = self.get_contract()
        encoded_multisend_data = b"".join([x.encoded_data for x in multi_send_txs])
        return multisend_contract.functions.multiSend(
            encoded_multisend_data
        ).build_transaction({"gas": 1, "gasPrice": 1, "chainId": self.chain_id})["data"]


def _make_multisend(txs: List[Transactable], blockchain: Blockchain) -> tuple:
    multisend_address = MULTISENDS.get(blockchain)
    transactions = [
        MultiSendTx(
            MultiSendOperation.CALL,
            tx.contract_address,
            tx.value,
            tx.data
        ) for tx in txs
    ]
    data = MultiSendOffline(
        address=multisend_address,
        chain_id=blockchain.chain_id,
    ).build_tx_data(transactions)
    return multisend_address, data


def multi_or_one(txs: List[Transactable], blockchain: Blockchain) -> TxData:
    if len(txs) > 1:
        contract_address, data = _make_multisend(txs, blockchain)
        return TxData(contract_address=contract_address,
                      data=data,
                      operation=Operation.DELEGATE_CALL,
                      value=0)
    elif len(txs) == 1:
        return txs[0]
    else:
        raise ValueError("No transactions found")


def tenderly_simulate(account_id: str,
                      project: str,
                      api_token: str,
                      block_number: int,
                      from_addr: str,
                      to_addr: str,
                      calldata: str,
                      gas: int,
                      save: bool = True,
                      save_if_fails: bool = True,
                      gas_price: int | None = None,
                      value: int = 0,
                      network_id: str = "1",
                      transaction_index: int = 0,
                      access_list: list | None = None,
                      sim_type: str = "full",
                      block_header: dict | None = None,
                      state_objects: dict | None = None
                      ) -> dict:
    """
    Simulate a transaction using the Tenderly Simulation API.

    Check the docs at https://docs.tenderly.co/simulations-and-forks/reference/tenderly-simulation-api

    :param account_id: Something like  2ae12345-d123-9876-abcd-123456123456. Get it using tenderly-cli whoami.
    :param project: project slug. It is the name that is in the url of the dashboard.
    :param api_token: the API token. Something like abIcb3qwhdPSPasd-asdfgA-foobarbaz.
    :param block_number: Number of the block to be used for the simulation.
    :param from_addr: Address initiating the transaction.
    :param to_addr: The recipient address of the transaction.
    :param calldata: Encoded contract method call data.
    :param gas_price: Price of the gas in Wei.
    :param gas: Amount of gas provided for the simulation.
    :param network_id: ID of the network on which the simulation is being run. Eg: "1"
    :param value: Amount of Ether (in Wei) sent along with the transaction.
    :param transaction_index: Index of the transaction within the block.
    :param sim_type: One of 'quick', 'abi' or 'full'.
    :param save: Flag indicating whether to save the simulation in dashboard UI.
    :param save_if_fails: Flag indicating whether to save failed simulation in dashboard UI.
    :param access_list: List of addresses with their storage keys to grant access for this transaction.
           Eg: [{"address": "0x3f41a1cfd3c8b8d9c162de0f42307a0095a6e5df", "storage_keys": [] }]
    :param block_header: Details of the block header based on the provided block number.
           Eg: { "number": "0x110ace7", "hash": "0x0000000000000000000000000000000000000000000000000000000000000000", // ... }
    :param state_objects: Overrides for specific state objects.

    :return: Simulation data as returned by Tenderly
    """
    url = API_URL + f"account/{account_id}/project/{project}/simulate"
    headers = {"X-Access-Key": api_token}
    data = {
        "network_id": network_id,
        "block_number": block_number,
        "from": from_addr,
        "input": calldata,
        "to": to_addr,
        "gas": gas,
        "transaction_index": transaction_index,
        "value": str(value),
        "save": save,
        "save_if_fails": save_if_fails,
        "simulation_type": sim_type,
    }
    if gas_price is not None:
        data["gas_price"] = str(gas_price)
    if access_list:
        data["access_list"] = access_list
    if block_header:
        data["block_header"] = block_header
    if state_objects:
        data["state_objects"] = state_objects

    response = requests.post(url=url, json=data, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data


def simulate_tx(tx: dict, block: int, account_id: str, project: str, api_token: str, sim_type: str = 'full', **kwargs) -> dict:
    """
    Helper function to simulate an already built transaction

    :param tx: Transaction built with roles.build() or any tx data as expected by web3
    :param account_id: Something like  2ae12345-d123-9876-abcd-123456123456. Get it using tenderly-cli whoami.
    :param project: project slug. It is the name that is in the url of the dashboard.
    :param api_token: the API token. Something like abIcb3qwhdPSPasd-asdfgA-foobarbaz.
    :param block: Number of the block to be used for the simulation.
    :param sim_type: One of 'quick', 'abi' or 'full'.
    :param kwargs: Other parameters to pass to tenderly_simulate.
    :return:
    """
    sim_data = tenderly_simulate(account_id=account_id, project=project, api_token=api_token,
                                 from_addr=tx['from'],
                                 to_addr=tx['to'],
                                 value=tx['value'],
                                 network_id=str(tx['chainId']),
                                 gas=tx['gas'],
                                 calldata=tx['data'],
                                 block_number=block,
                                 sim_type=sim_type,
                                 **kwargs,
                                 )
    return sim_data
