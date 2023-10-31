from roles_royce.constants import Chain
from roles_royce.abi_utils import load_abi, AddressOrAbi

class EthereumAddressesAndAbis:
    LendingPoolV3 = AddressOrAbi(address='0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
                                abi=load_abi('lending_pool_v3.json'),
                                name='LendingPoolV3')
    aEthWETH = AddressOrAbi(address='0x4d5F47FA6A74757f35C14fD3a6Ef8E3C9BC514E8',
                            abi=load_abi('aEthWETH.json'),
                            name='aEthWETH')
    WrappedTokenGatewayV3 = AddressOrAbi(address='0xD322A49006FC828F9B5B37Ab215F99B4E5caB19C',
                            abi=load_abi('wrapped_token_gateway_v3.json'),
                            name='WrappedTokenGatewayV3')
    AAVE = AddressOrAbi(address='0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
                        abi=load_abi('Aave.json'),
                        name='Aave')
    ABPT = AddressOrAbi(address='0x41A08648C3766F9F9d85598fF102a08f4ef84F84',
                        abi=load_abi('ABPT.json'),
                        name='ABPT')
    stkAAVE = AddressOrAbi(address='0x4da27a545c0c5b758a6ba100e3a049001de870f5',
                        abi=load_abi('stkAAVE.json'),
                        name='stkAAVE')
    stkABPT = AddressOrAbi(address='0xa1116930326D21fB917d5A27F1E9943A9595fb47',
                        abi=load_abi('stkABPT.json'),
                        name='stkABPT')
    variableDebtWETH = AddressOrAbi(address='0xeA51d7853EEFb32b6ee06b1C12E6dcCA88Be0fFE',
                            abi=load_abi('variableDebtWETH.json'),
                            name='variableDebtWETH')
    stableDebtWETH = AddressOrAbi(address='0x102633152313C81cD80419b6EcF66d14Ad68949A',
                            abi=load_abi('stableDebtWETH.json'),
                            name='stableDebtWETH')

    # ERC20 = AddressOrAbi(abi=load_abi('erc20.json'), name='erc20')

AddressesAndAbis = {
    Chain.Ethereum: EthereumAddressesAndAbis
}