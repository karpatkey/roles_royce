import json
import os.path
import pathlib

from web3.types import Address
from web3 import Web3

from defabipedia import balancer, aura
from defabipedia.types import Chains
from roles_royce.protocols.balancer.utils import Pool, PoolKind
from roles_royce.applications.panic_button_app.config.config_builder import seed_file, add_positions

def json_builder(dao: str, blockchain: str, w3: Web3, protocol: str, position_ids: list[str], addresses: list[Address], folder_path: str = None):
    """builds json from lists of addresses

    Args:
        dao (str): give the DAO name
        blockchain (str): give the blockchain
        w3 (Web3): endpoint to get data from
        protocol (str): the protocol which template will be used
        position_ids (list[str]): name of the positions to add
        addresses (list[Address]): list of addresses to add (for Balancer and Aura bpt addresses are enough)
        folder_path (str, optional): folder_path with the DAO files and the templates. Defaults to None.
    """
    dao = dao.replace(" ","")
    if not folder_path:
        folder_path = pathlib.Path(os.path.dirname(__file__)).resolve().parent / 'config'
    filename = folder_path / f"strategies{dao}{blockchain}.json"

    if os.path.isfile(filename):
        add_positions(w3, filename, folder_path, protocol, position_ids, addresses)
        
    else:
        seed_file(filename, dao, blockchain)
        add_positions(w3, filename, folder_path, protocol, position_ids, addresses)

    print('done')