import concurrent
import logging
import time
from threading import Event, Thread

from google.cloud import bigquery
from prometheus_client import start_http_server as prometheus_start_http_server
from web3 import Web3

from roles_royce.applications.spark_liquidation_bot.utils import ENV, Gauges
from roles_royce.toolshed.alerting import (LoggingLevel, Messenger,
                                           SlackMessenger, TelegramMessenger)
from roles_royce.toolshed.anti_liquidation.spark import SparkCDPManager

ENV = ENV()

# Prometheus metrics from prometheus_client import Info
prometheus_start_http_server(ENV.PROMETHEUS_PORT)
gauges = Gauges()

# Alert flag
threshold_health_factor_flag = Event()

# # Messenger system
# slack_messenger = SlackMessenger(webhook=ENV.SLACK_WEBHOOK_URL)
# slack_messenger.start()
# telegram_messenger = TelegramMessenger(bot_token=ENV.TELEGRAM_BOT_TOKEN, chat_id=ENV.TELEGRAM_CHAT_ID)
# telegram_messenger.start()

# Configure logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger instance
logger = logging.getLogger(__name__)
# messenger = Messenger(slack_messenger, telegram_messenger)

# Addresses to monitor
current_addresses = []

# Here there would be the update list, every 30 mins from bigquery
# Needs the ENV variable that points to the file for credentials 
def get_addresses_from_bigquery():
    """Get addresses from the bigquery list"""
    client = bigquery.Client.from_service_account_json(ENV.BIGQUERY_CREDENTIALS_PATH)

    query = """
    SELECT address FROM `karpatkey-data-warehouse.liquidation_bot_spark.dwh_gnosis_spark_user_address` 
    """
    for _ in range(3):
        try:
            query_job = client.query(query)
            return [row.address for row in query_job]
        except Exception as e:
            logging.error(f"Error querying BigQuery: {e}. Retrying...")
            time.sleep(20)

    logger.error("Failed to retrieve addresses from BigQuery after multiple retries.")
    return []

def update_address_list():
    global current_addresses
    new_addresses = get_addresses_from_bigquery()

    # Check if there's a difference between the new and current addresses
    if new_addresses and new_addresses != current_addresses:
        current_addresses = new_addresses

MAX_THREADS = 10
def check_health_factor():
    """Check health factor for all addresses. Starts a thread for each address to check health factor. 
    threads are for parallel execution.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Use executor.submit to start tasks and collect the resulting Future objects
        futures = [executor.submit(check_health_for_address, address) for address in current_addresses]
        
        # Collect and handle results/errors
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                pass

def check_health_for_address(address):
    """For a single address, check health factor and send alert if it is below the threshold.

    Args:
        address (str): address to check health factor for.
    """
    try:
        spark_cdp_manager = SparkCDPManager(w3=Web3(Web3.HTTPProvider("https://gcarch.karpatkey.dev")), owner_address=address)
        health_factor = spark_cdp_manager.get_health_factor()

        if health_factor <= ENV.THRESHOLD_HEALTH_FACTOR:
            title = "Health factor dropped below the critical threshold"
            message = (f"  Current health factor: ({health_factor}).\n"
                    f"  Health factor threshold: ({ENV.ALERTING_HEALTH_FACTOR}).\n"
                    f"  Address: ({address}).")
            # messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=threshold_health_factor_flag.is_set())
            logger.info([title, message])

            # Get CDP data for the address to update prometheus gauges
            cdp_data = spark_cdp_manager.get_cdp_balances_data()
            list_values = [x for x in cdp_data[0].values()]

            # Update prometheus gauges
            gauges.address.set(address)
            gauges.health_factor.set(health_factor)
            gauges.underlying_address.set(list_values[0])
            gauges.interest_bearing_balance.set(list_values[1])
            gauges.stable_debt_balance.set(list_values[2])
            gauges.variable_debt_balance.set(list_values[3])
            gauges.underlying_price_usd.set(list_values[4])
            gauges.collateral_enabled.set(list_values[5])
            gauges.liquidation_threshold.set(list_values[6])
            gauges.last_updated.set_to_current_time()

    except Exception as e:
        logger.error(f"Error while checking health factor for address {address}. Error: {e}")

# --------------- This is the main function that runs the bot

def main():
    """Main function that runs the bot."""
    last_address_update = 0

    while True:
        current_time = time.time()

        if current_time - last_address_update > ENV.ADDRESS_UPDATE_INTERVAL:
            update_address_list()
            last_address_update = current_time

        # check health factor
        check_health_factor()
        # wait 3 mins
        time.sleep(ENV.COOLDOWN_MINUTES * 60)

if __name__ == "__main__":
    main()
    