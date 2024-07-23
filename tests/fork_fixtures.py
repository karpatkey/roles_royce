import gzip
import json
import os
from pathlib import Path
import pytest
from eth_account.signers.local import LocalAccount
from web3._utils.encoding import Web3JsonEncoder
from web3 import Web3
from web3.providers.base import BaseProvider

from tests.fork_utils import (
    ETH_FORK_NODE_URL,
    ETH_LOCAL_NODE_PORT,
    ETH_LOCAL_NODE_DEFAULT_BLOCK,
    GC_FORK_NODE_URL,
    GC_LOCAL_NODE_PORT,
    GC_LOCAL_NODE_DEFAULT_BLOCK,
    TEST_ACCOUNTS,
    LocalNode,
    _local_node,
)


@pytest.fixture(scope="session")
def local_node_eth(request) -> LocalNode:
    node = LocalNode(ETH_FORK_NODE_URL, ETH_LOCAL_NODE_PORT, ETH_LOCAL_NODE_DEFAULT_BLOCK)
    _local_node(request, node)
    return node


@pytest.fixture(scope="session")
def local_node_gc(request) -> LocalNode:
    node = LocalNode(GC_FORK_NODE_URL, GC_LOCAL_NODE_PORT, GC_LOCAL_NODE_DEFAULT_BLOCK)
    _local_node(request, node)
    return node


@pytest.fixture(scope="session")
def accounts() -> list[LocalAccount]:
    return TEST_ACCOUNTS


class RecordMiddleware:
    interactions = []

    def __init__(self, make_request, w3):
        self.w3 = w3
        self.make_request = make_request

    @classmethod
    def clear_interactions(cls):
        cls.interactions = []

    def __call__(self, method, params, reentrant=False):
        self.interactions.append({"request": {"method": method, "params": list(params)}})
        response = self.make_request(method, params)

        del response["jsonrpc"]
        del response["id"]
        self.interactions.append({"response": response})
        return response


class ReplayAndAssertMiddleware:
    interactions = None

    @classmethod
    def set_interactions(cls, interactions: list):
        cls.interactions = interactions
        cls.interactions.reverse()

    def __init__(self, make_request, w3):
        self.w3 = w3
        self.make_request = make_request

    def __call__(self, method, params):
        recorded_request = self.interactions.pop()
        assert "request" in recorded_request
        assert method == recorded_request["request"]["method"]

        recorded_response = self.interactions.pop()
        assert "response" in recorded_response
        recorded_response["response"]["jsonrpc"] = "2.0"
        recorded_response["response"]["id"] = 69
        return recorded_response["response"]


class DoNothingWeb3Provider(BaseProvider):
    def __init__(self, chain_id):
        self.chain_id = chain_id

    def make_request(self, method, params):
        if method == "eth_chainId":
            return {"jsonrpc": "2.0", "id": 1, "result": hex(self.chain_id)}


class DoNothingLocalNode:
    def __init__(self, chain_id):
        self.w3 = Web3(DoNothingWeb3Provider(chain_id))

    def reset_state(self):
        pass

    def unlock_account(self, address: str):
        pass

    def set_block(self, block):
        pass


def _local_node_replay(local_node, request, chain_name, chain_id):
    if "record" not in local_node.w3.middleware_onion:
        local_node.w3.middleware_onion.inject(RecordMiddleware, "record", layer=0)

    test_file_path = Path(request.node.path)
    directory = test_file_path.parent.resolve()
    test_name = request.node.name
    filename = f"{test_file_path.name}-{test_name}-{chain_name}.json.gz"
    web3_test_data_file = directory / "test_data" / filename

    if os.path.exists(web3_test_data_file):
        mode = "replay_and_assert"
    else:
        mode = "record"

    if not web3_test_data_file.parent.exists():
        os.makedirs(web3_test_data_file.parent)

    RecordMiddleware.clear_interactions()

    if mode == "replay_and_assert":
        with gzip.open(web3_test_data_file, mode="rt") as f:
            ReplayAndAssertMiddleware.set_interactions(json.load(f))
        fake_local_node = DoNothingLocalNode(chain_id)
        fake_local_node.w3.middleware_onion.inject(ReplayAndAssertMiddleware, "replay_and_assert", layer=0)
        yield fake_local_node
    else:
        yield local_node

    local_node.w3.middleware_onion.remove("record")

    if mode == "record":
        # TODO: don't write the file if the test failed
        # https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures
        data = json.dumps(RecordMiddleware.interactions, indent=2, cls=Web3JsonEncoder)
        with gzip.open(web3_test_data_file, mode="wt") as f:
            f.write(data)


@pytest.fixture()
def local_node_eth_replay(local_node_eth, request) -> LocalNode:
    marker = request.node.get_closest_marker("replay_web3_off")
    if marker is not None:
        yield local_node_eth
    else:
        yield from _local_node_replay(local_node_eth, request, "ethereum", chain_id=0x1)


@pytest.fixture()
def local_node_gc_replay(local_node_gc, request) -> LocalNode:
    yield from _local_node_replay(local_node_gc, request, "gnosis", chain_id=0x64)
