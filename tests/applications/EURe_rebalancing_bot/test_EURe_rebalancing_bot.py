from roles_royce.applications.EURe_rebalancing_bot.swaps import SwapsData, Swapper, SwapsDataManager
from tests.utils import local_node_gc


def test_swaps_data():
    swaps_data = SwapsData(amount_WXDAI=100,
                           amount_EURe=1000,
                           EURe_to_WXDAI=1053.445869120268,
                           WXDAI_to_EURe=94.84944577552906,
                           EUR_price=1.056273)
    assert swaps_data.get_EURe_to_WXDAI_drift() == - 0.002676515332429963
    assert swaps_data.get_WXDAI_to_EURe_drift() == 0.001869086376554252


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
    assert swaps_data == SwapsData(amount_WXDAI=100,
                                   amount_EURe=1000,
                                   EURe_to_WXDAI=1057.8967239949632,
                                   WXDAI_to_EURe=94.4092662187878,
                                   EUR_price=1.0617255)
