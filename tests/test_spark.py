from roles_royce.protocols.eth import spark
from roles_royce.constants import ETHAddr
from .utils import local_node, accounts, get_balance, steal_token, create_simple_safe


def test_withdrawal_with_sdai_integration(local_node, accounts):
    w3 = local_node
    safe = create_simple_safe(w3, accounts[0])

    # steal DAIs from a large holder and send them to the safe
    ADDRESS_WITH_LOTS_OF_TOKENS = "0x075e72a5eDf65F0A5f44699c7654C1a76941Ddc8"

    steal_token(w3, ETHAddr.DAI, holder=ADDRESS_WITH_LOTS_OF_TOKENS, to=safe.address, amount=1_000_000)
    assert get_balance(w3, ETHAddr.DAI, safe.address) == 1_000_000

    safe.send([spark.ApproveWithdrawalDAI(amount=1_000_000),
               spark.DepositDAI(amount=1_000_000, avatar=safe.address)])
    assert get_balance(w3, ETHAddr.DAI, safe.address) == 0
    assert get_balance(w3, ETHAddr.sDAI, safe.address) == 976_458

    safe.send([spark.WithdrawWithSDAI(amount=976_458, avatar=safe.address)])
    assert get_balance(w3, ETHAddr.DAI, safe.address) == 999_999
    assert get_balance(w3, ETHAddr.sDAI, safe.address) == 0

