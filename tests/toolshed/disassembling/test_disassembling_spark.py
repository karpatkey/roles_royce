from decimal import Decimal

from roles_royce.constants import ETHAddr
from roles_royce.protocols.eth import spark
from roles_royce.toolshed.protocol_utils.spark.utils import SparkUtils
from roles_royce.toolshed.disassembling import SparkDisassembler

from defabipedia.types import Chain

from tests.roles import apply_presets, deploy_roles, setup_common_roles
from tests.utils import create_simple_safe, get_balance, steal_token, top_up_address
from tests.fork_fixtures import accounts
from tests.fork_fixtures import local_node_eth_replay as local_node_eth



def test_integration_1(local_node_eth, accounts):
    w3 = local_node_eth.w3
    block = 19917381
    local_node_eth.set_block(block)

    avatar_safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_contract = deploy_roles(avatar=avatar_safe.address, w3=w3)
    setup_common_roles(avatar_safe, roles_contract)
    blockchain = Chain.get_blockchain_from_web3(w3)
    presets = """{"version": "1.0","chainId": "1","meta":{ "description": "","txBuilderVersion": "1.8.0"},"createdAt": 1695904723785,"transactions": [
        {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
        "data": "0x5e826695000000000000000000000000000000000000000000000000000000000000000400000000000000000000000083F20F44975D03b1b09e64809B757c47f942BEeA",
        "value": "0"},
        {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
        "data": "0x2fcf52d1000000000000000000000000000000000000000000000000000000000000000400000000000000000000000083F20F44975D03b1b09e64809B757c47f942BEeAba087652000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "value": "0"},
        {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
        "data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000004000000000000000000000000d758500ddec05172aaa035911387c8e0e789cf6a",
        "value": "0"},
        {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86",
        "data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000004000000000000000000000000d758500ddec05172aaa035911387c8e0e789cf6a1cff79cd000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "value": "0"}
    ]}"""

    apply_presets(
        avatar_safe,
        roles_contract,
        json_data=presets,
        replaces=[
            ("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", avatar_safe.address[2:])
        ],
    )
    DAIER = "0xfE9fE2eF61faF6E291b06903dFf85DF25a989498"
    steal_token(w3, ETHAddr.DAI, holder=DAIER, to=avatar_safe.address, amount=1_000)
    # Deposit DAI, get sDAI
    avatar_safe.send(
        [
            spark.ApproveDAIforSDAI(amount=1_000),
            spark.DepositDAIforSDAI(blockchain=blockchain, amount=1_000, avatar=avatar_safe.address)
        ]
    )
    assert get_balance(w3, ETHAddr.DAI, avatar_safe.address) == 0
    chi = SparkUtils.get_chi(w3)
    assert get_balance(w3, ETHAddr.sDAI, avatar_safe.address) == int(Decimal(1_000) / (Decimal(chi) / Decimal(1e27)))  # 976

    avatar_safe_address = avatar_safe.address
    disassembler_address = accounts[4].address
    private_key = accounts[4].key
    role = 4

    dsr_disassembler = SparkDisassembler(
        w3=w3,
        avatar_safe_address=avatar_safe_address,
        roles_mod_address=roles_contract.address,
        role=role,
        signer_address=disassembler_address,
    )

    txn_transactable = dsr_disassembler.exit_1(percentage=50)
    dsr_disassembler.send(txn_transactable, private_key=private_key)

    assert get_balance(w3, ETHAddr.sDAI, avatar_safe.address) == 461
