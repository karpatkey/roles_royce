from roles_royce.constants import StrEnum
from defabipedia.types import Chains, load_abi, ContractAbi, ContractSpec


class Abis:
    ERC20 = ContractAbi(abi=load_abi('erc20.json'), name='erc20')


class EthereumAddresses(StrEnum):
    ZERO = "0x0000000000000000000000000000000000000000"
    AAVE = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"
    ABPT = "0x41A08648C3766F9F9d85598fF102a08f4ef84F84"
    AURA = "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF"
    AURABAL = "0x616e8BfA43F920657B3497DBf40D6b1A02D4608d"
    stkAURABAL = "0xfAA2eD111B4F580fCb85C48E6DC6782Dc5FCD7a6"
    BAL = "0xba100000625a3754423978a60c9317c58a424e3D"
    GNO = "0x6810e776880C02933D47DB1b9fc05908e5386b96"
    rETH = "0xae78736Cd615f374D3085123A210448E74Fc6393"
    spGNO = "0x7b481aCC9fDADDc9af2cBEA1Ff2342CB1733E50F"
    stkAAVE = "0x4da27a545c0c5B758a6BA100e3a049001de870f5"
    stkABPT = "0xa1116930326D21fB917d5A27F1E9943A9595fb47"
    stETH = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    wstETH = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
    unstETH = "0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1"
    DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    sDAI = "0x83F20F44975D03b1b09e64809B757c47f942BEeA"
    USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


Addresses = {
    Chains.Ethereum: EthereumAddresses,
}


# Before adding tokens to the EthereumContractSpecs, make sure there's no other functions needed other than the ones
# in the ERC20 abi
class EthereumContractSpecs:
    DAI = ContractSpec(address='0x6B175474E89094C44Da98b954EedeAC495271d0F',
                       abi=load_abi('erc20.json'),
                       name='DAI')


ContractSpecs = {
    Chains.Ethereum: EthereumContractSpecs,
}