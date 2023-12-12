from defabipedia.types import Chains, load_abi, ContractSpec, ContractAbi
from defabipedia.tokens import Abis as TokenAbis


class EthereumContractSpecs:
    CdpManager = ContractSpec(address='0x5ef30b9986345249bc32d8928B7ee64DE9435E39',
                              abi=load_abi('cdp_manager.json'),
                              name='CdpManager')
    ProxyRegistry = ContractSpec(address='0x4678f0a6958e4D2Bc4F1BAF7Bc52E8F3564f3fE4',
                                 abi=load_abi('proxy_registry.json'),
                                 name='ProxyRegistry')
    ProxyActions = ContractSpec(address='0x82ecD135Dce65Fbc6DbdD0e4237E0AF93FFD5038',
                                abi=load_abi('proxy_actions.json'),
                                name='ProxyActions')
    Vat = ContractSpec(address='0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B',
                       abi=load_abi('vat.json'),
                       name='Vat')
    Jug = ContractSpec(address='0x19c0976f590D67707E62397C87829d896Dc0f1F1',
                       abi=load_abi('jug.json'),
                       name='Jug')
    DaiJoin = ContractSpec(address='0x9759A6Ac90977b93B58547b4A71c78317f391A28',
                           abi=load_abi('dai_join.json'),
                           name='DaiJoin')
    DsrManager = ContractSpec(address='0x373238337Bfe1146fb49989fc222523f83081dDb',
                              abi=load_abi('dsr_manager.json'),
                              name='DsrManager')
    ProxyActionsDsr = ContractSpec(address='0x07ee93aEEa0a36FfF2A9B95dd22Bd6049EE54f26',
                                   abi=load_abi('proxy_actions_dsr.json'),
                                   name='ProxyActionsDsr')
    Pot = ContractSpec(address='0x197E90f9FAD81970bA7976f33CbD77088E5D7cf7',
                       abi=load_abi('pot.json'),
                       name='pot')


class EthereumAbis(TokenAbis):
    GemJoin = ContractAbi(abi=load_abi('gem_join.json'), name='GemJoin')


ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs
}

Abis = {
    Chains.Ethereum: EthereumAbis
}