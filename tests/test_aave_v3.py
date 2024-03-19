from decimal import Decimal

from defabipedia._1inch import ContractSpecs as _1inchContractSpecs
from defabipedia.aave_v3 import ContractSpecs
from defabipedia.spark import ContractSpecs as SparkContractSpecs
from defabipedia.tokens import Abis as TokenAbis
from defabipedia.types import Chain
from eth_abi import encode
from pytest import approx

from roles_royce.constants import ETHAddr
from roles_royce.protocols.eth import aave_v3
from roles_royce.toolshed.protocol_utils.aave_v3.cdp import AaveV3CDPManager, CDPData

from .utils import get_balance, local_node_eth

USER = "0xDf3A7a27704196Af5149CD67D881279e32AF2C21"
USER2 = "0x7420fA58bA44E1141d5E9ADB6903BE549f7cE0b5"
GNOSIS_DAO = "0x849D52316331967b6fF1198e5E32A0eB168D039d"

# -----------------------------------------------------#
"""Unit Tests"""


# -----------------------------------------------------#
def test_approve_token():
    method = aave_v3.ApproveToken(token=ETHAddr.WETH, amount=123)
    assert (
        method.data
        == "0x095ea7b300000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_approve_AEthWETH():
    method = aave_v3.ApproveAEthWETH(amount=123)
    assert (
        method.data
        == "0x095ea7b300000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].aEthWETH.address


def test_approve_stkAAVE():
    method = aave_v3.ApproveForStkAAVE(amount=123)
    assert (
        method.data
        == "0x095ea7b30000000000000000000000004da27a545c0c5b758a6ba100e3a049001de870f5000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].AAVE.address


def test_approve_stkABPT():
    method = aave_v3.ApproveForStkABPT(amount=123)
    assert (
        method.data
        == "0x095ea7b3000000000000000000000000a1116930326d21fb917d5a27f1e9943a9595fb47000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].ABPT.address


def test_approve_delegation():
    method = aave_v3.ApproveDelegation(target=ContractSpecs[Chain.ETHEREUM].variableDebtWETH.address, amount=123)
    assert (
        method.data
        == "0xc04a8a10000000000000000000000000d322a49006fc828f9b5b37ab215f99b4e5cab19c000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert method.contract_address == "0xeA51d7853EEFb32b6ee06b1C12E6dcCA88Be0fFE"


def test_deposit_token():
    method = aave_v3.DepositToken(asset=ETHAddr.WETH, amount=123, avatar=GNOSIS_DAO)
    assert (
        method.data
        == "0x617ba037000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000000"
    )


def test_withdraw_token():
    method = aave_v3.WithdrawToken(asset=ETHAddr.WETH, amount=123, avatar=GNOSIS_DAO)
    assert (
        method.data
        == "0x69328dec000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
    )


def test_deposit_ETH():
    method = aave_v3.DepositETH(eth_amount=123, avatar=GNOSIS_DAO)
    assert (
        method.data
        == "0x474cf53d00000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000000"
    )


def test_withdraw_ETH():
    method = aave_v3.WithdrawETH(amount=123, avatar=GNOSIS_DAO)
    assert (
        method.data
        == "0x80500d2000000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
    )


def test_collateralize():
    method = aave_v3.Collateralize(asset=ETHAddr.WETH, use_as_collateral=True)
    assert (
        method.data
        == "0x5a3b74b9000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000001"
    )


def test_borrow():
    method = aave_v3.Borrow(
        asset=ETHAddr.WETH, amount=123, interest_rate_mode=aave_v3.InterestRateMode.VARIABLE, avatar=GNOSIS_DAO
    )
    assert (
        method.data
        == "0xa415bcad000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
    )


def test_repay():
    method = aave_v3.Repay(
        asset=ETHAddr.WETH, amount=123, interest_rate_mode=aave_v3.InterestRateMode.VARIABLE, avatar=GNOSIS_DAO
    )
    assert (
        method.data
        == "0x573ade81000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
    )


def test_borrow_ETH():
    method = aave_v3.BorrowETH(amount=123, interest_rate_mode=aave_v3.InterestRateMode.VARIABLE)
    assert (
        method.data
        == "0x66514c9700000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000000000000000000000000000000000000000007b00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000"
    )


def test_repay_ETH():
    method = aave_v3.RepayETH(eth_amount=123, interest_rate_mode=aave_v3.InterestRateMode.VARIABLE, avatar=GNOSIS_DAO)
    assert (
        method.data
        == "0x02c5fcf800000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d"
    )


def test_swap_borrow_rate_mode():
    method = aave_v3.SwapBorrowRateMode(asset=ETHAddr.WETH, interest_rate_mode=aave_v3.InterestRateMode.VARIABLE)
    assert (
        method.data
        == "0x94ba89a2000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000002"
    )


def test_stake_AAVE():
    method = aave_v3.StakeAAVE(avatar=GNOSIS_DAO, amount=123)
    assert (
        method.data
        == "0xadc9772e000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].stkAAVE.address


def test_stake_ABPT():
    method = aave_v3.StakeABPT(avatar=GNOSIS_DAO, amount=123)
    assert (
        method.data
        == "0xadc9772e000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].stkABPT.address


def test_claim_rewards_and_stake():
    method = aave_v3.ClaimRewardsAndStake(avatar=GNOSIS_DAO, amount=123)
    assert (
        method.data
        == "0x955e18af000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_unstake_AAVE():
    method = aave_v3.UnstakeAAVE(avatar=GNOSIS_DAO, amount=123)
    assert (
        method.data
        == "0x1e9a6950000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].stkAAVE.address


def test_unstake_ABPT():
    method = aave_v3.UnstakeABPT(avatar=GNOSIS_DAO, amount=123)
    assert (
        method.data
        == "0x1e9a6950000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].stkABPT.address


def test_cooldown_stkAAVE():
    method = aave_v3.CooldownStkAAVE(value=123, avatar=GNOSIS_DAO)
    assert method.data == "0x787a08a6"
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].stkAAVE.address


def test_cooldown_stkABPT():
    method = aave_v3.CooldownStkABPT(value=123, avatar=GNOSIS_DAO)
    assert method.data == "0x787a08a6"
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].stkABPT.address


def test_claim_AAVE_rewards():
    method = aave_v3.ClaimAAVERewards(avatar=GNOSIS_DAO, amount=123)
    assert (
        method.data
        == "0x9a99b4f0000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].stkAAVE.address


def test_claim_ABPT_rewards():
    method = aave_v3.ClaimABPTRewards(avatar=GNOSIS_DAO, amount=123)
    assert (
        method.data
        == "0x9a99b4f0000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].stkABPT.address


def test_swap_and_repay():
    method = aave_v3.SwapAndRepay(
        collateral_asset=ETHAddr.USDC,
        debt_asset=ETHAddr.WETH,
        collateral_amount=123,
        debt_repay_amount=123,
        debt_rate_mode=aave_v3.InterestRateMode.VARIABLE,
        buy_all_balance_offset=0,
        calldata="0x0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000000004842298207a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca0000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000562c9b4164b58103000000000000000000000000000000000000000000000000000000028fa6ae0000000000000000000000000000000000000000000000000056169161cebe049800000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000000022000000000000000000000000000000000000000000000000000000000000003a0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009abf798f5314bfd793a9e57a654bed35af4a1d600100000000000000000000000000000000000000000000000000000000031388000000000000000000000000000000000000000000000000000000000000044000000000000000000000000000000000000000000000000000000000652742c577e189f1a03f43afae287d193069d849000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000e592427a0aece92de3edee1f18e0157c058615640000000000000000000000000000000000000000000000000000000000000144f28c0498000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000653028e4000000000000000000000000000000000000000000000000000000028fa6ae00000000000000000000000000000000000000000000000000562c9b4164b581010000000000000000000000000000000000000000000000000000000000000042a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480001f4c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000647f39c581f595b53c5cb19bd0b3f8da6c935e2ca00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        permit_amount=123,
        permit_deadline=1697053784,
        permit_v=27,
        permit_r="0xf63fe2ddf43a364fb088ca5fbabc1928b6bbf11b35aec8502907902baf240935",
        permit_s="0x3e452b86b67a5c5ce46fdc83c1e23db730f7e2b9aa1d12ab25faf581be38140b",
    )
    assert (
        method.data
        == "0x4db9dc97000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000006526fc58000000000000000000000000000000000000000000000000000000000000001bf63fe2ddf43a364fb088ca5fbabc1928b6bbf11b35aec8502907902baf2409353e452b86b67a5c5ce46fdc83c1e23db730f7e2b9aa1d12ab25faf581be38140b00000000000000000000000000000000000000000000000000000000000005000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000000004842298207a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca0000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000562c9b4164b58103000000000000000000000000000000000000000000000000000000028fa6ae0000000000000000000000000000000000000000000000000056169161cebe049800000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000000022000000000000000000000000000000000000000000000000000000000000003a0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009abf798f5314bfd793a9e57a654bed35af4a1d600100000000000000000000000000000000000000000000000000000000031388000000000000000000000000000000000000000000000000000000000000044000000000000000000000000000000000000000000000000000000000652742c577e189f1a03f43afae287d193069d849000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000e592427a0aece92de3edee1f18e0157c058615640000000000000000000000000000000000000000000000000000000000000144f28c0498000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000653028e4000000000000000000000000000000000000000000000000000000028fa6ae00000000000000000000000000000000000000000000000000562c9b4164b581010000000000000000000000000000000000000000000000000000000000000042a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480001f4c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000647f39c581f595b53c5cb19bd0b3f8da6c935e2ca00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].ParaSwapRepayAdapter.address


def test_swap_and_deposit():
    method = aave_v3.SwapAndDeposit(
        from_asset=ETHAddr.USDC,
        to_asset=ETHAddr.WETH,
        amount=123,
        min_amount_to_receive=123,
        swap_all_balance_offset=aave_v3.InterestRateMode.VARIABLE,
        calldata="0x0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000000004842298207a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca0000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000562c9b4164b58103000000000000000000000000000000000000000000000000000000028fa6ae0000000000000000000000000000000000000000000000000056169161cebe049800000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000000022000000000000000000000000000000000000000000000000000000000000003a0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009abf798f5314bfd793a9e57a654bed35af4a1d600100000000000000000000000000000000000000000000000000000000031388000000000000000000000000000000000000000000000000000000000000044000000000000000000000000000000000000000000000000000000000652742c577e189f1a03f43afae287d193069d849000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000e592427a0aece92de3edee1f18e0157c058615640000000000000000000000000000000000000000000000000000000000000144f28c0498000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000653028e4000000000000000000000000000000000000000000000000000000028fa6ae00000000000000000000000000000000000000000000000000562c9b4164b581010000000000000000000000000000000000000000000000000000000000000042a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480001f4c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000647f39c581f595b53c5cb19bd0b3f8da6c935e2ca00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        augustus="0xDEF171Fe48CF0115B1d80b88dc8eAB59176FEe57",
        permit_amount=123,
        permit_deadline=1697053784,
        permit_v=27,
        permit_r="0xf63fe2ddf43a364fb088ca5fbabc1928b6bbf11b35aec8502907902baf240935",
        permit_s="0x3e452b86b67a5c5ce46fdc83c1e23db730f7e2b9aa1d12ab25faf581be38140b",
    )
    assert (
        method.data
        == "0xd3454a35000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000000000007b00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000180000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee57000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000006526fc58000000000000000000000000000000000000000000000000000000000000001bf63fe2ddf43a364fb088ca5fbabc1928b6bbf11b35aec8502907902baf2409353e452b86b67a5c5ce46fdc83c1e23db730f7e2b9aa1d12ab25faf581be38140b00000000000000000000000000000000000000000000000000000000000005000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000000004842298207a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca0000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000562c9b4164b58103000000000000000000000000000000000000000000000000000000028fa6ae0000000000000000000000000000000000000000000000000056169161cebe049800000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000000022000000000000000000000000000000000000000000000000000000000000003a0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009abf798f5314bfd793a9e57a654bed35af4a1d600100000000000000000000000000000000000000000000000000000000031388000000000000000000000000000000000000000000000000000000000000044000000000000000000000000000000000000000000000000000000000652742c577e189f1a03f43afae287d193069d849000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000e592427a0aece92de3edee1f18e0157c058615640000000000000000000000000000000000000000000000000000000000000144f28c0498000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000653028e4000000000000000000000000000000000000000000000000000000028fa6ae00000000000000000000000000000000000000000000000000562c9b4164b581010000000000000000000000000000000000000000000000000000000000000042a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480001f4c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000647f39c581f595b53c5cb19bd0b3f8da6c935e2ca00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].ParaSwapLiquidityAdapter.address


def test_delegate_AAVE():
    method = aave_v3.DelegateAAVE(delegatee=USER)
    assert method.data == "0x5c19a95c000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c21"
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].AAVE.address


def test_delegate_AAVE_by_type():
    method = aave_v3.DelegateAAVEByType(delegatee=USER, delegation_type=aave_v3.DelegationType.VOTING)
    assert (
        method.data
        == "0xdc937e1c000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c210000000000000000000000000000000000000000000000000000000000000000"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].AAVE.address


def test_delegate_stkAAVE():
    method = aave_v3.DelegatestkAAVE(delegatee=USER)
    assert method.data == "0x5c19a95c000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c21"
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].stkAAVE.address


def test_delegate_stkAAVE_by_type():
    method = aave_v3.DelegatestkAAVEByType(delegatee=USER, delegation_type=aave_v3.DelegationType.VOTING)
    assert (
        method.data
        == "0xdc937e1c000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c210000000000000000000000000000000000000000000000000000000000000000"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].stkAAVE.address


def test_submit_vote():
    method = aave_v3.SubmitVote(proposal_id=123, support=True)
    assert (
        method.data
        == "0x612c56fa000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000001"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].GovernanceV2.address


def test_liquidation_call():
    method = aave_v3.LiquidationCall(
        collateral_asset=ETHAddr.WETH, debt_asset=ETHAddr.USDC, user=USER, debt_to_cover=123, receive_a_token=False
    )
    assert (
        method.data
        == "0x00a718a9000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c21000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000000"
    )
    assert method.contract_address == ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address


CLOSE_FACTOR_HF_THRESHOLD = 0.95
DEFAULT_LIQUIDATION_CLOSE_FACTOR = 0.5
MAX_LIQUIDATION_CLOSE_FACTOR = 1

# -----------------------------------------------------#
"""Integration Tests"""
# -----------------------------------------------------#


def test_integration_liquidation_call(local_node_eth):
    w3 = local_node_eth.w3
    block = 18430238
    local_node_eth.set_block(block)

    cdp = AaveV3CDPManager(w3=w3, owner_address=USER)

    balances = cdp.get_cdp_balances_data(block=block)
    health_factor = cdp.get_health_factor(block=block)
    assert health_factor < Decimal("1")

    asset_to_liquidate = ETHAddr.USDC
    asset_to_liquidate_contract = w3.eth.contract(address=asset_to_liquidate, abi=TokenAbis.ERC20.abi)
    asset_to_pay_debt = ETHAddr.wstETH
    asset_to_pay_debt_contract = w3.eth.contract(address=asset_to_pay_debt, abi=TokenAbis.ERC20.abi)

    pdp = w3.eth.contract(
        address=ContractSpecs[Chain.ETHEREUM].ProtocolDataProvider.address,
        abi=ContractSpecs[Chain.ETHEREUM].ProtocolDataProvider.abi,
    )
    liquidation_bonus = Decimal(
        pdp.functions.getReserveConfigurationData(asset_to_liquidate).call(block_identifier=block)[3] / 10000
    )
    assert liquidation_bonus == approx(1.045)
    liquidation_protocol_fee = Decimal(
        pdp.functions.getLiquidationProtocolFee(asset_to_liquidate).call(block_identifier=block) / 10000
    )
    assert liquidation_protocol_fee == approx(0.2)

    collateral_usd = 0
    debt_usd = 0
    asset_to_liquidate_data = {}
    asset_to_pay_debt_data = {}
    for balance in balances:
        if balance[CDPData.CollateralEnabled]:
            collateral_usd += (
                balance[CDPData.InterestBearingBalance]
                * balance[CDPData.UnderlyingPriceUSD]
                * balance[CDPData.LiquidationThreshold]
            )

        debt_usd += (balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]) * balance[
            CDPData.UnderlyingPriceUSD
        ]

        if balance[CDPData.UnderlyingAddress] == asset_to_liquidate:
            asset_to_liquidate_data["amount"] = Decimal(balance[CDPData.InterestBearingBalance])
            asset_to_liquidate_data["price"] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_liquidate_data["decimals"] = asset_to_liquidate_contract.functions.decimals().call()
        elif balance[CDPData.UnderlyingAddress] == asset_to_pay_debt:
            asset_to_pay_debt_data["amount"] = Decimal(
                balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]
            )
            asset_to_pay_debt_data["price"] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_pay_debt_data["decimals"] = asset_to_pay_debt_contract.functions.decimals().call()

    # Address with lots of wstETH
    wallet = "0x5313b39bf226ced2332C81eB97BB28c6fD50d1a3"
    local_node_eth.unlock_account(wallet)

    if health_factor < 1 and health_factor > CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = DEFAULT_LIQUIDATION_CLOSE_FACTOR
    elif health_factor < CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = MAX_LIQUIDATION_CLOSE_FACTOR

    debt_to_cover_no_decimals = asset_to_pay_debt_data["amount"] * Decimal(close_factor)
    assert debt_to_cover_no_decimals == Decimal("0.2411476123882345670")
    max_amount_collateral_to_liquidate = (
        asset_to_pay_debt_data["price"]
        * debt_to_cover_no_decimals
        * liquidation_bonus
        / asset_to_liquidate_data["price"]
    )
    assert max_amount_collateral_to_liquidate == Decimal("515.5563674588096668427157459")
    bonus = max_amount_collateral_to_liquidate - (
        asset_to_pay_debt_data["price"] * debt_to_cover_no_decimals / asset_to_liquidate_data["price"]
    )
    assert bonus == Decimal("22.2009919001400956487218981")
    protocol_fee = bonus * liquidation_protocol_fee
    assert protocol_fee == Decimal("4.440198380028019376224903391")
    max_amount_collateral_to_liquidate_final = max_amount_collateral_to_liquidate - protocol_fee
    assert max_amount_collateral_to_liquidate_final == Decimal("511.1161690787816474664908425")

    asset_to_pay_debt_contract.functions.approve(
        ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address,
        115792089237316195423570985008687907853269984665640564039457584007913129639935,
    ).transact({"from": wallet})
    lending_pool_v3 = w3.eth.contract(
        address=ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address, abi=ContractSpecs[Chain.ETHEREUM].LendingPoolV3.abi
    )

    asset_to_liquidate_before_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_before_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    debt_to_cover = int((debt_to_cover_no_decimals) * (10 ** asset_to_pay_debt_data["decimals"]))
    assert debt_to_cover == 241147612388234567

    liquidation_call = lending_pool_v3.functions.liquidationCall(
        asset_to_liquidate,
        asset_to_pay_debt,
        USER,
        115792089237316195423570985008687907853269984665640564039457584007913129639935,
        False,
    ).transact({"from": wallet})

    asset_to_liquidate_after_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_after_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    collateral_liquidated = abs(asset_to_liquidate_after_liquidation - asset_to_liquidate_before_liquidation)
    assert collateral_liquidated == approx(509115018)
    debt_covered = abs(asset_to_pay_debt_after_liquidation - asset_to_pay_debt_before_liquidation)
    assert debt_covered == approx(240203457612662254)

    collateral_liquidated_usd = (
        collateral_liquidated * asset_to_liquidate_data["price"] / (10 ** asset_to_liquidate_data["decimals"])
    )
    debt_covered_usd = debt_covered * asset_to_pay_debt_data["price"] / (10 ** asset_to_pay_debt_data["decimals"])

    debt_calculation_delta = abs(debt_to_cover - debt_covered) / (10 ** asset_to_pay_debt_data["decimals"])
    collateral_calculation_delta = abs(
        max_amount_collateral_to_liquidate_final
        - (collateral_liquidated / Decimal(10 ** asset_to_liquidate_data["decimals"]))
    )

    health_factor = cdp.get_health_factor(block="latest")
    assert health_factor > Decimal("1")


def test_integration_liquidation_call2(local_node_eth):
    w3 = local_node_eth.w3
    block = 18038102
    local_node_eth.set_block(block)

    cdp = AaveV3CDPManager(w3=w3, owner_address=USER2)

    balances = cdp.get_cdp_balances_data(block=block)
    health_factor = cdp.get_health_factor(block=block)

    asset_to_liquidate = ETHAddr.WBTC
    asset_to_liquidate_contract = w3.eth.contract(address=asset_to_liquidate, abi=TokenAbis.ERC20.abi)
    asset_to_pay_debt = ETHAddr.LINK
    asset_to_pay_debt_contract = w3.eth.contract(address=asset_to_pay_debt, abi=TokenAbis.ERC20.abi)

    pdp = w3.eth.contract(
        address=ContractSpecs[Chain.ETHEREUM].ProtocolDataProvider.address,
        abi=ContractSpecs[Chain.ETHEREUM].ProtocolDataProvider.abi,
    )
    liquidation_bonus = Decimal(
        pdp.functions.getReserveConfigurationData(asset_to_liquidate).call(block_identifier=block)[3] / 10000
    )
    liquidation_protocol_fee = Decimal(
        pdp.functions.getLiquidationProtocolFee(asset_to_liquidate).call(block_identifier=block) / 10000
    )

    collateral_usd = 0
    debt_usd = 0
    asset_to_liquidate_data = {}
    asset_to_pay_debt_data = {}
    for balance in balances:
        if balance[CDPData.CollateralEnabled]:
            collateral_usd += (
                balance[CDPData.InterestBearingBalance]
                * balance[CDPData.UnderlyingPriceUSD]
                * balance[CDPData.LiquidationThreshold]
            )

        debt_usd += (balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]) * balance[
            CDPData.UnderlyingPriceUSD
        ]

        if balance[CDPData.UnderlyingAddress] == asset_to_liquidate:
            asset_to_liquidate_data["amount"] = Decimal(balance[CDPData.InterestBearingBalance])
            asset_to_liquidate_data["price"] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_liquidate_data["decimals"] = asset_to_liquidate_contract.functions.decimals().call()
        elif balance[CDPData.UnderlyingAddress] == asset_to_pay_debt:
            asset_to_pay_debt_data["amount"] = Decimal(
                balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]
            )
            asset_to_pay_debt_data["price"] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_pay_debt_data["decimals"] = asset_to_pay_debt_contract.functions.decimals().call()

    # Address with lots of LINK
    wallet = "0x40B38765696e3d5d8d9d834D8AaD4bB6e418E489"
    local_node_eth.unlock_account(wallet)

    if health_factor < 1 and health_factor > CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = DEFAULT_LIQUIDATION_CLOSE_FACTOR
    elif health_factor < CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = MAX_LIQUIDATION_CLOSE_FACTOR

    debt_to_cover_no_decimals = asset_to_pay_debt_data["amount"] * Decimal(close_factor)
    max_amount_collateral_to_liquidate = (
        asset_to_pay_debt_data["price"]
        * debt_to_cover_no_decimals
        * liquidation_bonus
        / asset_to_liquidate_data["price"]
    )
    bonus = max_amount_collateral_to_liquidate - (
        asset_to_pay_debt_data["price"] * debt_to_cover_no_decimals / asset_to_liquidate_data["price"]
    )
    protocol_fee = bonus * liquidation_protocol_fee
    max_amount_collateral_to_liquidate_final = max_amount_collateral_to_liquidate - protocol_fee

    asset_to_pay_debt_contract.functions.approve(
        ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address,
        115792089237316195423570985008687907853269984665640564039457584007913129639935,
    ).transact({"from": wallet})
    lending_pool_v3 = w3.eth.contract(
        address=ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address, abi=ContractSpecs[Chain.ETHEREUM].LendingPoolV3.abi
    )

    asset_to_liquidate_before_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_before_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    debt_to_cover = int((debt_to_cover_no_decimals) * (10 ** asset_to_pay_debt_data["decimals"]))

    liquidation_call = lending_pool_v3.functions.liquidationCall(
        asset_to_liquidate,
        asset_to_pay_debt,
        USER2,
        115792089237316195423570985008687907853269984665640564039457584007913129639935,
        False,
    ).transact({"from": wallet})

    asset_to_liquidate_after_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_after_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    collateral_liquidated = abs(asset_to_liquidate_after_liquidation - asset_to_liquidate_before_liquidation)
    debt_covered = abs(asset_to_pay_debt_after_liquidation - asset_to_pay_debt_before_liquidation)

    collateral_liquidated_usd = (
        collateral_liquidated * asset_to_liquidate_data["price"] / (10 ** asset_to_liquidate_data["decimals"])
    )
    debt_covered_usd = debt_covered * asset_to_pay_debt_data["price"] / (10 ** asset_to_pay_debt_data["decimals"])

    debt_calculation_delta = abs(debt_to_cover - debt_covered) / (10 ** asset_to_pay_debt_data["decimals"])
    collateral_calculation_delta = abs(
        max_amount_collateral_to_liquidate_final
        - (collateral_liquidated / Decimal(10 ** asset_to_liquidate_data["decimals"]))
    )

    health_factor = cdp.get_health_factor(block="latest")
    assert health_factor < Decimal("1")

    # The health factor is still bellow 1 so we liquidate again

    asset_to_liquidate = ETHAddr.WBTC
    asset_to_liquidate_contract = w3.eth.contract(address=asset_to_liquidate, abi=TokenAbis.ERC20.abi)
    asset_to_pay_debt = ETHAddr.USDC
    asset_to_pay_debt_contract = w3.eth.contract(address=asset_to_pay_debt, abi=TokenAbis.ERC20.abi)

    pdp = w3.eth.contract(
        address=ContractSpecs[Chain.ETHEREUM].ProtocolDataProvider.address,
        abi=ContractSpecs[Chain.ETHEREUM].ProtocolDataProvider.abi,
    )
    liquidation_bonus = Decimal(pdp.functions.getReserveConfigurationData(asset_to_liquidate).call()[3] / 10000)
    liquidation_protocol_fee = Decimal(pdp.functions.getLiquidationProtocolFee(asset_to_liquidate).call() / 10000)

    collateral_usd = 0
    debt_usd = 0
    asset_to_liquidate_data = {}
    asset_to_pay_debt_data = {}
    for balance in balances:
        if balance[CDPData.CollateralEnabled]:
            collateral_usd += (
                balance[CDPData.InterestBearingBalance]
                * balance[CDPData.UnderlyingPriceUSD]
                * balance[CDPData.LiquidationThreshold]
            )

        debt_usd += (balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]) * balance[
            CDPData.UnderlyingPriceUSD
        ]

        if balance[CDPData.UnderlyingAddress] == asset_to_liquidate:
            asset_to_liquidate_data["amount"] = Decimal(balance[CDPData.InterestBearingBalance])
            asset_to_liquidate_data["price"] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_liquidate_data["decimals"] = asset_to_liquidate_contract.functions.decimals().call()
        elif balance[CDPData.UnderlyingAddress] == asset_to_pay_debt:
            asset_to_pay_debt_data["amount"] = Decimal(
                balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]
            )
            asset_to_pay_debt_data["price"] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_pay_debt_data["decimals"] = asset_to_pay_debt_contract.functions.decimals().call()

    wallet = "0x7713974908Be4BEd47172370115e8b1219F4A5f0"
    local_node_eth.unlock_account(wallet)

    if health_factor < 1 and health_factor > CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = DEFAULT_LIQUIDATION_CLOSE_FACTOR
    elif health_factor < CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = MAX_LIQUIDATION_CLOSE_FACTOR

    debt_to_cover_no_decimals = asset_to_pay_debt_data["amount"] * Decimal(close_factor)
    max_amount_collateral_to_liquidate = (
        asset_to_pay_debt_data["price"]
        * debt_to_cover_no_decimals
        * liquidation_bonus
        / asset_to_liquidate_data["price"]
    )
    bonus = max_amount_collateral_to_liquidate - (
        asset_to_pay_debt_data["price"] * debt_to_cover_no_decimals / asset_to_liquidate_data["price"]
    )
    protocol_fee = bonus * liquidation_protocol_fee
    max_amount_collateral_to_liquidate_final = max_amount_collateral_to_liquidate - protocol_fee

    asset_to_pay_debt_contract.functions.approve(
        ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address,
        115792089237316195423570985008687907853269984665640564039457584007913129639935,
    ).transact({"from": wallet})
    lending_pool_v3 = w3.eth.contract(
        address=ContractSpecs[Chain.ETHEREUM].LendingPoolV3.address, abi=ContractSpecs[Chain.ETHEREUM].LendingPoolV3.abi
    )

    asset_to_liquidate_before_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_before_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    debt_to_cover = int((debt_to_cover_no_decimals) * (10 ** asset_to_pay_debt_data["decimals"]))

    liquidation_call = lending_pool_v3.functions.liquidationCall(
        asset_to_liquidate,
        asset_to_pay_debt,
        USER2,
        115792089237316195423570985008687907853269984665640564039457584007913129639935,
        False,
    ).transact({"from": wallet})

    asset_to_liquidate_after_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_after_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    collateral_liquidated = abs(asset_to_liquidate_after_liquidation - asset_to_liquidate_before_liquidation)
    debt_covered = abs(asset_to_pay_debt_after_liquidation - asset_to_pay_debt_before_liquidation)

    collateral_liquidated_usd = (
        collateral_liquidated * asset_to_liquidate_data["price"] / (10 ** asset_to_liquidate_data["decimals"])
    )
    debt_covered_usd = debt_covered * asset_to_pay_debt_data["price"] / (10 ** asset_to_pay_debt_data["decimals"])

    debt_calculation_delta = abs(debt_to_cover - debt_covered) / (10 ** asset_to_pay_debt_data["decimals"])
    collateral_calculation_delta = abs(
        max_amount_collateral_to_liquidate_final
        - (collateral_liquidated / Decimal(10 ** asset_to_liquidate_data["decimals"]))
    )

    health_factor = cdp.get_health_factor(block="latest")
    assert health_factor > Decimal("1")


def test_bonus_matrix(local_node_eth, owner_address=USER2):
    w3 = local_node_eth.w3
    block = 18038102
    local_node_eth.set_block(block)

    assets = {"collaterals": {}, "debts": {}}
    bonus = {"collaterals": []}

    cdp = AaveV3CDPManager(w3=w3, owner_address=owner_address)

    balances = cdp.get_cdp_balances_data(block=block)
    health_factor = cdp.get_health_factor(block=block)

    pdp = w3.eth.contract(
        address=ContractSpecs[Chain.ETHEREUM].ProtocolDataProvider.address,
        abi=ContractSpecs[Chain.ETHEREUM].ProtocolDataProvider.abi,
    )

    if health_factor < 1 and health_factor > CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = DEFAULT_LIQUIDATION_CLOSE_FACTOR
    elif health_factor < CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = MAX_LIQUIDATION_CLOSE_FACTOR

    for balance in balances:
        asset_contract = w3.eth.contract(address=balance[CDPData.UnderlyingAddress], abi=TokenAbis.ERC20.abi)
        if balance[CDPData.CollateralEnabled]:
            assets["collaterals"][balance[CDPData.UnderlyingAddress]] = {}
            assets["collaterals"][balance[CDPData.UnderlyingAddress]]["amount"] = Decimal(
                balance[CDPData.InterestBearingBalance]
            )
            assets["collaterals"][balance[CDPData.UnderlyingAddress]]["price"] = Decimal(
                balance[CDPData.UnderlyingPriceUSD]
            )
            assets["collaterals"][balance[CDPData.UnderlyingAddress]][
                "decimals"
            ] = asset_contract.functions.decimals().call()
            assets["collaterals"][balance[CDPData.UnderlyingAddress]]["liquidation_bonus"] = Decimal(
                pdp.functions.getReserveConfigurationData(balance[CDPData.UnderlyingAddress]).call()[3] / 10000
            )
            assets["collaterals"][balance[CDPData.UnderlyingAddress]]["liquidation_protocol_fee"] = Decimal(
                pdp.functions.getLiquidationProtocolFee(balance[CDPData.UnderlyingAddress]).call() / 10000
            )

        asset_debt = balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]

        if asset_debt > 0:
            assets["debts"][balance[CDPData.UnderlyingAddress]] = {}
            assets["debts"][balance[CDPData.UnderlyingAddress]]["amount"] = asset_debt
            assets["debts"][balance[CDPData.UnderlyingAddress]]["price"] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            assets["debts"][balance[CDPData.UnderlyingAddress]]["decimals"] = asset_contract.functions.decimals().call()

    for collateral in assets["collaterals"]:
        bonus["collaterals"].append(collateral)
        for debt in assets["debts"]:
            bonus[debt] = []
            debt_to_cover = assets["debts"][debt]["amount"] * Decimal(close_factor)
            max_amount_collateral_to_liquidate = (
                assets["debts"][debt]["price"]
                * debt_to_cover
                * assets["collaterals"][collateral]["liquidation_bonus"]
                / assets["collaterals"][collateral]["price"]
            )
            debt_bonus = max_amount_collateral_to_liquidate - (
                assets["debts"][debt]["price"] * debt_to_cover / assets["collaterals"][collateral]["price"]
            )
            protocol_fee = debt_bonus * assets["collaterals"][collateral]["liquidation_protocol_fee"]
            debt_final_bonus_usd = (debt_bonus - protocol_fee) * assets["collaterals"][collateral]["price"]
            bonus[debt].append(debt_final_bonus_usd)

    assert bonus[ETHAddr.USDC] == [Decimal("15.55790638500001372223700750")]
    assert bonus[ETHAddr.DAI] == [Decimal("12.01965608671154246291107133")]
    assert bonus[ETHAddr.LINK] == [Decimal("13.83766300975449775812302420")]

    return bonus


def test_integration_1inch_swap(local_node_eth):
    w3 = local_node_eth.w3
    block = 18587363
    local_node_eth.set_block(block)

    # BASE_URL = "https://api.1inch.dev/swap/v5.2/1/swap?src=%s&dst=%s&amount=%d&from=%s&slippage=%d&allowPartialFill=%s&disableEstimate=%s"
    # headers = {'accept': 'application/json', 'Authorization': f'Bearer {API_KEY}'}

    src_token = ETHAddr.ETH
    dst_token = ETHAddr.WETH
    amount = 1000000000000000000

    value = 0
    if src_token == ETHAddr.ETH:
        value = amount

    local_node_eth.unlock_account(GNOSIS_DAO)

    src_token_contract = w3.eth.contract(address=src_token, abi=TokenAbis.ERC20.abi)

    # Approve src_token with 1inch Aggregation Router as spender
    src_token_contract.functions.approve(
        _1inchContractSpecs[Chain.ETHEREUM].AggregationRouterV5.address,
        115792089237316195423570985008687907853269984665640564039457584007913129639935,
    ).transact({"from": GNOSIS_DAO})

    # api_response = requests.get(BASE_URL % (src_token.lower(), dst_token.lower(), amount, GNOSIS_DAO, 2, False, True), headers=headers).json()
    # mock api response
    api_response = {
        "toAmount": "1000000000000000000",
        "tx": {
            "from": "0x849d52316331967b6ff1198e5e32a0eb168d039d",
            "to": "0x1111111254eeb25477b68fb85ed929f73a960582",
            "data": "0x12aa3caf000000000000000000000000e37e799d5077682fa0a244d46e5649f71457bd09000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000e37e799d5077682fa0a244d46e5649f71457bd09000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000de0b6b3a76400000000000000000000000000000000000000000000000000000d99a8cec7e200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000001600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008600000000000000000000000000000000000000000000000000006800001a4061c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2d0e30db080206c4eca27c02aaa39b223fe8d0a0e5c4f27ead9083c756cc21111111254eeb25477b68fb85ed929f73a9605820000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000008b1ccac8",
            "value": "1000000000000000000",
            "gas": 0,
            "gasPrice": "43220576181",
        },
    }
    router_contract = w3.eth.contract(
        address=_1inchContractSpecs[Chain.ETHEREUM].AggregationRouterV5.address,
        abi=_1inchContractSpecs[Chain.ETHEREUM].AggregationRouterV5.abi,
    )

    func_obj, func_params = router_contract.decode_function_input(api_response["tx"]["data"])

    # https://github.com/1inch/1inchProtocol/blob/811f7b69b67d1d9657e3e9c18a2e97f3e2b2b33a/README.md#flags-description
    flags = 0

    if src_token == ETHAddr.ETH:
        src_token_balance_before = w3.eth.get_balance(GNOSIS_DAO)
    else:
        src_token_balance_before = get_balance(w3, src_token, GNOSIS_DAO)

    if dst_token == ETHAddr.ETH:
        dst_token_balance_before = w3.eth.get_balance(GNOSIS_DAO)
    else:
        dst_token_balance_before = get_balance(w3, dst_token, GNOSIS_DAO)

    swap = func_obj(**func_params).transact({"from": GNOSIS_DAO, "value": value})

    if src_token == ETHAddr.ETH:
        src_token_balance_after = w3.eth.get_balance(GNOSIS_DAO)
    else:
        src_token_balance_after = get_balance(w3, src_token, GNOSIS_DAO)

    if dst_token == ETHAddr.ETH:
        dst_token_balance_after = w3.eth.get_balance(GNOSIS_DAO)
    else:
        dst_token_balance_after = get_balance(w3, dst_token, GNOSIS_DAO)

    collateral = ETHAddr.WETH

    # https://github.com/phoenixlabsresearch/sparklend-liquidator/blob/7f999858bb2570ea68db4ac2d3fb095431bb7a7b/contracts/LiquidateLoan.sol#L145C8-L145C9
    # api_response['tx']['data'] contains the _swapPath that should be sent to the executeFlashLoans function
    # The executeFlashLoans function calls the ILendingPool(_lendingPool).flashLoan() function which takes the params parameter with the following encoding:
    flash_loan_params = encode(
        ["address", "address", "address", "address", "address", "bytes"],
        [
            GNOSIS_DAO,
            SparkContractSpecs[Chain.ETHEREUM].LendingPoolV3.address,
            collateral,
            USER,
            _1inchContractSpecs[Chain.ETHEREUM].AggregationRouterV5.address,
            bytes.fromhex(api_response["tx"]["data"][2:]),
        ],
    )

    assert (
        flash_loan_params.hex()
        == "000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000c13e21b648a5ee794902342038ff3adab66be987000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c210000000000000000000000001111111254eeb25477b68fb85ed929f73a96058200000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000022812aa3caf000000000000000000000000e37e799d5077682fa0a244d46e5649f71457bd09000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000e37e799d5077682fa0a244d46e5649f71457bd09000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000de0b6b3a76400000000000000000000000000000000000000000000000000000d99a8cec7e200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000001600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008600000000000000000000000000000000000000000000000000006800001a4061c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2d0e30db080206c4eca27c02aaa39b223fe8d0a0e5c4f27ead9083c756cc21111111254eeb25477b68fb85ed929f73a9605820000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000008b1ccac8000000000000000000000000000000000000000000000000"
    )
