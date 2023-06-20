from dataclasses import dataclass

class CrossChainAddr:
    BalancerVault = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

class ETHAddr:
    ZERO = "0x0000000000000000000000000000000000000000"
    AAVE = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"
    AaveLendingPoolV2 = "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9"
    ABPT = "0x41A08648C3766F9F9d85598fF102a08f4ef84F84"
    AURABooster = "0xA57b8d98dAE62B26Ec3bcC4a365338157060B234"
    BAL = "0xba100000625a3754423978a60c9317c58a424e3D"
    ParaSwapRepayAdapter = "0x80Aca0C645fEdABaa20fd2Bf0Daf57885A309FE6"
    WrappedTokenGatewayV2 = "0xEFFC18fC3b7eb8E676dac549E0c693ad50D1Ce31"
    stkAAVE = "0x4da27a545c0c5B758a6BA100e3a049001de870f5"
    stkABPT = "0xa1116930326D21fB917d5A27F1E9943A9595fb47"
    WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    stETH = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    wstETH = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
    unstETH = "0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1"

class GCAddr:
    USDT = "0x4ECaBa5870353805a9F068101A40E0f32ed605C6"


@dataclass
class Blockchain:
    name: str
    chain_id: int

    def __str__(self):
        return self.name

    def __int__(self):
        return self.chain_id

    def __hash__(self):
        return self.chain_id


class Chain:
    ETHEREUM = Blockchain("ethereum", 0x1)
    POLYGON = Blockchain("polygon", 0x89)
    GC = Blockchain("gnosisChain", 0x64)
