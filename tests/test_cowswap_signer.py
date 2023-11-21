from web3 import Web3
from roles_royce import roles
import roles_royce.protocols.eth.cowswap_signer as cowswap_signer
from roles_royce.constants import GCAddr
from tests.utils import (local_node_gc, accounts, fork_unlock_account, create_simple_safe, steal_token, top_up_address)
from tests.roles import setup_common_roles, deploy_roles, apply_presets
from defabipedia.types import Chains
from time import time
import pytest

def test_cowswap_signer_v1():

    avatar_safe = "0x458cD345B4C05e8DF39d0A07220feb4Ec19F5e6f"

    sell_token = "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"
    buy_token = "0x9C58BAcC331c9aa871AFD802DB6379a98e80CEdb"
    sell_amount = 999749122606373987
    buy_amount = 5537011879839777
    fee_amount = 250877393626013
    kind = "sell"
    valid_duration = 1700372412
    fee_amount_bp = 250877393626013  

    signer_tx = cowswap_signer.SignOrder(blockchain=Chains.Gnosis,
                                         avatar=avatar_safe,
                                         sell_token=sell_token,
                                         buy_token=buy_token,
                                         sell_amount=sell_amount,
                                         buy_amount=buy_amount,
                                         fee_amount=fee_amount,
                                         valid_to=valid_duration,
                                         kind=kind,
                                         valid_duration=valid_duration,
                                         fee_amount_bp=fee_amount_bp)
    
    assert signer_tx.data == "0x569d3489000000000000000000000000e91d153e0b41518a2ce8dd3d7944fa863463a97d0000000000000000000000009c58bacc331c9aa871afd802db6379a98e80cedb000000000000000000000000458cd345b4c05e8df39d0a07220feb4ec19f5e6f0000000000000000000000000000000000000000000000000ddfd287b5761c630000000000000000000000000000000000000000000000000013abe20a3708210000000000000000000000000000000000000000000000000000000065599fbce09e64f0458093a33addd5c6c3e089b0acfdd59b92edd5be4a762a32131b49a40000000000000000000000000000000000000000000000000000e42bf1ede39df3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee34677500000000000000000000000000000000000000000000000000000000000000005a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc95a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc90000000000000000000000000000000000000000000000000000000065599fbc0000000000000000000000000000000000000000000000000000e42bf1ede39d"

#@pytest.mark.skip("WIP")
def test_cowswap_signer(local_node_gc, accounts):
    w3 = local_node_gc.w3
    block = 31032252
    
    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    steal_token(w3, "0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6", "0x4D8027E6e6e3E1Caa9AC23267D10Fb7d20f85A37", avatar_safe.address, 100)
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    presets = """{"version": "1.0","chainId": "100","meta": {"name": null,"description": "","txBuilderVersion": "1.8.0"},
                "createdAt": 1700232202399,"transactions": [
                {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000E522f854b978650Dc838Ade0e39FbC1417A2FfB0","value": "0"},
                {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000E522f854b978650Dc838Ade0e39FbC1417A2FfB0569d3489000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002","value": "0"}]}"""

    apply_presets(avatar_safe, roles_contract, json_data=presets,
                  replaces=[("E522f854b978650Dc838Ade0e39FbC1417A2FfB0", avatar_safe.address[2:])])

    blockchain = Chains.get_blockchain_from_web3(w3)

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    sell_token = "0x6C76971f98945AE98dD7d4DFcA8711ebea946eA6"
    buy_token = "0x9C58BAcC331c9aa871AFD802DB6379a98e80CEdb"
    sell_amount = 290704006280142
    buy_amount = 3445312896845187
    fee_amount = 1700598708
    kind = "sell"
    valid_duration = 60 ** 30
    valid_to = int(time()) + 120
    fee_amount_bp = int((fee_amount / sell_amount) *10000  )

    signer_tx = cowswap_signer.SignOrder(blockchain=Chains.Gnosis,
                                         avatar=avatar_safe_address,
                                         sell_token=sell_token,
                                         buy_token=buy_token,
                                         sell_amount=sell_amount,
                                         buy_amount=buy_amount,
                                         fee_amount=fee_amount,
                                         valid_to=valid_to,
                                         kind=kind,
                                         valid_duration=valid_duration,
                                         fee_amount_bp=fee_amount_bp)
    
    checking = roles.check([signer_tx], 
                           role=role, 
                           account=disassembler_address, 
                           roles_mod_address=roles_contract.address,
                           web3=w3, 
                           block=block)
    
    assert checking