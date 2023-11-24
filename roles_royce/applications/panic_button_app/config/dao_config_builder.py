from web3 import Web3
from roles_royce.applications.panic_button_app.config.config_builder import DAOStrategiesBuilder, DAO, \
    BalancerPosition, AuraPosition
import os
from defabipedia.balancer import ContractSpecs as BalancerContractSpecs
from defabipedia.types import Chains


def main(dao, blockchain, balancer, aura):
    PUBLIC_ETH_NODE_URL = 'https://eth.llamarpc.com'
    PUBLIC_GC_NODE_URL = 'https://rpc.ankr.com/gnosis'

    w3_eth = Web3(Web3.HTTPProvider(os.environ.get("RR_ETH_FORK_URL", PUBLIC_ETH_NODE_URL)))
    w3_gc = Web3(Web3.HTTPProvider(os.environ.get("RR_GC_FORK_URL", PUBLIC_GC_NODE_URL)))

    if blockchain == Chains.Gnosis:
        w3 = w3_gc
    elif blockchain == Chains.Ethereum:
        w3 = w3_eth

    jsons = DAOStrategiesBuilder(dao, blockchain, balancer=balancer, aura=aura)
    jsons.build_json(w3)


if __name__ == "__main__":
    main()