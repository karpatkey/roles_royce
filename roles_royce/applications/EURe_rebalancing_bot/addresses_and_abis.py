from defabipedia.types import Chains, load_local_abi, ContractSpec, ContractAbi, ContractAddress


class GnosisChainAddressesAndAbis:
    DepositZap = ContractSpec(address='0xE3FFF29d4DC930EBb787FeCd49Ee5963DADf60b6',
                              abi=load_local_abi('deposit_zap.json'),
                              name='deposit_zap')
    ChainlinkFeed = ContractSpec(address='0xab70BCB260073d036d1660201e9d5405F5829b7a',
                                 abi=load_local_abi('eur_chainlink_feed.json'),
                                 name='eur_chainlink_feed')
    ERC20 = ContractAbi(abi=load_local_abi('erc20.json'),
                        name='erc20')
    WXDAI = ContractAddress(address='0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d',
                            name='wxdai')
    EURe = ContractAddress(address='0xcB444e90D8198415266c6a2724b7900fb12FC56E',
                           name='eure')


AddressesAndAbis = {
    Chains.Gnosis: GnosisChainAddressesAndAbis
}
