import json
import logging
import time
from datetime import datetime

from defabipedia.types import Chain
from defabipedia.xdai_bridge import ContractSpecs

from roles_royce.applications.bridge_keeper.core import DynamicData, StaticData
from roles_royce.applications.bridge_keeper.utils import Flags
from roles_royce.toolshed.alerting.alerting import LoggingLevel, Messenger

logger = logging.getLogger(__name__)


def log_initial_data(static_data: StaticData, messenger: Messenger):
    title = "Bridge Keeper started"
    message = (
        f"  xDAI bridge address: {ContractSpecs[Chain.ETHEREUM].xDaiBridge.address}\n"
        f"  Bot address: {static_data.env.BOT_ADDRESS}\n"
        f"  Refill threshold: {static_data.env.REFILL_THRESHOLD:,.2f} DAI\n"
        f"  Invest threshold: {static_data.env.INVEST_THRESHOLD:,.2f} DAI\n"
        f"  Amount of interest to pay: {static_data.env.AMOUNT_OF_INTEREST_TO_PAY:,.2f} DAI\n"
        f"  Minutes before claim epoch to pay interest: {static_data.env.MINUTES_BEFORE_CLAIM_EPOCH}\n"
        f"  ETH gas alerting threshold: {static_data.env.GAS_ETH_THRESHOLD:,.2f} ETH\n"
    )
    messenger.log_and_alert(LoggingLevel.Info, title, message)


def log_status_update(static_data: StaticData, dynamic_data: DynamicData, flags: Flags):
    status = json.dumps(
        {
            "dynamic_data": json.loads(f"{dynamic_data}"),
            "static_data": json.loads(f"{static_data}"),
            "flags": json.loads(f"{flags}"),
        }
    )
    title = "Status update"
    message = (
        f"  {status}\n"
        f"  Static data:\n"
        f"    Refill threshold: {static_data.env.REFILL_THRESHOLD:,.2f} DAI.\n"
        f"    Invest threshold: {static_data.env.INVEST_THRESHOLD:,.2f} DAI.\n"
        f"    Amount of interest to pay: {static_data.env.AMOUNT_OF_INTEREST_TO_PAY:,.2f} DAI\n"
        f"    Minutes before claim epoch to pay interest: {static_data.env.MINUTES_BEFORE_CLAIM_EPOCH}\n"
        f"    ETH gas alerting threshold: {static_data.env.GAS_ETH_THRESHOLD} ETH\n"
        f"  Dynamic data:\n"
        f'    Bridge"s DAI balance: {dynamic_data.bridge_DAI_balance / (10 ** static_data.decimals_DAI):,.2f} DAI.\n'
        f"    Next claim epoch: {datetime.utcfromtimestamp(dynamic_data.next_claim_epoch)} UTC.\n"
        f"    Minutes left till next interest payment: {int((dynamic_data.next_claim_epoch - 60 * static_data.env.MINUTES_BEFORE_CLAIM_EPOCH - time.time())/60)}\n"
        f"    Minimum cash threshold: {dynamic_data.min_cash_threshold / (10 ** static_data.decimals_DAI):,.2f} DAI.\n"
        f"    Claimable interest: {dynamic_data.claimable / (10 ** static_data.decimals_DAI):,.2f} DAI.\n"
        f"    Minimum interest paid: {dynamic_data.min_interest_paid / (10 ** static_data.decimals_DAI):,.2f} DAI.\n"
        f'    Bot"s ETH balance: {dynamic_data.bot_ETH_balance / (10 ** 18):,.5f} ETH.\n'
        f"  Flags:\n"
        f"    Lack of gas warning: {flags.lack_of_gas_warning.is_set()}.\n"
        f"    Interest paid: {flags.interest_payed.is_set()}.\n"
        f"    Transaction executed: {flags.tx_executed.is_set()}.\n"
        f"  Execution Triggering Conditions:\n"
        f"    Interest is paid if the next claim epoch is in less than (Minutes before claim epoch) and "
        f"Minimum interest paid <  min(Amount of interest to pay, Claimable interest).\n"
        f'    The bridge is refilled if Bridge"s DAI balance < min(Refill threshold, Minimum cash threshold).\n'
        f'    DAI is invested if Bridge"s DAI balance > Invest threshold + Minimum cash threshold.'
        f"    \n"
    )

    logger.info(title + ".\n" + message)
