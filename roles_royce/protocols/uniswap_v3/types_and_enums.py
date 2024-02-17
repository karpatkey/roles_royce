from enum import IntEnum

# Possible Fees for Uniwsap v3 Pools
# https://docs.uniswap.org/sdk/v3/reference/enums/FeeAmount
class FeeAmount(IntEnum):
    LOWEST = 100
    LOW = 500
    MEDIUM = 3000
    HIGH = 10000