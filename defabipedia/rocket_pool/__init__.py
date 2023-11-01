from defabipedia.types import Chains, load_abi, ContractSpec, ContractAbi
from defabipedia.tokens import Abis as TokenAbis


class EthereumContractSpecs:
    Storage = ContractSpec(address='0x1d8f8f00cfa6758d7bE78336684788Fb0ee0Fa46',
                           abi=load_abi('storage.json'),
                           name='Storage')
    SwapRouter = ContractSpec(address="0x16D5A408e807db8eF7c578279BEeEe6b228f1c1C",
                              abi=load_abi('swap_router.json'),
                              name='SwapRouter')
    rETH = ContractSpec(address="0xae78736Cd615f374D3085123A210448E74Fc6393",
                        abi=load_abi('rETH.json'),
                        name='rETH')


class EthereumAbis(TokenAbis):
    DepositPool = ContractAbi(abi=load_abi('deposit_pool.json'),
                              name='DepositPool')
    ProtocolSettingsDeposit = ContractAbi(abi=load_abi('protocol_settings_deposit.json'),
                                          name='ProtocolSettingsDeposit')


ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs
}

Abis = {
    Chains.Ethereum: EthereumAbis
}
