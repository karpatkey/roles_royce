import json
import os
from functools import wraps
from pathlib import Path
from unittest.mock import patch

import pytest
from eth_account.signers.local import LocalAccount
from web3._utils.encoding import Web3JsonEncoder

from tests.utils import (
    LocalNode,
    ETH_FORK_NODE_URL,
    ETH_LOCAL_NODE_PORT,
    ETH_LOCAL_NODE_DEFAULT_BLOCK,
    _local_node,
    GC_FORK_NODE_URL,
    GC_LOCAL_NODE_PORT,
    GC_LOCAL_NODE_DEFAULT_BLOCK,
    TEST_ACCOUNTS,
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


def mark_reentrant(func):
    func._is_running = False

    @wraps(func)
    def wrapper(*args, **kwargs):
        if func._is_running:
            return func(*args, **kwargs, reentrant=True)
        try:
            func._is_running = True

            return func(*args, **kwargs)
        finally:
            func._is_running = False

    return wrapper


class RecordMiddleware:
    interactions = []

    def __init__(self, make_request, w3):
        self.w3 = w3
        self.make_request = make_request

    @classmethod
    def clear_interactions(cls):
        cls.interactions = []

    @mark_reentrant
    def __call__(self, method, params, reentrant=False):
        if not reentrant:
            self.interactions.append({"request": {"method": method, "params": list(params)}})

        response = self.make_request(method, params)

        if not reentrant:
            self.interactions.append({"response": response})
        return response


class ReplayAndAssertMiddleware:
    interactions = None
    active = False

    @classmethod
    def activate(cls, value: bool):
        cls.active = value

    @classmethod
    def set_interactions(cls, interactions: list):
        cls.interactions = interactions
        cls.interactions.reverse()

    def __init__(self, make_request, w3):
        self.w3 = w3
        self.make_request = make_request

    def __call__(self, method, params):
        if not self.active:
            return self.make_request(method, params)

        recorded_request = self.interactions.pop()
        assert "request" in recorded_request
        assert method == recorded_request["request"]["method"]

        # TODO: some tests do not provide exactly the same params every time
        # assert list(params) == recorded_request["request"]["params"]

        recorded_response = self.interactions.pop()
        assert "response" in recorded_response
        return recorded_response["response"]


class FakeLocalNode:
    def __init__(self, origintal_local_node: LocalNode):
        self.w3 = origintal_local_node.w3

    def reset_state(self):
        pass

    def unlock_account(self, address: str):
        pass

    def set_block(self, block):
        pass


def _local_node_replay(local_node, request, chain_name):
    if "record" not in local_node.w3.middleware_onion:
        local_node.w3.middleware_onion.add(RecordMiddleware, "record")
    if "replay_and_assert" not in local_node.w3.middleware_onion:
        local_node.w3.middleware_onion.add(ReplayAndAssertMiddleware, "replay_and_assert")

    test_file_path = Path(request.node.path)
    directory = test_file_path.parent.resolve()
    test_name = request.node.name
    filename = f"{test_file_path.name}::{test_name}::{chain_name}.json"
    web3_test_data_file = directory / "test_data" / filename

    if os.path.exists(web3_test_data_file):
        mode = "replay_and_assert"
    else:
        mode = "record"

    if not web3_test_data_file.parent.exists():
        os.makedirs(web3_test_data_file.parent)

    if mode == "record":
        RecordMiddleware.clear_interactions()
        ReplayAndAssertMiddleware.activate(False)
    else:
        ReplayAndAssertMiddleware.activate(True)

        with open(web3_test_data_file, "r") as f:
            ReplayAndAssertMiddleware.set_interactions(json.load(f))

    if mode == "replay_and_assert":
        with patch.object(local_node.w3.provider, "make_request", lambda *args: None):
            yield FakeLocalNode(local_node)
    else:
        yield local_node

    ReplayAndAssertMiddleware.activate(False)
    if mode == "record":
        data = json.dumps(RecordMiddleware.interactions, indent=2, cls=Web3JsonEncoder)
        with open(web3_test_data_file, "w") as f:
            f.write(data)


@pytest.fixture()
def local_node_eth_replay(local_node_eth, request) -> LocalNode:
    marker = request.node.get_closest_marker("replay_web3_off")
    if marker is not None:
        yield local_node_eth
    else:
        yield from _local_node_replay(local_node_eth, request, "ethereum")


@pytest.fixture()
def local_node_gc_replay(local_node_gc, request) -> LocalNode:
    yield from _local_node_replay(local_node_gc, request, "gnosis")
