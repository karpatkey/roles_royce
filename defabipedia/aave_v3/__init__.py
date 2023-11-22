from defabipedia.types import Chains, load_abi, ContractSpec, ContractAbi
from ..tokens import Abis as TokenAbis


class AllAbis(TokenAbis):  # The inheritance with TokenAbis adds the ERC20 abi
    PriceOracle = ContractAbi(abi=load_abi('price_oracle.json'), name='price_oracle')

class EthereumContractSpecs:
    ProtocolDataProvider = ContractSpec(address='0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3',
                                        abi=load_abi('protocol_data_provider.json'),
                                        name='ProtocolDataProvider')
    PoolAddressesProvider = ContractSpec(address='0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e',
                                        abi=load_abi('protocol_address_provider.json'),
                                        name='PoolAddressesProvider')
    LendingPoolV3 = ContractSpec(address='0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
                                abi=load_abi('lending_pool_v3.json'),
                                name='LendingPoolV3')
    aEthWETH = ContractSpec(address='0x4d5F47FA6A74757f35C14fD3a6Ef8E3C9BC514E8',
                            abi=load_abi('aEthWETH.json'),
                            name='aEthWETH')
    WrappedTokenGatewayV3 = ContractSpec(address='0xD322A49006FC828F9B5B37Ab215F99B4E5caB19C',
                                        abi=load_abi('wrapped_token_gateway_v3.json'),
                                        name='WrappedTokenGatewayV3')
    AAVE = ContractSpec(address='0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
                        abi=load_abi('AAVE.json'),
                        name='Aave')
    ABPT = ContractSpec(address='0x41A08648C3766F9F9d85598fF102a08f4ef84F84',
                        abi=load_abi('ABPT.json'),
                        name='ABPT')
    stkAAVE = ContractSpec(address='0x4da27a545c0c5b758a6ba100e3a049001de870f5',
                            abi=load_abi('stkAAVE.json'),
                            name='stkAAVE')
    stkABPT = ContractSpec(address='0xa1116930326D21fB917d5A27F1E9943A9595fb47',
                            abi=load_abi('stkABPT.json'),
                            name='stkABPT')
    variableDebtWETH = ContractSpec(address='0xeA51d7853EEFb32b6ee06b1C12E6dcCA88Be0fFE',
                                    abi=load_abi('variableDebtWETH.json'),
                                    name='variableDebtWETH')
    stableDebtWETH = ContractSpec(address='0x102633152313C81cD80419b6EcF66d14Ad68949A',
                                abi=load_abi('stableDebtWETH.json'),
                                name='stableDebtWETH')
    ParaSwapRepayAdapter = ContractSpec(address='0x1809f186D680f239420B56948C58F8DbbCdf1E18',
                                        abi=load_abi('paraswap_repay_adapter.json'),
                                        name='ParaSwapRepayAdapter')
    ParaSwapLiquidityAdapter = ContractSpec(address='0x872fBcb1B582e8Cd0D0DD4327fBFa0B4C2730995',
                                            abi=load_abi('paraswap_liquidity_adapter.json'),
                                            name='ParaSwapLiquidityAdapter')
    GovernanceV2 = ContractSpec(address='0xEC568fffba86c094cf06b22134B23074DFE2252c',
                                abi=load_abi('governance_v2.json'),
                                name='GovernanceV2')

ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs
}

Abis = {
    Chains.Ethereum: AllAbis
}