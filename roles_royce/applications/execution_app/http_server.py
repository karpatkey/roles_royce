from fastapi import FastAPI, Response
from pydantic import BaseModel

from .simulate import simulate as simulate_tx
from .transaction_builder import build_transaction, transaction_check

app = FastAPI()


class BuildParams(BaseModel):
    dao: str
    blockchain: str
    protocol: str
    percentage: float
    strategy: str
    arguments: list[dict[str, object]]


class CheckParams(BaseModel):
    rpc_url: str
    dao: str
    blockchain: str
    protocol: str
    tx_transactables: str


class SimulateParams(BaseModel):
    rpc_url: str
    dao: str
    blockchain: str
    transaction: dict


@app.post("/build")
def build(params: BuildParams, response: Response):
    res = build_transaction(
        dao=params.dao,
        blockchain=params.blockchain,
        protocol=params.protocol,
        percentage=params.percentage,
        exit_strategy=params.strategy,
        exit_arguments=params.arguments,
        run_check=False,
    )

    response.status_code = res["status"]

    return res


@app.post("/check")
def check(params: CheckParams, response: Response):
    res = transaction_check(
        dao=params.dao,
        blockchain=params.blockchain,
        protocol=params.protocol,
        tx_transactables=params.tx_transactables,
        rpc_url=params.rpc_url,
    )
    response.status_code = res["status"]
    return res


@app.post("/simulate")
def simulate(params: SimulateParams, response: Response):
    res = simulate_tx(
        dao=params.dao, blockchain=params.blockchain, transaction=params.transaction, rpc_url=params.rpc_url
    )
    response.status_code = res["status"]
    return res
