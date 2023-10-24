from roles_royce.constants import Chain
from roles_royce.abi_utils import load_abi, AddressOrAbi
from ..tokens import Abis as TokenAbis


class Abis(TokenAbis): # The inheritance with TokenAbis adds the ERC20 abi
    BaseRewardPool = AddressOrAbi(abi=load_abi('base_reward_pool.json'),
                                  name='base_reward_pool')


class EthereumAddresses:
    Booster = AddressOrAbi(address='0xA57b8d98dAE62B26Ec3bcC4a365338157060B234',
                           abi=load_abi('booster.json'),
                           name='booster')


class EthereumAddressesAndAbis(Abis, EthereumAddresses):
    pass


class GnosisAddresses:
    Booster = AddressOrAbi(address='0x98Ef32edd24e2c92525E59afc4475C1242a30184',
                           abi=load_abi('booster.json'),
                           name='booster')


class GnosisAddressesAndAbis(Abis, EthereumAddresses):
    pass


AddressesAndAbis = {
    Chain.Ethereum: EthereumAddressesAndAbis,
    Chain.Gnosis: GnosisAddressesAndAbis
}
