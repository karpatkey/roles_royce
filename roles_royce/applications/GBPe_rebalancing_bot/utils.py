import threading
from dataclasses import dataclass, field


@dataclass
class Flags:
    # flag to stop alerting when the bot's xDAI balance is below 0.1
    lack_of_gas_warning: threading.Event = field(default_factory=threading.Event)

    # flag to stop alerting when the x3CRV balance is below 1
    lack_of_x3CRV: threading.Event = field(default_factory=threading.Event)

    # flag to stop alerting when the GBPe balance is below 1
    lack_of_GBPe: threading.Event = field(default_factory=threading.Event)

    tx_executed: threading.Event = field(default_factory=threading.Event)
