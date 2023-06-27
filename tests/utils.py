import atexit
import logging
import os
import pytest
import socket
import subprocess
import shlex
import time

from web3 import Web3, HTTPProvider

ETH_FORK_NODE_URL = os.environ.get("RR_ETH_FORK_URL", "https://rpc.ankr.com/eth")
LOCAL_NODE_PORT = 8546
ETH_LOCAL_NODE_URL = f"http://127.0.0.1:{LOCAL_NODE_PORT}"
DIR_OF_THIS_FILE = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def web3_gnosis() -> Web3:
    return Web3(HTTPProvider("https://rpc.ankr.com/gnosis"))


@pytest.fixture(scope="module")
def web3_eth() -> Web3:
    return Web3(HTTPProvider(ETH_LOCAL_NODE_URL))

def wait_for_port(port, host='localhost', timeout=5.0):
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
        stdout, stderr = self.proc.communicate()
        retcode = self.proc.returncode

        self.proc = None
        return retcode

    def is_running(self):
        return self.proc is not None

def hardhat_unlock_account(w3, address):
    return w3.provider.make_request("hardhat_impersonateAccount", [address])


def hardhat_reset_state(w3, url, block):
    resp = w3.provider.make_request("hardhat_reset", [{"forking": {"jsonRpcUrl": url, "blockNumber": block}}])
    assert resp['result']


@pytest.fixture(scope='session')
def local_node(request):
    block = 17565000  # TODO: expose the configuration of the block per test
    log_filename = "/tmp/rr_hardhat_log.txt"
    logger.info(f"Writing Hardhat log to {log_filename}")
    hardhat_log = open(log_filename, "w")
    node = SimpleDaemonRunner(
        cmd=f"npx hardhat node --show-stack-traces --fork '{ETH_FORK_NODE_URL}' --fork-block-number {block} --port {LOCAL_NODE_PORT}",
             popen_kwargs={'stdout': hardhat_log, 'stderr': hardhat_log}
    )
    node.start()

    wait_for_port(LOCAL_NODE_PORT)
    w3 = Web3(HTTPProvider(f"http://localhost:{LOCAL_NODE_PORT}"))
    assert w3.eth.block_number == block

    def stop():
        node.stop()

    request.addfinalizer(stop)
    return w3

@pytest.fixture(autouse=True)
def local_node_reset(local_node):
    hardhat_reset_state(local_node, url=ETH_FORK_NODE_URL, block=17565000)