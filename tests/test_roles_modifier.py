from unittest.mock import patch

import pytest

from roles_royce.roles_modifier import (
    AGGRESIVE_FEE_MULTIPLER,
    AGGRESIVE_GAS_LIMIT_MULTIPLIER,
    NORMAL_FEE_MULTIPLER,
    NORMAL_GAS_LIMIT_MULTIPLIER,
    GasStrategies,
    RolesMod,
    set_gas_strategy,
)

from .utils import local_node_gc

ROLE = 2
ROLES_MOD_ADDRESS = "0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503"
ACCOUNT = "0x7e19DE37A31E40eec58977CEA36ef7fB70e2c5CD"

USDT = "0x4ECaBa5870353805a9F068101A40E0f32ed605C6"
TEST_BLOCK = 28209960


class RolesModTester(RolesMod):
    """Test class that captures the tx and do not send it to the blockchain"""

    def _sign_transaction(self, tx):
        self._tx = tx
        return super()._sign_transaction(tx)

    def _send_raw_transaction(self, raw_transaction):
        return bytes()

    def estimate_gas(self, contract_address: str, data: str, block: int | str = "latest") -> int:
        return super().estimate_gas(contract_address, data, block=TEST_BLOCK)


@pytest.mark.skip(reason="test passes locally but we get different gas results on CI")
def test_check_and_execute(local_node_gc):
    w3 = local_node_gc.w3
    local_node_gc.set_block(TEST_BLOCK)
    usdt_approve = "0x095ea7b30000000000000000000000007f90122bf0700f9e7e1f688fe926940e8839f35300000000000000000000000000000000000000000000000000000000000003e8"
    roles = RolesModTester(
        role=ROLE, contract_address="0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503", web3=w3, account=ACCOUNT
    )

    assert roles.check(contract_address=USDT, data=usdt_approve)

    roles.private_key = "0xa60429f7d6b751ca19d52302826b4a611893fbb138f0059f354b79846f2ab125"
    with patch.object(roles.web3.eth, "get_transaction_count", lambda x: 42):
        roles.execute(contract_address="0x4ECaBa5870353805a9F068101A40E0f32ed605C6", data=usdt_approve, check=False)
        assert roles._tx["value"] == 0
        assert roles._tx["chainId"] == 0x64
        # Different Rpc endpoints return different values for the gas
        # "https://rpc.ankr.com/gnosis" returns 132_451
        # "https://gnosis-mainnet.public.blastapi.io" returns 142_641
        # Some endpoints fail when calling the estimate_gas method
        assert roles._tx["gas"] == 132_451 or roles._tx["gas"] == 142_641
        assert roles._tx["nonce"] == 42


def test_gas_limit_estimation(local_node_gc):
    w3 = local_node_gc.w3
    local_node_gc.set_block(TEST_BLOCK)
    usdt_approve = "0x095ea7b30000000000000000000000007f90122bf0700f9e7e1f688fe926940e8839f35300000000000000000000000000000000000000000000000000000000000003e8"
    roles = RolesModTester(
        role=ROLE, contract_address="0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503", web3=w3, account=ACCOUNT
    )
    # Different Rpc endpoints return different values for the gas
    # "https://rpc.ankr.com/gnosis" returns 101887
    # "https://gnosis-mainnet.public.blastapi.io" returns 94608
    # Some endpoints fail when calling the estimate_gas method
    assert (
        roles.estimate_gas(contract_address=USDT, data=usdt_approve, block=TEST_BLOCK) == 94608
        or roles.estimate_gas(contract_address=USDT, data=usdt_approve) == 101887
    )


@pytest.mark.skip(reason="test passes locally but we get different gas results on CI")
def test_gas_strategy(local_node_gc):
    w3 = local_node_gc.w3
    local_node_gc.set_block(TEST_BLOCK)
    usdt_approve = "0x095ea7b30000000000000000000000007f90122bf0700f9e7e1f688fe926940e8839f35300000000000000000000000000000000000000000000000000000000000003e8"

    estimated_gas = 100
    base_fee_per_gas = 50
    with patch.object(RolesModTester, "estimate_gas", lambda *args, **kwargs: estimated_gas):
        with patch.object(RolesModTester, "get_base_fee_per_gas", lambda *args, **kwargs: base_fee_per_gas):
            roles = RolesModTester(
                role=ROLE, contract_address="0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503", web3=w3, account=ACCOUNT
            )
            tx = roles.build(contract_address=USDT, data=usdt_approve, max_priority_fee=2000)
            assert tx["gas"] == estimated_gas * NORMAL_GAS_LIMIT_MULTIPLIER
            assert tx["maxPriorityFeePerGas"] == 2000
            assert tx["maxFeePerGas"] == 2000 + base_fee_per_gas * NORMAL_FEE_MULTIPLER

    set_gas_strategy(GasStrategies.AGGRESIVE)

    estimated_gas = 100
    base_fee_per_gas = 50
    with patch.object(RolesModTester, "estimate_gas", lambda *args, **kwargs: estimated_gas):
        with patch.object(RolesModTester, "get_base_fee_per_gas", lambda *args, **kwargs: base_fee_per_gas):
            roles = RolesModTester(
                role=ROLE, contract_address="0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503", web3=w3, account=ACCOUNT
            )
            tx = roles.build(contract_address=USDT, data=usdt_approve, max_priority_fee=2000)
            assert tx["gas"] == estimated_gas * AGGRESIVE_GAS_LIMIT_MULTIPLIER
            assert tx["maxPriorityFeePerGas"] == 2000
            assert tx["maxFeePerGas"] == 2000 + base_fee_per_gas * AGGRESIVE_FEE_MULTIPLER
