from roles_royce.applications.EURe_rebalancing_bot.utils import SwapsData, Swapper, SwapsDataManager
from tests.utils import web3_gnosis


def test_swaps_data(web3_gnosis):
    swaps_data = SwapsData(amount_WXDAI=100,
                           amount_EURe=1000,
                           EURe_to_WXDAI=1053.445869120268,
                           WXDAI_to_EURe=94.84944577552906,
                           EUR_price=1.056273)
    assert swaps_data.get_EURe_to_WXDAI_drift() == -0.002676515332429963
    assert swaps_data.get_WXDAI_to_EURe_drift() == 0.001869086376554252


def test_get_data(web3_gnosis):
    manager = SwapsDataManager(web3_gnosis)
    swaps_data = manager.get_data(100, 1000)
    assert swaps_data == SwapsData(amount_WXDAI=100,
                                   amount_EURe=1000,
                                   EURe_to_WXDAI=1053.445869120268,
                                   WXDAI_to_EURe=94.84944577552906,
                                   EUR_price=1.056273)


def test_get_EURe_to_WXDAI_curve(web3_gnosis):
    manager = SwapsDataManager(web3_gnosis)
    assert manager.get_EURe_to_WXDAI_curve(193) == 203.3151952479325


def test_get_WXDAI_to_EURe_curve(web3_gnosis):
    manager = SwapsDataManager(web3_gnosis)
    assert manager.get_WXDAI_to_EURe_curve(200) == 189.69887814278448


def test_get_EUR_oracle_price(web3_gnosis):
    manager = SwapsDataManager(web3_gnosis)
    # Since there's no Fixer API key set the function returns the Chainlink price
    assert manager.get_EUR_oracle_price() == 1.05536
