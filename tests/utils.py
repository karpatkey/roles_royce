import atexit
import codecs
import json
import logging
import os
import shutil

import pytest
import socket
import subprocess
import shlex
import time

from eth_account import Account
from eth_account.signers.local import LocalAccount

from web3 import Web3, HTTPProvider
from roles_royce.evm_utils import erc20_abi
from roles_royce.constants import ETHAddr
from .safe import SimpleSafe

REMOTE_NODE_URL = codecs.decode(
    b'x\x9c\xcb())(\xb6\xd2\xd7O-\xc9\xd0\xcdM\xcc\xcc\xcbK-\xd1K\xd7K\xccI\xceH\xcd\xad\xd4K\xce\xcf\xd5/3\xd2\x0f'
    b'u)74-6NNu\xb3\xcc\x0f\nH\n\xcb\xccq4\xd4u\xcd3(53+\xf32\n(\x06\x00Q\x92\x17X',
    "zlib").decode()

ETH_FORK_NODE_URL = os.environ.get("RR_ETH_FORK_URL", REMOTE_NODE_URL)
LOCAL_NODE_PORT = 8546
LOCAL_NODE_DEFAULT_BLOCK = 17565000
RUN_LOCAL_NODE = os.environ.get("RR_RUN_LOCAL_NODE", False)
ETH_LOCAL_NODE_URL = f"http://127.0.0.1:{LOCAL_NODE_PORT}"
DIR_OF_THIS_FILE = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(__name__)


def gen_test_accounts() -> list[LocalAccount]:
    # test accounts are generated using the mnemonic:
    #   "test test test test test test test test test test test junk" and derivation path "m/44'/60'/0'/0"
    keys = [
        "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
        "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
        "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",
        "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",
        "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",
        "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e",
        "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356",
        "0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97",
        "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6"]
    return [Account.from_key(key) for key in keys]


TEST_ACCOUNTS = gen_test_accounts()
SCRAPE_ACCOUNT = Account.from_key("0xf214f2b2cd398c806f84e317254e0f0b801d0643303237d97a22a48e01628897")


@pytest.fixture(scope="module")
def web3_gnosis() -> Web3:
    return Web3(HTTPProvider("https://rpc.ankr.com/gnosis"))


@pytest.fixture(scope="module")
def web3_eth() -> Web3:
    return Web3(HTTPProvider(REMOTE_NODE_URL))


def wait_for_port(port, host='localhost', timeout=5.0):
    """Wait until a port starts accepting TCP connections."""
    start_time = time.time()
    while True:
        try:
            s = socket.create_connection((host, port), timeout=timeout)
            s.close()
            return
        except socket.error:
            time.sleep(0.05)
            if time.time() - start_time >= timeout:
                raise socket.error("Timeout waiting for port")


class SimpleDaemonRunner(object):
    def __init__(self, cmd, popen_kwargs=None):
        self.console = None
        self.proc = None
        self.cmd = cmd
        self.popen_kwargs = popen_kwargs or {}

    def start(self):
        if self.is_running():
            raise ValueError("Process is already running")
        logger.info("Starting daemon: %s %s", self.cmd, self.popen_kwargs)
        self.proc = subprocess.Popen(shlex.split(self.cmd), **self.popen_kwargs)
        atexit.register(self.stop)

    def stop(self):
        if not self.proc:
            return

        self.proc.terminate()
        stdout, stderr = self.proc.communicate(timeout=20)
        retcode = self.proc.returncode

        self.proc = None
        return retcode

    def is_running(self):
        return self.proc is not None


def fork_unlock_account(w3, address):
    """Unlock the given address on the forked node."""
    return w3.provider.make_request("anvil_impersonateAccount", [address])


def fork_reset_state(w3, url, block):
    """Reset the state of the forked node to the state of the mainnet node at the given block."""
    return w3.provider.make_request("anvil_reset", [{"forking": {"jsonRpcUrl": url, "blockNumber": block}}])


def run_hardhat():
    """Run hardhat node in the background."""
    try:
        npm = shutil.which("npm")
        subprocess.check_call([npm, "--version"])
        if "hardhat" not in json.loads(subprocess.check_output([npm, "list", "--json"])).get("dependencies", {}):
            raise subprocess.CalledProcessError
    except subprocess.CalledProcessError:
        raise RuntimeError('Hardhat is not installed properly. Check the README for instructions.')

    log_filename = "/tmp/rr_hardhat_log.txt"
    logger.info(f"Writing Hardhat log to {log_filename}")
    hardhat_log = open(log_filename, "w")
    npx = shutil.which("npx")
    node = SimpleDaemonRunner(
        cmd=f"{npx} hardhat node --show-stack-traces --fork '{ETH_FORK_NODE_URL}' --fork-block-number {LOCAL_NODE_DEFAULT_BLOCK} --port {LOCAL_NODE_PORT}",
        popen_kwargs={'stdout': hardhat_log, 'stderr': hardhat_log}
    )
    node.start()
    return node


def run_anvil():
    """Run anvil node in the background"""
    log_filename = "/tmp/rr_fork_node_log.txt"
    logger.info(f"Writing Anvil log to {log_filename}")
    log = open(log_filename, "w")
    node = SimpleDaemonRunner(
        cmd=f"anvil --accounts 15 -f '{ETH_FORK_NODE_URL}' --fork-block-number {LOCAL_NODE_DEFAULT_BLOCK} --port {LOCAL_NODE_PORT}",
        popen_kwargs={'stdout': log, 'stderr': log}
    )
    node.start()
    return node


@pytest.fixture(scope='session')
def local_node(request):
    """Run a local node for testing"""
    if RUN_LOCAL_NODE:
        node = run_anvil()

        def stop():
            node.stop()

        request.addfinalizer(stop)

    wait_for_port(LOCAL_NODE_PORT, timeout=20)

    w3 = Web3(HTTPProvider(f"http://localhost:{LOCAL_NODE_PORT}"))

    class LatencyMeasurerMiddleware:
        def __init__(self, make_request, w3):
            self.w3 = w3
            self.make_request = make_request

        def __call__(self, method, params):
            import time
            start_time = time.monotonic()
            response = self.make_request(method, params)
            logger.debug("Web3 time spent in %s: %f seconds", method, time.monotonic() - start_time)
            return response

    w3.middleware_onion.add(LatencyMeasurerMiddleware, "call_counter")

    fork_reset_state(w3, url=ETH_FORK_NODE_URL, block=LOCAL_NODE_DEFAULT_BLOCK)
    assert w3.eth.block_number == LOCAL_NODE_DEFAULT_BLOCK
    return w3


@pytest.fixture(autouse=True)
def local_node_reset(local_node):
    """Reset the local node state after each test"""
    fork_reset_state(local_node, url=ETH_FORK_NODE_URL, block=LOCAL_NODE_DEFAULT_BLOCK)


def local_node_set_block(w3, block):
    """Set the local node to a specific block"""
    fork_reset_state(w3, url=ETH_FORK_NODE_URL, block=block)


@pytest.fixture(scope='session')
def accounts() -> list[LocalAccount]:
    return TEST_ACCOUNTS


def steal_token(w3, token, holder, to, amount):
    """Steal tokens from a holder to another address"""
    fork_unlock_account(w3, holder)
    ctract = w3.eth.contract(address=token, abi=erc20_abi)
    tx = ctract.functions.transfer(to, amount).transact({"from": holder})
    return tx


def get_balance(w3, token, address):
    """Get the token or ETH balance of an address"""
    if token == ETHAddr.ZERO:
        return w3.eth.get_balance(address)
    else:
        ctract = w3.eth.contract(address=token, abi=erc20_abi)
        return ctract.functions.balanceOf(address).call()


def get_allowance(w3, token, owner_address, spender_address):
    """Get the token allowance of an address"""
    ctract = w3.eth.contract(address=token, abi=erc20_abi)
    return ctract.functions.allowance(owner_address, spender_address).call()


def create_simple_safe(w3: Web3, owner: LocalAccount) -> SimpleSafe:
    """Create a Safe with one owner and 100 ETH in balance"""

    safe = SimpleSafe.build(owner, ETH_LOCAL_NODE_URL)
    top_up_address(w3=w3, address=safe.address, amount=100)
    fork_unlock_account(w3, safe.address)
    return safe


def top_up_address(w3: Web3, address: str, amount: int) -> None:
    """Top up an address with ETH"""
    w3.eth.send_transaction({"to": address, "value": Web3.to_wei(amount, "ether"), "from": SCRAPE_ACCOUNT.address})
