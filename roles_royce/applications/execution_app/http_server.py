from fastapi import FastAPI, Response
from pydantic import BaseModel

from .transaction_builder import build_transaction_env, transaction_check_env
from .utils import ENV

app = FastAPI()


class BuildParams(BaseModel):
    env: ENV
    protocol: str
    percentage: float
    strategy: str
    arguments: list[dict[str, object]]


class CheckParams(BaseModel):
    env: ENV
    protocol: str
    tx_transactables: str


@app.post("/build")
def build(params: BuildParams, response: Response):
    res = build_transaction_env(
        env=params.env,
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
    res = transaction_check_env(
        env=params.env,
        protocol=params.protocol,
        tx_transactables=params.tx_transactables,
    )
    response.status_code = res["status"]
    return res
