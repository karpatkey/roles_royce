from enum import IntEnum


class SwapKind(IntEnum):
    OutGivenExactIn = 0
    InGivenExactOut = 1


class PoolKind(IntEnum):
    StablePool = 0
    MetaStablePool = 1
    ComposableStablePool = 2
    WeightedPool = 3


# Refs
# StablePool encoding https://github.com/balancer/balancer-v2-monorepo/blob/d2c47f13aa5f7db1b16e37f37c9631b9a38f25a4/pkg/balancer-js/src/pool-stable/encoder.ts


# https://etherscan.io/address/0xff4ce5aaab5a627bf82f4a571ab1ce94aa365ea6#code
class StablePoolExitKind(IntEnum):
    EXACT_BPT_IN_FOR_ONE_TOKEN_OUT = 0
    EXACT_BPT_IN_FOR_TOKENS_OUT = 1
    BPT_IN_FOR_EXACT_TOKENS_OUT = 2


# https://github.com/balancer/balancer-v2-monorepo/blob/fc3e5735a07438ab506931f56adf64dede1441b1/pkg/interfaces/contracts/pool-stable/StablePoolUserData.sol#L4
class StablePoolv2ExitKind(IntEnum):
    EXACT_BPT_IN_FOR_ONE_TOKEN_OUT = 0
    BPT_IN_FOR_EXACT_TOKENS_OUT = 1
    EXACT_BPT_IN_FOR_ALL_TOKENS_OUT = 2
    RECOVERY_MODE_EXIT_KIND = 255


# TODO: Check if there are any deployed pools with this enum

# Weighted pools v1 uses the same exit kind enum as StablePoolExitKind, versions after v1 use StablePoolv2ExitKind, see StablePoolUserData
# https://github.com/balancer/balancer-v2-monorepo/blob/fc3e5735a07438ab506931f56adf64dede1441b1/pkg/interfaces/contracts/pool-weighted/WeightedPoolUserData.sol


# Composable stable pools use the same exit kind enum as StablePoolExitKind but with a different ordering, also they have a recovery mode
# https://github.com/balancer/balancer-v2-monorepo/blob/fc3e5735a07438ab506931f56adf64dede1441b1/pkg/pool-stable/contracts/ComposableStablePool.sol#L53
# https://docs.balancer.fi/reference/joins-and-exits/pool-exits.html#userdata
class ComposableStablePoolExitKind(IntEnum):
    EXACT_BPT_IN_FOR_ONE_TOKEN_OUT = 0
    BPT_IN_FOR_EXACT_TOKENS_OUT = 1
    EXACT_BPT_IN_FOR_TOKENS_OUT = 2
    RECOVERY_MODE_EXIT_KIND = 255


# Meta stable pools use the same exit kind enum as the Weighted pools v1 and so have no recovery mode
# https://etherscan.io/address/0xb08885e6026bab4333a80024ec25a1a3e1ff2b8a#code
# https://etherscan.io/address/0x1e19cf2d73a72ef1332c882f20534b6519be0276#code


# https://github.com/balancer/balancer-v2-monorepo/blob/fc3e5735a07438ab506931f56adf64dede1441b1/pkg/interfaces/contracts/pool-stable/StablePoolUserData.sol#L4
class StablePoolJoinKind(IntEnum):
    INIT = 0
    EXACT_TOKENS_IN_FOR_BPT_OUT = 1
    TOKEN_IN_FOR_EXACT_BPT_OUT = 2
    ALL_TOKENS_IN_FOR_EXACT_BPT_OUT = 3


# Composable stable pools use the StablePoolUserData for the join kind
# https://github.com/balancer/balancer-v2-monorepo/blob/fc3e5735a07438ab506931f56adf64dede1441b1/pkg/pool-stable/contracts/ComposableStablePool.sol#L53

# Weighted pools use the same join kind enum as StablePoolUserData
# https://github.com/balancer/balancer-v2-monorepo/blob/fc3e5735a07438ab506931f56adf64dede1441b1/pkg/interfaces/contracts/pool-weighted/WeightedPoolUserData.sol
