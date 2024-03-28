import json
from dataclasses import dataclass
from decimal import Decimal

from defabipedia.tokens import EthereumTokenAddr, erc20_contract
from defabipedia.types import Chain
from defabipedia.xdai_bridge import ContractSpecs
from web3 import Web3
from web3.types import TxReceipt

from roles_royce.applications.bridge_keeper.env import ENV
from roles_royce.applications.utils import to_dict


@dataclass
class StaticData:
    env: ENV
    decimals_DAI: int = 18

    def __str__(self):
        return json.dumps(to_dict(self, exclude_key="PRIVATE_KEY"), separators=(",", ":"))


@dataclass
class DynamicData:
    bridge_DAI_balance: int
    next_claim_epoch: int
    min_cash_threshold: int
    claimable: int
    bot_ETH_balance: int
    min_interest_paid: int

    def __str__(self):
        return json.dumps(to_dict(self, exclude_key="PRIVATE_KEY"), separators=(",", ":"))


def update_dynamic_data(w3_eth: Web3, w3_gnosis: Web3, static_data: StaticData) -> DynamicData:
    bridge_DAI_balance = (
        erc20_contract(w3=w3_eth, address=EthereumTokenAddr.DAI)
        .functions.balanceOf(ContractSpecs[Chain.ETHEREUM].xDaiBridge.address)
        .call()
    )
    bridge_contract = ContractSpecs[Chain.ETHEREUM].xDaiBridge.contract(w3_eth)
    interest_receiver_contract = ContractSpecs[Chain.GNOSIS].BridgeInterestReceiver.contract(w3_gnosis)
    min_cash_threshold = bridge_contract.functions.minCashThreshold(EthereumTokenAddr.DAI).call()
    next_claim_epoch = interest_receiver_contract.functions.nextClaimEpoch().call()
    claimable = bridge_contract.functions.interestAmount(EthereumTokenAddr.DAI).call()
    min_interest_paid = bridge_contract.functions.minInterestPaid(EthereumTokenAddr.DAI).call()
    bot_ETH_balance = w3_eth.eth.get_balance(static_data.env.BOT_ADDRESS)
    return DynamicData(
        bridge_DAI_balance=bridge_DAI_balance,
        next_claim_epoch=next_claim_epoch,
        min_cash_threshold=min_cash_threshold,
        claimable=claimable,
        min_interest_paid=min_interest_paid,
        bot_ETH_balance=bot_ETH_balance,
    )


def refill_bridge(w3: Web3, static_data: StaticData) -> TxReceipt:
    bridge_contract = ContractSpecs[Chain.ETHEREUM].xDaiBridge.contract(w3)
    unsigned_tx = bridge_contract.functions.refillBridge().build_transaction(
        {
            "from": static_data.env.BOT_ADDRESS,
            "nonce": w3.eth.get_transaction_count(static_data.env.BOT_ADDRESS),
        }
    )
    unsigned_tx.update({"gas": int(1.5 * unsigned_tx["gas"])})
    if static_data.env.PRIVATE_KEY == "":
        tx_hash = w3.eth.send_transaction(unsigned_tx)  # The account has already been unlocked in the fork
    else:
        signed_tx = w3.eth.account.sign_transaction(unsigned_tx, private_key=static_data.env.PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def invest_DAI(w3: Web3, static_data: StaticData) -> TxReceipt:
    bridge_contract = ContractSpecs[Chain.ETHEREUM].xDaiBridge.contract(w3)
    unsigned_tx = bridge_contract.functions.investDai().build_transaction(
        {
            "from": static_data.env.BOT_ADDRESS,
            "nonce": w3.eth.get_transaction_count(static_data.env.BOT_ADDRESS),
        }
    )
    unsigned_tx.update({"gas": int(1.5 * unsigned_tx["gas"])})
    if static_data.env.PRIVATE_KEY == "":
        tx_hash = w3.eth.send_transaction(unsigned_tx)  # The account has already been unlocked in the fork
    else:
        signed_tx = w3.eth.account.sign_transaction(unsigned_tx, private_key=static_data.env.PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def pay_interest(w3: Web3, static_data: StaticData, dynamic_data: DynamicData) -> TxReceipt:
    bridge_contract = ContractSpecs[Chain.ETHEREUM].xDaiBridge.contract(w3)
    # see https://etherscan.io/address/0x166124b75c798cedf1b43655e9b5284ebd5203db#code#F7#L141
    amount = min(
        int(Decimal(static_data.env.AMOUNT_OF_INTEREST_TO_PAY) * Decimal(10**static_data.decimals_DAI)),
        dynamic_data.claimable,
    )
    unsigned_tx = bridge_contract.functions.payInterest(EthereumTokenAddr.DAI, amount).build_transaction(
        {
            "from": static_data.env.BOT_ADDRESS,
            "nonce": w3.eth.get_transaction_count(static_data.env.BOT_ADDRESS),
        }
    )
    unsigned_tx.update({"gas": int(1.5 * unsigned_tx["gas"])})
    if static_data.env.PRIVATE_KEY == "":
        tx_hash = w3.eth.send_transaction(unsigned_tx)  # The account has already been unlocked in the fork
    else:
        signed_tx = w3.eth.account.sign_transaction(unsigned_tx, private_key=static_data.env.PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt
