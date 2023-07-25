from roles_royce import check, send, Chain
from roles_royce.protocols.eth import lido
from roles_royce.constants import ETHAddr
from .utils import web3_eth, local_node, accounts, get_balance, hardhat_unlock_account, create_simple_safe

# Test safe
AVATAR = "0xC01318baB7ee1f5ba734172bF7718b5DC6Ec90E1"
ROLES_MOD_ADDRESS = "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86"
MANAGER = "0x216071B1B5681D67A75f7eEAF92CEC8262bE29f7"
ROLE = 1


def test_methods(web3_eth):
    approve = lido.ApproveWithdrawalStETHwithWstETH(amount=100)
    status = check([approve], role=ROLE, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status


def test_withdrawal_approvals():
    approve_steth = lido.ApproveWithdrawalStETHWithUnstETH(amount=100)
    approve_wsteth = lido.ApproveWithdrawalWstETH(amount=100)
    assert approve_steth.data == "0x095ea7b3000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b10000000000000000000000000000000000000000000000000000000000000064"
    assert approve_wsteth.data == "0x095ea7b3000000000000000000000000889edc2edab5f40e902b864ad4d7ade8e412f9b10000000000000000000000000000000000000000000000000000000000000064"


def test_deposit(web3_eth):
    deposit = lido.Deposit(eth_amount=10)
    assert deposit.value == 10
    assert deposit.target_address == ETHAddr.stETH
    status = check([deposit], role=ROLE, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status


def test_wrap(web3_eth):
    approve = lido.ApproveWithdrawalStETHwithWstETH(amount=100)
    wrap = lido.Wrap(amount=10)
    status = check([approve, wrap], role=ROLE, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status


def test_unwrap(web3_eth):
    unwrap = lido.Unwrap(amount=1_000_000_000_000)
    status = check([unwrap], role=ROLE, account=MANAGER, roles_mod_address=ROLES_MOD_ADDRESS,
                   blockchain=Chain.ETHEREUM, web3=web3_eth, block=17067157)
    assert status


def test_request_withdrawal_steth():
    request = lido.RequestWithdrawalsStETH(amounts=[1_000], avatar=AVATAR)
    assert request.data == "0xd66810420000000000000000000000000000000000000000000000000000000000000040000000000000000000000000" \
                           "c01318bab7ee1f5ba734172bf7718b5dc6ec90e10000000000000000000000000000000000000000000000000000000000000001" \
                           "00000000000000000000000000000000000000000000000000000000000003e8"


def test_request_withdrawal_wsteth():
    request = lido.RequestWithdrawalsWstETH(amounts=[1_000], avatar=AVATAR)
    assert request.data == "0x19aa62570000000000000000000000000000000000000000000000000000000000000040000000000000000000000000" \
                           "c01318bab7ee1f5ba734172bf7718b5dc6ec90e10000000000000000000000000000000000000000000000000000000000000001" \
                           "00000000000000000000000000000000000000000000000000000000000003e8"


def test_claim_withdrawal():
    claim = lido.ClaimWithdrawals(request_ids=[1], hints=[35])
    assert claim.data == "0xe3afe0a3000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000" \
                         "000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000001" \
                         "00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001" \
                         "0000000000000000000000000000000000000000000000000000000000000023"


def test_integration(local_node, accounts):
    w3 = local_node
    safe = create_simple_safe(w3, accounts[0])
    safe.send([lido.Deposit(eth_amount=1_000_000)])
    steth_balance = get_balance(w3, ETHAddr.stETH, safe.address)

    txs = [
        lido.ApproveWithdrawalStETHwithWstETH(amount=steth_balance),
        lido.Wrap(amount=steth_balance),
        lido.ApproveWithdrawalStETHwithWstETH(amount=0)
    ]
    safe.send(txs)
    wsteth_balance = get_balance(w3, ETHAddr.wstETH, safe.address)

    txs = [lido.ApproveWithdrawalWstETH(amount=wsteth_balance),
           lido.Unwrap(amount=wsteth_balance),
           lido.ApproveWithdrawalWstETH(amount=0)
           ]
    safe.send(txs)

    assert get_balance(w3, ETHAddr.wstETH, safe.address) == 0
    steth_balance = get_balance(w3, ETHAddr.stETH, safe.address)
    assert steth_balance > 0

    safe.send([lido.ApproveWithdrawalStETHWithUnstETH(amount=steth_balance),
               lido.RequestWithdrawalsStETH(amounts=[steth_balance], avatar=safe.address)])
    nft_ids = lido.GetWithdrawalRequests(owner=safe.address).call(w3)
    assert len(nft_ids) == 1

    statuses = lido.GetWithdrawalStatus(nft_ids).call(w3)
    amount_of_stETH, shares, owner, timestamp, is_finalized, is_claimed = statuses[0]
    assert not is_finalized
    assert not is_claimed
    assert owner == safe.address
    assert amount_of_stETH == steth_balance
    # ClaimWithdrawal can't be called until the withdrawal request is finalized.
    # It will get finalized when reports are sent, and can take 24hs

    # Now we use a NFT that we don't own, but we know it is finalized
    statuses = lido.GetWithdrawalStatus([3002]).call(w3)
    amount_of_stETH, shares, owner, timestamp, is_finalized, is_claimed = statuses[0]
    assert is_finalized and not is_claimed

    hardhat_unlock_account(w3, owner)
    # TODO
    # claim = lido.ClaimWithdrawal(request_id=3002)
    # tx_hash = w3.eth.send_transaction({"to": claim.contract_address, "value": claim.value, "data": claim.data,
    #                                "type": claim.operation,
    #                                "from": owner})
    # receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
