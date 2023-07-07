import os
from web3 import Web3
from gnosis.safe import addresses, Safe, SafeOperation
from gnosis.eth import EthereumNetwork, EthereumClient
from eth_account import Account

from roles_royce.protocols.eth import balancer,aura
from roles_royce import send, Chain
from roles_royce.evm_utils import roles_abi, roles_bytecode, dai_abi, steth_contract_abi
from roles_royce.utils import MULTISENDS
from roles_royce.constants import ETHAddr
from .utils import local_node, local_node_reset, ETH_LOCAL_NODE_URL, hardhat_unlock_account


def safe_send(safe, signer_key, to, data, value=0):
    safe_tx = safe.build_multisig_tx(to=to, value=value, data=data, operation=SafeOperation.CALL.value,
                                     safe_tx_gas=500000,
                                     base_gas=500000, gas_price=1, gas_token=ETHAddr.ZERO, refund_receiver=ETHAddr.ZERO)
    safe_tx.sign(signer_key)
    safe_tx.execute(signer_key)
    return safe_tx


def test_safe_and_roles(local_node):
    w3 = local_node
    ethereum_client = EthereumClient(ETH_LOCAL_NODE_URL)

    # workarround https://github.com/ethereum/web3.py/pull/3002 / MethodUnavailable: {'code': -32601, 'message': 'Method eth_maxPriorityFeePerGas not found', 'data': {'message': 'Method eth_maxPriorityFeePerGas not found'}}
    ethereum_client.w3.eth._max_priority_fee = lambda: 0
    w3.eth._max_priority_fee = lambda: 0

    # test accounts are generated using the Mnemonic: "test test test test test test test test test test test junk"
    test_account0_addr = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    test_account0_private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    test_account1_addr = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    test_account1_private_key = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
    test_account2_addr = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
    test_account2_private_key = "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"
    test_account3_addr = "0x90F79bf6EB2c4f870365E785982E1f101E93b906"
    test_account3_private_key = "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6"
    test_account4_addr = "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65"
    test_account4_private_key = "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a"
    test_account5_addr = "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc"
    test_account5_private_key = "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba"

    assert w3.eth.get_balance(test_account0_addr) == 10000000000000000000000

    ethereum_tx_sent = Safe.create(ethereum_client, deployer_account=Account.from_key(test_account0_private_key),
                                   master_copy_address=addresses.MASTER_COPIES[EthereumNetwork.MAINNET][0][0],
                                   owners=[test_account0_addr], threshold=1)

    safe = Safe(ethereum_tx_sent.contract_address, ethereum_client)
    safe.retrieve_all_info()

    # send ETH to the safe
    balance_eth = 0.01
    w3.eth.send_transaction({"to": safe.address, "value": Web3.to_wei(balance_eth, "ether")})
    assert w3.eth.get_balance(safe.address) == Web3.to_wei(balance_eth, "ether")

    # steal DAIs from a large holder and send them to the safe
    ADDRESS_WITH_LOTS_OF_TOKENS = "0x075e72a5eDf65F0A5f44699c7654C1a76941Ddc8"

    DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    DAI_ABI = dai_abi

    dai_ctract = w3.eth.contract(address=DAI, abi=DAI_ABI)
    dai_decimals = dai_ctract.functions.decimals().call()
    dai_amount = 5 * (10 ** dai_decimals)

    hardhat_unlock_account(w3, ADDRESS_WITH_LOTS_OF_TOKENS)
    dai_ctract.functions.transfer(safe.address, dai_amount).transact({"from": ADDRESS_WITH_LOTS_OF_TOKENS})
    assert dai_ctract.functions.balanceOf(safe.address).call() == 5 * (10 ** dai_decimals)

    # send some DAIs from the safe to the test_address
    transfer_dai = dai_ctract.functions.transfer(test_account0_addr, 2 * (10 ** dai_decimals)).build_transaction({"from": safe.address})[
        'data']
    tx = safe.build_multisig_tx(to=DAI, value=0, data=transfer_dai, operation=SafeOperation.CALL.value, safe_tx_gas=500000,
                                base_gas=500000, gas_price=1, gas_token=ETHAddr.ZERO, refund_receiver=ETHAddr.ZERO)
    tx.sign(test_account0_private_key)
    tx.execute(test_account0_private_key)
    assert dai_ctract.functions.balanceOf(test_account0_addr).call() == 2 * (10 ** dai_decimals)
    assert dai_ctract.functions.balanceOf(safe.address).call() == 3 * (10 ** dai_decimals)

    # Deploy a Roles contrat without using the ProxyFactory (to simplify things)
    role_constructor_bytes = "000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001"
    bytecode_without_default_constructor = roles_bytecode[:-len(role_constructor_bytes)]

    owner = avatar = target = w3.to_checksum_address(test_account0_addr)
    role_ctract = w3.eth.contract(abi=roles_abi, bytecode=bytecode_without_default_constructor)

    tx_receipt = role_ctract.constructor(owner, avatar, target).transact()  # deploy!
    roles_ctract_address = w3.eth.get_transaction_receipt(tx_receipt).contractAddress

    role_ctract = w3.eth.contract(roles_ctract_address, abi=roles_abi)
    assert role_ctract.functions.avatar().call() == avatar

    # give the roles_mod to the safe
    role_ctract.functions.setMultisend(MULTISENDS[Chain.ETHEREUM]).transact()
    role_ctract.functions.setTarget(safe.address).transact()
    role_ctract.functions.setAvatar(safe.address).transact()
    role_ctract.functions.transferOwnership(safe.address).transact()
    assert role_ctract.functions.owner().call() == safe.address
    assert role_ctract.functions.avatar().call() == safe.address
    assert role_ctract.functions.target().call() == safe.address

    # set roles_mod as module of safe
    enable_module_roles = safe.contract.functions.enableModule(roles_ctract_address).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=safe.address, data=enable_module_roles, signer_key=test_account0_private_key)
    assert safe.contract.functions.isModuleEnabled(roles_ctract_address).call()

    # enable an EOA for setting as a manager role
    enable_module_1 = role_ctract.functions.enableModule(test_account1_addr).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=enable_module_1, signer_key=test_account0_private_key)
    assert role_ctract.functions.isModuleEnabled(test_account1_addr).call()

    # assign the manager role to the test_account1_addr
    assign_role_1 = role_ctract.functions.assignRoles(test_account1_addr, [1], [True]).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=assign_role_1, signer_key=test_account0_private_key)

    # enable an EOA for setting as a revoker role
    enable_module_2 = role_ctract.functions.enableModule(test_account2_addr).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=enable_module_2, signer_key=test_account0_private_key)
    assert role_ctract.functions.isModuleEnabled(test_account2_addr).call()

    # assign the revoker role to the test_account2_addr
    assign_role_2 = role_ctract.functions.assignRoles(test_account2_addr, [2], [True]).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=assign_role_2, signer_key=test_account0_private_key)

    # enable an EOA for setting as a harvester role
    enable_module_3 = role_ctract.functions.enableModule(test_account3_addr).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=enable_module_3, signer_key=test_account0_private_key)
    assert role_ctract.functions.isModuleEnabled(test_account3_addr).call()

    # assign the role to the test_account3_addr
    assign_role_3 = role_ctract.functions.assignRoles(test_account3_addr, [3], [True]).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=assign_role_3, signer_key=test_account0_private_key)

    # enable an EOA for setting as a disassembler role
    enable_module_4 = role_ctract.functions.enableModule(test_account4_addr).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=enable_module_4, signer_key=test_account0_private_key)
    assert role_ctract.functions.isModuleEnabled(test_account4_addr).call()

    # assign the role to the test_account4_addr
    assign_role_4 = role_ctract.functions.assignRoles(test_account4_addr, [4], [True]).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=assign_role_4, signer_key=test_account0_private_key)

    # enable an EOA for setting as a swapper role
    enable_module_5 = role_ctract.functions.enableModule(test_account5_addr).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=enable_module_5, signer_key=test_account0_private_key)
    assert role_ctract.functions.isModuleEnabled(test_account5_addr).call()

    # assign the role to the test_account5_addr
    assign_role_5 = role_ctract.functions.assignRoles(test_account5_addr, [5], [True]).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=assign_role_5, signer_key=test_account0_private_key)

    # TODO: preset to approve method (spender: vault)

    # TODO: preset to deposit pool tokens for Balancer Pool Token

    # TODO: preset to approve BPT with AURA Booster as spender

    # TODO: preset to deposit Balancer Pool Token in AURA

    # TODO: preset to withdraw Balancer Pool Token from AURA

    # TODO: preset to withdraw Balancer Pool Token in exchange for pool token

    # approve tokens in balancer and aura
    approve_vault = balancer.ApproveForVault
    approve_aura_booster = aura.ApproveForBooster
    send_approve = send([approve_vault,approve_aura_booster], role=2, private_key=test_account2_private_key, roles_mod_address=roles_ctract_address,
                        blockchain=Chain.ETHEREUM, web3=w3)
    assert send_approve

    # deposit tokens in balancer and stake in aura
    deposit_balancer = balancer.SingleAssetJoin
    deposit_aura = aura.DepositBPT
    send_deposits = send([deposit_balancer,deposit_aura], role=1, private_key=test_account1_private_key, roles_mod_address=roles_ctract_address,
                        blockchain=Chain.ETHEREUM, web3=w3)
    assert send_deposits

    # withdraw tokens from aura and balancer
    withdraw_aura = aura.WithdrawAndUndwrapStakedBPT
    withdraw_balancer = balancer.SingleAssetExit
    send_approve = send([withdraw_aura,withdraw_balancer], role=4, private_key=test_account4_private_key, roles_mod_address=roles_ctract_address,
                        blockchain=Chain.ETHEREUM, web3=w3)
    assert send_approve

    # check that the stETH tokens are in the safe
    steth_contract_address = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    steth_contract = w3.eth.contract(address=steth_contract_address, abi=steth_contract_abi)
    assert steth_contract.functions.balanceOf(safe.address).call() == 999999999999999


def test_simple_account_balance(local_node):
    w3 = local_node

    # test accounts are generated using the Mnemonic: "test test test test test test test test test test test junk"
    test_account0_addr = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

    assert w3.eth.get_balance(test_account0_addr) == 10000000000000000000000
