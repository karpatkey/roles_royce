from dataclasses import dataclass


class ETHAddr:
    AaveLendingPoolV2 = "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9"
    ParaSwapRepayAdapter = "0x80Aca0C645fEdABaa20fd2Bf0Daf57885A309FE6"
    WrappedTokenGatewayV2 = "0xEFFC18fC3b7eb8E676dac549E0c693ad50D1Ce31"
    AAVE = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"
    ABPT = "0x41A08648C3766F9F9d85598fF102a08f4ef84F84"
    stkAAVE = "0x4da27a545c0c5B758a6BA100e3a049001de870f5"
    stkABPT = "0xa1116930326D21fB917d5A27F1E9943A9595fb47"


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
    GNOSIS = Blockchain("gnosisChain", 0x64)
