from roles_royce.applications.uniswap_v3_keeper.utils import get_nft_id_from_mint_tx, get_all_active_nfts
from ...utils import local_node_eth


def test_get_nft_id_from_mint_tx(local_node_eth):
    w3 = local_node_eth.w3
    tx_hash = '0xf2de66993c7038cd44312245f14245fd63cca3e2fefbbc112a59897fb81b6dc4'
    block = 19346560
    recipient = '0xAD10e5921fde9ee5FFf49696239001CE1Fd36ea1'
    local_node_eth.set_block(block)
    tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
    nft_id = get_nft_id_from_mint_tx(w3, tx_receipt, recipient)
    assert nft_id == 686794


def test_get_all_active_nfts(local_node_eth):
    w3 = local_node_eth.w3
    block = 19346560
    recipient = '0xAD10e5921fde9ee5FFf49696239001CE1Fd36ea1'
    local_node_eth.set_block(block)
    nfts = get_all_active_nfts(w3, recipient)
    assert nfts == [679322, 686794]