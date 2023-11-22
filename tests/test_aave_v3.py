from roles_royce.protocols.eth import aave_v3
from .utils import (local_node_eth, accounts, get_balance, steal_token, create_simple_safe, top_up_address)
from .roles import setup_common_roles, deploy_roles, apply_presets
from eth_abi import encode
from roles_royce import roles
from roles_royce.constants import ETHAddr
from decimal import Decimal
from pytest import approx
from roles_royce.toolshed.protocol_utils.aave_v3.addresses_and_abis import AddressesAndAbis
from roles_royce.toolshed.protocol_utils.aave_v3.cdp import AaveV3CDPManager, CDPData
from roles_royce.constants import Chain
import requests

USER = "0xDf3A7a27704196Af5149CD67D881279e32AF2C21"
USER2 = "0x7420fA58bA44E1141d5E9ADB6903BE549f7cE0b5"
GNOSIS_DAO = "0x849D52316331967b6fF1198e5E32A0eB168D039d"

#-----------------------------------------------------#
"""Unit Tests"""
#-----------------------------------------------------#
def test_approve_token():
    method = aave_v3.ApproveToken(token=ETHAddr.WETH, amount=123)
    assert method.data == '0x095ea7b300000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000000000000000000000000000000000000000007b'

def test_approve_AEthWETH():
    method = aave_v3.ApproveAEthWETH(amount=123)
    assert method.data == '0x095ea7b300000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000000000000000000000000000000000000000007b'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].aEthWETH.address

def test_approve_stkAAVE():
    method = aave_v3.ApproveForStkAAVE(amount=123)
    assert method.data == '0x095ea7b30000000000000000000000004da27a545c0c5b758a6ba100e3a049001de870f5000000000000000000000000000000000000000000000000000000000000007b'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].AAVE.address

def test_approve_stkABPT():
    method = aave_v3.ApproveForStkABPT(amount=123)
    assert method.data == '0x095ea7b3000000000000000000000000a1116930326d21fb917d5a27f1e9943a9595fb47000000000000000000000000000000000000000000000000000000000000007b'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].ABPT.address

def test_approve_delegation():
    method = aave_v3.ApproveDelegation(target= AddressesAndAbis[Chain.Ethereum].variableDebtWETH.address, amount=123)
    assert method.data == '0xc04a8a10000000000000000000000000d322a49006fc828f9b5b37ab215f99b4e5cab19c000000000000000000000000000000000000000000000000000000000000007b'
    assert method.contract_address == '0xeA51d7853EEFb32b6ee06b1C12E6dcCA88Be0fFE'

def test_deposit_token():
    method = aave_v3.DepositToken(asset=ETHAddr.WETH, amount=123, avatar=GNOSIS_DAO)
    assert method.data == '0x617ba037000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000000'

def test_withdraw_token():
    method = aave_v3.WithdrawToken(asset=ETHAddr.WETH, amount=123, avatar=GNOSIS_DAO)
    assert method.data == '0x69328dec000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d'

def test_deposit_ETH():
    method = aave_v3.DepositETH(eth_amount=123, avatar=GNOSIS_DAO)
    assert method.data == '0x474cf53d00000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d0000000000000000000000000000000000000000000000000000000000000000'

def test_withdraw_ETH():
    method = aave_v3.WithdrawETH(amount=123, avatar=GNOSIS_DAO)
    assert method.data == '0x80500d2000000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d'

def test_collateralize():
    method = aave_v3.Collateralize(asset=ETHAddr.WETH, use_as_collateral=True)
    assert method.data == '0x5a3b74b9000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000001'

def test_borrow():
    method = aave_v3.Borrow(asset=ETHAddr.WETH, amount=123, interest_rate_mode=aave_v3.InterestRateMode.VARIABLE, avatar=GNOSIS_DAO)
    assert method.data == '0xa415bcad000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d'

def test_repay():
    method = aave_v3.Repay(asset=ETHAddr.WETH, amount=123, interest_rate_mode=aave_v3.InterestRateMode.VARIABLE, avatar=GNOSIS_DAO)
    assert method.data == '0x573ade81000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d'

def test_borrow_ETH():
    method = aave_v3.BorrowETH(amount=123, interest_rate_mode=aave_v3.InterestRateMode.VARIABLE)
    assert method.data == '0x66514c9700000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000000000000000000000000000000000000000007b00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000'

def test_repay_ETH():
    method = aave_v3.RepayETH(eth_amount=123, interest_rate_mode=aave_v3.InterestRateMode.VARIABLE, avatar=GNOSIS_DAO)
    assert method.data == '0x02c5fcf800000000000000000000000087870bca3f3fd6335c3f4ce8392d69350b4fa4e2000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d'

def test_swap_borrow_rate_mode():
    method = aave_v3.SwapBorrowRateMode(asset=ETHAddr.WETH, interest_rate_mode=aave_v3.InterestRateMode.VARIABLE)
    assert method.data == '0x94ba89a2000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000002'

def test_stake_AAVE():
    method = aave_v3.StakeAAVE(avatar=GNOSIS_DAO, amount=123)
    assert method.data == '0xadc9772e000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].stkAAVE.address

def test_stake_ABPT():
    method = aave_v3.StakeABPT(avatar=GNOSIS_DAO, amount=123)
    assert method.data == '0xadc9772e000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].stkABPT.address

def test_claim_rewards_and_stake():
    method = aave_v3.ClaimRewardsAndStake(avatar=GNOSIS_DAO, amount=123)
    assert method.data == '0x955e18af000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b'

def test_unstake_AAVE():
    method = aave_v3.UnstakeAAVE(avatar=GNOSIS_DAO, amount=123)
    assert method.data == '0x1e9a6950000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].stkAAVE.address

def test_unstake_ABPT():
    method = aave_v3.UnstakeABPT(avatar=GNOSIS_DAO, amount=123)
    assert method.data == '0x1e9a6950000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].stkABPT.address

def test_cooldown_stkAAVE():
    method = aave_v3.CooldownStkAAVE(value=123, avatar=GNOSIS_DAO)
    assert method.data == '0x787a08a6'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].stkAAVE.address

def test_cooldown_stkABPT():
    method = aave_v3.CooldownStkABPT(value=123, avatar=GNOSIS_DAO)
    assert method.data == '0x787a08a6'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].stkABPT.address

def test_claim_AAVE_rewards():
    method = aave_v3.ClaimAAVERewards(avatar=GNOSIS_DAO, amount=123)
    assert method.data == '0x9a99b4f0000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].stkAAVE.address

def test_claim_ABPT_rewards():
    method = aave_v3.ClaimABPTRewards(avatar=GNOSIS_DAO, amount=123)
    assert method.data == '0x9a99b4f0000000000000000000000000849d52316331967b6ff1198e5e32a0eb168d039d000000000000000000000000000000000000000000000000000000000000007b'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].stkABPT.address

def test_swap_and_repay():
    method = aave_v3.SwapAndRepay(collateral_asset=ETHAddr.USDC, 
                                  debt_asset=ETHAddr.WETH, 
                                  collateral_amount=123, 
                                  debt_repay_amount=123, 
                                  debt_rate_mode=aave_v3.InterestRateMode.VARIABLE, 
                                  buy_all_balance_offset=0, 
                                  calldata='0x0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000000004842298207a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca0000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000562c9b4164b58103000000000000000000000000000000000000000000000000000000028fa6ae0000000000000000000000000000000000000000000000000056169161cebe049800000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000000022000000000000000000000000000000000000000000000000000000000000003a0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009abf798f5314bfd793a9e57a654bed35af4a1d600100000000000000000000000000000000000000000000000000000000031388000000000000000000000000000000000000000000000000000000000000044000000000000000000000000000000000000000000000000000000000652742c577e189f1a03f43afae287d193069d849000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000e592427a0aece92de3edee1f18e0157c058615640000000000000000000000000000000000000000000000000000000000000144f28c0498000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000653028e4000000000000000000000000000000000000000000000000000000028fa6ae00000000000000000000000000000000000000000000000000562c9b4164b581010000000000000000000000000000000000000000000000000000000000000042a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480001f4c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000647f39c581f595b53c5cb19bd0b3f8da6c935e2ca00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000', 
                                  permit_amount=123, 
                                  permit_deadline=1697053784, 
                                  permit_v=27, 
                                  permit_r='0xf63fe2ddf43a364fb088ca5fbabc1928b6bbf11b35aec8502907902baf240935', 
                                  permit_s='0x3e452b86b67a5c5ce46fdc83c1e23db730f7e2b9aa1d12ab25faf581be38140b') 
    assert method.data == '0x4db9dc97000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000006526fc58000000000000000000000000000000000000000000000000000000000000001bf63fe2ddf43a364fb088ca5fbabc1928b6bbf11b35aec8502907902baf2409353e452b86b67a5c5ce46fdc83c1e23db730f7e2b9aa1d12ab25faf581be38140b00000000000000000000000000000000000000000000000000000000000005000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000000004842298207a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca0000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000562c9b4164b58103000000000000000000000000000000000000000000000000000000028fa6ae0000000000000000000000000000000000000000000000000056169161cebe049800000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000000022000000000000000000000000000000000000000000000000000000000000003a0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009abf798f5314bfd793a9e57a654bed35af4a1d600100000000000000000000000000000000000000000000000000000000031388000000000000000000000000000000000000000000000000000000000000044000000000000000000000000000000000000000000000000000000000652742c577e189f1a03f43afae287d193069d849000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000e592427a0aece92de3edee1f18e0157c058615640000000000000000000000000000000000000000000000000000000000000144f28c0498000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000653028e4000000000000000000000000000000000000000000000000000000028fa6ae00000000000000000000000000000000000000000000000000562c9b4164b581010000000000000000000000000000000000000000000000000000000000000042a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480001f4c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000647f39c581f595b53c5cb19bd0b3f8da6c935e2ca00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].ParaSwapRepayAdapter.address

def test_swap_and_deposit():
    method = aave_v3.SwapAndDeposit(from_asset=ETHAddr.USDC, 
                                  to_asset=ETHAddr.WETH, 
                                  amount=123, 
                                  min_amount_to_receive=123, 
                                  swap_all_balance_offset=aave_v3.InterestRateMode.VARIABLE, 
                                  calldata='0x0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000000004842298207a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca0000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000562c9b4164b58103000000000000000000000000000000000000000000000000000000028fa6ae0000000000000000000000000000000000000000000000000056169161cebe049800000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000000022000000000000000000000000000000000000000000000000000000000000003a0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009abf798f5314bfd793a9e57a654bed35af4a1d600100000000000000000000000000000000000000000000000000000000031388000000000000000000000000000000000000000000000000000000000000044000000000000000000000000000000000000000000000000000000000652742c577e189f1a03f43afae287d193069d849000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000e592427a0aece92de3edee1f18e0157c058615640000000000000000000000000000000000000000000000000000000000000144f28c0498000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000653028e4000000000000000000000000000000000000000000000000000000028fa6ae00000000000000000000000000000000000000000000000000562c9b4164b581010000000000000000000000000000000000000000000000000000000000000042a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480001f4c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000647f39c581f595b53c5cb19bd0b3f8da6c935e2ca00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000', 
                                  augustus='0xDEF171Fe48CF0115B1d80b88dc8eAB59176FEe57',
                                  permit_amount=123, 
                                  permit_deadline=1697053784, 
                                  permit_v=27, 
                                  permit_r='0xf63fe2ddf43a364fb088ca5fbabc1928b6bbf11b35aec8502907902baf240935', 
                                  permit_s='0x3e452b86b67a5c5ce46fdc83c1e23db730f7e2b9aa1d12ab25faf581be38140b') 
    assert method.data == '0xd3454a35000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000000000007b00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000180000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee57000000000000000000000000000000000000000000000000000000000000007b000000000000000000000000000000000000000000000000000000006526fc58000000000000000000000000000000000000000000000000000000000000001bf63fe2ddf43a364fb088ca5fbabc1928b6bbf11b35aec8502907902baf2409353e452b86b67a5c5ce46fdc83c1e23db730f7e2b9aa1d12ab25faf581be38140b00000000000000000000000000000000000000000000000000000000000005000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000000004842298207a00000000000000000000000000000000000000000000000000000000000000200000000000000000000000007f39c581f595b53c5cb19bd0b3f8da6c935e2ca0000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000562c9b4164b58103000000000000000000000000000000000000000000000000000000028fa6ae0000000000000000000000000000000000000000000000000056169161cebe049800000000000000000000000000000000000000000000000000000000000001e0000000000000000000000000000000000000000000000000000000000000022000000000000000000000000000000000000000000000000000000000000003a0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009abf798f5314bfd793a9e57a654bed35af4a1d600100000000000000000000000000000000000000000000000000000000031388000000000000000000000000000000000000000000000000000000000000044000000000000000000000000000000000000000000000000000000000652742c577e189f1a03f43afae287d193069d849000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000e592427a0aece92de3edee1f18e0157c058615640000000000000000000000000000000000000000000000000000000000000144f28c0498000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee5700000000000000000000000000000000000000000000000000000000653028e4000000000000000000000000000000000000000000000000000000028fa6ae00000000000000000000000000000000000000000000000000562c9b4164b581010000000000000000000000000000000000000000000000000000000000000042a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480001f4c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000647f39c581f595b53c5cb19bd0b3f8da6c935e2ca00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].ParaSwapLiquidityAdapter.address

def test_delegate_AAVE():
    method = aave_v3.DelegateAAVE(delegatee=USER)
    assert method.data == '0x5c19a95c000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c21'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].AAVE.address

def test_delegate_AAVE_by_type():
    method = aave_v3.DelegateAAVEByType(delegatee=USER, delegation_type=aave_v3.DelegationType.VOTING)
    assert method.data == '0xdc937e1c000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c210000000000000000000000000000000000000000000000000000000000000000'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].AAVE.address

def test_delegate_stkAAVE():
    method = aave_v3.DelegateAAVE(delegatee=USER)
    assert method.data == '0x5c19a95c000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c21'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].stkAAVE.address

def test_delegate_stkAAVE_by_type():
    method = aave_v3.DelegateAAVEByType(delegatee=USER, delegation_type=aave_v3.DelegationType.VOTING)
    assert method.data == '0xdc937e1c000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c210000000000000000000000000000000000000000000000000000000000000000'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].stkAAVE.address

def test_submit_vote():
    method = aave_v3.SubmitVote(proposal_id=123, support=True)
    assert method.data == '0x612c56fa000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000001'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].GovernanceV2.address

def test_liquidation_call():
    method = aave_v3.LiquidationCall(collateral_asset=ETHAddr.WETH, debt_asset=ETHAddr.USDC, user=USER, debt_to_cover=123, receive_a_token=False)
    assert method.data == '0x00a718a9000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000df3a7a27704196af5149cd67d881279e32af2c21000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000000'
    assert method.contract_address == AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address


CLOSE_FACTOR_HF_THRESHOLD = 0.95
DEFAULT_LIQUIDATION_CLOSE_FACTOR = 0.5
MAX_LIQUIDATION_CLOSE_FACTOR = 1

#-----------------------------------------------------#
"""Integration Tests"""
#-----------------------------------------------------#

def test_integration_liquidation_call(local_node_eth):
    w3 = local_node_eth.w3
    block = 18430238
    local_node_eth.set_block(block)

    cdp = AaveV3CDPManager(w3=w3, owner_address=USER)

    balances = cdp.get_cdp_balances_data(block=block)
    # print(balances)
    health_factor = cdp.get_health_factor(block=block)
    # print(health_factor)
    # # cdp_data = cdp.get_cdp_data(block=block)

    asset_to_liquidate = ETHAddr.USDC
    asset_to_liquidate_contract = w3.eth.contract(address=asset_to_liquidate, abi=AddressesAndAbis[Chain.Ethereum].ERC20.abi)
    asset_to_pay_debt = ETHAddr.wstETH
    asset_to_pay_debt_contract = w3.eth.contract(address=asset_to_pay_debt, abi=AddressesAndAbis[Chain.Ethereum].ERC20.abi)

    pdp = w3.eth.contract(address=AddressesAndAbis[Chain.Ethereum].ProtocolDataProvider.address, abi=AddressesAndAbis[Chain.Ethereum].ProtocolDataProvider.abi)
    liquidation_bonus = Decimal(pdp.functions.getReserveConfigurationData(asset_to_liquidate).call(block_identifier=block)[3] / 10000)
    liquidation_protocol_fee = Decimal(pdp.functions.getLiquidationProtocolFee(asset_to_liquidate).call(block_identifier=block) / 10000)

    collateral_usd = 0
    debt_usd = 0
    asset_to_liquidate_data = {}
    asset_to_pay_debt_data = {}
    for balance in balances:
        if balance[CDPData.CollateralEnabled]:
            collateral_usd += balance[CDPData.InterestBearingBalance] * balance[CDPData.UnderlyingPriceUSD] * balance[CDPData.LiquidationThreshold]
        
        debt_usd += (balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]) * balance[CDPData.UnderlyingPriceUSD]

        if balance[CDPData.UnderlyingAddress] == asset_to_liquidate:
            asset_to_liquidate_data['amount'] = Decimal(balance[CDPData.InterestBearingBalance])
            asset_to_liquidate_data['price'] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_liquidate_data['decimals'] = asset_to_liquidate_contract.functions.decimals().call()
        elif balance[CDPData.UnderlyingAddress] == asset_to_pay_debt:
            asset_to_pay_debt_data['amount'] = Decimal(balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance])
            asset_to_pay_debt_data['price'] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_pay_debt_data['decimals'] = asset_to_pay_debt_contract.functions.decimals().call()

    wallet = '0x5313b39bf226ced2332C81eB97BB28c6fD50d1a3'
    local_node_eth.unlock_account(wallet)

    if health_factor < 1 and health_factor > CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = DEFAULT_LIQUIDATION_CLOSE_FACTOR
    elif health_factor < CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = MAX_LIQUIDATION_CLOSE_FACTOR
    
    debt_to_cover_no_decimals = asset_to_pay_debt_data['amount'] * Decimal(close_factor)
    max_amount_collateral_to_liquidate = asset_to_pay_debt_data['price'] * debt_to_cover_no_decimals * liquidation_bonus / asset_to_liquidate_data['price']
    bonus = max_amount_collateral_to_liquidate - (asset_to_pay_debt_data['price'] * debt_to_cover_no_decimals / asset_to_liquidate_data['price'])
    protocol_fee = bonus * liquidation_protocol_fee
    max_amount_collateral_to_liquidate_final = max_amount_collateral_to_liquidate - protocol_fee
    
    asset_to_pay_debt_contract.functions.approve(AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address, 115792089237316195423570985008687907853269984665640564039457584007913129639935).transact({"from": wallet})
    lending_pool_v3 = w3.eth.contract(address=AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address, abi=AddressesAndAbis[Chain.Ethereum].LendingPoolV3.abi)

    asset_to_liquidate_before_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_before_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    debt_to_cover = int((debt_to_cover_no_decimals)*(10**asset_to_pay_debt_data['decimals']))
    
    liquidation_call = lending_pool_v3.functions.liquidationCall(asset_to_liquidate, asset_to_pay_debt, USER, 115792089237316195423570985008687907853269984665640564039457584007913129639935, False).transact({"from": wallet})
    
    asset_to_liquidate_after_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_after_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    collateral_liquidated = abs(asset_to_liquidate_after_liquidation - asset_to_liquidate_before_liquidation)
    debt_covered = abs(asset_to_pay_debt_after_liquidation - asset_to_pay_debt_before_liquidation)

    collateral_liquidated_usd = collateral_liquidated * asset_to_liquidate_data['price'] / (10**asset_to_liquidate_data['decimals'])
    debt_covered_usd = debt_covered * asset_to_pay_debt_data['price'] / (10**asset_to_pay_debt_data['decimals'])

    debt_calculation_delta = abs(debt_to_cover - debt_covered) / (10**asset_to_pay_debt_data['decimals'])
    collateral_calculation_delta = abs(max_amount_collateral_to_liquidate_final - (collateral_liquidated / Decimal(10**asset_to_liquidate_data['decimals']))) 
    balances = cdp.get_cdp_balances_data(block='latest')
    print(balances)
    health_factor = cdp.get_health_factor(block='latest')
    print(health_factor)


def test_integration_liquidation_call2(local_node_eth):
    w3 = local_node_eth.w3
    block = 18038102
    local_node_eth.set_block(block)

    cdp = AaveV3CDPManager(w3=w3, owner_address=USER2)

    balances = cdp.get_cdp_balances_data(block=block)
    # print(balances)
    health_factor = cdp.get_health_factor(block=block)
    # print(health_factor)
    # # cdp_data = cdp.get_cdp_data(block=block)

    asset_to_liquidate = ETHAddr.WBTC
    asset_to_liquidate_contract = w3.eth.contract(address=asset_to_liquidate, abi=AddressesAndAbis[Chain.Ethereum].ERC20.abi)
    asset_to_pay_debt = ETHAddr.LINK
    asset_to_pay_debt_contract = w3.eth.contract(address=asset_to_pay_debt, abi=AddressesAndAbis[Chain.Ethereum].ERC20.abi)

    pdp = w3.eth.contract(address=AddressesAndAbis[Chain.Ethereum].ProtocolDataProvider.address, abi=AddressesAndAbis[Chain.Ethereum].ProtocolDataProvider.abi)
    liquidation_bonus = Decimal(pdp.functions.getReserveConfigurationData(asset_to_liquidate).call(block_identifier=block)[3] / 10000)
    liquidation_protocol_fee = Decimal(pdp.functions.getLiquidationProtocolFee(asset_to_liquidate).call(block_identifier=block) / 10000)

    collateral_usd = 0
    debt_usd = 0
    asset_to_liquidate_data = {}
    asset_to_pay_debt_data = {}
    for balance in balances:
        if balance[CDPData.CollateralEnabled]:
            collateral_usd += balance[CDPData.InterestBearingBalance] * balance[CDPData.UnderlyingPriceUSD] * balance[CDPData.LiquidationThreshold]
        
        debt_usd += (balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]) * balance[CDPData.UnderlyingPriceUSD]

        if balance[CDPData.UnderlyingAddress] == asset_to_liquidate:
            asset_to_liquidate_data['amount'] = Decimal(balance[CDPData.InterestBearingBalance])
            asset_to_liquidate_data['price'] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_liquidate_data['decimals'] = asset_to_liquidate_contract.functions.decimals().call()
        elif balance[CDPData.UnderlyingAddress] == asset_to_pay_debt:
            asset_to_pay_debt_data['amount'] = Decimal(balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance])
            asset_to_pay_debt_data['price'] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_pay_debt_data['decimals'] = asset_to_pay_debt_contract.functions.decimals().call()

    wallet = '0x40B38765696e3d5d8d9d834D8AaD4bB6e418E489'
    local_node_eth.unlock_account(wallet)

    if health_factor < 1 and health_factor > CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = DEFAULT_LIQUIDATION_CLOSE_FACTOR
    elif health_factor < CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = MAX_LIQUIDATION_CLOSE_FACTOR
    
    # debt_to_cover = debt_usd / asset_to_pay_debt_data['price'] 
    # debt_to_cover = debt_to_cover * Decimal(close_factor)
    debt_to_cover_no_decimals = asset_to_pay_debt_data['amount'] * Decimal(close_factor)
    max_amount_collateral_to_liquidate = asset_to_pay_debt_data['price'] * debt_to_cover_no_decimals * liquidation_bonus / asset_to_liquidate_data['price']
    bonus = max_amount_collateral_to_liquidate - (asset_to_pay_debt_data['price'] * debt_to_cover_no_decimals / asset_to_liquidate_data['price'])
    protocol_fee = bonus * liquidation_protocol_fee
    max_amount_collateral_to_liquidate_final = max_amount_collateral_to_liquidate - protocol_fee
    
    asset_to_pay_debt_contract.functions.approve(AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address, 115792089237316195423570985008687907853269984665640564039457584007913129639935).transact({"from": wallet})
    lending_pool_v3 = w3.eth.contract(address=AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address, abi=AddressesAndAbis[Chain.Ethereum].LendingPoolV3.abi)

    asset_to_liquidate_before_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_before_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    debt_to_cover = int((debt_to_cover_no_decimals)*(10**asset_to_pay_debt_data['decimals']))
    
    liquidation_call = lending_pool_v3.functions.liquidationCall(asset_to_liquidate, asset_to_pay_debt, USER2, 115792089237316195423570985008687907853269984665640564039457584007913129639935, False).transact({"from": wallet})
    
    asset_to_liquidate_after_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_after_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    collateral_liquidated = abs(asset_to_liquidate_after_liquidation - asset_to_liquidate_before_liquidation)
    debt_covered = abs(asset_to_pay_debt_after_liquidation - asset_to_pay_debt_before_liquidation)

    collateral_liquidated_usd = collateral_liquidated * asset_to_liquidate_data['price'] / (10**asset_to_liquidate_data['decimals'])
    debt_covered_usd = debt_covered * asset_to_pay_debt_data['price'] / (10**asset_to_pay_debt_data['decimals'])

    debt_calculation_delta = abs(debt_to_cover - debt_covered) / (10**asset_to_pay_debt_data['decimals'])
    collateral_calculation_delta = abs(max_amount_collateral_to_liquidate_final - (collateral_liquidated / Decimal(10**asset_to_liquidate_data['decimals']))) 

    balances = cdp.get_cdp_balances_data(block='latest')
    print(balances)
    health_factor = cdp.get_health_factor(block='latest')
    print(health_factor)




    asset_to_liquidate = ETHAddr.WBTC
    asset_to_liquidate_contract = w3.eth.contract(address=asset_to_liquidate, abi=AddressesAndAbis[Chain.Ethereum].ERC20.abi)
    asset_to_pay_debt = ETHAddr.USDC
    asset_to_pay_debt_contract = w3.eth.contract(address=asset_to_pay_debt, abi=AddressesAndAbis[Chain.Ethereum].ERC20.abi)

    pdp = w3.eth.contract(address=AddressesAndAbis[Chain.Ethereum].ProtocolDataProvider.address, abi=AddressesAndAbis[Chain.Ethereum].ProtocolDataProvider.abi)
    liquidation_bonus = Decimal(pdp.functions.getReserveConfigurationData(asset_to_liquidate).call()[3] / 10000)
    liquidation_protocol_fee = Decimal(pdp.functions.getLiquidationProtocolFee(asset_to_liquidate).call() / 10000)

    collateral_usd = 0
    debt_usd = 0
    asset_to_liquidate_data = {}
    asset_to_pay_debt_data = {}
    for balance in balances:
        if balance[CDPData.CollateralEnabled]:
            collateral_usd += balance[CDPData.InterestBearingBalance] * balance[CDPData.UnderlyingPriceUSD] * balance[CDPData.LiquidationThreshold]
        
        debt_usd += (balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]) * balance[CDPData.UnderlyingPriceUSD]

        if balance[CDPData.UnderlyingAddress] == asset_to_liquidate:
            asset_to_liquidate_data['amount'] = Decimal(balance[CDPData.InterestBearingBalance])
            asset_to_liquidate_data['price'] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_liquidate_data['decimals'] = asset_to_liquidate_contract.functions.decimals().call()
        elif balance[CDPData.UnderlyingAddress] == asset_to_pay_debt:
            asset_to_pay_debt_data['amount'] = Decimal(balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance])
            asset_to_pay_debt_data['price'] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            asset_to_pay_debt_data['decimals'] = asset_to_pay_debt_contract.functions.decimals().call()

    wallet = '0x7713974908Be4BEd47172370115e8b1219F4A5f0'
    local_node_eth.unlock_account(wallet)

    if health_factor < 1 and health_factor > CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = DEFAULT_LIQUIDATION_CLOSE_FACTOR
    elif health_factor < CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = MAX_LIQUIDATION_CLOSE_FACTOR
    
    # debt_to_cover = debt_usd / asset_to_pay_debt_data['price'] 
    # debt_to_cover = debt_to_cover * Decimal(close_factor)
    debt_to_cover_no_decimals = asset_to_pay_debt_data['amount'] * Decimal(close_factor)
    max_amount_collateral_to_liquidate = asset_to_pay_debt_data['price'] * debt_to_cover_no_decimals * liquidation_bonus / asset_to_liquidate_data['price']
    bonus = max_amount_collateral_to_liquidate - (asset_to_pay_debt_data['price'] * debt_to_cover_no_decimals / asset_to_liquidate_data['price'])
    protocol_fee = bonus * liquidation_protocol_fee
    max_amount_collateral_to_liquidate_final = max_amount_collateral_to_liquidate - protocol_fee
    
    asset_to_pay_debt_contract.functions.approve(AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address, 115792089237316195423570985008687907853269984665640564039457584007913129639935).transact({"from": wallet})
    lending_pool_v3 = w3.eth.contract(address=AddressesAndAbis[Chain.Ethereum].LendingPoolV3.address, abi=AddressesAndAbis[Chain.Ethereum].LendingPoolV3.abi)

    asset_to_liquidate_before_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_before_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    debt_to_cover = int((debt_to_cover_no_decimals)*(10**asset_to_pay_debt_data['decimals']))
    
    liquidation_call = lending_pool_v3.functions.liquidationCall(asset_to_liquidate, asset_to_pay_debt, USER2, 115792089237316195423570985008687907853269984665640564039457584007913129639935, False).transact({"from": wallet})
    
    asset_to_liquidate_after_liquidation = get_balance(w3, asset_to_liquidate, wallet)
    asset_to_pay_debt_after_liquidation = get_balance(w3, asset_to_pay_debt, wallet)

    collateral_liquidated = abs(asset_to_liquidate_after_liquidation - asset_to_liquidate_before_liquidation)
    debt_covered = abs(asset_to_pay_debt_after_liquidation - asset_to_pay_debt_before_liquidation)

    collateral_liquidated_usd = collateral_liquidated * asset_to_liquidate_data['price'] / (10**asset_to_liquidate_data['decimals'])
    debt_covered_usd = debt_covered * asset_to_pay_debt_data['price'] / (10**asset_to_pay_debt_data['decimals'])

    debt_calculation_delta = abs(debt_to_cover - debt_covered) / (10**asset_to_pay_debt_data['decimals'])
    collateral_calculation_delta = abs(max_amount_collateral_to_liquidate_final - (collateral_liquidated / Decimal(10**asset_to_liquidate_data['decimals']))) 

    balances = cdp.get_cdp_balances_data(block='latest')
    print(balances)
    health_factor = cdp.get_health_factor(block='latest')
    print(health_factor)


def test_bonus_matrix(local_node_eth, owner_address=USER2):
    w3 = local_node_eth.w3
    block = 18038102
    local_node_eth.set_block(block)

    assets = {'collaterals': {}, 'debts': {}}
    bonus = {'collaterals': []}

    cdp = AaveV3CDPManager(w3=w3, owner_address=owner_address)

    balances = cdp.get_cdp_balances_data(block=block)
    health_factor = cdp.get_health_factor(block=block)

    pdp = w3.eth.contract(address=AddressesAndAbis[Chain.Ethereum].ProtocolDataProvider.address, abi=AddressesAndAbis[Chain.Ethereum].ProtocolDataProvider.abi)

    if health_factor < 1 and health_factor > CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = DEFAULT_LIQUIDATION_CLOSE_FACTOR
    elif health_factor < CLOSE_FACTOR_HF_THRESHOLD:
        close_factor = MAX_LIQUIDATION_CLOSE_FACTOR

    for balance in balances:
        asset_contract = w3.eth.contract(address=balance[CDPData.UnderlyingAddress], abi=AddressesAndAbis[Chain.Ethereum].ERC20.abi)
        if balance[CDPData.CollateralEnabled]:
            assets['collaterals'][balance[CDPData.UnderlyingAddress]] = {}
            assets['collaterals'][balance[CDPData.UnderlyingAddress]]['amount'] = Decimal(balance[CDPData.InterestBearingBalance])
            assets['collaterals'][balance[CDPData.UnderlyingAddress]]['price'] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            assets['collaterals'][balance[CDPData.UnderlyingAddress]]['decimals'] = asset_contract.functions.decimals().call()
            assets['collaterals'][balance[CDPData.UnderlyingAddress]]['liquidation_bonus'] = Decimal(pdp.functions.getReserveConfigurationData(balance[CDPData.UnderlyingAddress]).call()[3] / 10000)
            assets['collaterals'][balance[CDPData.UnderlyingAddress]]['liquidation_protocol_fee'] = Decimal(pdp.functions.getLiquidationProtocolFee(balance[CDPData.UnderlyingAddress]).call() / 10000)
        
        asset_debt = balance[CDPData.VariableDebtBalance] + balance[CDPData.StableDebtBalance]

        if asset_debt > 0:
            assets['debts'][balance[CDPData.UnderlyingAddress]] = {}
            assets['debts'][balance[CDPData.UnderlyingAddress]]['amount'] = asset_debt
            assets['debts'][balance[CDPData.UnderlyingAddress]]['price'] = Decimal(balance[CDPData.UnderlyingPriceUSD])
            assets['debts'][balance[CDPData.UnderlyingAddress]]['decimals'] = asset_contract.functions.decimals().call()   
    
    for collateral in assets['collaterals']:
        bonus['collaterals'].append(collateral)
        for debt in assets['debts']:
            bonus[debt] = []
            debt_to_cover = assets['debts'][debt]['amount'] * Decimal(close_factor)
            max_amount_collateral_to_liquidate = assets['debts'][debt]['price'] * debt_to_cover * assets['collaterals'][collateral]['liquidation_bonus'] / assets['collaterals'][collateral]['price']
            debt_bonus = max_amount_collateral_to_liquidate - (assets['debts'][debt]['price'] * debt_to_cover / assets['collaterals'][collateral]['price'])
            protocol_fee = debt_bonus * assets['collaterals'][collateral]['liquidation_protocol_fee']
            debt_final_bonus_usd = (debt_bonus - protocol_fee) * assets['collaterals'][collateral]['price']
            bonus[debt].append(debt_final_bonus_usd)

    return bonus


def test_integration_1inch_swap(local_node_eth):

    w3 = local_node_eth.w3
    block = 18587363
    local_node_eth.set_block(block)

    _1INCH_AGGREGATION_ROUTER = "0x1111111254EEB25477B68fb85Ed929f73A960582"
    SPARK_LENDING_POOL = "0xC13e21B648A5Ee794902342038FF3aDAB66BE987"
    ABI_ROUTER = '[{"inputs":[{"internalType":"contract IWETH","name":"weth","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"AccessDenied","type":"error"},{"inputs":[],"name":"AdvanceNonceFailed","type":"error"},{"inputs":[],"name":"AlreadyFilled","type":"error"},{"inputs":[],"name":"ArbitraryStaticCallFailed","type":"error"},{"inputs":[],"name":"BadPool","type":"error"},{"inputs":[],"name":"BadSignature","type":"error"},{"inputs":[],"name":"ETHTransferFailed","type":"error"},{"inputs":[],"name":"ETHTransferFailed","type":"error"},{"inputs":[],"name":"EmptyPools","type":"error"},{"inputs":[],"name":"EthDepositRejected","type":"error"},{"inputs":[],"name":"GetAmountCallFailed","type":"error"},{"inputs":[],"name":"IncorrectDataLength","type":"error"},{"inputs":[],"name":"InsufficientBalance","type":"error"},{"inputs":[],"name":"InvalidMsgValue","type":"error"},{"inputs":[],"name":"InvalidMsgValue","type":"error"},{"inputs":[],"name":"InvalidatedOrder","type":"error"},{"inputs":[],"name":"MakingAmountExceeded","type":"error"},{"inputs":[],"name":"MakingAmountTooLow","type":"error"},{"inputs":[],"name":"OnlyOneAmountShouldBeZero","type":"error"},{"inputs":[],"name":"OrderExpired","type":"error"},{"inputs":[],"name":"PermitLengthTooLow","type":"error"},{"inputs":[],"name":"PredicateIsNotTrue","type":"error"},{"inputs":[],"name":"PrivateOrder","type":"error"},{"inputs":[],"name":"RFQBadSignature","type":"error"},{"inputs":[],"name":"RFQPrivateOrder","type":"error"},{"inputs":[],"name":"RFQSwapWithZeroAmount","type":"error"},{"inputs":[],"name":"RFQZeroTargetIsForbidden","type":"error"},{"inputs":[],"name":"ReentrancyDetected","type":"error"},{"inputs":[],"name":"RemainingAmountIsZero","type":"error"},{"inputs":[],"name":"ReservesCallFailed","type":"error"},{"inputs":[],"name":"ReturnAmountIsNotEnough","type":"error"},{"inputs":[],"name":"SafePermitBadLength","type":"error"},{"inputs":[],"name":"SafeTransferFailed","type":"error"},{"inputs":[],"name":"SafeTransferFromFailed","type":"error"},{"inputs":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"res","type":"bytes"}],"name":"SimulationResults","type":"error"},{"inputs":[],"name":"SwapAmountTooLarge","type":"error"},{"inputs":[],"name":"SwapWithZeroAmount","type":"error"},{"inputs":[],"name":"TakingAmountExceeded","type":"error"},{"inputs":[],"name":"TakingAmountIncreased","type":"error"},{"inputs":[],"name":"TakingAmountTooHigh","type":"error"},{"inputs":[],"name":"TransferFromMakerToTakerFailed","type":"error"},{"inputs":[],"name":"TransferFromTakerToMakerFailed","type":"error"},{"inputs":[],"name":"UnknownOrder","type":"error"},{"inputs":[],"name":"WrongAmount","type":"error"},{"inputs":[],"name":"WrongGetter","type":"error"},{"inputs":[],"name":"ZeroAddress","type":"error"},{"inputs":[],"name":"ZeroMinReturn","type":"error"},{"inputs":[],"name":"ZeroReturnAmount","type":"error"},{"inputs":[],"name":"ZeroTargetIsForbidden","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"maker","type":"address"},{"indexed":false,"internalType":"uint256","name":"newNonce","type":"uint256"}],"name":"NonceIncreased","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"maker","type":"address"},{"indexed":false,"internalType":"bytes32","name":"orderHash","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"remainingRaw","type":"uint256"}],"name":"OrderCanceled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"maker","type":"address"},{"indexed":false,"internalType":"bytes32","name":"orderHash","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"remaining","type":"uint256"}],"name":"OrderFilled","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bytes32","name":"orderHash","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"makingAmount","type":"uint256"}],"name":"OrderFilledRFQ","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"inputs":[{"internalType":"uint8","name":"amount","type":"uint8"}],"name":"advanceNonce","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"offsets","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"and","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"arbitraryStaticCall","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"salt","type":"uint256"},{"internalType":"address","name":"makerAsset","type":"address"},{"internalType":"address","name":"takerAsset","type":"address"},{"internalType":"address","name":"maker","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"address","name":"allowedSender","type":"address"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"},{"internalType":"uint256","name":"offsets","type":"uint256"},{"internalType":"bytes","name":"interactions","type":"bytes"}],"internalType":"struct OrderLib.Order","name":"order","type":"tuple"}],"name":"cancelOrder","outputs":[{"internalType":"uint256","name":"orderRemaining","type":"uint256"},{"internalType":"bytes32","name":"orderHash","type":"bytes32"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"orderInfo","type":"uint256"}],"name":"cancelOrderRFQ","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"orderInfo","type":"uint256"},{"internalType":"uint256","name":"additionalMask","type":"uint256"}],"name":"cancelOrderRFQ","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"salt","type":"uint256"},{"internalType":"address","name":"makerAsset","type":"address"},{"internalType":"address","name":"takerAsset","type":"address"},{"internalType":"address","name":"maker","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"address","name":"allowedSender","type":"address"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"},{"internalType":"uint256","name":"offsets","type":"uint256"},{"internalType":"bytes","name":"interactions","type":"bytes"}],"internalType":"struct OrderLib.Order","name":"order","type":"tuple"}],"name":"checkPredicate","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"contract IClipperExchangeInterface","name":"clipperExchange","type":"address"},{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"contract IERC20","name":"dstToken","type":"address"},{"internalType":"uint256","name":"inputAmount","type":"uint256"},{"internalType":"uint256","name":"outputAmount","type":"uint256"},{"internalType":"uint256","name":"goodUntil","type":"uint256"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"vs","type":"bytes32"}],"name":"clipperSwap","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"contract IClipperExchangeInterface","name":"clipperExchange","type":"address"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"contract IERC20","name":"dstToken","type":"address"},{"internalType":"uint256","name":"inputAmount","type":"uint256"},{"internalType":"uint256","name":"outputAmount","type":"uint256"},{"internalType":"uint256","name":"goodUntil","type":"uint256"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"vs","type":"bytes32"}],"name":"clipperSwapTo","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"contract IClipperExchangeInterface","name":"clipperExchange","type":"address"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"contract IERC20","name":"dstToken","type":"address"},{"internalType":"uint256","name":"inputAmount","type":"uint256"},{"internalType":"uint256","name":"outputAmount","type":"uint256"},{"internalType":"uint256","name":"goodUntil","type":"uint256"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"vs","type":"bytes32"},{"internalType":"bytes","name":"permit","type":"bytes"}],"name":"clipperSwapToWithPermit","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"destroy","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"eq","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"salt","type":"uint256"},{"internalType":"address","name":"makerAsset","type":"address"},{"internalType":"address","name":"takerAsset","type":"address"},{"internalType":"address","name":"maker","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"address","name":"allowedSender","type":"address"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"},{"internalType":"uint256","name":"offsets","type":"uint256"},{"internalType":"bytes","name":"interactions","type":"bytes"}],"internalType":"struct OrderLib.Order","name":"order","type":"tuple"},{"internalType":"bytes","name":"signature","type":"bytes"},{"internalType":"bytes","name":"interaction","type":"bytes"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"},{"internalType":"uint256","name":"skipPermitAndThresholdAmount","type":"uint256"}],"name":"fillOrder","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"info","type":"uint256"},{"internalType":"address","name":"makerAsset","type":"address"},{"internalType":"address","name":"takerAsset","type":"address"},{"internalType":"address","name":"maker","type":"address"},{"internalType":"address","name":"allowedSender","type":"address"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"}],"internalType":"struct OrderRFQLib.OrderRFQ","name":"order","type":"tuple"},{"internalType":"bytes","name":"signature","type":"bytes"},{"internalType":"uint256","name":"flagsAndAmount","type":"uint256"}],"name":"fillOrderRFQ","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"info","type":"uint256"},{"internalType":"address","name":"makerAsset","type":"address"},{"internalType":"address","name":"takerAsset","type":"address"},{"internalType":"address","name":"maker","type":"address"},{"internalType":"address","name":"allowedSender","type":"address"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"}],"internalType":"struct OrderRFQLib.OrderRFQ","name":"order","type":"tuple"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"vs","type":"bytes32"},{"internalType":"uint256","name":"flagsAndAmount","type":"uint256"}],"name":"fillOrderRFQCompact","outputs":[{"internalType":"uint256","name":"filledMakingAmount","type":"uint256"},{"internalType":"uint256","name":"filledTakingAmount","type":"uint256"},{"internalType":"bytes32","name":"orderHash","type":"bytes32"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"info","type":"uint256"},{"internalType":"address","name":"makerAsset","type":"address"},{"internalType":"address","name":"takerAsset","type":"address"},{"internalType":"address","name":"maker","type":"address"},{"internalType":"address","name":"allowedSender","type":"address"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"}],"internalType":"struct OrderRFQLib.OrderRFQ","name":"order","type":"tuple"},{"internalType":"bytes","name":"signature","type":"bytes"},{"internalType":"uint256","name":"flagsAndAmount","type":"uint256"},{"internalType":"address","name":"target","type":"address"}],"name":"fillOrderRFQTo","outputs":[{"internalType":"uint256","name":"filledMakingAmount","type":"uint256"},{"internalType":"uint256","name":"filledTakingAmount","type":"uint256"},{"internalType":"bytes32","name":"orderHash","type":"bytes32"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"info","type":"uint256"},{"internalType":"address","name":"makerAsset","type":"address"},{"internalType":"address","name":"takerAsset","type":"address"},{"internalType":"address","name":"maker","type":"address"},{"internalType":"address","name":"allowedSender","type":"address"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"}],"internalType":"struct OrderRFQLib.OrderRFQ","name":"order","type":"tuple"},{"internalType":"bytes","name":"signature","type":"bytes"},{"internalType":"uint256","name":"flagsAndAmount","type":"uint256"},{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"permit","type":"bytes"}],"name":"fillOrderRFQToWithPermit","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"salt","type":"uint256"},{"internalType":"address","name":"makerAsset","type":"address"},{"internalType":"address","name":"takerAsset","type":"address"},{"internalType":"address","name":"maker","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"address","name":"allowedSender","type":"address"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"},{"internalType":"uint256","name":"offsets","type":"uint256"},{"internalType":"bytes","name":"interactions","type":"bytes"}],"internalType":"struct OrderLib.Order","name":"order_","type":"tuple"},{"internalType":"bytes","name":"signature","type":"bytes"},{"internalType":"bytes","name":"interaction","type":"bytes"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"},{"internalType":"uint256","name":"skipPermitAndThresholdAmount","type":"uint256"},{"internalType":"address","name":"target","type":"address"}],"name":"fillOrderTo","outputs":[{"internalType":"uint256","name":"actualMakingAmount","type":"uint256"},{"internalType":"uint256","name":"actualTakingAmount","type":"uint256"},{"internalType":"bytes32","name":"orderHash","type":"bytes32"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"salt","type":"uint256"},{"internalType":"address","name":"makerAsset","type":"address"},{"internalType":"address","name":"takerAsset","type":"address"},{"internalType":"address","name":"maker","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"address","name":"allowedSender","type":"address"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"},{"internalType":"uint256","name":"offsets","type":"uint256"},{"internalType":"bytes","name":"interactions","type":"bytes"}],"internalType":"struct OrderLib.Order","name":"order","type":"tuple"},{"internalType":"bytes","name":"signature","type":"bytes"},{"internalType":"bytes","name":"interaction","type":"bytes"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"},{"internalType":"uint256","name":"skipPermitAndThresholdAmount","type":"uint256"},{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"permit","type":"bytes"}],"name":"fillOrderToWithPermit","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"gt","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"salt","type":"uint256"},{"internalType":"address","name":"makerAsset","type":"address"},{"internalType":"address","name":"takerAsset","type":"address"},{"internalType":"address","name":"maker","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"address","name":"allowedSender","type":"address"},{"internalType":"uint256","name":"makingAmount","type":"uint256"},{"internalType":"uint256","name":"takingAmount","type":"uint256"},{"internalType":"uint256","name":"offsets","type":"uint256"},{"internalType":"bytes","name":"interactions","type":"bytes"}],"internalType":"struct OrderLib.Order","name":"order","type":"tuple"}],"name":"hashOrder","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"increaseNonce","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"maker","type":"address"},{"internalType":"uint256","name":"slot","type":"uint256"}],"name":"invalidatorForOrderRFQ","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"lt","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonce","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"makerAddress","type":"address"},{"internalType":"uint256","name":"makerNonce","type":"uint256"}],"name":"nonceEquals","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"offsets","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"or","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"orderHash","type":"bytes32"}],"name":"remaining","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"orderHash","type":"bytes32"}],"name":"remainingRaw","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32[]","name":"orderHashes","type":"bytes32[]"}],"name":"remainingsRaw","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"rescueFunds","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"simulate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IAggregationExecutor","name":"executor","type":"address"},{"components":[{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"contract IERC20","name":"dstToken","type":"address"},{"internalType":"address payable","name":"srcReceiver","type":"address"},{"internalType":"address payable","name":"dstReceiver","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"minReturnAmount","type":"uint256"},{"internalType":"uint256","name":"flags","type":"uint256"}],"internalType":"struct GenericRouter.SwapDescription","name":"desc","type":"tuple"},{"internalType":"bytes","name":"permit","type":"bytes"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"},{"internalType":"uint256","name":"spentAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"time","type":"uint256"}],"name":"timestampBelow","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"timeNonceAccount","type":"uint256"}],"name":"timestampBelowAndNonceEquals","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"minReturn","type":"uint256"},{"internalType":"uint256[]","name":"pools","type":"uint256[]"}],"name":"uniswapV3Swap","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"int256","name":"amount0Delta","type":"int256"},{"internalType":"int256","name":"amount1Delta","type":"int256"},{"internalType":"bytes","name":"","type":"bytes"}],"name":"uniswapV3SwapCallback","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"minReturn","type":"uint256"},{"internalType":"uint256[]","name":"pools","type":"uint256[]"}],"name":"uniswapV3SwapTo","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"minReturn","type":"uint256"},{"internalType":"uint256[]","name":"pools","type":"uint256[]"},{"internalType":"bytes","name":"permit","type":"bytes"}],"name":"uniswapV3SwapToWithPermit","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"minReturn","type":"uint256"},{"internalType":"uint256[]","name":"pools","type":"uint256[]"}],"name":"unoswap","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"minReturn","type":"uint256"},{"internalType":"uint256[]","name":"pools","type":"uint256[]"}],"name":"unoswapTo","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"minReturn","type":"uint256"},{"internalType":"uint256[]","name":"pools","type":"uint256[]"},{"internalType":"bytes","name":"permit","type":"bytes"}],"name":"unoswapToWithPermit","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
    BASE_URL = "https://api.1inch.dev/swap/v5.2/1/swap?src=%s&dst=%s&amount=%d&from=%s&slippage=%d&allowPartialFill=%s&disableEstimate=%s"

    headers = {'accept': 'application/json', 'Authorization': f'Bearer {API_KEY}'}

    src_token = '0x03Be5C903c727Ee2C8C4e9bc0AcC860Cca4715e2'
    dst_token = ETHAddr.WETH
    amount = 1000000000000000000

    value = 0
    if src_token == ETHAddr.E_ADDRESS:
        value = amount

    local_node_eth.unlock_account(GNOSIS_DAO)

    src_token_contract = w3.eth.contract(address=src_token, abi=AddressesAndAbis[Chain.Ethereum].ERC20.abi)

    # Approve src_token with 1inch Aggregation Router as spender
    src_token_contract.functions.approve(_1INCH_AGGREGATION_ROUTER, 115792089237316195423570985008687907853269984665640564039457584007913129639935).transact({"from": GNOSIS_DAO})

    api_response = requests.get(BASE_URL % (src_token.lower(), dst_token.lower(), amount, GNOSIS_DAO, 2, False, True), headers=headers).json()

    router_contract = w3.eth.contract(address=_1INCH_AGGREGATION_ROUTER, abi=ABI_ROUTER)

    func_obj, func_params = router_contract.decode_function_input(api_response['tx']['data'])

    # https://github.com/1inch/1inchProtocol/blob/811f7b69b67d1d9657e3e9c18a2e97f3e2b2b33a/README.md#flags-description
    flags = 0

    if src_token == ETHAddr.E_ADDRESS:
        src_token_balance_before = w3.eth.get_balance(GNOSIS_DAO)
    else:
        src_token_balance_before = get_balance(w3, src_token, GNOSIS_DAO)
    
    if dst_token == ETHAddr.E_ADDRESS:
        dst_token_balance_before = w3.eth.get_balance(GNOSIS_DAO)
    else:  
        dst_token_balance_before = get_balance(w3, dst_token, GNOSIS_DAO)

    swap = func_obj(**func_params).transact({"from": GNOSIS_DAO, "value": value})
    
    if src_token == ETHAddr.E_ADDRESS:
        src_token_balance_after = w3.eth.get_balance(GNOSIS_DAO)
    else:
        src_token_balance_after = get_balance(w3, src_token, GNOSIS_DAO)
    
    if dst_token == ETHAddr.E_ADDRESS:
        dst_token_balance_after = w3.eth.get_balance(GNOSIS_DAO)
    else:  
        dst_token_balance_after = get_balance(w3, dst_token, GNOSIS_DAO)

    collateral = ETHAddr.WETH
    flash_loan_params = encode(['address', 'address', 'address', 'address', 'address', 'bytes'], [GNOSIS_DAO, SPARK_LENDING_POOL, collateral, USER, _1INCH_AGGREGATION_ROUTER, bytes.fromhex(api_response['tx']['data'][2:])])
    print('idiota')