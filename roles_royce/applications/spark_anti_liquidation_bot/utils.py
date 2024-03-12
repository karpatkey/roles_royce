from dataclasses import dataclass, field
import threading
from prometheus_client import Gauge
import schedule
import time
from decouple import config
from web3.types import Address, ChecksumAddress
from web3 import Web3
from roles_royce.toolshed.alerting.alerting import Messenger, LoggingLevel
from roles_royce.toolshed.anti_liquidation.spark import SparkCDP
import logging
