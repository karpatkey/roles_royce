from web3 import Web3
from roles_royce.applications.panic_button_app.config.config_builder import DAOStrategiesBuilder, DAO, \
    BalancerPosition, AuraPosition, LidoPosition
import os
from defabipedia.types import Chain, Blockchain


def main(dao: DAO, blockchain: Blockchain, balancer: list[BalancerPosition], aura: list[AuraPosition], lido: list[LidoPosition]):
    PUBLIC_ETH_NODE_URL = 'https://eth.llamarpc.com'
    PUBLIC_GC_NODE_URL = 'https://rpc.ankr.com/gnosis'

    w3_eth = Web3(Web3.HTTPProvider(os.environ.get("RR_ETH_FORK_URL", PUBLIC_ETH_NODE_URL)))
    w3_gc = Web3(Web3.HTTPProvider(os.environ.get("RR_GC_FORK_URL", PUBLIC_GC_NODE_URL)))

    if blockchain == Chain.GNOSIS:
        w3 = w3_gc
    elif blockchain == Chain.ETHEREUM:
        w3 = w3_eth

    strategies = DAOStrategiesBuilder(dao, blockchain, balancer=balancer, aura=aura, lido=lido)
    strategies_dict = strategies.build_dict(w3)
    return strategies_dict


if __name__ == "__main__":
    main()