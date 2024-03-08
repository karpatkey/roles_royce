from roles_royce.applications.uniswap_v3_keeper.utils import get_nft_id_from_mint_tx, get_all_nfts, get_amounts_quotient_from_price_delta
from ...utils import local_node_eth
from roles_royce.protocols.uniswap_v3 import NFTPosition
from decimal import Decimal


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
    owner = '0xAD10e5921fde9ee5FFf49696239001CE1Fd36ea1'
    local_node_eth.set_block(block)
    some_nfts_with_zero_liquidity = [676429, 677049, 677090, 677097, 677131, 677132, 677157, 677159, 677165, 677167,
                                     677386, 677387, 677474, 677858, 678420, 678477, 678479, 678630, 678908, 678910,
                                     678913, 678917, 678922, 678947, 679149, 679237, 679324, 679692, 680626, 681351,
                                     681862, 681939, 681963, 683307, 683335, 684071, 684147, 684229, 684253, 684472,
                                     684634, 685015, 685167, 685279, 685476, 685500, 685709, 686049, 686137, 686364,
                                     686579, 686618, 686730]
    nfts = get_all_nfts(w3, owner, discarded_nfts=some_nfts_with_zero_liquidity)
    assert nfts == [679322, 686794]

    nfts_2 = get_all_nfts(w3, owner, discarded_nfts=some_nfts_with_zero_liquidity+[679322])
    assert nfts_2 == [686794]

    owner_2 = '0x4B36e5f444Caf85fC87643Db0d6E38874730B0a0'
    nfts_to_discard = [626119, 627878, 670353, 672727, 673958, 674087, 674134, 674303, 674574,
                       674947, 676353, 676393, 676842, 677972, 679229, 679725, 682856]
    nfts = get_all_nfts(w3, owner_2, discarded_nfts=nfts_to_discard, active=False,
                        token0='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599')
    assert nfts == [628770, 669179, 673304]

    nfts = get_all_nfts(w3, owner_2, discarded_nfts=nfts_to_discard, active=False, fee=3000)
    assert nfts == [683496, 686280, 686294]


def test_get_amounts_quotient_from_price_delta(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(19386603)

    nft_position = NFTPosition(w3, 689161)
    pool = nft_position.pool

    price_delta = 3
    assert get_amounts_quotient_from_price_delta(pool, price_delta) == Decimal('48221047202711169.56427028895')


