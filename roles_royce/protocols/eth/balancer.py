from enum import IntEnum
import eth_abi
from roles_royce.constants import ETHAddr, CrossChainAddr
from roles_royce.protocols.base import Method, InvalidArgument, AvatarSafeAddress, Address
from roles_royce.protocols.base import BaseApproveForToken


# Refs
# StablePool encoding https://github.com/balancer/balancer-v2-monorepo/blob/d2c47f13aa5f7db1b16e37f37c9631b9a38f25a4/pkg/balancer-js/src/pool-stable/encoder.ts


class ApproveForVault(BaseApproveForToken):
    """approve Token with BalancerVault as spender"""
    fixed_arguments = {"spender": CrossChainAddr.BalancerVault}


# There is another ExitKind that is for Weighted Pools
class StablePoolExitKind(IntEnum):
    EXACT_BPT_IN_FOR_ONE_TOKEN_OUT = 0
    BPT_IN_FOR_EXACT_TOKENS_OUT = 1
    EXACT_BPT_IN_FOR_ALL_TOKENS_OUT = 2


class QueryExit(Method):
    """calculate amounts out for certain BPTin"""
    name = "queryExit"


# When providing your assets, you must ensure that the tokens are sorted numerically by token address.
# It's also important to note that the values in minAmountsOut correspond to the same index value in assets,
# so these arrays must be made in parallel after sorting.

class Exit(Method):
    name = "exitPool"
    in_signature = (
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

    def __init__(self, pool_id: str, avatar: Address, assets: list[Address], min_amounts_out: list[int], user_data: list):
        super().__init__(avatar=avatar)
        self.args.pool_id = pool_id
        self.args.assets = assets
        self.args.min_amounts_out = min_amounts_out
        self.args.user_data = self.encode_user_data(user_data)
        self.args.request = [self.args.assets, self.args.min_amounts_out, self.args.user_data, self.fixed_arguments['to_internal_balance']]

    def encode_user_data(self, user_data):
        return eth_abi.encode(self.user_data_abi, user_data)


class SingleAssetExit(Exit):
    """Single Asset Exit

    User sends a precise quantity of BPT, and receives an estimated but unknown (computed at run time) quantity of a single token.
    """

    exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT
    user_data_abi = ['uint256', 'uint256', 'uint256']

    def __init__(self, pool_id: str, avatar: Address, assets: list[Address], min_amounts_out: list[int],
                 bpt_amount_in: int, exit_token_index: int):
        """

        :param bpt_amount_in: the amount of BPT to be burned
        :param exit_token_index: the index of the token to removed from the pool
        """
        super().__init__(pool_id, avatar, assets, min_amounts_out, user_data=[self.exit_kind, bpt_amount_in, exit_token_index])


class ProportionalExit(Exit):
    """Proportional Exit

    User sends a precise quantity of BPT, and receives an estimated but unknown (computed at run time) quantities of all tokens.
    """

    exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_ALL_TOKENS_OUT
    user_data_abi = ['uint256', 'uint256']

    def __init__(self, pool_id: str, avatar: Address, assets: list[Address], min_amounts_out: list[int], bpt_amount_in: int):
        """
        :param bpt_amount_in: the amount of BPT to burn in exchange for withdrawn tokens
        """
        super().__init__(pool_id, avatar, assets, min_amounts_out, user_data=[self.exit_kind, bpt_amount_in])


class CustomExit(Exit):
    """Custom Exit

    User sends an estimated but unknown (computed at run time) quantity of BPT, and receives precise quantities of specified tokens.
    """
    exit_kind = StablePoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT
    user_data_abi = ['uint256', 'uint256[]', 'uint256']

    def __init__(self, pool_id: str, avatar: Address, assets: list[Address],
                 amounts_out: list[int], max_bpt_amount_in: int):
        """

        :param amounts_out: are the amounts of each token to be withdrawn from the pool
        :param max_bpt_amount_in: is the minimum acceptable BPT to burn in return for withdrawn tokens
        """
        super().__init__(pool_id, avatar, assets, amounts_out, user_data=[self.exit_kind, amounts_out, max_bpt_amount_in])


class QueryExitMixin:
    name = "queryExit"
    target_address = '0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5'
    out_signature = [("bpt_in", "uint256"), ("amounts_out", "uint256[]")]

class SingleAssetQueryExit(QueryExitMixin, SingleAssetExit):
    pass

class ProportionalExitQueryExit(QueryExitMixin, ProportionalExit):
    pass

class CustomQueryExit(QueryExitMixin, CustomExit):
    pass

# There is another JoinKind that is for Weighted Pools
class StablePoolJoinKind(IntEnum):
    EXACT_TOKENS_IN_FOR_BPT_OUT = 0
    TOKEN_IN_FOR_EXACT_BPT_OUT = 1
    ALL_TOKENS_IN_FOR_EXACT_BPT_OUT = 2


class QueryJoin(Method):
    """calculate BPT out for certain tokens in"""
    name = "queryJoin"


# When providing your assets, you must ensure that the tokens are sorted numerically by token address.
# It's also important to note that the values in maxAmountsIn correspond to the same index value in assets,
# so these arrays must be made in parallel after sorting.

class Join(Method):
    name = "joinPool"
    in_signature = (
        ("pool_id", "bytes32"),
        ("sender", "address"),
        ("recipient", "address"),
        ("request", (
            ("assets", "address[]"),  # list of tokens, ordered numerically
            ("max_amounts_in", "uint256[]"),  # the higher limits for the tokens to deposit
            ("user_data", "bytes"),  # userData encodes a ExitKind to tell the pool what style of join you're performing
            ("to_internal_balance", "bool"))
         )
    )
    fixed_arguments = {"sender": AvatarSafeAddress, "recipient": AvatarSafeAddress, "to_internal_balance": False}
    target_address = CrossChainAddr.BalancerVault
    exit_kind: StablePoolJoinKind
    user_data_abi = None

    def __init__(self, pool_id: str, avatar: Address, assets: list[Address], max_amounts_in: list[int], user_data: list):
        super().__init__(avatar=avatar)
        self.args.pool_id = pool_id
        self.args.assets = assets
        self.args.max_amounts_in = max_amounts_in
        self.args.user_data = self.encode_user_data(user_data)
        self.args.request = [self.args.assets, self.args.max_amounts_in, self.args.user_data, self.fixed_arguments['to_internal_balance']]

    def encode_user_data(self, user_data):
        return eth_abi.encode(self.user_data_abi, user_data)


class SingleAssetJoin(Join):
    """Single Asset Join

    User sends an estimated but unknown (computed at run time) quantity of a single token, and receives a precise quantity of BPT.
    """

    join_kind = StablePoolJoinKind.TOKEN_IN_FOR_EXACT_BPT_OUT
    user_data_abi = ['uint256', 'uint256', 'uint256']

    def __init__(self, pool_id: str, avatar: Address, assets: list[Address], max_amounts_in: list[int],
                 bpt_amount_out: int, join_token_index: int):
        """

        :param bpt_amount_out: the amount of BPT to be minted
        :param join_token_index: the index of the token to enter the pool
        """
        super().__init__(pool_id, avatar, assets, max_amounts_in, user_data=[self.join_kind, bpt_amount_out, join_token_index])


class ProportionalJoin(Join):
    """Proportional Join

    User sends estimated but unknown (computed at run time) quantities of tokens, and receives precise quantity of BPT.
    """

    join_kind = StablePoolJoinKind.ALL_TOKENS_IN_FOR_EXACT_BPT_OUT
    user_data_abi = ['uint256', 'uint256']

    def __init__(self, pool_id: str, avatar: Address, assets: list[Address], max_amounts_in: list[int], bpt_amount_out: int):
        """
        :param bpt_amount_out: the amount of BPT to mint in exchange for deposited tokens
        """
        super().__init__(pool_id, avatar, assets, max_amounts_in, user_data=[self.join_kind, bpt_amount_out])


class ExactTokensJoin(Join):
    """Exact Tokens Join

    User sends precise quantities of tokens, and receives an estimated but unknown (computed at run time) quantity of BPT.
    """
    join_kind = StablePoolJoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT
    user_data_abi = ['uint256', 'uint256[]', 'uint256']

    def __init__(self, pool_id: str, avatar: Address, assets: list[Address],
                 amounts_in: list[int], min_bpt_out: int):
        """

        :param amounts_in: are the amounts of each token to be deposited into the pool
        :param min_bpt_out: is the minimum acceptable BPT to mint in return for deposited tokens
        """
        super().__init__(pool_id, avatar, assets, amounts_in, user_data=[self.join_kind, amounts_in, min_bpt_out])


class QueryJoinMixin:
    name = "queryJoin"
    target_address = '0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5'
    out_signature = [("bpt_out", "uint256"), ("amounts_in", "uint256[]")]

class SingleAssetQueryJoin(QueryJoinMixin, SingleAssetJoin):
    pass

class ProportionalExitQueryJoin(QueryJoinMixin, ProportionalJoin):
    pass

class ExactAssetQueryJoin(QueryJoinMixin, ExactTokensJoin):
    pass