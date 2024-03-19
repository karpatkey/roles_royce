from defabipedia.types import Blockchain
from web3 import Web3

from roles_royce.applications.panic_button_app.config.config_builder import (
    DAO,
    AuraPosition,
    BalancerPosition,
    DAOStrategiesBuilder,
    LidoPosition,
)
from roles_royce.applications.panic_button_app.pulley_fork import PulleyFork


def main(
    dao: DAO,
    blockchain: Blockchain,
    balancer: list[BalancerPosition],
    aura: list[AuraPosition],
    lido: list[LidoPosition],
):
    with PulleyFork(blockchain) as fork:
        w3 = Web3(Web3.HTTPProvider(fork.url()))

        strategies = DAOStrategiesBuilder(dao, blockchain, balancer=balancer, aura=aura, lido=lido)
        strategies_dict = strategies.build_dict(w3)
        return strategies_dict


if __name__ == "__main__":
    main()
