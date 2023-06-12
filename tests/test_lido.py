from roles_royce import check, Chain
from roles_royce.protocols.eth import lido
from roles_royce.constants import ETHAddr
from .utils import web3_eth

AVATAR = "0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89"
ROLES_MOD_ADDRESS = "0xd8dd9164E765bEF903E429c9462E51F0Ea8514F9"


def test_methods():
    approve = lido.Approve(amount=1)
    # TODO

def test_deposit(web3_eth):
    deposit = lido.Deposit(eth_amount=10)
    assert deposit.value == 10
    assert deposit.target_address == ETHAddr.stETH
    # FIXME:
    status = check([deposit], role=1, account=AVATAR, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status

def test_wrap_and_unwrap():
    wrap = lido.Wrap(amount=5)
    unwrap = lido.Unwrap(amount=123)
    # TODO
