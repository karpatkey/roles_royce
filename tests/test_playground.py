from web3 import Web3
from gnosis.safe import addresses, Safe, SafeOperation
from gnosis.eth import EthereumNetwork, EthereumClient
from eth_account import Account

from roles_royce.protocols.eth import lido
from roles_royce import check, send, Chain
from roles_royce.utils_playground import _safe_abi, _role_abi, _role_bytecode, _dai_abi, _steth_contract_abi

ETHEREUM_NODE_URL = "http://127.0.0.1:8545"
gnosis_safe_proxy_address = "0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2"
gnosis_safe_proxy_factory_abi = """[{"anonymous":false,"inputs":[{"indexed":false,"internalType":"contract GnosisSafeProxy","name":"proxy","type":"address"},{"indexed":false,"internalType":"address","name":"singleton","type":"address"}],"name":"ProxyCreation","type":"event"},{"inputs":[{"internalType":"address","name":"_singleton","type":"address"},{"internalType":"bytes","name":"initializer","type":"bytes"},{"internalType":"uint256","name":"saltNonce","type":"uint256"}],"name":"calculateCreateProxyWithNonceAddress","outputs":[{"internalType":"contract GnosisSafeProxy","name":"proxy","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"singleton","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"createProxy","outputs":[{"internalType":"contract GnosisSafeProxy","name":"proxy","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_singleton","type":"address"},{"internalType":"bytes","name":"initializer","type":"bytes"},{"internalType":"uint256","name":"saltNonce","type":"uint256"},{"internalType":"contract IProxyCreationCallback","name":"callback","type":"address"}],"name":"createProxyWithCallback","outputs":[{"internalType":"contract GnosisSafeProxy","name":"proxy","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_singleton","type":"address"},{"internalType":"bytes","name":"initializer","type":"bytes"},{"internalType":"uint256","name":"saltNonce","type":"uint256"}],"name":"createProxyWithNonce","outputs":[{"internalType":"contract GnosisSafeProxy","name":"proxy","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"proxyCreationCode","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"proxyRuntimeCode","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"pure","type":"function"}]"""

safe_abi = _safe_abi

ethereum_client = EthereumClient(ETHEREUM_NODE_URL)


test_account_addr = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
test_account_private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
test_account_addr1 = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
test_account_private_key1 = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
account = Account.from_key(test_account_private_key)  #
# workarround https://github.com/ethereum/web3.py/pull/3002 / MethodUnavailable: {'code': -32601, 'message': 'Method eth_maxPriorityFeePerGas not found', 'data': {'message': 'Method eth_maxPriorityFeePerGas not found'}}
ethereum_client.w3.eth._max_priority_fee = lambda: 0

ethereum_tx_sent = Safe.create(ethereum_client, deployer_account=account,
                               master_copy_address=addresses.MASTER_COPIES[EthereumNetwork.MAINNET][0][0],
                               owners=[test_account_addr], threshold=1)

safe = Safe(ethereum_tx_sent.contract_address, ethereum_client)
safe.retrieve_all_info()


# SafeInfo(address='0x447786d977Ea11Ad0600E193b2d07A06EfB53e5F', fallback_handler='0x0000000000000000000000000000000000000000', guard='0x0000000000000000000000000000000000000000', master_copy='0xfb1bffC9d739B8D520DaF37dF666da4C687191EA', modules=[], nonce=0, owners=['0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'], threshold=1, version='1.3.0')

def send_tx(w3, tx, account) -> bytes:
    tx["from"] = account.address
    if "nonce" not in tx:
        tx["nonce"] = w3.eth.get_transaction_count(account.address, block_identifier="pending")
    if "gasPrice" not in tx and "maxFeePerGas" not in tx:
        tx["gasPrice"] = w3.eth.gas_price

    if "gas" not in tx:
        tx["gas"] = w3.eth.estimate_gas(tx)
    else:
        tx["gas"] *= 2

    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(bytes(signed_tx.rawTransaction))
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


balance_eth = 0.01
send_tx(ethereum_client.w3, tx={"to": safe.address, "value": Web3.to_wei(balance_eth, "ether")}, account=account)

safe_balance = safe.w3.eth.get_balance(safe.address)
print("safe address is: ",safe.address)
print(f"safe balance: {safe_balance}")

ADDRESS_WITH_LOTS_OF_TOKENS = "0x075e72a5eDf65F0A5f44699c7654C1a76941Ddc8"

DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
DAI_ABI = _dai_abi

w3 = ethereum_client.w3


def hardhat_unlock_account(w3, address):
    return w3.provider.make_request("hardhat_impersonateAccount", [address])


dai_ctract = w3.eth.contract(address=DAI, abi=DAI_ABI)
dai_decimals = dai_ctract.functions.decimals().call()
dai_amount = 1_000_000 * (10 ** dai_decimals)

safe_contract = w3.eth.contract(address=safe.address, abi=safe_abi)

# steal DAIs from a large holder and send them to the safe
hardhat_unlock_account(w3, ADDRESS_WITH_LOTS_OF_TOKENS)
dai_ctract.functions.transfer(safe.address, dai_amount).transact({"from": ADDRESS_WITH_LOTS_OF_TOKENS})
print("safe DAI balance:", dai_ctract.functions.balanceOf(safe.address).call())

# send some DAIs from the safe to the test_address
data = dai_ctract.functions.transfer(test_account_addr, 5_000_000).build_transaction({"from": safe.address})['data']

NULL_ADDRESS: str = "0x" + "0" * 40
tx = safe.build_multisig_tx(to=DAI, value=0, data=data, operation=SafeOperation.CALL.value, safe_tx_gas=500000,
                            base_gas=500000, gas_price=1, gas_token=NULL_ADDRESS, refund_receiver=NULL_ADDRESS)
tx.sign(test_account_private_key)
tx.execute(test_account_private_key)
print("safe DAI balance after transfer:", dai_ctract.functions.balanceOf(safe.address).call())


# Deploy a Roles contrat without using the ProxyFactory (to simplify things)
import web3
# from etherscan
role_bytecode = _role_bytecode
role_abi = _role_abi

role_constructor_bytes = "000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001"
bytecode_without_default_constructor = role_bytecode[:-len(role_constructor_bytes)]

web3_local = web3.Web3(web3.HTTPProvider("http://127.0.0.1:8545"))
role_ctract = web3_local.eth.contract(abi=role_abi, bytecode=role_bytecode)

# TODO: what is the target address ?
owner = avatar = target = web3_local.to_checksum_address(test_account_addr)
role_ctract.constructor(owner, avatar, target)

role_ctract = web3_local.eth.contract(abi=role_abi, bytecode=bytecode_without_default_constructor)

tx_receipt = role_ctract.constructor(owner, avatar, target).transact() # deploy!
roles_ctract_address = web3_local.eth.get_transaction_receipt(tx_receipt).contractAddress
print("roles mod deployed",roles_ctract_address)
role_ctract = web3_local.eth.contract(roles_ctract_address, abi=role_abi)
assert role_ctract.functions.avatar().call() == avatar
MULTISEND_CALL_ONLY = '0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761'

# give the roles_mod to the safe
role_ctract.functions.setMultisend(web3_local.to_checksum_address(MULTISEND_CALL_ONLY)).transact()
role_ctract.functions.setTarget(web3_local.to_checksum_address(safe.address)).transact()
role_ctract.functions.setAvatar(web3_local.to_checksum_address(safe.address)).transact()
role_ctract.functions.transferOwnership(web3_local.to_checksum_address(safe.address)).transact()

print("owner is now: ",role_ctract.functions.owner().call())
print("avatar is now: ",role_ctract.functions.avatar().call())
print("target is now: ",role_ctract.functions.target().call())

#set roles_mod as module of safe
txEnable = safe_contract.functions.enableModule(roles_ctract_address).build_transaction({"from": safe.address, "gas": 0, "gasPrice": 0})['data']
safe_tx = safe.build_multisig_tx(to=safe.address, value=0, data=txEnable, operation=SafeOperation.CALL.value, safe_tx_gas=500000,
                            base_gas=500000, gas_price=1, gas_token=NULL_ADDRESS, refund_receiver=NULL_ADDRESS)
safe_tx.sign(test_account_private_key)
safe_tx.execute(test_account_private_key)

print("is module {} enabled?".format(roles_ctract_address), safe_contract.functions.isModuleEnabled(roles_ctract_address).call())

#enable an EOA for setting as a role
txEnable = role_ctract.functions.enableModule(test_account_addr1).build_transaction({"from": safe.address, "gas": 0, "gasPrice": 0})['data']
safe_tx = safe.build_multisig_tx(to=roles_ctract_address, value=0, data=txEnable, operation=SafeOperation.CALL.value, safe_tx_gas=500000,
                            base_gas=500000, gas_price=1, gas_token=NULL_ADDRESS, refund_receiver=NULL_ADDRESS)
safe_tx.sign(test_account_private_key)
safe_tx.execute(test_account_private_key)

print("is module {} enabled?".format(test_account_addr1), role_ctract.functions.isModuleEnabled(test_account_addr1).call())

#assign the role
assign_roles = role_ctract.functions.assignRoles(test_account_addr1,[1],[True]).build_transaction({"from": safe.address, "gas": 0, "gasPrice": 0})['data']
safe_tx = safe.build_multisig_tx(to=roles_ctract_address, value=0, data=assign_roles, operation=SafeOperation.CALL.value, safe_tx_gas=500000,
                            base_gas=500000, gas_price=1, gas_token=NULL_ADDRESS, refund_receiver=NULL_ADDRESS)
safe_tx.sign(test_account_private_key)
safe_tx.execute(test_account_private_key)

#target stETH address preset
approve_steth_preset = "0x5e8266950000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84"

safe_tx = safe.build_multisig_tx(to=roles_ctract_address, value=0, data=approve_steth_preset, operation=SafeOperation.CALL.value, safe_tx_gas=500000,
                            base_gas=500000, gas_price=1, gas_token=NULL_ADDRESS, refund_receiver=NULL_ADDRESS)
safe_tx.sign(test_account_private_key)
safe_tx.execute(test_account_private_key)
print("scope stEtH address preset send")

#scope function submit to deposit eth preset
deposit_steth_preset = "0x33a0480c0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ae7ab96520de3a18e5e111b5eaab095312d7fe84a1903eab0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000140000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000001c000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000"

safe_tx = safe.build_multisig_tx(to=roles_ctract_address, value=0, data=deposit_steth_preset, operation=SafeOperation.CALL.value, safe_tx_gas=500000,
                            base_gas=500000, gas_price=1, gas_token=NULL_ADDRESS, refund_receiver=NULL_ADDRESS)
safe_tx.sign(test_account_private_key)
safe_tx.execute(test_account_private_key)
print("allow function submit preset send")

#submit ETH
deposit_eth = lido.Deposit(eth_amount=1_000_000_000_000_000)
send_approve = send([deposit_eth], role=1, private_key=test_account_private_key1,
                  roles_mod_address=roles_ctract_address, blockchain=Chain.ETHEREUM, web3=w3)
print("transaction execution is done?",send_approve)

steth_contract_address = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
steth_contract_abi = _steth_contract_abi
steth_contract = web3_local.eth.contract(address=steth_contract_address, abi=steth_contract_abi)

print("safe stETH balance after transfer:", steth_contract.functions.balanceOf(safe.address).call())
