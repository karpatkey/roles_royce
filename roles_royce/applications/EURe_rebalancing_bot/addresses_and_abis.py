from roles_royce.constants import Chain
from roles_royce.abi_utils import load_abi, AddressOrAbi


class GnosisChainAddressesAndAbis:
    DepositZap = AddressOrAbi(address='0xE3FFF29d4DC930EBb787FeCd49Ee5963DADf60b6',
                                   abi=load_abi('deposit_zap.json'),
                                   name='deposit_zap')
    ChainlinkFeed = AddressOrAbi(address='0xab70BCB260073d036d1660201e9d5405F5829b7a',
                                 abi=load_abi('eur_chainlink_feed.json'),
                                 name='eur_chainlink_feed')
    ERC20 = AddressOrAbi(abi=load_abi('erc20.json'),
                         name='erc20')
    WXDAI = AddressOrAbi(address='0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d',
                         name='wxdai')
    EURe = AddressOrAbi(address='0xcB444e90D8198415266c6a2724b7900fb12FC56E',
                        name='eure')


AddressesAndAbis = {
    Chain.GnosisChain: GnosisChainAddressesAndAbis
}