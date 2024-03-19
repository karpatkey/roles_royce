import requests


class PulleyFork(object):
    def __init__(self, chain: str):
        self.base_url = "http://localhost:4000"
        self.chain = {"ethereum": "1", "gnosis": "100"}.get(chain)
        if not self.chain:
            raise ValueError(f"Invalid blockchain: #{chain}. Must be Ethereum or Gnosis")
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
