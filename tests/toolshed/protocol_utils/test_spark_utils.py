from roles_royce.toolshed.protocol_utils.spark.utils import SparkToken, SparkUtils
from tests.utils import local_node_eth


def test_chi(local_node_eth):
    w3 = local_node_eth.w3
    block = 17837956
    local_node_eth.set_block(block + 123)
    assert SparkUtils.get_chi(w3=w3, block=block) == 1027669481839376650556452943


def test_spark_token_addresses(local_node_eth):
    w3 = local_node_eth.w3
    block = 17837956
    local_node_eth.set_block(block + 123)
    assert SparkUtils.get_spark_token_addresses(w3=w3, block=block) == [
        {
            SparkToken.UNDERLYING: "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            SparkToken.INTEREST_BEARING: "0x4DEDf26112B3Ec8eC46e7E31EA5e123490B05B8B",
            SparkToken.STABLE_DEBT: "0xfe2B7a7F4cC0Fb76f7Fc1C6518D586F1e4559176",
            SparkToken.VARIABLE_DEBT: "0xf705d2B7e92B3F38e6ae7afaDAA2fEE110fE5914",
        },
        {
            SparkToken.UNDERLYING: "0x83F20F44975D03b1b09e64809B757c47f942BEeA",
            SparkToken.INTEREST_BEARING: "0x78f897F0fE2d3B5690EbAe7f19862DEacedF10a7",
            SparkToken.STABLE_DEBT: "0xEc6C6aBEd4DC03299EFf82Ac8A0A83643d3cB335",
            SparkToken.VARIABLE_DEBT: "0xaBc57081C04D921388240393ec4088Aa47c6832B",
        },
        {
            SparkToken.UNDERLYING: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            SparkToken.INTEREST_BEARING: "0x377C3bd93f2a2984E1E7bE6A5C22c525eD4A4815",
            SparkToken.STABLE_DEBT: "0x887Ac022983Ff083AEb623923789052A955C6798",
            SparkToken.VARIABLE_DEBT: "0x7B70D04099CB9cfb1Db7B6820baDAfB4C5C70A67",
        },
        {
            SparkToken.UNDERLYING: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            SparkToken.INTEREST_BEARING: "0x59cD1C87501baa753d0B5B5Ab5D8416A45cD71DB",
            SparkToken.STABLE_DEBT: "0x3c6b93D38ffA15ea995D1BC950d5D0Fa6b22bD05",
            SparkToken.VARIABLE_DEBT: "0x2e7576042566f8D6990e07A1B61Ad1efd86Ae70d",
        },
        {
            SparkToken.UNDERLYING: "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
            SparkToken.INTEREST_BEARING: "0x12B54025C112Aa61fAce2CDB7118740875A566E9",
            SparkToken.STABLE_DEBT: "0x9832D969a0c8662D98fFf334A4ba7FeE62b109C2",
            SparkToken.VARIABLE_DEBT: "0xd5c3E3B566a42A6110513Ac7670C1a86D76E13E6",
        },
        {
            SparkToken.UNDERLYING: "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
            SparkToken.INTEREST_BEARING: "0x4197ba364AE6698015AE5c1468f54087602715b2",
            SparkToken.STABLE_DEBT: "0x4b29e6cBeE62935CfC92efcB3839eD2c2F35C1d9",
            SparkToken.VARIABLE_DEBT: "0xf6fEe3A8aC8040C3d6d81d9A4a168516Ec9B51D2",
        },
        {
            SparkToken.UNDERLYING: "0x6810e776880C02933D47DB1b9fc05908e5386b96",
            SparkToken.INTEREST_BEARING: "0x7b481aCC9fDADDc9af2cBEA1Ff2342CB1733E50F",
            SparkToken.STABLE_DEBT: "0xbf13910620722D4D4F8A03962894EB3335Bf4FaE",
            SparkToken.VARIABLE_DEBT: "0x57a2957651DA467fCD4104D749f2F3684784c25a",
        },
        {
            SparkToken.UNDERLYING: "0xae78736Cd615f374D3085123A210448E74Fc6393",
            SparkToken.INTEREST_BEARING: "0x9985dF20D7e9103ECBCeb16a84956434B6f06ae8",
            SparkToken.STABLE_DEBT: "0xa9a4037295Ea3a168DC3F65fE69FdA524d52b3e1",
            SparkToken.VARIABLE_DEBT: "0xBa2C8F2eA5B56690bFb8b709438F049e5Dd76B96",
        },
    ]
