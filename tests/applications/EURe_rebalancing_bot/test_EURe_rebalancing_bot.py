from decimal import Decimal

from roles_royce.applications.EURe_rebalancing_bot.swaps import Swapper, SwapsData, SwapsDataManager
from roles_royce.evm_utils import erc20_abi
from tests.utils import accounts, assign_role, local_node_gc


def test_swaps_data():
    swaps_data = SwapsData(
        amount_WXDAI=100,
        amount_EURe=1000,
        EURe_to_WXDAI=1053.445869120268,
        WXDAI_to_EURe=94.84944577552906,
        EUR_price=1.056273,
    )
    assert swaps_data.drift_EURe_to_WXDAI == -0.002676515332429963
    assert swaps_data.drift_WXDAI_to_EURe == 0.001869086376554252


def test_get_EURe_to_WXDAI_curve(local_node_gc):
    w3 = local_node_gc.w3

    manager = SwapsDataManager(w3)
    assert manager.get_EURe_to_WXDAI_curve(193) == 204.17807942284594


def test_get_WXDAI_to_EURe_curve(local_node_gc):
    w3 = local_node_gc.w3

    manager = SwapsDataManager(w3)
    assert manager.get_WXDAI_to_EURe_curve(200) == 188.8180456000913


def test_get_EUR_oracle_price(local_node_gc):
    w3 = local_node_gc.w3

    manager = SwapsDataManager(w3)
    # Since there's no Fixer API key set the function returns the Chainlink price
    assert manager.get_EUR_oracle_price() == 1.0617255


def test_get_data(local_node_gc):
    w3 = local_node_gc.w3
    manager = SwapsDataManager(w3)
    swaps_data = manager.get_data(100, 1000)
    assert swaps_data == SwapsData(
        amount_WXDAI=100,
        amount_EURe=1000,
        EURe_to_WXDAI=1057.8967239949632,
        WXDAI_to_EURe=94.4092662187878,
        EUR_price=1.0617255,
    )


def test_integration_swaps(local_node_gc, accounts):
    w3 = local_node_gc.w3

    max_slippage = 0.01
    avatar_safe_address = "0x51D34416593a8acF4127dc4a40625A8eFAB9940c"
    roles_mod_address = "0x48f9Ce12d5cc2d3655aAA6D38c5Edc6ECfBE84D7"
    # Role 1 already has the correct preset applied
    role = 1
    assign_role(local_node_gc, avatar_safe_address, roles_mod_address, role, accounts[0].address)
    private_key = accounts[0].key.hex()

    swapper = Swapper(
        w3=w3,
        private_keys=private_key,
        role=role,
        roles_mod_address=roles_mod_address,
        avatar_safe_address=avatar_safe_address,
        max_slippage=max_slippage,
    )
    swaps_data_manager = SwapsDataManager(w3)
    amount_WXDAI = 30000
    amount_EURe = 50900

    contract_EURe = w3.eth.contract(address="0xcB444e90D8198415266c6a2724b7900fb12FC56E", abi=erc20_abi)
    contract_WXDAI = w3.eth.contract(address="0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d", abi=erc20_abi)

    data = swaps_data_manager.get_data(amount_WXDAI, amount_EURe)
    balance_WXDAI_1 = contract_WXDAI.functions.balanceOf(avatar_safe_address).call()
    balance_EURe_1 = contract_EURe.functions.balanceOf(avatar_safe_address).call()
    assert data.drift_EURe_to_WXDAI == -0.004606515670540268
    assert data.drift_WXDAI_to_EURe == 0.0015133013027883724
    assert balance_WXDAI_1 == 52698145428369714746848
    assert balance_EURe_1 == 155137225438047710385402

    tx_receipt_EURe_to_WXDAI = swapper.swap_WXDAI_for_EURe(data)
    assert tx_receipt_EURe_to_WXDAI.status == 1

    data = swaps_data_manager.get_data(amount_WXDAI, amount_EURe)
    balance_WXDAI_2 = contract_WXDAI.functions.balanceOf(avatar_safe_address).call()
    balance_EURe_2 = contract_EURe.functions.balanceOf(avatar_safe_address).call()
    assert data.drift_EURe_to_WXDAI == -0.0033362264860316015
    assert data.drift_WXDAI_to_EURe == -0.0005208130376402886
    assert balance_WXDAI_2 == 22698145428369714746848
    assert balance_WXDAI_2 == balance_WXDAI_1 - int(Decimal(amount_WXDAI) * Decimal(10**18))
    assert balance_EURe_2 == 183430354569876169864074

    tx_receipt_EURe_to_WXDAI = swapper.swap_EURe_for_WXDAI(data)
    assert tx_receipt_EURe_to_WXDAI.status == 1

    data = swaps_data_manager.get_data(amount_WXDAI, amount_EURe)
    balance_WXDAI_3 = contract_WXDAI.functions.balanceOf(avatar_safe_address).call()
    balance_EURe_3 = contract_EURe.functions.balanceOf(avatar_safe_address).call()
    assert data.drift_EURe_to_WXDAI == -0.005351780119551619
    assert data.drift_WXDAI_to_EURe == 0.0027580600458207982
    assert balance_WXDAI_3 == 76559677600609370000862
    assert balance_EURe_3 == 132530354569876169864074
    assert balance_EURe_3 == balance_EURe_2 - int(Decimal(amount_EURe) * Decimal(10**18))
