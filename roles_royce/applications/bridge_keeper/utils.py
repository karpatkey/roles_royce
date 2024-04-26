import json
import threading
from dataclasses import dataclass, field


@dataclass
class Flags:
    lack_of_gas_warning: threading.Event = field(default_factory=threading.Event)
    interest_payed: threading.Event = field(default_factory=threading.Event)
    tx_executed: threading.Event = field(default_factory=threading.Event)

    def __str__(self):
        flags_dict = {attr: getattr(self, attr).is_set() for attr in self.__annotations__}
        return json.dumps(flags_dict, indent=4)
