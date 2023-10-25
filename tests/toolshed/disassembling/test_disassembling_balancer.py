from roles_royce.constants import ETHAddr
from tests.utils import (local_node_eth, accounts, fork_unlock_account, create_simple_safe, steal_token, top_up_address)
from roles_royce.toolshed.disassembling import BalancerDisassembler
from roles_royce.addresses_and_abis.balancer import Abis
from roles_royce.constants import Chains
from decimal import Decimal
import pytest
from roles_royce.evm_utils import erc20_abi
from tests.roles import setup_common_roles, deploy_roles, apply_presets
from pytest import approx

# Preset with the permission to call the exit() function in the Balancer vault (the avatar address is
# 0xc01318bab7ee1f5ba734172bf7718b5dc6ec90e1)
preset = '{"version":"1.0","chainId":"1","meta":{"name":null,"description":"","txBuilderVersion":"1.8.0"},' \
         '"createdAt":1695826823729,"transactions":[{"to":"0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",' \
         '"data":"0x5e8266950000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ba12222222228d8ba445958a75a0704d566bf2c8","value":"0"},{"to":"0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data":"0x33a0480c0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ba12222222228d8ba445958a75a0704d566bf2c88bdb3913000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000280000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000c01318bab7ee1f5ba734172bf7718b5dc6ec90e10000000000000000000000000000000000000000000000000000000000000020000000000000000000000000c01318bab7ee1f5ba734172bf7718b5dc6ec90e1","value":"0"}]}'


def test_integration_exit_1_1(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = 18421437
    local_node_eth.set_block(block)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)

    apply_presets(avatar_safe, roles_contract, json_data=preset,
                  replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])])

    blockchain = Chains.get_blockchain_from_web3(w3)

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[1].address
    private_key = accounts[1].key
    role = 1

    balancer_disassembler = BalancerDisassembler(w3=w3,
                                                 avatar_safe_address=avatar_safe.address,
                                                 roles_mod_address=roles_contract.address,
                                                 role=role,
                                                 signer_address=disassembler_address)
    # ----------------------------------------------------------------------------------------------------------------
    # Composable
    GHO_USDT_USDC_bpt_address = "0x8353157092ED8Be69a9DF8F95af097bbF33Cb2aF"
    # Initial data
    bpt_contract = w3.eth.contract(address=GHO_USDT_USDC_bpt_address,
                                   abi=Abis[blockchain].UniversalBPT.abi)
    steal_token(w3=w3, token=GHO_USDT_USDC_bpt_address, holder="0x854B004700885A61107B458f11eCC169A019b764",
                to=avatar_safe.address, amount=8_999_999_999_999_000_000)
    bpt_token_balance = bpt_contract.functions.balanceOf(avatar_safe.address).call()
    assert bpt_token_balance == 8_999_999_999_999_000_000

    txn_transactable = balancer_disassembler.exit_1_1(percentage=50,
                                                      exit_arguments=[{"bpt_address": GHO_USDT_USDC_bpt_address,
                                                                       "max_slippage": 0.01}])

    balancer_disassembler.send(txns=txn_transactable, private_key=private_key)

    bpt_token_balance_after = bpt_contract.functions.balanceOf(avatar_safe_address).call()
    assert bpt_token_balance_after == 4499999999999500000
    assert bpt_token_balance_after == int(Decimal(bpt_token_balance) / Decimal(2))

    # ----------------------------------------------------------------------------------------------------------------
    # Metastable
    rETH_WETH_bpt_address = "0x1E19CF2D73a72Ef1332C882F20534B6519Be0276"
    # Initial data
    bpt_contract = w3.eth.contract(address=rETH_WETH_bpt_address,
                                   abi=Abis[blockchain].UniversalBPT.abi)

    steal_token(w3=w3, token=rETH_WETH_bpt_address, holder="0xa7dB55e153C0c71Ff35432a9aBe2A853f886Ce0D",
                to=avatar_safe.address, amount=80_999_999)
    bpt_token_balance = bpt_contract.functions.balanceOf(avatar_safe.address).call()
    assert bpt_token_balance == 80_999_999

    txn_transactable = balancer_disassembler.exit_1_1(percentage=50,
                                                      exit_arguments=[{"bpt_address": rETH_WETH_bpt_address,
                                                                       "max_slippage": 1}])

    balancer_disassembler.send(txns=txn_transactable, private_key=private_key)

    bpt_token_balance_after = bpt_contract.functions.balanceOf(avatar_safe_address).call()
    assert bpt_token_balance_after == 40500000 or bpt_token_balance_after == 40499999
    assert bpt_token_balance_after == approx(int(Decimal(bpt_token_balance) / Decimal(2)))


def test_integration_exit_1_2(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = 18421437
    local_node_eth.set_block(block)
    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)

    apply_presets(avatar_safe, roles_contract, json_data=preset,
                  replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])])

    blockchain = Chains.get_blockchain_from_web3(w3)

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[1].address
    private_key = accounts[1].key
    role = 1

    fork_unlock_account(w3, disassembler_address)

    balancer_disassembler = BalancerDisassembler(w3=w3,
                                                 avatar_safe_address=avatar_safe.address,
                                                 roles_mod_address=roles_contract.address,
                                                 role=role,
                                                 signer_address=disassembler_address)
    # ----------------------------------------------------------------------------------------------------------------
    # Composable
    GHO_USDT_USDC_bpt_address = "0x8353157092ED8Be69a9DF8F95af097bbF33Cb2aF"

    bpt_contract = w3.eth.contract(address=GHO_USDT_USDC_bpt_address,
                                   abi=Abis[blockchain].UniversalBPT.abi)
    steal_token(w3=w3, token=GHO_USDT_USDC_bpt_address, holder="0x854B004700885A61107B458f11eCC169A019b764",
                to=avatar_safe.address, amount=8_999_999_999_999_000_000)
    bpt_token_balance = bpt_contract.functions.balanceOf(avatar_safe.address).call()
    assert bpt_token_balance == 8999999999999000000

    GHO_contract = w3.eth.contract(address=ETHAddr.GHO, abi=erc20_abi)
    GHO_balance = GHO_contract.functions.balanceOf(avatar_safe_address).call()
    assert GHO_balance == 0

    txn_transactable = balancer_disassembler.exit_1_2(percentage=30,
                                                      exit_arguments=[{"bpt_address": GHO_USDT_USDC_bpt_address,
                                                                       "token_out_address": ETHAddr.GHO,
                                                                       "max_slippage": 0.01}])

    balancer_disassembler.send(txns=txn_transactable, private_key=private_key)

    bpt_token_balance_after = bpt_contract.functions.balanceOf(avatar_safe_address).call()
    assert bpt_token_balance_after == 6299999999999300100
    assert bpt_token_balance_after == approx(int(Decimal(bpt_token_balance) * Decimal(0.7)))

    new_GHO_balance = GHO_contract.functions.balanceOf(avatar_safe_address).call()
    assert new_GHO_balance == 2736771989880524105

    # ----------------------------------------------------------------------------------------------------------------
    # Metastable
    rETH_WETH_bpt_address = "0x1E19CF2D73a72Ef1332C882F20534B6519Be0276"
    # Initial data
    bpt_contract = w3.eth.contract(address=rETH_WETH_bpt_address,
                                   abi=Abis[blockchain].UniversalBPT.abi)

    steal_token(w3=w3, token=rETH_WETH_bpt_address, holder="0xa7dB55e153C0c71Ff35432a9aBe2A853f886Ce0D",
                to=avatar_safe.address, amount=80_999_999)
    bpt_token_balance = bpt_contract.functions.balanceOf(avatar_safe.address).call()
    assert bpt_token_balance == 80_999_999

    WETH_contract = w3.eth.contract(address=ETHAddr.WETH, abi=erc20_abi)
    WETH_balance = WETH_contract.functions.balanceOf(avatar_safe_address).call()
    assert WETH_balance == 0

    txn_transactable = balancer_disassembler.exit_1_2(percentage=30,
                                                      exit_arguments=[{"bpt_address": rETH_WETH_bpt_address,
                                                                       "token_out_address": ETHAddr.WETH,
                                                                       "max_slippage": 1}])

    balancer_disassembler.send(txns=txn_transactable, private_key=private_key)

    bpt_token_balance_after = bpt_contract.functions.balanceOf(avatar_safe_address).call()
    assert bpt_token_balance_after == 56700000
    assert bpt_token_balance_after == approx(int(Decimal(bpt_token_balance) * Decimal(0.7)))


def test_integration_exit_1_3(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = 18193307
    local_node_eth.set_block(block)
    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)

    apply_presets(avatar_safe, roles_contract, json_data=preset,
                  replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])])

    blockchain = Chains.get_blockchain_from_web3(w3)

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[1].address
    private_key = accounts[1].key
    role = 1

    emergency = "0xA29F61256e948F3FB707b4b3B138C5cCb9EF9888"

    top_up_address(w3, emergency, 100)
    fork_unlock_account(w3, emergency)

    balancer_disassembler = BalancerDisassembler(w3=w3,
                                                 avatar_safe_address=avatar_safe.address,
                                                 roles_mod_address=roles_contract.address,
                                                 role=role,
                                                 signer_address=disassembler_address)
    DOLA_USDC_BPT = "0xFf4ce5AAAb5a627bf82f4A571AB1cE94Aa365eA6"

    bpt_contract = w3.eth.contract(address=DOLA_USDC_BPT,
                                   abi=Abis[blockchain].UniversalBPT.abi)
    steal_token(w3=w3, token=DOLA_USDC_BPT, holder="0xF59b324Cb65258DC52B5DB8ac4f991286603B7e1",
                to=avatar_safe.address, amount=4_000_000_000)
    bpt_balance = bpt_contract.functions.balanceOf(avatar_safe.address).call()
    assert bpt_balance == 4_000_000_000

    bpt_contract.functions.enableRecoveryMode().transact({'from': emergency})
    assert bpt_contract.functions.inRecoveryMode().call()

    DOLA_contract = w3.eth.contract(address="0x865377367054516e17014CcdED1e7d814EDC9ce4", abi=erc20_abi)
    DOLA_balance = DOLA_contract.functions.balanceOf(avatar_safe_address).call()
    assert DOLA_balance == 0

    USDC_contract = w3.eth.contract(address=ETHAddr.USDC, abi=erc20_abi)
    USDC_balance = USDC_contract.functions.balanceOf(avatar_safe_address).call()
    assert USDC_balance == 0

    txn_transactable = balancer_disassembler.exit_1_3(percentage=50,
                                                      exit_arguments=[{"bpt_address": DOLA_USDC_BPT}])

    balancer_disassembler.send(txns=txn_transactable, private_key=private_key)

    bpt_balance_after = bpt_contract.functions.balanceOf(avatar_safe_address).call()
    assert bpt_balance_after == 2_000_000_000
    assert bpt_balance_after == int(Decimal(bpt_balance) / Decimal(2))

    new_DOLA_balance = DOLA_contract.functions.balanceOf(avatar_safe_address).call()
    assert new_DOLA_balance == 1300986017

    new_USDC_balance = USDC_contract.functions.balanceOf(avatar_safe_address).call()
    assert new_USDC_balance == 0


# needs a proper preset
@pytest.mark.skip("WIP")
def test_integration_exit_2_1(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = 18193307
    local_node_eth.set_block(block)
    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)

    presets = """{"version":"1.0","chainId":"1","meta":{"name":null,"description":"","txBuilderVersion":"1.8.0"},"createdAt":1695826823729,"transactions":
                [{"to":"0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data":"0x5e8266950000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ba12222222228d8ba445958a75a0704d566bf2c8","value":"0"},
                 {"to":"0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data":"0x33a0480c0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ba12222222228d8ba445958a75a0704d566bf2c88bdb391300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000028000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000000020ff4ce5aaab5a627bf82f4a571ab1ce94aa365ea60000000000000000000005d90000000000000000000000000000000000000000000000000000000000000020000000000000000000000000c01318bab7ee1f5ba734172bf7718b5dc6ec90e10000000000000000000000000000000000000000000000000000000000000020000000000000000000000000c01318bab7ee1f5ba734172bf7718b5dc6ec90e1","value":"0"}]},
                 {"to":"0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data":"0x5e8266950000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ba12222222228d8ba445958a75a0704d566bf2c8","value":"0"},
                 {"to":"0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data":"0x33a0480c0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ba12222222228d8ba445958a75a0704d566bf2c88bdb391300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000028000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000000020ff4ce5aaab5a627bf82f4a571ab1ce94aa365ea60000000000000000000005d90000000000000000000000000000000000000000000000000000000000000020000000000000000000000000c01318bab7ee1f5ba734172bf7718b5dc6ec90e10000000000000000000000000000000000000000000000000000000000000020000000000000000000000000c01318bab7ee1f5ba734172bf7718b5dc6ec90e1","value":"0"}]}"""

    apply_presets(avatar_safe, roles_contract, json_data=presets,
                  replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])])

    blockchain = Chains.get_blockchain_from_web3(w3)

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[1].address
    private_key = accounts[1].key
    role = 1

    emergency = "0xA29F61256e948F3FB707b4b3B138C5cCb9EF9888"

    balancer_disassembler = BalancerDisassembler(w3=w3,
                                                 avatar_safe_address=avatar_safe.address,
                                                 roles_mod_address=roles_contract.address,
                                                 role=role,
                                                 signer_address=disassembler_address)

    OHM_DAI_BPT_gauge = "0x76FCf0e8C7Ff37A47a799FA2cd4c13cDe0D981C9"
    OHM = "0x64aa3364F17a4D01c6f1751Fd97C2BD3D7e7f1D5"

    bpt_gauge_contract = w3.eth.contract(address=OHM_DAI_BPT_gauge,
                                         abi=Abis[blockchain].Gauge.abi)
    steal_token(w3=w3, token=OHM_DAI_BPT_gauge, holder="0x03D27ae932AEA212f453E105D09A12fEEab3Bd49",
                to=avatar_safe.address, amount=4_000_000_000)
    bpt_gauge_balance = bpt_gauge_contract.functions.balanceOf(avatar_safe.address).call()
    assert bpt_gauge_balance == 4_000_000_000

    OHM_contract = w3.eth.contract(address=ETHAddr.OHM, abi=erc20_abi)
    OHM_balance = OHM_contract.functions.balanceOf(avatar_safe_address).call()
    assert OHM_balance == 0

    DAI_contract = w3.eth.contract(address=ETHAddr.DAI, abi=erc20_abi)
    DAI_balance = DAI_contract.functions.balanceOf(avatar_safe_address).call()
    assert DAI_balance == 0

    txn_transactable = balancer_disassembler.exit_2_1(percentage=50,
                                                      exit_arguments=[{"gauge_address": OHM_DAI_BPT_gauge,
                                                                       "max_slippage": 0.01}])

    txn = balancer_disassembler.send(txns=txn_transactable, private_key=private_key)

    bpt_gauge_balance_after = bpt_gauge_contract.functions.balanceOf(avatar_safe_address).call()
    assert bpt_gauge_balance_after == 4_000_000_000
    assert bpt_gauge_balance_after == int(Decimal(bpt_gauge_balance) / Decimal(2))

    new_OHM_balance = OHM_contract.functions.balanceOf(avatar_safe_address).call()
    assert new_OHM_balance == 400000

    new_DAI_balance = DAI_contract.functions.balanceOf(avatar_safe_address).call()
    assert new_DAI_balance == 400000
