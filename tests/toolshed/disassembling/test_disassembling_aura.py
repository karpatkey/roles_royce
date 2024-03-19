from decimal import Decimal

from defabipedia.aura import Abis
from defabipedia.types import Chain

from roles_royce.constants import ETHAddr
from roles_royce.toolshed.disassembling import AuraDisassembler
from tests.utils import fork_unlock_account, get_balance, local_node_eth, top_up_address

# TODO: build an adequate preset to execute the transactions with roles.send


def test_integration_exit_1(local_node_eth):
    w3 = local_node_eth.w3
    block = 18193307
    local_node_eth.set_block(block)

    blockchain = Chain.get_blockchain_from_web3(w3)

    avatar_safe_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    roles_mod_address = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
    disassembler_address = "0xb11ea45e2d787323dFCF50cb52b4B3126b94810d"
    # Role 4 already has the correct preset applied
    role = 4

    fork_unlock_account(w3, disassembler_address)
    top_up_address(w3, disassembler_address, 100)

    aura_disassembler = AuraDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_mod_address,
        role=role,
        signer_address=disassembler_address,
    )

    rETH_WETH_aura_rewards_address = "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D"

    # Initial data
    aura_rewards_contract = w3.eth.contract(
        address=rETH_WETH_aura_rewards_address, abi=Abis[blockchain].BaseRewardPool.abi
    )

    aura_token_balance = aura_rewards_contract.functions.balanceOf(avatar_safe_address).call()
    assert aura_token_balance == 1503886609846287458132

    txn_transactable = aura_disassembler.exit_1(
        percentage=50, exit_arguments=[{"rewards_address": rETH_WETH_aura_rewards_address}]
    )
    # Since we don't have the private key of the disassembler, we need to build the transaction and send it "manually"
    txn = aura_disassembler.build(txn_transactable, from_address=disassembler_address)
    w3.eth.send_transaction(txn)

    aura_token_balance_after = aura_rewards_contract.functions.balanceOf(avatar_safe_address).call()
    assert aura_token_balance_after == 751943304923143729066
    assert aura_token_balance_after == int(Decimal(aura_token_balance) / Decimal(2))


def test_integration_exit_2_1(local_node_eth):
    w3 = local_node_eth.w3
    block = 18193307
    local_node_eth.set_block(block)

    avatar_safe_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    roles_mod_address = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
    disassembler_address = "0xb11ea45e2d787323dFCF50cb52b4B3126b94810d"
    # Role 4 already has the correct preset applied at this block
    role = 4

    fork_unlock_account(w3, disassembler_address)
    top_up_address(w3, disassembler_address, 100)

    aura_disassembler = AuraDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_mod_address,
        role=role,
        signer_address=disassembler_address,
    )

    rETH_WETH_aura_rewards_address = "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D"

    txn_transactable = aura_disassembler.exit_2_1(
        percentage=50, exit_arguments=[{"rewards_address": rETH_WETH_aura_rewards_address, "max_slippage": 0.01}]
    )

    # Since we don't have the private key of the disassembler, we need to build the transaction and send it "manually"
    txn = aura_disassembler.build(txn_transactable)

    # Initial rETH and WETH balances
    reth_balance = get_balance(w3=w3, token=ETHAddr.rETH, address=avatar_safe_address)
    weth_balance = get_balance(w3=w3, token=ETHAddr.WETH, address=avatar_safe_address)
    assert reth_balance == 0
    assert weth_balance == 607803333328385148020

    w3.eth.send_transaction(txn)

    # FInal rETH and WETH balances
    new_reth_balance = get_balance(w3=w3, token=ETHAddr.rETH, address=avatar_safe_address)
    new_weth_balance = get_balance(w3=w3, token=ETHAddr.WETH, address=avatar_safe_address)
    assert new_reth_balance == 345158884782388730288
    assert new_weth_balance == 1005047469090086219542


def test_integration_exit_2_2(local_node_eth):
    w3 = local_node_eth.w3
    block = 18193307
    local_node_eth.set_block(block)

    avatar_safe_address = "0x849D52316331967b6fF1198e5E32A0eB168D039d"
    roles_mod_address = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
    disassembler_address = "0xb11ea45e2d787323dFCF50cb52b4B3126b94810d"
    # Role 4 already has the correct preset applied at this block
    role = 4

    fork_unlock_account(w3, disassembler_address)
    top_up_address(w3, disassembler_address, 100)

    aura_disassembler = AuraDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_mod_address,
        role=role,
        signer_address=disassembler_address,
    )

    rETH_WETH_aura_rewards_address = "0xDd1fE5AD401D4777cE89959b7fa587e569Bf125D"

    txn_transactable = aura_disassembler.exit_2_2(
        percentage=50,
        exit_arguments=[
            {"rewards_address": rETH_WETH_aura_rewards_address, "max_slippage": 0.01, "token_out_address": ETHAddr.WETH}
        ],
    )

    # Since we don't have the private key of the disassembler, we need to build the transaction and send it "manually"
    txn = aura_disassembler.build(txn_transactable)

    # Initial WETH balance
    weth_balance = get_balance(w3=w3, token=ETHAddr.WETH, address=avatar_safe_address)
    assert weth_balance == 607803333328385148020

    w3.eth.send_transaction(txn)

    new_weth_balance = get_balance(w3=w3, token=ETHAddr.WETH, address=avatar_safe_address)

    assert new_weth_balance == 1379413879858087032626
