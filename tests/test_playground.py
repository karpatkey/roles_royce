import os
from web3 import Web3
from gnosis.safe import addresses, Safe, SafeOperation
from gnosis.eth import EthereumNetwork, EthereumClient
from eth_account import Account

from roles_royce.protocols.eth import lido
from roles_royce import send, Chain
from roles_royce.utils_playground import safe_abi, role_abi, role_bytecode, dai_abi, steth_contract_abi
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
    bytecode_without_default_constructor = role_bytecode[:-len(role_constructor_bytes)]

    owner = avatar = target = w3.to_checksum_address(test_account0_addr)
    role_ctract = w3.eth.contract(abi=role_abi, bytecode=bytecode_without_default_constructor)

    tx_receipt = role_ctract.constructor(owner, avatar, target).transact()  # deploy!
    roles_ctract_address = w3.eth.get_transaction_receipt(tx_receipt).contractAddress

    role_ctract = w3.eth.contract(roles_ctract_address, abi=role_abi)
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

    # enable an EOA for setting as a role
    enable_module = role_ctract.functions.enableModule(test_account1_addr).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=enable_module, signer_key=test_account0_private_key)
    assert role_ctract.functions.isModuleEnabled(test_account1_addr).call()

    # assign the role to the test_account1_addr
    assign_roles = role_ctract.functions.assignRoles(test_account1_addr, [1], [True]).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=roles_ctract_address, data=assign_roles, signer_key=test_account0_private_key)

    # target stETH address preset
    approve_steth_preset = "0x5e8266950000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84"
    safe_send(safe, to=roles_ctract_address, data=approve_steth_preset, signer_key=test_account0_private_key)

    # scope function submit to deposit eth preset
    deposit_steth_preset = "0x33a0480c0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84a1903eab0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000140000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000001c000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000"
    safe_send(safe, to=roles_ctract_address, data=deposit_steth_preset, signer_key=test_account0_private_key)

    # submit ETH in exchage for stETH
    deposit_eth = lido.Deposit(eth_amount=1_000_000_000_000_000)
    send_approve = send([deposit_eth], role=1, private_key=test_account1_private_key, roles_mod_address=roles_ctract_address,
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