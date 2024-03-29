import math
from datetime import datetime

from defi_protocols.Balancer import VAULT
from defi_protocols.constants import XDAI, ZERO_ADDRESS
from defi_protocols.functions import get_contract, get_node, last_block
from web3 import HTTPProvider, Web3

from tests.utils import LOCAL_NODE_PORT, fork_reset_state, fork_unlock_account, get_allowance

BALANCER_QUERIES = "0x0F3e0c4218b7b0108a3643cFe9D3ec0d4F57c54e"

ABI_VAULT = '[{"inputs":[{"internalType":"enum IVault.SwapKind","name":"kind","type":"uint8"},{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"uint256","name":"assetInIndex","type":"uint256"},{"internalType":"uint256","name":"assetOutIndex","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"internalType":"struct IVault.BatchSwapStep[]","name":"swaps","type":"tuple[]"},{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.FundManagement","name":"funds","type":"tuple"},{"internalType":"int256[]","name":"limits","type":"int256[]"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"batchSwap","outputs":[{"internalType":"int256[]","name":"assetDeltas","type":"int256[]"}],"stateMutability":"payable","type":"function"}]'

# ABI Balancer Queries - queryExit, queryJoin, querySwap, queryBatchSwap
ABI_BALANCER_QUERIES = '[{"inputs":[{"internalType":"contract IVault","name":"_vault","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"enum IVault.SwapKind","name":"kind","type":"uint8"},{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"uint256","name":"assetInIndex","type":"uint256"},{"internalType":"uint256","name":"assetOutIndex","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"internalType":"struct IVault.BatchSwapStep[]","name":"swaps","type":"tuple[]"},{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.FundManagement","name":"funds","type":"tuple"}],"name":"queryBatchSwap","outputs":[{"internalType":"int256[]","name":"assetDeltas","type":"int256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"minAmountsOut","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.ExitPoolRequest","name":"request","type":"tuple"}],"name":"queryExit","outputs":[{"internalType":"uint256","name":"bptIn","type":"uint256"},{"internalType":"uint256[]","name":"amountsOut","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"maxAmountsIn","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"}],"internalType":"struct IVault.JoinPoolRequest","name":"request","type":"tuple"}],"name":"queryJoin","outputs":[{"internalType":"uint256","name":"bptOut","type":"uint256"},{"internalType":"uint256[]","name":"amountsIn","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"enum IVault.SwapKind","name":"kind","type":"uint8"},{"internalType":"contract IAsset","name":"assetIn","type":"address"},{"internalType":"contract IAsset","name":"assetOut","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"internalType":"struct IVault.SingleSwap","name":"singleSwap","type":"tuple"},{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.FundManagement","name":"funds","type":"tuple"}],"name":"querySwap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"vault","outputs":[{"internalType":"contract IVault","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'

SAFE_ADDRESS = "0x51D34416593a8acF4127dc4a40625A8eFAB9940c"

EURe = "0xcB444e90D8198415266c6a2724b7900fb12FC56E"
EURe_ABI = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes3","name":"ticker","type":"bytes3"},{"indexed":true,"internalType":"address","name":"old","type":"address"},{"indexed":true,"internalType":"address","name":"current","type":"address"}],"name":"Controller","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"}],"name":"OwnershipRenounced","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"data","type":"bytes"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"stateMutability":"nonpayable","type":"fallback"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PREDICATE_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"who","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes32","name":"h","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"burnFrom","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"claimOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getController","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mintTo","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_contractAddr","type":"address"}],"name":"reclaimContract","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"reclaimEther","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract ERC20Basic","name":"_token","type":"address"}],"name":"reclaimToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes32","name":"h","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"recover","outputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"renounceRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"address_","type":"address"}],"name":"setController","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"ticker","outputs":[{"internalType":"bytes3","name":"","type":"bytes3"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_from","type":"address"},{"internalType":"uint256","name":"_value","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"tokenFallback","outputs":[],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"transferAndCall","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

bb_ag_USD = "0xFEdb19Ec000d38d92Af4B21436870F115db22725"
bb_ag_WXDAI = "0x41211BBa6d37F5a74b22e667533F080C7C7f3F13"

WXDAI = "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"
WXDAI_ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'

EURe_bb_ag_USD_POOL_ID = "0xa611a551b95b205ccd9490657acf7899daee5db700000000000000000000002e"
bb_ag_USD_POOL_ID = "0xfedb19ec000d38d92af4b21436870f115db22725000000000000000000000010"
bb_ag_WXDAI_POOL_ID = "0x41211bba6d37f5a74b22e667533f080c7c7f3f1300000000000000000000000b"

decimalsEURe = 18
decimalsWXDAI = 18

SLIPPAGE = "0.1"


def get_EURe_to_USD_balancer(amount):
    web3 = get_node(XDAI)

    amount = int(amount * 10**decimalsEURe)

    batch_swap_steps = []

    swap_kind = 0  # 0 = "Out Given Exact In" or 1 = "In Given Exact Out"
    user_data = "0x"

    # Step 1: Swap EURe for bb-ag-USD
    index_asset_in = 0
    index_asset_out = 1
    batch_swap_steps.append([EURe_bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, amount, user_data])

    # Step 2: Swap bb-ag-USD for bb-ag-WXDAI
    index_asset_in = 1
    index_asset_out = 2
    batch_swap_steps.append([bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Step 3: Swap bb-ag-WXDAI for WXDAI
    index_asset_in = 2
    index_asset_out = 3
    batch_swap_steps.append([bb_ag_WXDAI_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Assets
    assets = [EURe, bb_ag_USD, bb_ag_WXDAI, WXDAI]

    # FundsManagement
    funds_management = [SAFE_ADDRESS, False, SAFE_ADDRESS, False]

    balancer_queries = get_contract(BALANCER_QUERIES, XDAI, web3=web3, abi=ABI_BALANCER_QUERIES)

    # try:
    swap = balancer_queries.functions.queryBatchSwap(int(swap_kind), batch_swap_steps, assets, funds_management).call()

    amount_out = abs(swap[3]) / 10**decimalsEURe

    return amount_out


def get_USD_to_EURe_balancer(amount):
    web3 = get_node(XDAI)

    amount = int(amount * 10**decimalsWXDAI)

    batch_swap_steps = []

    swap_kind = 0  # 0 = "Out Given Exact In" or 1 = "In Given Exact Out"
    user_data = "0x"

    # Step 1: Swap WXDAI for bb-ag-WXDAI
    index_asset_in = 0
    index_asset_out = 1
    batch_swap_steps.append([bb_ag_WXDAI_POOL_ID, index_asset_in, index_asset_out, amount, user_data])

    # Step 2: Swap bb-ag-WXDAI for bb-ag-USD
    index_asset_in = 1
    index_asset_out = 2
    batch_swap_steps.append([bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Step 1: Swap bb-ag-USD for EURe
    index_asset_in = 2
    index_asset_out = 3
    batch_swap_steps.append([EURe_bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Assets
    assets = [WXDAI, bb_ag_WXDAI, bb_ag_USD, EURe]

    # FundsManagement
    funds_management = [SAFE_ADDRESS, False, SAFE_ADDRESS, False]

    balancer_queries = get_contract(BALANCER_QUERIES, XDAI, web3=web3, abi=ABI_BALANCER_QUERIES)

    # try:
    swap = balancer_queries.functions.queryBatchSwap(int(swap_kind), batch_swap_steps, assets, funds_management).call()

    amount_out = abs(swap[0]) / 10**decimalsWXDAI

    return amount_out


def swap_EURe_for_WXDAI_balancer(amount):
    block = last_block(XDAI)

    web3 = Web3(HTTPProvider(f"http://localhost:{LOCAL_NODE_PORT}"))
    fork_reset_state(web3, url="https://rpc.gnosischain.com/", block=block)
    fork_unlock_account(web3, SAFE_ADDRESS)

    EURe_contract = web3.eth.contract(address=EURe, abi=EURe_ABI)
    balance = EURe_contract.functions.balanceOf(SAFE_ADDRESS).call()
    if balance < amount * (10**decimalsEURe):
        raise ValueError("Not enough EURe to swap. Current EURe balance: %.3f." % (balance / (10**decimalsEURe)))
    vault = web3.eth.contract(address=VAULT, abi=ABI_VAULT)
    amount_int = int(amount * (10**decimalsEURe))
    if amount_int == 0:
        raise ValueError("Amount to swap is too small. Amount of EURe to swap: %f." % (amount * (10**decimalsEURe)))

    amount_out = get_EURe_to_USD_balancer(amount)
    min_amount_out = ((1 - float(SLIPPAGE)) * amount_out) * -1

    batch_swap_steps = []

    swap_kind = 0  # 0 = "Out Given Exact In" or 1 = "In Given Exact Out"
    user_data = "0x"

    # Step 1: Swap EURe for bb-ag-USD
    index_asset_in = 0
    index_asset_out = 1
    batch_swap_steps.append([EURe_bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, amount_int, user_data])

    # Step 2: Swap bb-ag-USD for bb-ag-WXDAI
    index_asset_in = 1
    index_asset_out = 2
    batch_swap_steps.append([bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Step 3: Swap bb-ag-WXDAI for WXDAI
    index_asset_in = 2
    index_asset_out = 3
    batch_swap_steps.append([bb_ag_WXDAI_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Assets
    assets = [EURe, bb_ag_USD, bb_ag_WXDAI, WXDAI]

    # FundsManagement
    funds_management = [SAFE_ADDRESS, False, SAFE_ADDRESS, False]

    # Limits
    limits = [int(amount * (10**decimalsEURe)), 0, 0, int(min_amount_out * (10**decimalsWXDAI))]

    # Deadline
    deadline = math.floor(datetime.now().timestamp() + 1800)

    EURe_contract.functions.approve(VAULT, amount_int).transact({"from": SAFE_ADDRESS})
    allowance = get_allowance(web3, EURe, SAFE_ADDRESS, VAULT)
    tx = vault.functions.batchSwap(swap_kind, batch_swap_steps, assets, funds_management, limits, deadline).transact(
        {"from": SAFE_ADDRESS}
    )
    while True:
        try:
            txn_receipt = web3.eth.get_transaction_receipt(tx.hex())
            break
        except:
            pass

    logs = txn_receipt.logs
    amount_received = 0
    if txn_receipt is not None:
        for element in logs:
            if element["topics"] == [
                bytes.fromhex("ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"),
                bytes.fromhex("000000000000000000000000ba12222222228d8ba445958a75a0704d566bf2c8"),
                bytes.fromhex("00000000000000000000000051d34416593a8acf4127dc4a40625a8efab9940c"),
            ]:
                amount_received = int(element["data"].hex(), base=16) / (10**decimalsWXDAI)
        if txn_receipt.status == 1 and amount_received != 0:
            msg = "%.2f EURe was swapped for %.2f WXDAI" % (amount, amount_received)
        else:
            msg = "Failed to swap %.2f EURe" % amount
        return msg + "." + txn_receipt["transactionHash"].hex()
    else:
        msg = "Failed to swap %.2f EURe" % amount
        return msg


def swap_WXDAI_for_EURe_balancer(amount):
    block = last_block(XDAI)

    web3 = Web3(HTTPProvider(f"http://localhost:{LOCAL_NODE_PORT}"))
    fork_reset_state(web3, url="https://rpc.gnosischain.com/", block=block)
    fork_unlock_account(web3, SAFE_ADDRESS)

    WXDAI_contract = web3.eth.contract(address=WXDAI, abi=WXDAI_ABI)
    balance = WXDAI_contract.functions.balanceOf(SAFE_ADDRESS).call()
    if balance < amount * (10**decimalsWXDAI):
        raise ValueError("Not enough WXDAI to swap. Current WXDAI balance: %.3f." % (balance / (10**decimalsWXDAI)))
    vault = web3.eth.contract(address=VAULT, abi=ABI_VAULT)
    amount_int = int(amount * (10**decimalsWXDAI))
    if amount_int == 0:
        raise ValueError("Amount to swap is too small. Amount of WXDAI to swap: %f." % amount)

    amount_out = get_USD_to_EURe_balancer(amount)
    min_amount_out = ((1 - float(SLIPPAGE)) * amount_out) * -1

    batch_swap_steps = []

    swap_kind = 0  # 0 = "Out Given Exact In" or 1 = "In Given Exact Out"
    user_data = "0x"

    # Step 1: Swap WXDAI for bb-ag-WXDAI
    index_asset_in = 0
    index_asset_out = 1
    batch_swap_steps.append([bb_ag_WXDAI_POOL_ID, index_asset_in, index_asset_out, amount_int, user_data])

    # Step 2: Swap bb-ag-WXDAI for bb-ag-USD
    index_asset_in = 1
    index_asset_out = 2
    batch_swap_steps.append([bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Step 3: Swap bb-ag-USD for EURe
    index_asset_in = 2
    index_asset_out = 3
    batch_swap_steps.append([EURe_bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Assets
    assets = [WXDAI, bb_ag_WXDAI, bb_ag_USD, EURe]

    # FundsManagement
    funds_management = [SAFE_ADDRESS, False, SAFE_ADDRESS, False]

    # Limits
    limits = [int(amount * (10**decimalsWXDAI)), 0, 0, int(min_amount_out * (10**decimalsEURe))]

    # Deadline
    deadline = math.floor(datetime.now().timestamp() + 1800)

    WXDAI_contract.functions.approve(VAULT, amount_int).transact({"from": SAFE_ADDRESS})
    allowance = get_allowance(web3, WXDAI, SAFE_ADDRESS, VAULT)
    tx = vault.functions.batchSwap(swap_kind, batch_swap_steps, assets, funds_management, limits, deadline).transact(
        {"from": SAFE_ADDRESS}
    )
    while True:
        try:
            txn_receipt = web3.eth.get_transaction_receipt(tx.hex())
            break
        except:
            pass

    logs = txn_receipt.logs
    amount_received = 0
    if txn_receipt is not None:
        for element in logs:
            if element["topics"] == [
                bytes.fromhex("ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"),
                bytes.fromhex("000000000000000000000000ba12222222228d8ba445958a75a0704d566bf2c8"),
                bytes.fromhex("00000000000000000000000051d34416593a8acf4127dc4a40625a8efab9940c"),
            ]:
                amount_received = int(element["data"].hex(), base=16) / (10**decimalsWXDAI)
        if txn_receipt.status == 1 and amount_received != 0:
            msg = "%.2f WXDAI was swapped for %.2f EURe" % (amount, amount_received)
        else:
            msg = "Failed to swap %.2f WXDAI" % amount
        return msg + "." + txn_receipt["transactionHash"].hex()
    else:
        msg = "Failed to swap %.2f WXDAI" % amount
        return msg


print(swap_EURe_for_WXDAI_balancer(1))
print(swap_WXDAI_for_EURe_balancer(1))
