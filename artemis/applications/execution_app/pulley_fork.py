import requests
from decouple import config


class PulleyFork(object):
    def __init__(self, chain: str):
        self.base_url: str = config("PULLEY_URL", default="http://localhost:4000", cast=str)
        c = {"ethereum": "1", "gnosis": "100"}.get(chain.lower())
        if not c:
            raise ValueError(f"Invalid blockchain: '{chain}'. Must be Ethereum or Gnosis")
        else:
            self.chain = c
        self.fork_id = ""

    def __enter__(self):
        self.fork_id = self.start()
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        requests.delete(self.url())

    def start(self):
        response = requests.post(self.base_url + "/" + self.chain + "/forks")
        self.response = response.json()
        return self.response["id"]

    def url(self):
        return self.base_url + "/forks/" + self.fork_id
