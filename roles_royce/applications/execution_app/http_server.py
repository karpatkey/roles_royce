from fastapi import FastAPI, Response
from pydantic import BaseModel

from .simulate import simulate as simulate_tx
from .transaction_builder import build_transaction, transaction_check

app = FastAPI()


class BuildParams(BaseModel):
    rpc_url: str
    dao: str
    blockchain: str
    protocol: str
    percentage: float
    strategy: str
    arguments: list[dict[str, object]]


class SimulateParams(BaseModel):
    rpc_url: str
    dao: str
    blockchain: str
    transaction: dict


@app.post("/build")
async def build(params: BuildParams, response: Response):
    res = build_transaction(
        dao=params.dao,
        blockchain=params.blockchain,
        protocol=params.protocol,
        percentage=params.percentage,
        exit_strategy=params.strategy,
        exit_arguments=params.arguments,
        run_check=False,
        # rpc_url=params.rpc_url,
    )

    response.status = res["status"]

    return res


@app.post("/check")
async def check(params: BuildParams, response: Response):
    res = transaction_check(
        dao=params.dao,
        blockchain=params.blockchain,
        protocol=params.protocol,
        percentage=params.percentage,
        exit_strategy=params.strategy,
        exit_arguments=params.arguments,
        rpc_url=params.rpc_url,
    )
    response.status = res["status"]
    return res


@app.post("/simulate")
async def sumilate(params: SimulateParams, response: Response):
    res = simulate_tx(
        dao=params.dao, blockchain=params.blockchain, transaction=params.transaction, rpc_url=params.rpc_url
    )
    response.status = res["status"]
    return res
