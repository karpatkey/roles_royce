from roles_royce import check, send, Chain
from roles_royce.protocols.eth import lido
from roles_royce.constants import ETHAddr
from .utils import web3_eth

# Test safe
AVATAR = "0xC01318baB7ee1f5ba734172bF7718b5DC6Ec90E1"
ROLES_MOD_ADDRESS = "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86"
MANAGER = "0x216071B1B5681D67A75f7eEAF92CEC8262bE29f7"
ROLE = 1


def test_methods(web3_eth):
    approve = lido.Approve(amount=100)
    status = check([approve], role=ROLE, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status


def test_deposit(web3_eth):
    deposit = lido.Deposit(eth_amount=10)
    assert deposit.value == 10
    assert deposit.target_address == ETHAddr.stETH
    status = check([deposit], role=ROLE, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status


def test_wrap(web3_eth):
    approve = lido.Approve(amount=100)
    wrap = lido.Wrap(amount=10)
    status = check([approve, wrap], role=ROLE, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status


def test_unwrap(web3_eth):
    unwrap = lido.Unwrap(amount=1_000_000_000_000)
    status = check([unwrap], role=ROLE, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status

def test_request_withdrawal():
    request = lido.RequestWithdrawals(_amounts=[1_000], _owner=AVATAR)
    assert request.data == "0xd66810420000000000000000000000000000000000000000000000000000000000000040000000000000000000000000" \
                            "c01318bab7ee1f5ba734172bf7718b5dc6ec90e10000000000000000000000000000000000000000000000000000000000000001" \
                            "00000000000000000000000000000000000000000000000000000000000003e8"
def test_claim_withdrawal():
    claim = lido.ClaimWithdrawals(_requestIds=[1], _hints=[35])
    assert claim.data == "0xe3afe0a3000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000" \
                            "000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000001" \
                            "00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001" \
                            "0000000000000000000000000000000000000000000000000000000000000023"

