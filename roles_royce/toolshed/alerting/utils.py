from dataclasses import dataclass
from typing import Any, Dict, Union, cast

from defabipedia.types import Blockchain, Chain
from eth_typing import HexStr
from eth_utils import event_abi_to_log_topic
from hexbytes import HexBytes
from web3 import Web3
from web3._utils.abi import get_abi_input_names, get_abi_input_types, map_abi_data
from web3._utils.normalizers import BASE_RETURN_NORMALIZERS
from web3.contract import Contract
from web3.types import Address, ChecksumAddress, TxReceipt

from roles_royce.evm_utils import erc20_abi


@dataclass
class Event:
    name: str
    topic: HexBytes
    values: dict


class EventLogDecoder:
    """Helper to decode events from tx receipts."""

    def __init__(self, contract: Contract):
        self.contract = contract
        self.event_abis = [abi for abi in self.contract.abi if abi["type"] == "event"]
        self._sign_abis = {event_abi_to_log_topic(abi): abi for abi in self.event_abis}

    def decode_log(self, result: Dict[str, Any]):
        data = b""
        for t in result["topics"]:
            data += t
        data += result["data"]
        return self.decode_event_input(data)

    def decode_event_input(self, data: Union[HexStr, str, bytes]) -> Event | None:
        # type ignored b/c expects data arg to be HexBytes
        data = HexBytes(data)  # type: ignore
        selector, params = data[:32], data[32:]

        try:
            func_abi = self._sign_abis[selector]
        except KeyError:
            return None

        names = get_abi_input_names(func_abi)
        types = get_abi_input_types(func_abi)

        decoded = self.contract.w3.codec.decode(types, cast(HexBytes, params))
        normalized = map_abi_data(BASE_RETURN_NORMALIZERS, types, decoded)
        values = dict(zip(names, normalized))
        return Event(name=func_abi["name"], topic=selector, values=values)


erc20_event_log_decoder = EventLogDecoder(Web3().eth.contract(abi=erc20_abi))


def get_token_amounts_from_transfer_events(
    tx_receipt: TxReceipt, target_address: str | ChecksumAddress | Address, w3: Web3
) -> (list[dict], str):
    transfers = []
    message = ""
    for element in tx_receipt.logs:
        address = element["address"]
        event = erc20_event_log_decoder.decode_log(element)
        if not event:
            continue

        if event.name == "Transfer" and (
            event.values["to"] == target_address or event.values["from"] == target_address
        ):
            token_address = Web3.to_checksum_address(address)
            target_address = Web3.to_checksum_address(target_address)
            token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)
            a = w3.eth.block_number
            token_decimals = token_contract.functions.decimals().call()
            token_symbol = token_contract.functions.symbol().call()

            transfer = event.values.copy()
            amount = transfer.pop("value") / (10**token_decimals)
            transfer["amount"] = amount
            transfers.append(transfer)

            if transfer["from"] == target_address:
                message = (
                    message
                    + f"  {target_address}  ----- {transfer['amount']:,.3f} {token_symbol} ---->  {transfer['to']}."
                )
            else:
                message = (
                    message
                    + f"  {target_address}  <---- {transfer['amount']:,.3f} {token_symbol} -----  {transfer['from']}."
                )
            if element != transfers[-1]:
                message = message + "\n\n"

    message = message[:-1]
    return transfers, message


ExplorerTxUrls = {Chain.ETHEREUM: "https://etherscan.io/tx/", Chain.GNOSIS: "https://gnosisscan.io/tx/"}


def get_tx_link(tx_receipt: TxReceipt, chain: Blockchain) -> str:
    return f"{ExplorerTxUrls[chain]}{tx_receipt.transactionHash.hex()}"


def get_tx_executed_msg(tx_receipt: TxReceipt, chain: Blockchain) -> (str, str):
    tx_link = get_tx_link(tx_receipt, chain)
    if tx_receipt.status == 1:
        message_slack = f"  *Txn hash (Success):* <{tx_link}|{tx_receipt.transactionHash.hex()}>."
        message = f"  Txn hash (Success): {tx_link}."
    else:
        message_slack = f"  *Txn hash (Failure):* <{tx_link}|{tx_receipt.transactionHash.hex()}>."
        message = f"  Txn hash (Failure): {tx_link}."

    return message, message_slack


def get_tx_receipt_message_with_transfers(
    tx_receipt: object, target_address: str | ChecksumAddress | Address, w3: Web3
) -> (str, str):
    chain = Chain.get_blockchain_from_web3(w3)
    tx_executed_message, tx_executed_message_slack = get_tx_executed_msg(tx_receipt, chain)
    transfers, transfers_message = get_token_amounts_from_transfer_events(tx_receipt, target_address, w3)

    if transfers_message != "":
        message = tx_executed_message + "\n\n" + transfers_message
        message_slack = tx_executed_message_slack + "\n\n" + transfers_message
    else:
        message = tx_executed_message
        message_slack = tx_executed_message_slack

    return message, message_slack
