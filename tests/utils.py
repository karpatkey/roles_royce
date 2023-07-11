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
from gnosis.safe import addresses, Safe, SafeOperation
from gnosis.eth import EthereumNetwork, EthereumClient

from roles_royce import send, Chain
from roles_royce.constants import ETHAddr
from roles_royce.evm_utils import roles_abi, roles_bytecode, erc20_abi
from roles_royce.utils import MULTISENDS

REMOTE_NODE_URL = codecs.decode(b'x\x9c\x05\xc1[\x12\x80 \x08\x00\xc0\x1b\x89\x8a\xf8\xe86\xea\xc8\xc4G\xd4\x14u\xfevw\xb3\xeb\xd9\x00\x8e.'
                                b'\xaa\xcb\x9c(\xbfwwr\xc2\x87\x10\xb9M,%\xd7\xc1\x94\x02\xcd\x91V\xf6\xdc\xb0\xc6\x91C\xf0\xf4\x03~\xaa\x12\xb1',
                                "zlib")

ETH_FORK_NODE_URL = os.environ.get("RR_ETH_FORK_URL", "https://rpc.ankr.com/eth")
LOCAL_NODE_PORT = 8546
LOCAL_NODE_DEFAULT_BLOCK = 17565000
HARDHAT_STANDALONE = os.environ.get("RR_HARDHAT_STANDALONE", False)
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
    if not HARDHAT_STANDALONE:
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

        def stop():
            node.stop()

        request.addfinalizer(stop)

    wait_for_port(LOCAL_NODE_PORT)

    w3 = Web3(HTTPProvider(f"http://localhost:{LOCAL_NODE_PORT}"))
    hardhat_reset_state(w3, url=ETH_FORK_NODE_URL, block=LOCAL_NODE_DEFAULT_BLOCK)
    assert w3.eth.block_number == LOCAL_NODE_DEFAULT_BLOCK
    return w3


@pytest.fixture(autouse=True)
def local_node_reset(local_node):
    hardhat_reset_state(local_node, url=ETH_FORK_NODE_URL, block=LOCAL_NODE_DEFAULT_BLOCK)


def local_node_set_block(w3, block):
    hardhat_reset_state(w3, url=ETH_FORK_NODE_URL, block=block)


@pytest.fixture(scope='session')
def accounts() -> list[LocalAccount]:
    return TEST_ACCOUNTS


def steal_token(w3, token, holder, to, amount):
    hardhat_unlock_account(w3, holder)
    ctract = w3.eth.contract(address=token, abi=erc20_abi)
    tx = ctract.functions.transfer(to, amount).transact({"from": holder})
    return tx


def get_balance(w3, token, address):
    ctract = w3.eth.contract(address=token, abi=erc20_abi)
    return ctract.functions.balanceOf(address).call()


def create_simple_safe(owner: LocalAccount) -> Safe:
    """Create a Safe with one owner and 100 ETH in balance"""
    ethereum_client = EthereumClient(ETH_LOCAL_NODE_URL)
    # workarround https://github.com/ethereum/web3.py/pull/3002 / MethodUnavailable: {'code': -32601, 'message': 'Method eth_maxPriorityFeePerGas not found', 'data': {'message': 'Method eth_maxPriorityFeePerGas not found'}}
    # TODO: remove workaround when web3py v6.6.0 is released
    ethereum_client.w3.eth._max_priority_fee = lambda: 0
    ethereum_tx_sent = Safe.create(ethereum_client, deployer_account=owner,
                                   master_copy_address=addresses.MASTER_COPIES[EthereumNetwork.MAINNET][0][0],
                                   owners=[owner.address], threshold=1)

    safe = Safe(ethereum_tx_sent.contract_address, ethereum_client)

    ethereum_client.w3.eth.send_transaction({"to": safe.address, "value": Web3.to_wei(100, "ether"), "from": SCRAPE_ACCOUNT.address})
    hardhat_unlock_account(ethereum_client.w3, safe.address)
    return safe


def safe_send(safe, signer_key, to, data, value=0):
    safe_tx = safe.build_multisig_tx(to=to, value=value, data=data, operation=SafeOperation.CALL.value,
                                     safe_tx_gas=500000,
                                     base_gas=500000, gas_price=1, gas_token=ETHAddr.ZERO, refund_receiver=ETHAddr.ZERO)
    safe_tx.sign(signer_key)
    safe_tx.execute(signer_key)
    return safe_tx


def deploy_roles(w3, avatar):
    # Deploy a Roles contrat without using the ProxyFactory (to simplify things)
    role_constructor_bytes = "000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001"
    bytecode_without_default_constructor = roles_bytecode[:-len(role_constructor_bytes)]

    ctract = w3.eth.contract(abi=roles_abi, bytecode=bytecode_without_default_constructor)

    owner = avatar = target = w3.to_checksum_address(avatar)
    tx_receipt = ctract.constructor(owner, avatar, target).transact({"from": avatar})  # deploy!
    roles_ctract_address = w3.eth.get_transaction_receipt(tx_receipt).contractAddress

    ctract = w3.eth.contract(roles_ctract_address, abi=roles_abi)
    ctract.functions.setMultisend(MULTISENDS[Chain.ETHEREUM]).transact({"from": avatar})
    return ctract

def setup_common_roles(safe, roles_ctract):
    # set roles_mod as module of safe
    enable_module_roles = safe.contract.functions.enableModule(roles_ctract.address).build_transaction({"from": safe.address})['data']
    safe_send(safe, to=safe.address, data=enable_module_roles, signer_key=TEST_ACCOUNTS[0].key)

    # enable an asign roles to the test EOAs
    # EOA           | ROLE N | ROLE NAME
    # accounts[1]   |  1     | Manager
    # accounts[2]   |  2     | revoker
    # accounts[3]   |  3     | harvester
    # accounts[4]   |  4     | disassembler
    # accounts[5]   |  5     | swapper

    for role_number in range(1, 6):
        account = TEST_ACCOUNTS[role_number]
        enable_module = roles_ctract.functions.enableModule(account.address).build_transaction({"from": safe.address})['data']
        safe_send(safe, to=roles_ctract.address, data=enable_module, signer_key=TEST_ACCOUNTS[0].key)

        assign_role = roles_ctract.functions.assignRoles(account.address, [role_number], [True]).build_transaction({"from": safe.address})['data']
        safe_send(safe, to=roles_ctract.address, data=assign_role, signer_key=TEST_ACCOUNTS[0].key)
