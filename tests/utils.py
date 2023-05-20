import pytest
from web3 import Web3, HTTPProvider


@pytest.fixture(scope="module")
def web3_gnosis():
    return Web3(HTTPProvider("https://rpc.gnosischain.com/"))


@pytest.fixture(scope="module")
def web3_eth():
    return Web3(HTTPProvider("https://rpc.ankr.com/eth"))
