from enum import IntEnum
import eth_abi
from roles_royce.constants import ETHAddr, CrossChainAddr
from roles_royce.protocols.base import Method, InvalidArgument, AvatarSafeAddress, Address
from roles_royce.protocols.eth.aave import Approve

# Refs
# StablePool encoding https://github.com/balancer/balancer-v2-monorepo/blob/d2c47f13aa5f7db1b16e37f37c9631b9a38f25a4/pkg/balancer-js/src/pool-stable/encoder.ts


class ApproveForVault(Approve):
    """approve Token with BalancerVault as spender"""
    fixed_arguments = {"spender": CrossChainAddr.BalancerVault}

    def __init__(self, token: Address, amount: int):
        super().__init__(amount)
        self.token = token

# There is another ExitKind that is for Weighted Pools
class StablePoolExitKind(IntEnum):
    EXACT_BPT_IN_FOR_ONE_TOKEN_OUT = 0
    EXACT_BPT_IN_FOR_TOKENS_OUT = 1
    BPT_IN_FOR_EXACT_TOKENS_OUT = 2


class QueryExit(Method):
    """calculate amounts out for certain BPTin"""
    name = "queryExit"


# When providing your assets, you must ensure that the tokens are sorted numerically by token address.
# It's also important to note that the values in minAmountsOut correspond to the same index value in assets,
# so these arrays must be made in parallel after sorting.

class Exit(Method):
    name = "exitPool"
    signature = (
        ("pool_id", "bytes32"),
        ("sender", "address"),
        ("recipient", "address"),
        ("request", (
            ("assets", "address[]"),  # list of tokens, ordered numerically
            ("min_amounts_out", "uint256[]"),  # the lower limits for the tokens to receive
            ("user_data", "bytes"),  # userData encodes a ExitKind to tell the pool what style of exit you're performing
            ("to_internal_balance", "bool"))
         )
    )
    fixed_arguments = {"sender": AvatarSafeAddress, "recipient": AvatarSafeAddress, "to_internal_balance": False}
    target_address = CrossChainAddr.BalancerVault
    exit_kind: StablePoolExitKind
    user_data_abi = None

    def encode_user_data(self, user_data):
        return eth_abi.encode(self.user_data_abi, user_data)

class SingleAssetExit(Exit):
    """Single Asset Exit

    User sends a precise quantity of BPT, and receives an estimated but unknown (computed at run time) quantity of a single token.
    """

    exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT
    user_data_abi = ['uint256', 'uint256', 'uint256']

    def __init__(self, bpt_amount_in: int, exit_token_index: int):
        """

        :param bpt_amount_in: the amount of BPT to be burned
        :param exit_token_index: the index of the token to removed from the pool
        """
        self.user_data = self.encode_user_data([self.exit_kind, bpt_amount_in, exit_token_index])

class ProportionalExit(Exit):
    """Proportional Exit

    User sends a precise quantity of BPT, and receives an estimated but unknown (computed at run time) quantities of all tokens.
    """

    exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT
    user_data_abi = ['uint256', 'uint256']

    def __init__(self, pool_id: str, avatar: Address, assets: list[Address], min_amounts_out: list[int], bpt_amount_in: int):
        """
        :param bpt_amount_in: the amount of BPT to burn in exchange for withdrawn tokens
        """
        self.pool_id = pool_id
        self.avatar = avatar
        self.assets = assets
        self.min_amounts_out = min_amounts_out
        self.user_data = self.encode_user_data([self.exit_kind, bpt_amount_in])
        self.request = [self.assets, self.min_amounts_out, self.user_data, False]


class CustomExit(Exit):
    """Custom Exit

    User sends an estimated but unknown (computed at run time) quantity of BPT, and receives precise quantities of specified tokens.
    """
    exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT
    user_data_abi = ['uint256', 'uint256[]', 'uint256']

    def __init__(self, pool_id: str, avatar: Address, amounts_out: list[int], max_bpt_amount_in: int):
        """

        :param amounts_out: are the amounts of each token to be withdrawn from the pool
        :param max_bpt_amount_in: is the minimum acceptable BPT to burn in return for withdrawn tokens
        """
        self.pool_id = pool_id
        self.user_data = self.encode_user_data([self.exit_kind, amounts_out, max_bpt_amount_in])


# example with web3/Roles https://github.com/KarpatkeyDAO/manager-role/blob/main/Balancer/boosted_pool_manager.py

# TODO: fix Method abi encoding