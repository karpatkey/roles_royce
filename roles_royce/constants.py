from dataclasses import dataclass
from web3 import Web3


class CrossChainAddr:
    BalancerVault = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"


class ETHAddr:
    ZERO = "0x0000000000000000000000000000000000000000"
    AAVE = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"
    AAVE_V2_LendingPool = "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9"
    AAVE_V2_ParaSwapLiquidityAdapter = "0x135896DE8421be2ec868E0b811006171D9df802A"
    AAVE_V2_ParaSwapRepayAdapter = "0x80Aca0C645fEdABaa20fd2Bf0Daf57885A309FE6"
    AAVE_V2_WrappedTokenGateway = "0xEFFC18fC3b7eb8E676dac549E0c693ad50D1Ce31"
    AAVE_V2_Governance = "0xEC568fffba86c094cf06b22134B23074DFE2252c"
    ABPT = "0x41A08648C3766F9F9d85598fF102a08f4ef84F84"
    AURA = "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF"
    AURABAL = "0x616e8BfA43F920657B3497DBf40D6b1A02D4608d"
    AURABAL_stakingrewarder = "0x00A7BA8Ae7bca0B10A32Ea1f8e2a1Da980c6CAd2"
    AURABAL_bal_weth_depositor = "0xeAd792B55340Aa20181A80d6a16db6A0ECd1b827"
    AURABAL_bal_depositor = "0x68655AD9852a99C87C0934c7290BB62CFa5D4123"
    AURABooster = "0xA57b8d98dAE62B26Ec3bcC4a365338157060B234"
    AURALocker = "0x3Fa73f1E5d8A792C80F426fc8F84FBF7Ce9bBCAC"
    stkAURABAL = "0xfAA2eD111B4F580fCb85C48E6DC6782Dc5FCD7a6"
    AURA_rewardpool_dep_wrapper = "0xB188b1CB84Fb0bA13cb9ee1292769F903A9feC59"
    BAL = "0xba100000625a3754423978a60c9317c58a424e3D"
    B_80BAL_20WETH = "0x5c6Ee304399DBdB9C8Ef030aB642B10820DB8F56"
    BALANCER_Queries = "0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5"
    COMPOUND_Bulker = "0xa397a8C2086C554B531c02E29f3291c9704B00c7"
    COMPOUND_CometRewards = "0x1B0e765F6224C21223AeA2af16c1C46E38885a40"
    GNO = "0x6810e776880C02933D47DB1b9fc05908e5386b96"
    spGNO = "0x7b481aCC9fDADDc9af2cBEA1Ff2342CB1733E50F"
    stkAAVE = "0x4da27a545c0c5B758a6BA100e3a049001de870f5"
    stkABPT = "0xa1116930326D21fB917d5A27F1E9943A9595fb47"
    WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    stETH = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    wstETH = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
    unstETH = "0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1"
    MakerCDPManager = "0x5ef30b9986345249bc32d8928B7ee64DE9435E39"
    MakerJug = "0x19c0976f590D67707E62397C87829d896Dc0f1F1"
    MakerProxy = "0x82ecd135dce65fbc6dbdd0e4237e0af93ffd5038"
    MakerIOU = "0x447db3e7Cf4b4Dcf7cADE7bDBc375018408B8098"
    MakerDSRManager = "0x373238337Bfe1146fb49989fc222523f83081dDb"
    DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    sDAI = "0x83F20F44975D03b1b09e64809B757c47f942BEeA"
    SparkLendingPoolV3 = "0xC13e21B648A5Ee794902342038FF3aDAB66BE987"
    USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    COMPOUND_V2_Comptroller = "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B"
    COMPOUND_V2_Maximillion = "0xf859A1AD94BcF445A406B892eF0d3082f4174088"


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
    Ethereum = Blockchain("ethereum", 0x1)
    Polygon = Blockchain("polygon", 0x89)
    GnosisChain = Blockchain("gnosisChain", 0x64)

  
    @classmethod
    def get_blockchain_by_chain_id(cls, chain_id):
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, Blockchain) and attr_value.chain_id == chain_id:
                return attr_value
        raise ValueError(f"No Blockchain with chain_id {chain_id} found in Chain.")

    @classmethod
    def get_blockchain_from_web3(cls, w3: Web3):
        return cls.get_blockchain_by_chain_id(w3.eth.chain_id)
