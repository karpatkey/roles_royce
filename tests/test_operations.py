from rolling_roles import check, send, GenericMethodTransaction, Operation, Chain
from .utils import web3_gnosis, web3_eth

approve = GenericMethodTransaction(
    function_name="approve",
    function_args=["0x7f90122BF0700F9E7e1F688fe926940E8839F353", 1000],
    contract_address="0x4ECaBa5870353805a9F068101A40E0f32ed605C6",
    contract_abi='[{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve",'
                 '"outputs":[{"name":"result","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]',
    operation=Operation.CALL,
    value=0,
)
add_liquidity = GenericMethodTransaction(
    function_name="add_liquidity",
    function_args=[[0, 0, 100], 0],
    contract_address="0x7f90122bf0700f9e7e1f688fe926940e8839f353",
    contract_abi='[{"stateMutability":"nonpayable","type":"function","name":"add_liquidity","inputs":[{"name":"_amounts","type":"uint256[3]"},'
                 '{"name":"_min_mint_amount","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}],"gas":7295966}]',
    operation=Operation.CALL,
    value=0,
)


def test_check_one(web3_gnosis):
    ROLES_MOD_ADDRESS = "0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503"
    ACCOUNT = "0x7e19DE37A31E40eec58977CEA36ef7fB70e2c5CD"
    status = check(txs=[approve], role=2, account=ACCOUNT, roles_mod_address=ROLES_MOD_ADDRESS,
                   web3=web3_gnosis, blockchain=Chain.GNOSIS)
    assert status


def test_check_multi(web3_gnosis):
    ROLES_MOD_ADDRESS = "0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503"
    ACCOUNT = "0x7e19DE37A31E40eec58977CEA36ef7fB70e2c5CD"
    status = check(txs=[approve, add_liquidity], role=2, account=ACCOUNT, roles_mod_address=ROLES_MOD_ADDRESS,
                   web3=web3_gnosis, blockchain=Chain.GNOSIS)
    assert status

def test_aave_approve(web3_eth):
    from rolling_roles.protocols.eth.aave import ApproveForAaveLendingPoolV2
    USDT_CONTRACT = '0x4ECaBa5870353805a9F068101A40E0f32ed605C6'
    approve = ApproveForAaveLendingPoolV2(token=USDT_CONTRACT, amount=123)
    ROLES_MOD_ADDRESS = "0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503"
    ACCOUNT = "0x7e19DE37A31E40eec58977CEA36ef7fB70e2c5CD"
    status = check(txs=[approve], role=2, account=ACCOUNT, roles_mod_address=ROLES_MOD_ADDRESS,
                   web3=web3_eth, blockchain=Chain.ETHEREUM)
    assert status