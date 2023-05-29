import pytest
from web3 import Web3, HTTPProvider


@pytest.fixture(scope="module")
def web3_gnosis() -> Web3:
    return Web3(HTTPProvider("https://rpc.ankr.com/gnosis"))


@pytest.fixture(scope="module")
def web3_eth() -> Web3:
    return Web3(HTTPProvider("https://rpc.ankr.com/eth"))
