import pytest
import os
import pathlib
import json
from web3 import Web3
from web3.types import Address

from roles_royce.applications.panic_button_app.config.dao_config_builder import json_builder

def test_json_builder():
    dao = "karpatkey DAO"
    blockchain = "Ethereum"
    w3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))
    protocol = "balancer"
    position_ids = ["Position ID 1", "Position ID 2"]
    addresses = [Address("0x92762b42a06dcdddc5b7362cfb01e631c4d44b40"), Address("0xcfca23ca9ca720b6e98e3eb9b6aa0ffc4a5c08b9")]

    folder_path = pathlib.Path(os.path.dirname(__file__)).resolve().parent / 'panic_button_app'
    filename = folder_path / f"strategies{dao.replace(' ', '')}{blockchain}.json"

    json_builder(dao, blockchain, w3, protocol, position_ids, addresses, folder_path)
    assert os.path.isfile(filename)

    with open(filename, 'r') as f:
        data = json.load(f)
        assert data['dao'] == dao.replace(" ","")
        assert data['blockchain'] == blockchain

