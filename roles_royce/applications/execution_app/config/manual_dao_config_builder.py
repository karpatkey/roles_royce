import os

from defabipedia.balancer import ContractSpecs as BalancerContractSpecs
from defabipedia.types import Chain
from web3 import Web3

from roles_royce.applications.execution_app.config.config_builder import (
    DAO,
    AuraPosition,
    BalancerPosition,
    DAOStrategiesBuilder,
)


def main():
    PUBLIC_ETH_NODE_URL = "https://eth.llamarpc.com"
    PUBLIC_GC_NODE_URL = "https://rpc.ankr.com/gnosis"

    w3_eth = Web3(
        Web3.HTTPProvider(os.environ.get("RR_ETH_FORK_URL", PUBLIC_ETH_NODE_URL))
    )  # Will use the endpoint stored as github secret if possible
    w3_gc = Web3(
        Web3.HTTPProvider(os.environ.get("RR_GC_FORK_URL", PUBLIC_GC_NODE_URL))
    )  # Will use the endpoint stored as github secret if possible

    strategies_gnosis_dao_ethereum = DAOStrategiesBuilder(
        DAO.GnosisDAO,
        Chain.ETHEREUM,
        aura=[
            AuraPosition(position_id="33", bpt_address="0x1e19cf2d73a72ef1332c882f20534b6519be0276"),
            AuraPosition(position_id="35", bpt_address="0x3dd0843a028c86e0b760b1a76929d1c5ef93a2dd"),
            AuraPosition(position_id="38", bpt_address="0x92762b42a06dcdddc5b7362cfb01e631c4d44b40"),
            AuraPosition(position_id="40", bpt_address="0xde8c195aa41c11a0c4787372defbbddaa31306d2"),
        ],
    )

    strategies_gnosis_dao_ethereum.build_json(w3_eth)

    strategies_gnosis_dao_gnosis_chain = DAOStrategiesBuilder(
        DAO.GnosisDAO,
        Chain.GNOSIS,
        balancer=[
            BalancerPosition(position_id="107", bpt_address="0xa99fd9950b5d5dceeaf4939e221dca8ca9b938ab", staked=False),
            BalancerPosition(position_id="108", bpt_address="0x388cae2f7d3704c937313d990298ba67d70a3709", staked=False),
            BalancerPosition(position_id="167", bpt_address="0xbad20c15a773bf03ab973302f61fabcea5101f0a", staked=False),
            BalancerPosition(position_id="205", bpt_address="0x5519e2d8a0af0944ea639c6dbad69a174de3ecf8", staked=False),
            BalancerPosition(position_id="237", bpt_address="0x2086f52651837600180de173b09470f54ef74910", staked=False),
            BalancerPosition(position_id="238", bpt_address="0xeb30c85cc528537f5350cf5684ce6a4538e13394", staked=False),
            BalancerPosition(position_id="245", bpt_address="0x4683e340a8049261057d5ab1b29c8d840e75695e", staked=False),
            BalancerPosition(position_id="247", bpt_address="0x00df7f58e1cf932ebe5f54de5970fb2bdf0ef06d", staked=False),
            BalancerPosition(position_id="249", bpt_address="0x0c1b9ce6bf6c01f587c2ee98b0ef4b20c6648753", staked=False),
            BalancerPosition(position_id="251", bpt_address="0x4cdabe9e07ca393943acfb9286bbbd0d0a310ff6", staked=False),
            BalancerPosition(position_id="276", bpt_address="0xbc2acf5e821c5c9f8667a36bb1131dad26ed64f9", staked=False),
            BalancerPosition(position_id="320", bpt_address="0x7644fa5d0ea14fcf3e813fdf93ca9544f8567655", staked=False),
            BalancerPosition(position_id="323", bpt_address="0x06135a9ae830476d3a941bae9010b63732a055f4", staked=False),
        ],
        aura=[
            AuraPosition(position_id="275", bpt_address="0xdd439304a77f54b1f7854751ac1169b279591ef7"),
            AuraPosition(position_id="225", bpt_address="0x21d4c792ea7e38e0d0819c2011a2b1cb7252bd99"),
            AuraPosition(position_id="231", bpt_address="0xbad20c15a773bf03ab973302f61fabcea5101f0a"),
        ],
    )

    strategies_gnosis_dao_gnosis_chain.build_json(w3_gc)

    strategies_gnosis_ltd_ethereum = DAOStrategiesBuilder(
        DAO.GnosisLTD,
        Chain.ETHEREUM,
        balancer=[
            BalancerPosition(
                position_id="123", bpt_address=BalancerContractSpecs[Chain.ETHEREUM].BPT_COW_WETH.address, staked=False
            ),
            BalancerPosition(position_id="174", bpt_address="0x7b50775383d3d6f0215a8f290f2c9e2eebbeceb2", staked=False),
        ],
        aura=[AuraPosition(position_id="19", bpt_address=BalancerContractSpecs[Chain.ETHEREUM].BPT_COW_WETH.address)],
    )
    strategies_gnosis_ltd_ethereum.build_json(w3_eth)

    strategies_gnosis_ltd_gnosis_chain = DAOStrategiesBuilder(
        DAO.GnosisLTD,
        Chain.GNOSIS,
        balancer=[
            BalancerPosition(position_id="271", bpt_address="0x7644fa5d0ea14fcf3e813fdf93ca9544f8567655", staked=False)
        ],
        aura=[AuraPosition(position_id="244", bpt_address="0x2086f52651837600180de173b09470f54ef74910")],
    )

    strategies_gnosis_ltd_gnosis_chain.build_json(w3_gc)


if __name__ == "__main__":
    main()
