import logging
from dataclasses import dataclass
from typing import List

import requests
from defabipedia.types import Blockchain, Chain
from eth_abi import abi
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from web3 import Web3

from roles_royce.generic_method import Transactable, TxData
from roles_royce.roles_modifier import Operation

TENDERLY_API_URL = "https://api.tenderly.co/api/v1/"
TENDERLY_DASHBOARD_URL = "https://dashboard.tenderly.co/"


@dataclass
class TenderlyCredentials:
    """Tenderly credentials dataclass.

    Attributes:
        account_id (str): Something like  2ae12345-d123-9876-abcd-123456123456. Get it using tenderly-cli whoami.
        project (str): project slug. It is the name that is in the url of the dashboard.
        api_token (str): the API token. Something like abIcb3qwhdPSPasd-asdfgA-foobarbaz.
    """

    account_id: str
    project: str
    api_token: str


def tenderly_simulate(
    tenderly_credentials: TenderlyCredentials,
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
    state_objects: dict | None = None,
) -> dict:
    """Simulate a transaction using the Tenderly Simulation API.

    Check the docs at https://docs.tenderly.co/simulations-and-forks/reference/tenderly-simulation-api

    Args:
        tenderly_credentials (TenderlyCredentials): Tenderly credentials.
        block_number (int): Number of the block to be used for the simulation.
        from_addr (str): Address initiating the transaction.
        to_addr (str): The recipient address of the transaction.
        calldata: Encoded contract method call data.
        gas_price: Price of the gas in Wei.
        gas: Amount of gas provided for the simulation.
        network_id: ID of the network on which the simulation is being run. Eg: "1"
        value: Amount of Ether (in Wei) sent along with the transaction.
        transaction_index: Index of the transaction within the block.
        sim_type: One of 'quick', 'abi' or 'full'.
        save: Flag indicating whether to save the simulation in dashboard UI.
        save_if_fails: Flag indicating whether to save failed simulation in dashboard UI.
        access_list: List of addresses with their storage keys to grant access for this transaction.
            Eg: [{"address": "0x3f41a1cfd3c8b8d9c162de0f42307a0095a6e5df", "storage_keys": [] }]
        block_header: Details of the block header based on the provided block number. Eg: {
            "number": "0x110ace7", "hash":
            "0x0000000000000000000000000000000000000000000000000000000000000000", // ... }
        state_objects: Overrides for specific state objects.

    Returns:
        Simulation data dictionary as returned by Tenderly
    """
    url = (
        TENDERLY_API_URL + f"account/{tenderly_credentials.account_id}/project/{tenderly_credentials.project}/simulate"
    )
    headers = {"X-Access-Key": tenderly_credentials.api_token}
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


def simulate_tx(
    tx: dict,
    block: int,
    tenderly_credentials: TenderlyCredentials,
    sim_type: str = "full",
    share: bool = False,
    **kwargs,
) -> dict:
    """Helper function to simulate an already built transaction

    Args:
        tx: Transaction built with roles.build() or any tx data as expected by web3
        tenderly_credentials (TenderlyCredentials): Tenderly credentials.
        block: Number of the block to be used for the simulation.
        sim_type: One of 'quick', 'abi' or 'full'.
        **kwargs: Other parameters to pass to tenderly_simulate.
        share: If true the simulation will be public and a link will be retrieved in
            result['share_url']

    Returns:
        Return the simulation data.
    """
    sim_data = tenderly_simulate(
        tenderly_credentials=tenderly_credentials,
        from_addr=tx["from"],
        to_addr=tx["to"],
        value=tx["value"],
        network_id=str(tx["chainId"]),
        gas=tx["gas"],
        calldata=tx["data"],
        block_number=block,
        sim_type=sim_type,
        **kwargs,
    )
    if share:
        url = tenderly_share_simulation(
            tenderly_credentials=tenderly_credentials, simulation_id=sim_data["simulation"]["id"]
        )
        sim_data["share_url"] = url
    return sim_data


def tenderly_share_simulation(tenderly_credentials: TenderlyCredentials, simulation_id: str, share=True):
    """Publicly share a simulation.

    Args:
        tenderly_credentials (TenderlyCredentials): Tenderly credentials dataclass.
        simulation_id (str): Get it from the simulated data 'id' field.
        share (bool): Use False to unshare a shared simulation.
    """
    url = (
        TENDERLY_API_URL
        + f"account/{tenderly_credentials.account_id}/project/{tenderly_credentials.project}/simulations/{simulation_id}/"
    )
    url += "share" if share else "unshare"
    headers = {"X-Access-Key": tenderly_credentials.api_token}
    response = requests.post(url=url, headers=headers)
    response.raise_for_status()

    return f"{TENDERLY_DASHBOARD_URL}shared/simulation/{simulation_id}"
