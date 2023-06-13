from roles_royce import check, Chain
from roles_royce.protocols.eth import lido
from roles_royce.constants import ETHAddr
from .utils import web3_eth

# Test safe
AVATAR = "0xC01318baB7ee1f5ba734172bF7718b5DC6Ec90E1"
ROLES_MOD_ADDRESS = "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86"
MANAGER = "0x216071B1B5681D67A75f7eEAF92CEC8262bE29f7"  # Role=1

def test_methods(web3_eth):
    approve = lido.Approve(amount=100)
    status = check([approve], role=1, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status

def test_deposit(web3_eth):
    deposit = lido.Deposit(eth_amount=10)
    assert deposit.value == 10
    assert deposit.target_address == ETHAddr.stETH
    status = check([deposit], role=1, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status

def test_unwrap(web3_eth):
    unwrap = lido.Unwrap(amount=100)
    status = check([unwrap], role=1, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status

def test_wrap(web3_eth):
    # ENS preset
    AVATAR = "0x4F2083f5fBede34C2714aFfb3105539775f7FE64"
    ROLES_MOD_ADDRESS = "0xf20325cf84b72e8BBF8D8984B8f0059B984B390B"
    MANAGER = "0xb423e0f6E7430fa29500c5cC9bd83D28c8BD8978"
    wrap = lido.Wrap(amount=10)
    status = check([wrap], role=1, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status
