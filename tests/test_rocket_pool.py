from decimal import Decimal

from defabipedia import Chain
from defabipedia.rocket_pool import Abis, ContractSpecs
from pytest import approx

from roles_royce import roles
from roles_royce.protocols.eth import rocket_pool

from .roles import apply_presets, deploy_roles, setup_common_roles
from .utils import accounts, create_simple_safe, get_balance, local_node_eth, top_up_address

rETH = ContractSpecs[Chain.ETHEREUM].rETH.address

# -----------------------------------------------------#
"""Unit Tests"""


# -----------------------------------------------------#
def test_approve_for_swap_router():
    method = rocket_pool.ApproveForSwapRouter(amount=123)
    assert (
        method.data
        == "0x095ea7b300000000000000000000000016d5a408e807db8ef7c578279beeee6b228f1c1c000000000000000000000000000000000000000000000000000000000000007b"
    )


def test_deposit(local_node_eth):
    w3 = local_node_eth.w3
    local_node_eth.set_block(18443122)

    storage_contract = ContractSpecs[Chain.ETHEREUM].Storage.contract(w3)
    deposit_pool_hash = w3.solidity_keccak(["string", "string"], ["contract.address", "rocketDepositPool"]).hex()

    deposit_pool_address = storage_contract.functions.getAddress(deposit_pool_hash).call()
    method = rocket_pool.Deposit(deposit_pool=deposit_pool_address, value=1000000000000000000)
    assert method.target_address == "0xDD3f50F8A6CafbE9b31a427582963f465E745AF8"
    assert method.data == "0xd0e30db0"


def test_burn():
    method = rocket_pool.Burn(amount=123)
    assert method.data == "0x42966c68000000000000000000000000000000000000000000000000000000000000007b"


def test_swap_to():
    method = rocket_pool.SwapTo(
        uniswap_portion=0, balancer_portion=10, min_tokens_out=99, ideal_tokens_out=100, value=100
    )
    assert (
        method.data
        == "0x55362f4d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000630000000000000000000000000000000000000000000000000000000000000064"
    )


def test_swap_from():
    method = rocket_pool.SwapFrom(
        uniswap_portion=0, balancer_portion=10, min_tokens_out=99, ideal_tokens_out=100, tokens_in=100
    )
    assert (
        method.data
        == "0xa824ae8b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000006300000000000000000000000000000000000000000000000000000000000000640000000000000000000000000000000000000000000000000000000000000064"
    )


# -----------------------------------------------------#
# Integration Tests


def setup_safe(w3, accounts):
    safe = create_simple_safe(w3=w3, owner=accounts[0])
    top_up_address(w3=w3, address=safe.address, amount=99)
    roles_ctract = deploy_roles(avatar=safe.address, w3=w3)
    setup_common_roles(safe, roles_ctract)

    presets = """{"version": "1.0","chainId": "1","meta":{ "description": "","txBuilderVersion": "1.8.0"},"createdAt": 1695904723785,"transactions": [
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ae78736cd615f374d3085123a210448e74fc6393","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x33a0480c0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ae78736cd615f374d3085123a210448e74fc6393095ea7b30000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000140000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000001c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002000000000000000000000000016d5a408e807db8ef7c578279beeee6b228f1c1c","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000001000000000000000000000000ae78736cd615f374d3085123a210448e74fc639342966c68000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000001000000000000000000000000dd3f50f8a6cafbe9b31a427582963f465e745af8","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x2fcf52d10000000000000000000000000000000000000000000000000000000000000001000000000000000000000000dd3f50f8a6cafbe9b31a427582963f465e745af8d0e30db0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x5e826695000000000000000000000000000000000000000000000000000000000000000100000000000000000000000016d5a408e807db8ef7c578279beeee6b228f1c1c","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x2fcf52d1000000000000000000000000000000000000000000000000000000000000000100000000000000000000000016d5a408e807db8ef7c578279beeee6b228f1c1c55362f4d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x2fcf52d1000000000000000000000000000000000000000000000000000000000000000100000000000000000000000016d5a408e807db8ef7c578279beeee6b228f1c1ca824ae8b000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000","value": "0"}
    ]}"""
    apply_presets(
        safe, roles_ctract, json_data=presets, replaces=[("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", safe.address[2:])]
    )
    return safe, roles_ctract


def test_integration_rocket_pool_deposit_pool(local_node_eth, accounts):
    w3 = local_node_eth.w3
    local_node_eth.set_block(18443122)
    safe, roles_ctract = setup_safe(w3, accounts)

    storage_contract = ContractSpecs[Chain.ETHEREUM].Storage.contract(w3)
    deposit_pool_hash = w3.solidity_keccak(["string", "string"], ["contract.address", "rocketDepositPool"]).hex()
    protocol_settings_deposit_hash = w3.solidity_keccak(
        ["string", "string"], ["contract.address", "rocketDAOProtocolSettingsDeposit"]
    ).hex()

    deposit_pool_address = storage_contract.functions.getAddress(deposit_pool_hash).call()
    deposit_pool_contract = w3.eth.contract(address=deposit_pool_address, abi=Abis[Chain.ETHEREUM].DepositPool.abi)
    protocol_settings_deposit_address = storage_contract.functions.getAddress(protocol_settings_deposit_hash).call()
    protocol_settings_deposit_contract = w3.eth.contract(
        address=protocol_settings_deposit_address, abi=Abis[Chain.ETHEREUM].ProtocolSettingsDeposit.abi
    )
    rETH_contract = ContractSpecs[Chain.ETHEREUM].rETH.contract(w3)
    exchange_rate = rETH_contract.functions.getExchangeRate().call()
    swap_router_contract = ContractSpecs[Chain.ETHEREUM].SwapRouter.contract(w3)

    eth_amount = 1000000000000000000

    assert protocol_settings_deposit_contract.functions.getMinimumDeposit().call() < eth_amount

    # capacityNeeded
    capacity_needed = deposit_pool_contract.functions.getBalance().call() + eth_amount
    # maxDepositPoolSize
    max_deposit_pool_size = protocol_settings_deposit_contract.functions.getMaximumDepositPoolSize().call()

    if capacity_needed > max_deposit_pool_size:
        # optimiseSwapTo
        # @param _amount The amount of ETH to swap
        # @param _steps The more number of steps used the more optimal the swap will be (10 is a reasonable number for most swaps)
        optimise_swap_to = swap_router_contract.functions.optimiseSwapTo(eth_amount, 10).call()

        # swapTo
        swap_to = rocket_pool.SwapTo(
            uniswap_portion=optimise_swap_to[0][0],
            balancer_portion=optimise_swap_to[0][1],
            min_tokens_out=int(Decimal(optimise_swap_to[1] * 0.99)),
            ideal_tokens_out=optimise_swap_to[1],
            value=eth_amount,
        )
        roles.send([swap_to], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3)

        rETH_balance = get_balance(w3, rETH, safe.address)
        assert rETH_balance == approx(optimise_swap_to[1])

    else:
        deposit = rocket_pool.Deposit(deposit_pool=deposit_pool_address, value=eth_amount)
        roles.send([deposit], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3)

        rETH_balance = get_balance(w3, rETH, safe.address)
        # Staking Directly via Rocket Pool
        # The advantage is that you will always get exactly as much rETH as your ETH is worth
        # (minus a 0.05% deposit fee), since Rocket Pool's contracts will directly mint the
        # rETH that you receive.
        assert rETH_balance == approx((eth_amount / (exchange_rate / 10**18)) * 0.9995)

        # burn
        burn = rocket_pool.Burn(amount=rETH_balance)
        roles.send([burn], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3)

        rETH_balance = get_balance(w3, rETH, safe.address)
        assert rETH_balance == 0


def test_integration_rocket_pool_secondary_markets(local_node_eth, accounts):
    w3 = local_node_eth.w3
    local_node_eth.set_block(18463312)
    safe, roles_ctract = setup_safe(w3, accounts)

    storage_contract = ContractSpecs[Chain.ETHEREUM].Storage.contract(w3)
    deposit_pool_hash = w3.solidity_keccak(["string", "string"], ["contract.address", "rocketDepositPool"]).hex()
    protocol_settings_deposit_hash = w3.solidity_keccak(
        ["string", "string"], ["contract.address", "rocketDAOProtocolSettingsDeposit"]
    ).hex()

    deposit_pool_address = storage_contract.functions.getAddress(deposit_pool_hash).call()
    deposit_pool_contract = w3.eth.contract(address=deposit_pool_address, abi=Abis[Chain.ETHEREUM].DepositPool.abi)
    protocol_settings_deposit_address = storage_contract.functions.getAddress(protocol_settings_deposit_hash).call()
    protocol_settings_deposit_contract = w3.eth.contract(
        address=protocol_settings_deposit_address, abi=Abis[Chain.ETHEREUM].ProtocolSettingsDeposit.abi
    )
    rETH_contract = ContractSpecs[Chain.ETHEREUM].rETH.contract(w3)
    exchange_rate = rETH_contract.functions.getExchangeRate().call()
    swap_router_contract = ContractSpecs[Chain.ETHEREUM].SwapRouter.contract(w3)

    eth_amount = 1000000000000000000

    assert protocol_settings_deposit_contract.functions.getMinimumDeposit().call() < eth_amount

    # capacityNeeded
    capacity_needed = deposit_pool_contract.functions.getBalance().call() + eth_amount
    # maxDepositPoolSize
    max_deposit_pool_size = protocol_settings_deposit_contract.functions.getMaximumDepositPoolSize().call()

    if capacity_needed > max_deposit_pool_size:
        # optimiseSwapTo
        # @param _amount The amount of ETH to swap
        # @param _steps The more number of steps used the more optimal the swap will be (10 is a reasonable number for most swaps)
        optimise_swap_to = swap_router_contract.functions.optimiseSwapTo(eth_amount, 10).call()

        # swapTo
        swap_to = rocket_pool.SwapTo(
            uniswap_portion=optimise_swap_to[0][0],
            balancer_portion=optimise_swap_to[0][1],
            min_tokens_out=int(Decimal(optimise_swap_to[1] * 0.99)),
            ideal_tokens_out=optimise_swap_to[1],
            value=eth_amount,
        )
        roles.send([swap_to], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3)

        rETH_balance = get_balance(w3, rETH, safe.address)
        assert rETH_balance == approx(optimise_swap_to[1])

        # Swap the rETH for ETH in secondary markets
        # The rETH contracts does the following check to if there's sufficient  ETH balance for exchange:
        # See: function burn(uint256 _rethAmount) override external in rETH conctract
        # // Get ETH amount
        # uint256 ethAmount = getEthValue(_rethAmount);
        # // Get & check ETH balance
        # uint256 ethBalance = getTotalCollateral();
        # require(ethBalance >= ethAmount, "Insufficient ETH balance for exchange");

        # Take rETH contract logic to Python
        # total_collateral = rETH_contract.functions.getTotalCollateral().call()
        # eth_amount = total_collateral + 1000_000_000_000_000_000
        # rETH_amount = rETH_contract.functions.getRethValue(eth_amount).call()
        # if total_collateral >= eth_amount -> Swaps rETH for ETH in the Deposit Pool else swaps rETH for ETH in secondary markets
        # In this case we will swap a small amount of rETH for ETH in secondary markets without doing the check

        approve_rETH = rocket_pool.ApproveForSwapRouter(amount=rETH_balance)
        roles.send([approve_rETH], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3)

        # optimiseSwapFrom
        # @param _amount The amount of rETH to swap
        # @param _steps The more number of steps used the more optimal the swap will be (10 is a reasonable number for most swaps)
        optimise_swap_from = swap_router_contract.functions.optimiseSwapFrom(rETH_balance, 10).call()

        eth_balance_before_swap = w3.eth.get_balance(safe.address)

        # swapFrom
        swap_from = rocket_pool.SwapFrom(
            uniswap_portion=optimise_swap_from[0][0],
            balancer_portion=optimise_swap_from[0][1],
            min_tokens_out=int(Decimal(optimise_swap_from[1] * 0.99)),
            ideal_tokens_out=optimise_swap_from[1],
            tokens_in=rETH_balance,
        )
        roles.send([swap_from], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3)

        eth_balance_after_swap = w3.eth.get_balance(safe.address)
        assert eth_balance_after_swap == approx(eth_balance_before_swap + optimise_swap_from[1])

    else:
        deposit = rocket_pool.Deposit(deposit_pool=deposit_pool_address, value=eth_amount)
        roles.send([deposit], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3)

        rETH_balance = get_balance(w3, rETH, safe.address) / 10**18

        assert rETH_balance == approx(eth_amount / exchange_rate * 0.9995)
