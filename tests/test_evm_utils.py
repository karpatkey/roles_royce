from roles_royce.evm_utils import get_token_amounts_from_transfer_event
from roles_royce.constants import ETHAddr
from .utils import web3_eth

def test_get_token_transfers(web3_eth):
    tx_receipt = web3_eth.eth.get_transaction_receipt('0xfe5e7f623deceea833e7300f1a9b637afcb253cebca0d3968e9190faf1c2cbc4')
    transfers = get_token_amounts_from_transfer_event(tx_receipt, ETHAddr.WETH, '0x65389F6FFe361C0C27Ea5D9691616a2060f8a167', web3_eth)
    assert transfers == [{'from': '0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad', 'to': '0x65389f6ffe361c0c27ea5d9691616a2060f8a167', 'amount': 0.055}]

