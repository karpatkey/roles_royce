from roles_royce.constants import Chains
from roles_royce.abi_utils import load_abi, ContractSpec, ContractAbi
from ..tokens import Abis as TokenAbis


class Abis(TokenAbis):
    BaseRewardPool = ContractAbi(abi=load_abi('base_reward_pool.json'), name='base_reward_pool')

class EthereumContractSpecs:
    Booster = ContractSpec(address='0xA57b8d98dAE62B26Ec3bcC4a365338157060B234',
                           abi=load_abi('booster.json'),
                           name='booster')


class GnosisContractSpecs:
    Booster = ContractSpec(address='0x98Ef32edd24e2c92525E59afc4475C1242a30184',
                           abi=load_abi('booster.json'),
                           name='booster')


ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs,
    Chains.Gnosis: GnosisContractSpecs
}

Abis = {
    Chains.Ethereum: Abis,
    Chains.Gnosis: Abis
}
