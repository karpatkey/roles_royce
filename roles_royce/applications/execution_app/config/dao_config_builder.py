from defabipedia.types import Blockchain
from web3 import Web3

from roles_royce.applications.execution_app.config.config_builder import (
    DAO,
    AuraPosition,
    BalancerPosition,
    DAOStrategiesBuilder,
    LidoPosition,
    WalletPosition,
)
from roles_royce.applications.execution_app.pulley_fork import PulleyFork


def main(
    dao: DAO,
    blockchain: Blockchain,
    balancer: list[BalancerPosition],
    aura: list[AuraPosition],
    lido: list[LidoPosition],
    wallet_tokens: list[WalletPosition],
):
    with PulleyFork(blockchain) as fork:
        w3 = Web3(Web3.HTTPProvider(fork.url()))

        strategies = DAOStrategiesBuilder(
            dao, blockchain, balancer=balancer, aura=aura, lido=lido, wallet_tokens=wallet_tokens
        )
        strategies_dict = strategies.build_dict(w3)
        return strategies_dict
