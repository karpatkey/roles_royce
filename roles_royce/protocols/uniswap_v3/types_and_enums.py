from enum import IntEnum


# Possible Fees for Uniwsap v3 Pools
# https://docs.uniswap.org/sdk/v3/reference/enums/FeeAmount
class FeeAmount(IntEnum):
    """Possible Fees for Uniwsap v3 Pools."""

    LOWEST = 100
    LOW = 500
    MEDIUM = 3000
    HIGH = 10000


TICK_SPACING = {FeeAmount.LOWEST: 1, FeeAmount.LOW: 10, FeeAmount.MEDIUM: 60, FeeAmount.HIGH: 200}
