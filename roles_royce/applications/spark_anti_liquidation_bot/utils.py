import logging
import threading
import time
from dataclasses import dataclass, field

import schedule
from decouple import config
from prometheus_client import Gauge
from web3 import Web3
from web3.types import Address, ChecksumAddress

from roles_royce.toolshed.alerting.alerting import LoggingLevel, Messenger
from roles_royce.toolshed.anti_liquidation.spark import SparkCDP
