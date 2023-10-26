import logging
import time
from threading import Event, Thread

from google.cloud import bigquery
from web3 import Web3

from roles_royce.applications.spark_liquidation_bot.utils import ENV
from roles_royce.toolshed.alerting import (LoggingLevel, Messenger,
                                           SlackMessenger, TelegramMessenger)
from roles_royce.toolshed.anti_liquidation.spark.cdp import SparkCDPManager

ENV = ENV()

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
    addresses = []
    client = bigquery.Client.from_service_account_json(ENV.BIGQUERY_CREDENTIALS_PATH)

    query = """
    SELECT address FROM `karpatkey-data-warehouse.liquidation_bot_spark.dwh_gnosis_spark_user_address` 
    """
    query_job = client.query(query)
    
    for row in query_job:
        addresses.append(row.address)

    return addresses

def update_address_list():
    global current_addresses
    new_addresses = get_addresses_from_bigquery()

    # Check if there's a difference between the new and current addresses
    if new_addresses != current_addresses:
        current_addresses = new_addresses

def check_health_factor():
    """Check health factor for all addresses. Starts a thread for each address to check health factor. 
    threads are for parallel execution.
    """
    # Create threads
    threads = []

    # Start threads
    for address in current_addresses:
        thread = Thread(target=check_health_for_address, args=(address,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete 
    for thread in threads:
        thread.join()
    

def check_health_for_address(address):
    """For a single address, check health factor and send alert if it is below the threshold.

    Args:
        address (str): address to check health factor for.
    """
    spark_cdp_manager = SparkCDPManager(w3=Web3(Web3.HTTPProvider("https://gcarch.karpatkey.dev")), owner_address=address)
    health_factor = spark_cdp_manager.get_health_factor()

    if health_factor <= ENV.THRESHOLD_HEALTH_FACTOR:
        title = "Health factor dropped below the critical threshold"
        message = (f"  Current health factor: ({health_factor}).\n"
                f"  Health factor threshold: ({ENV.ALERTING_HEALTH_FACTOR}).\n"
                f"  Address: ({address}).")
        # messenger.log_and_alert(LoggingLevel.Warning, title, message, alert_flag=threshold_health_factor_flag.is_set())
        logger.info([title, message])

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
    