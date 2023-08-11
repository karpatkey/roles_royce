from roles_royce.evm_utils import get_token_amounts_from_transfer_event
from roles_royce.constants import ETHAddr
from .utils import web3_eth

def test_get_token_transfers(web3_eth):
    tx_receipt = web3_eth.eth.get_transaction_receipt('0xfe5e7f623deceea833e7300f1a9b637afcb253cebca0d3968e9190faf1c2cbc4')
    transfers = get_token_amounts_from_transfer_event(tx_receipt, ETHAddr.WETH, '0x65389F6FFe361C0C27Ea5D9691616a2060f8a167', web3_eth)

    assert transfers == [{'from': '0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD', 'to': '0x65389F6FFe361C0C27Ea5D9691616a2060f8a167', 'amount': 0.055}]

