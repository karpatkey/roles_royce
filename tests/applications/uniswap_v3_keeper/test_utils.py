from roles_royce.applications.uniswap_v3_keeper.utils import get_nft_id_from_mint_tx, get_all_nfts
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


def test_get_all_nfts(local_node_eth):
    w3 = local_node_eth.w3
    block = 19346560
    recipient = '0xAD10e5921fde9ee5FFf49696239001CE1Fd36ea1'
    local_node_eth.set_block(block)
    nfts = get_all_nfts(w3, recipient)
    assert nfts == [676429,676483,677049,677079,677090,677097,677131,677132,677157,677159,677165,677167,677386,677387,
                    677474,677858,678420,678477,678479,678630,678908,678910,678913,678917,678922,678947,679149,679237,
                    679322,679324,679692,680626,681351,681862,681939,681963,683307,683335,684071,684147,684229,684253,
                    684472,684634,685015,685167,685279,685476,685500,685709,686049,686137,686364,686579,686618,686730,
                    686794]