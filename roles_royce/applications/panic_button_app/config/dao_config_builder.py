from web3 import Web3
from roles_royce.applications.panic_button_app.config.config_builder import DAOStrategiesBuilder, DAO, \
    BalancerPosition, AuraPosition, LidoPosition
import os
from defabipedia.types import Chains, Blockchain


def main(dao: DAO, blockchain: Blockchain, balancer: list[BalancerPosition], aura: list[AuraPosition], lido: list[LidoPosition]):
    PUBLIC_ETH_NODE_URL = 'https://rpc.mevblocker.io'
    PUBLIC_GC_NODE_URL = 'https://rpc.ankr.com/gnosis'

    w3_eth = Web3(Web3.HTTPProvider(os.environ.get("RR_ETH_FORK_URL", PUBLIC_ETH_NODE_URL)))
    w3_gc = Web3(Web3.HTTPProvider(os.environ.get("RR_GC_FORK_URL", PUBLIC_GC_NODE_URL)))

    if blockchain == Chains.Gnosis:
        w3 = w3_gc
    elif blockchain == Chains.Ethereum:
        w3 = w3_eth

    jsons = DAOStrategiesBuilder(dao, blockchain, balancer=balancer, aura=aura, lido=lido)
    jsons.build_json(w3)


if __name__ == "__main__":
    main()