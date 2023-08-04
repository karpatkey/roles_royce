import pytest
from roles_royce import check, send, GenericMethodTransaction, Operation, Chain
from roles_royce.constants import GCAddr, CrossChainAddr
from roles_royce.utils import multi_or_one, MULTISENDS
from .utils import web3_gnosis, web3_eth

POOLID = "0xf48f01dcb2cbb3ee1f6aab0e742c2d3941039d56000200000000000000000012"
ROLES_MOD_ADDRESS = "0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503"
ACCOUNT = "0x7e19DE37A31E40eec58977CEA36ef7fB70e2c5CD"
ASSETS = ["0xbb9Cd48d33033F5EfFBeDec9Dd700C7D7E1dCF50","0xFFFf76A3280e95dC855696111C2562Da09db2Ac0"]
AMOUNTS_IN = [160092885394460,0]
LP_TOKEN = "0xF48f01DCB2CbB3ee1f6AaB0e742c2D3941039d56"
USER_DATA = '0x000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000002451b940a5dbe00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000919a8790a41c0000000000000000000000000000000000000000000000000000000000000000'
INTERNAL_BALANCE = False

# joinPool = GenericMethodTransaction(
#     function_name="joinPool",
#     function_args=[POOLID,ROLES_MOD_ADDRESS,ROLES_MOD_ADDRESS,(ASSETS,AMOUNTS_IN,USER_DATA,INTERNAL_BALANCE)],
#     contract_address=CrossChainAddr.BalancerVault,
#     contract_abi='[{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},'
#                     '{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},'
#                     '{"internalType":"uint256[]","name":"maxAmountsIn","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},'
#                     '{"internalType":"bool","name":"fromInternalBalance","type":"bool"}],"internalType":"struct IVault.JoinPoolRequest","name":"request","type":"tuple"}],'
#                     '"name":"joinPool","outputs":[],"stateMutability":"payable","type":"function"}]',
#     operation=Operation.CALL,
#     value=0,
# )
getPool = GenericMethodTransaction(
    function_name="getPool",
    function_args=[POOLID],
    contract_address=CrossChainAddr.BalancerVault,
    contract_abi='[{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"}],"name":"getPool","outputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"enum IVault.PoolSpecialization","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}]',
    operation=Operation.CALL,
    value=0,
)

@pytest.mark.xfail(reason='still WIP')
def test_check_multi(web3_gnosis):
    status = check(txs=[getPool], role=2, account=ACCOUNT, roles_mod_address=ROLES_MOD_ADDRESS,
                   web3=web3_gnosis)
    assert status