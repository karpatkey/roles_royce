import eth_abi
from roles_royce.constants import ETHAddr, CrossChainAddr, MAX_UINT256
from roles_royce.protocols.base import ContractMethod, AvatarAddress, Address
from roles_royce.protocols.base import BaseApproveForToken
from web3 import Web3
from roles_royce.toolshed.protocol_utils.balancer import get_pool_kind_from_pid, get_assets_from_pid, \
    get_pool_balances_from_pid, get_bpt_index_from_composable_pid, StablePoolExitKind, StablePoolv2ExitKind, ComposableStablePoolExitKind, \
    StablePoolJoinKind, SwapKind
from decimal import Decimal
from roles_royce.toolshed.protocol_utils.balancer import PoolKind


class ApproveForVault(BaseApproveForToken):
    """approve Token with BalancerVault as spender"""
    fixed_arguments = {"spender": CrossChainAddr.BalancerVault}

class Stake(ContractMethod):
    """Stake BPT in gauge"""
    name = "deposit"
    in_signature = [("value", "uint256")]

    def __init__(self, gauge_address: Address, amount: int):
        super().__init__()
        self.target_address = gauge_address
        self.args.value = amount

class Unstake(ContractMethod):
    """Unstake BPT from gauge"""
    name = "withdraw"
    in_signature = [("value", "uint256")]

    def __init__(self, gauge_address: Address, amount: int):
        super().__init__()
        self.target_address = gauge_address
        self.args.value = amount


class QueryExit(ContractMethod):
    """calculate amounts out for certain BPTin"""
    name = "queryExit"


# When providing your assets, you must ensure that the tokens are sorted numerically by token address.
# It's also important to note that the values in minAmountsOut correspond to the same index value in assets,
# so these arrays must be made in parallel after sorting.

class Exit(ContractMethod):
    name = "exitPool"
    in_signature = (
        ("pool_id", "bytes32"),
        ("sender", "address"),
        ("recipient", "address"),
        ("request", (
            (
                ("assets", "address[]"),  # list of tokens, ordered numerically
                ("min_amounts_out", "uint256[]"),  # the lower limits for the tokens to receive
                ("user_data", "bytes"),
                # userData encodes a ExitKind to tell the pool what style of exit you're performing
                ("to_internal_balance", "bool")
            ),
            "tuple"),
         )
    )
    fixed_arguments = {"sender": AvatarAddress, "recipient": AvatarAddress, "to_internal_balance": False}
    target_address = CrossChainAddr.BalancerVault
    user_data_abi = None
    assets = None

    def __init__(self,
                 pool_id: str,
                 avatar: Address,
                 assets: list[Address],
                 min_amounts_out: list[int],
                 user_data: list):
        super().__init__(avatar=avatar)
        self.args.pool_id = pool_id
        self.args.assets = assets
        self.args.min_amounts_out = min_amounts_out
        self.args.user_data = self.encode_user_data(user_data)
        self.args.request = [self.args.assets, self.args.min_amounts_out, self.args.user_data,
                             self.fixed_arguments['to_internal_balance']]

    def encode_user_data(self, user_data):
        return eth_abi.encode(self.user_data_abi, user_data)


class _ExactBptSingleTokenExit(Exit):
    """Single Asset Exit

    User sends a precise quantity of BPT, and receives an estimated but unknown (computed at run time) quantity of a single token.
    """

    user_data_abi = ['uint256', 'uint256', 'uint256']

    def __init__(self, pool_kind: PoolKind, pool_id: str, avatar: Address, assets: list[Address],
                 bpt_amount_in: int,
                 exit_token_index: int,
                 min_amounts_out: list[int]):
        """

        :param bpt_amount_in: the amount of BPT to be burned
        :param exit_token_index: the index of the token to removed from the pool
        """
        if pool_kind == PoolKind.ComposableStablePool:
            self.exit_kind = ComposableStablePoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT
        else:
            self.exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT

        super().__init__(pool_id, avatar, assets, min_amounts_out,
                         user_data=[self.exit_kind, bpt_amount_in, exit_token_index])


class ExactBptSingleTokenExit(_ExactBptSingleTokenExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_in: int,
                 token_out_address: Address,
                 min_amount_out: int,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)
        pool_kind = get_pool_kind_from_pid(w3, pool_id)
        exit_token_index = assets.index(token_out_address)
        min_amounts_out = [0] * exit_token_index + [min_amount_out] + [0] * (
                len(assets) - exit_token_index - 1)

        super().__init__(pool_kind, pool_id, avatar, assets, bpt_amount_in, exit_token_index, min_amounts_out)


class _ExactBptProportionalExit(Exit):
    """Proportional Exit

    User sends a precise quantity of BPT, and receives an estimated but unknown (computed at run time) quantities of all tokens.
    """

    user_data_abi = ['uint256', 'uint256']

    def __init__(self,
                 pool_kind: PoolKind,
                 pool_id: str,
                 avatar: Address,
                 assets: list[Address],
                 bpt_amount_in: int,
                 min_amounts_out: list[int]):
        """
        :param bpt_amount_in: the amount of BPT to burn in exchange for withdrawn tokens
        """
        if pool_kind == PoolKind.ComposableStablePool:
            exit_kind = ComposableStablePoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT
        else:
            exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT

        super().__init__(pool_id, avatar, assets, min_amounts_out, user_data=[exit_kind, bpt_amount_in])


class ExactBptProportionalExit(_ExactBptProportionalExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str, avatar: Address,
                 bpt_amount_in: int,
                 min_amounts_out: list[int],
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)
        pool_kind = get_pool_kind_from_pid(w3, pool_id)

        super().__init__(pool_kind, pool_id, avatar, assets, bpt_amount_in, min_amounts_out)


class _ExactTokensExit(Exit):
    """Custom Exit

    User sends an estimated but unknown (computed at run time) quantity of BPT, and receives precise quantities of specified tokens.
    """
    user_data_abi = ['uint256', 'uint256[]', 'uint256']

    def __init__(self,
                 pool_kind: PoolKind,
                 pool_id: str,
                 avatar: Address,
                 assets: list[Address],
                 amounts_out: list[int],
                 max_bpt_amount_in: int):
        """

        :param amounts_out: are the amounts of each token to be withdrawn from the pool
        :param max_bpt_amount_in: is the minimum acceptable BPT to burn in return for withdrawn tokens
        """

        if pool_kind == PoolKind.ComposableStablePool:
            exit_kind = ComposableStablePoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT
        else:
            exit_kind = StablePoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT

        super().__init__(pool_id, avatar, assets, amounts_out,
                         user_data=[exit_kind, amounts_out, max_bpt_amount_in])


class ExactTokensExit(_ExactTokensExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 amounts_out: list[int],
                 max_bpt_amount_in: int,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)
        pool_kind = get_pool_kind_from_pid(w3, pool_id)

        super().__init__(pool_kind, pool_id, avatar, assets, amounts_out, max_bpt_amount_in)


class ExactSingleTokenExit(ExactTokensExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 token_out_address: Address,
                 amount_out: int,
                 max_bpt_amount_in: int,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        exit_token_index = assets.index(token_out_address)
        amounts_out = [0] * exit_token_index + [amount_out] + [0] * (len(assets) - exit_token_index - 1)

        super().__init__(w3, pool_id, avatar, amounts_out, max_bpt_amount_in, assets=assets)


class _ExactBptRecoveryModeExit(Exit):
    user_data_abi = ['uint256', 'uint256']

    def __init__(self,
                 pool_id: str,
                 avatar: Address,
                 assets: list[Address],
                 bpt_amount_in: int,
                 min_amounts_out: list[int]):
        """
        :param bpt_amount_in: the amount of BPT to burn in exchange for withdrawn tokens
        """
        exit_kind = StablePoolv2ExitKind.RECOVERY_MODE_EXIT_KIND

        super().__init__(pool_id, avatar, assets, min_amounts_out, user_data=[exit_kind, bpt_amount_in])


class ExactBptRecoveryModeExit(_ExactBptRecoveryModeExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str, avatar: Address,
                 bpt_amount_in: int,
                 min_amounts_out: list[int],
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        super().__init__(pool_id, avatar, assets, bpt_amount_in, min_amounts_out)


# -----------------------------------------------------------------------------------------------------------------------
# Query Exit

class QueryExitMixin:
    name = "queryExit"
    target_address = ETHAddr.BALANCER_Queries
    out_signature = [("bpt_in", "uint256"), ("amounts_out", "uint256[]")]


class ExactBptSingleTokenQueryExit(QueryExitMixin, ExactBptSingleTokenExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_in: int,
                 token_out_address: Address):
        super().__init__(w3, pool_id, avatar, bpt_amount_in, token_out_address, 0)


class ExactBptProportionalQueryExit(QueryExitMixin, ExactBptProportionalExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 bpt_amount_in: int,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        super().__init__(w3, pool_id, ETHAddr.ZERO, bpt_amount_in, [0] * len(assets), assets=assets)


class ExactTokensQueryExit(QueryExitMixin, ExactTokensExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 amounts_out: list[int],
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        super().__init__(w3, pool_id, avatar, amounts_out, MAX_UINT256, assets=assets)


class ExactSingleTokenQueryExit(QueryExitMixin, ExactSingleTokenExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 token_in_address: Address,
                 amount_out: int):
        super().__init__(w3, pool_id, avatar, token_in_address, amount_out, MAX_UINT256)


# TODO: I think this one is not necessary because we are not querying but calculating the balances
class ExactBptRecoveryModeQueryExit(QueryExitMixin, ExactBptRecoveryModeExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str, avatar: Address,
                 bpt_amount_in: int,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        super().__init__(w3, pool_id, avatar, bpt_amount_in, [0] * len(assets), assets=assets)


# -----------------------------------------------------------------------------------------------------------------------
# Query Join

class QueryJoin(ContractMethod):
    """calculate BPT out for certain tokens in"""
    name = "queryJoin"


# When providing your assets, you must ensure that the tokens are sorted numerically by token address.
# It's also important to note that the values in maxAmountsIn correspond to the same index value in assets,
# so these arrays must be made in parallel after sorting.

class Join(ContractMethod):
    name = "joinPool"
    in_signature = (
        ("pool_id", "bytes32"),
        ("sender", "address"),
        ("recipient", "address"),
        ("request", ((
                         ("assets", "address[]"),  # list of tokens, ordered numerically
                         ("max_amounts_in", "uint256[]"),  # the higher limits for the tokens to deposit
                         ("user_data", "bytes"),
                         # userData encodes a ExitKind to tell the pool what style of join you're performing
                         ("from_internal_balance", "bool")
                     ), "tuple")
         )
    )
    fixed_arguments = {"sender": AvatarAddress, "recipient": AvatarAddress, "from_internal_balance": False}
    target_address = CrossChainAddr.BalancerVault
    user_data_abi = None
    assets = None

    def __init__(self,
                 pool_id: str,
                 avatar: Address,
                 assets: list[Address],
                 max_amounts_in: list[int],
                 user_data: list):
        super().__init__(avatar=avatar)
        self.args.pool_id = pool_id
        self.args.assets = assets
        self.args.max_amounts_in = max_amounts_in
        self.args.user_data = self.encode_user_data(user_data)
        self.args.request = [self.args.assets, self.args.max_amounts_in, self.args.user_data,
                             self.fixed_arguments['from_internal_balance']]

    def encode_user_data(self, user_data):
        return eth_abi.encode(self.user_data_abi, user_data)


class _ExactBptSingleTokenJoin(Join):
    """Single Asset Join

    User sends an estimated but unknown (computed at run time) quantity of a single token, and receives a precise quantity of BPT.
    """

    user_data_abi = ['uint256', 'uint256', 'uint256']
    join_kind = StablePoolJoinKind.TOKEN_IN_FOR_EXACT_BPT_OUT

    def __init__(self,
                 pool_id: str,
                 avatar: Address,
                 assets: list[Address],
                 max_amounts_in: list[int],
                 bpt_amount_out: int,
                 join_token_index: int):
        """

        :param bpt_amount_out: the amount of BPT to be minted
        :param join_token_index: the index of the token to enter the pool
        """
        super().__init__(pool_id, avatar, assets, max_amounts_in,
                         user_data=[self.join_kind, bpt_amount_out, join_token_index])


class ExactBptSingleTokenJoin(_ExactBptSingleTokenJoin):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_out: int,
                 token_in_address: Address,
                 max_amount_in: int,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)
        join_token_index = assets.index(token_in_address)
        max_amounts_in = [0] * join_token_index + [max_amount_in] + [0] * (len(assets) - join_token_index - 1)

        super().__init__(pool_id, avatar, assets, max_amounts_in, bpt_amount_out, join_token_index)


class _ProportionalJoin(Join):
    """
    Proportional Join

    User sends estimated but unknown (computed at run time) quantities of tokens, and receives precise quantity of BPT.
    """

    user_data_abi = ['uint256', 'uint256']
    join_kind = StablePoolJoinKind.ALL_TOKENS_IN_FOR_EXACT_BPT_OUT

    def __init__(self,
                 pool_id: str,
                 avatar: Address,
                 assets: list[Address],
                 bpt_amount_out: int,
                 max_amounts_in: list[int]):
        """
        :param max_amounts_in: the maximum amounts of each token to be deposited into the pool
        :param bpt_amount_out: the amount of BPT to be minted
        """

        super().__init__(pool_id, avatar, assets, max_amounts_in, user_data=[self.join_kind, bpt_amount_out])


class ProportionalJoin(_ProportionalJoin):
    def __init__(self, w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_out: int,
                 max_amounts_in: list[int],
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        super().__init__(pool_id, avatar, assets, bpt_amount_out, max_amounts_in)


class _ExactTokensJoin(Join):
    """Exact Tokens Join

    User sends precise quantities of tokens, and receives an estimated but unknown (computed at run time) quantity of BPT.
    """
    user_data_abi = ['uint256', 'uint256[]', 'uint256']
    join_kind = StablePoolJoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT

    def __init__(self,
                 pool_id: str,
                 avatar: Address,
                 assets: list[Address],
                 amounts_in: list[int],
                 min_bpt_amount_out: int):
        """
        :param amounts_in: the amounts of each token to be deposited into the pool
        :param min_bpt_amount_out: the minimum acceptable BPT to be minted in return for deposited tokens

        """

        super().__init__(pool_id, avatar, assets, amounts_in,
                         user_data=[self.join_kind, amounts_in, min_bpt_amount_out])


class ExactTokensJoin(_ExactTokensJoin):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 amounts_in: list[int],
                 min_bpt_amount_out: int,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        super().__init__(pool_id, avatar, assets, amounts_in, min_bpt_amount_out)


class ExactSingleTokenJoin(_ExactTokensJoin):
    """Exact Single Token Join
    """

    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 token_in_address: Address,
                 amount_in: int,
                 min_bpt_amount_out: int,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        join_token_index = assets.index(token_in_address)
        amounts_in = [0] * join_token_index + [amount_in] + [0] * (len(assets) - join_token_index - 1)

        super().__init__(pool_id, avatar, assets, amounts_in, min_bpt_amount_out)


class QueryJoinMixin:
    name = "queryJoin"
    target_address = ETHAddr.BALANCER_Queries
    out_signature = [("bpt_out", "uint256"), ("amounts_in", "uint256[]")]


class ExactBptSingleTokenQueryJoin(QueryJoinMixin, ExactBptSingleTokenJoin):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_out: int,
                 token_in_address: Address):
        super().__init__(w3, pool_id, avatar, bpt_amount_out, token_in_address, MAX_UINT256)


class ProportionalQueryJoin(QueryJoinMixin, ProportionalJoin):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_out: int,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)
        max_amounts_in = [MAX_UINT256] * len(assets)

        super().__init__(w3, pool_id, avatar, bpt_amount_out, max_amounts_in, assets=assets)


class ExactTokensQueryJoin(QueryJoinMixin, ExactTokensJoin):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 amounts_in: list[int]):
        super().__init__(w3, pool_id, avatar, amounts_in, 0)


class ExactSingleTokenQueryJoin(QueryJoinMixin, ExactSingleTokenJoin):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 token_in_address: Address,
                 amount_in: int):
        super().__init__(w3, pool_id, avatar, token_in_address, amount_in, 0)


class SingleSwap(ContractMethod):
    name = "swap"
    in_signature = (
        ("single_swap", (
            (
                ("pool_id", "bytes32"),
                ("kind", "uint8"),
                ("asset_in", "address"),
                ("asset_out", "address"),
                ("amount", "uint256"),
                ("user_data", "bytes"),
            ),
            "tuple"),
         ),
        ("funds", (
            (
                ("sender", "address"),
                ("from_internal_balance", "bool"),
                ("recipient", "address"),
                ("to_internal_balance", "bool")
            ),
            "tuple"),
         ),
        ("limit", "uint256"),
        ("deadline", "uint256")
    )
    fixed_arguments = {"sender": AvatarAddress, "recipient": AvatarAddress, "from_internal_balance": False,
                       "to_internal_balance": False, "user_data": "0x", "deadline": MAX_UINT256}
    target_address = CrossChainAddr.BalancerVault

    def __init__(self,
                 pool_id: str,
                 avatar: Address,
                 swap_kind: SwapKind,
                 token_in_address: Address,
                 token_out_address: Address,
                 amount: int,
                 limit: int):
        super().__init__(avatar=avatar)
        self.args.single_swap["pool_id"] = pool_id
        self.args.single_swap["kind"] = swap_kind
        self.args.single_swap["asset_in"] = token_in_address
        self.args.single_swap["asset_out"] = token_out_address
        self.args.single_swap["amount"] = amount
        self.args.single_swap["user_data"] = self.fixed_arguments["user_data"]
        self.args.funds = [self.fixed_arguments["sender"], self.fixed_arguments["from_internal_balance"],
                           self.fixed_arguments["recipient"], self.fixed_arguments["to_internal_balance"]]
        self.args.deadline = self.fixed_arguments["deadline"]
        self.args.limit = limit


class ExactTokenInSingleSwap(SingleSwap):
    def __init__(self,
                 pool_id: str,
                 avatar: Address,
                 token_in_address: Address,
                 token_out_address: Address,
                 amount_in: int,
                 min_amount_out: int):
        swap_kind = SwapKind.OutGivenExactIn
        super().__init__(pool_id, avatar, swap_kind, token_in_address, token_out_address, amount_in, min_amount_out)


class ExactTokenOutSingleSwap(SingleSwap):
    def __init__(self,
                 pool_id: str,
                 avatar: Address,
                 token_in_address: Address,
                 token_out_address: Address,
                 amount_out: int,
                 max_amount_in: int):
        swap_kind = SwapKind.InGivenExactOut
        super().__init__(pool_id, avatar, swap_kind, token_in_address, token_out_address, amount_out, max_amount_in)


# -----------------------------------------------------------------------------------------------------------------------
# The next are the classes ready to be used inputting max slippage

# Exit
class ExactBptSingleTokenExitTx(ExactBptSingleTokenExit):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_in: int,
                 token_out_address: Address,
                 max_slippage: float,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        m = ExactBptSingleTokenQueryExit(w3=w3,
                                         pool_id=pool_id,
                                         avatar=avatar,
                                         bpt_amount_in=bpt_amount_in,
                                         token_out_address=token_out_address)
        exit_token_index = assets.index(token_out_address)
        bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)
        # FIXME:we should do a better handling of rounding errors
        if not bpt_amount_in - 1 <= bpt_amount_in_sim <= bpt_amount_in + 1:
            raise ValueError(
                f"The bpt_amount_in = {bpt_amount_in} specified is not the same as the bpt_amount_in = {bpt_amount_in_sim} calculated by the query contract.")

        min_amount_out = int(Decimal(amounts_out_sim[exit_token_index]) * Decimal(1 - max_slippage))

        super().__init__(w3, pool_id, avatar, bpt_amount_in, token_out_address, min_amount_out, assets=assets)


class ExactSingleTokenExitTx(ExactSingleTokenExit):
    """Exact Single Token Exit"""

    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 token_in_address: Address,
                 amount_out: int,
                 max_slippage: float):
        m = ExactSingleTokenQueryExit(w3=w3,
                                      pool_id=pool_id,
                                      avatar=avatar,
                                      token_in_address=token_in_address,
                                      amount_out=amount_out)
        assets = get_assets_from_pid(w3, pool_id)
        exit_token_index = assets.index(token_in_address)
        bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)
        # FIXME:we should do a better handling of rounding errors, round instead of int?
        if amount_out - 1 <= amounts_out_sim[exit_token_index] <= amount_out + 1:
            raise ValueError(
                f"The amount_out = {amount_out} specified is not the same as the amount_out = {amounts_out_sim[exit_token_index]} calculated by the query contract.")
        max_bpt_amount_in = int(Decimal(bpt_amount_in_sim) * Decimal(1 + max_slippage))

        super().__init__(w3, pool_id, avatar, token_in_address, amount_out, max_bpt_amount_in, assets=assets)


class ExactBptProportionalExitTx(ExactBptProportionalExit):
    def __init__(self, w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_in: int,
                 max_slippage: float):
        m = ExactBptProportionalQueryExit(w3=w3,
                                          pool_id=pool_id,
                                          avatar=avatar,
                                          bpt_amount_in=bpt_amount_in)

        bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)
        # FIXME:we should do a better handling of rounding errors, round instead of int?
        if not bpt_amount_in_sim - 1 <= bpt_amount_in_sim <= bpt_amount_in + 1:
            raise ValueError(
                f"The bpt_amount_in = {bpt_amount_in} specified is not the same as the bpt_amount_in = {bpt_amount_in_sim} calculated by the query contract.")

        min_amounts_out = [int(Decimal(amount) * Decimal(1 - max_slippage)) for amount in amounts_out_sim]

        super().__init__(w3, pool_id, avatar, bpt_amount_in, min_amounts_out)


class ExactTokensExitTx(ExactTokensExit):

    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 amounts_out: list[int],
                 max_slippage: float):
        m = ExactTokensQueryExit(w3=w3,
                                 pool_id=pool_id,
                                 avatar=avatar,
                                 amounts_out=amounts_out)
        bpt_in, amounts_out_sim = m.call(web3=w3)

        # If the pool is composable stable, remove the amount corresponding to the bpt
        pool_kind = get_pool_kind_from_pid(w3, pool_id)
        if pool_kind == PoolKind.ComposableStablePool:
            bpt_index = get_bpt_index_from_composable_pid(w3, pool_id)
            del amounts_out_sim[bpt_index]

        for index in range(len(amounts_out)):
            if not amounts_out[index] - 1 <= amounts_out_sim[index] <= amounts_out[index] + 1:
                raise ValueError(
                    f"The amounts_out = {amounts_out} specified are not the same as the amounts_out = {amounts_out_sim} calculated by the query contract.")

        max_bpt_amount_in = int(Decimal(bpt_in) * Decimal(1 + max_slippage))

        super().__init__(w3, pool_id, avatar, amounts_out, max_bpt_amount_in)


class ExactSingleTokenProportionalExitTx(ExactTokensExit):
    def __init__(self, w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 token_out_address: Address,
                 amount_out: int,
                 max_slippage: float,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        token_index = assets.index(token_out_address)
        balances = get_pool_balances_from_pid(w3, pool_id)

        # Get the corresponding proportional amounts out
        amounts_out = [int(Decimal(balance) * Decimal(amount_out) / Decimal(balances[token_index])) for balance in
                       balances]

        # If the pool is composable stable, remove the amount corresponding to the bpt
        pool_kind = get_pool_kind_from_pid(w3, pool_id)
        if pool_kind == PoolKind.ComposableStablePool:
            bpt_index = get_bpt_index_from_composable_pid(w3, pool_id)
            del amounts_out[bpt_index]

        m = ExactTokensQueryExit(w3=w3,
                                 pool_id=pool_id,
                                 avatar=avatar,
                                 amounts_out=amounts_out)

        bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)
        if not amount_out - 1 <= amounts_out_sim[token_index] <= amount_out + 1:
            raise ValueError(
                f"The amount_out = {amount_out} specified is not the same as the amount_out = {amounts_out_sim[token_index]} calculated by the query contract.")

        max_bpt_amount_in = int(Decimal(bpt_amount_in_sim) * Decimal(1 + max_slippage))

        super().__init__(w3, pool_id, avatar, amounts_out, max_bpt_amount_in, assets=assets)


class ExactBptRecoveryModeExitTx(ExactBptRecoveryModeExit):
    def __init__(self, w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_in: int,
                 max_slippage: float):
        m = ExactBptRecoveryModeQueryExit(w3=w3,
                                          pool_id=pool_id,
                                          avatar=avatar,
                                          bpt_amount_in=bpt_amount_in)

        bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)
        if not bpt_amount_in_sim - 1 <= bpt_amount_in_sim <= bpt_amount_in + 1:
            raise ValueError(
                f"The bpt_amount_in = {bpt_amount_in} specified is not the same as the bpt_amount_in = {bpt_amount_in_sim} calculated by the query contract.")

        min_amounts_out = [int(Decimal(amount) * Decimal(1 - max_slippage)) for amount in amounts_out_sim]

        super().__init__(w3, pool_id, avatar, bpt_amount_in, min_amounts_out)


# -----------------------------------------------------------------------------------------------------------------------
# Join
class ExactBptSingleTokenJoinTx(ExactBptSingleTokenJoin):
    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_out: int,
                 token_in_address: Address,
                 max_slippage: float,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)

        m = ExactBptSingleTokenQueryJoin(w3=w3,
                                         pool_id=pool_id,
                                         avatar=avatar,
                                         bpt_amount_out=bpt_amount_out,
                                         token_in_address=token_in_address)

        join_token_index = assets.index(token_in_address)
        bpt_amount_out_sim, amounts_in_sim = m.call(web3=w3)
        if not bpt_amount_out - 1 <= bpt_amount_out_sim <= bpt_amount_out + 1:
            raise ValueError(
                f"The bpt_amount_out = {bpt_amount_out} specified is not the same as the bpt_amount_out = {bpt_amount_out_sim} calculated by the query contract."
            )

        max_amount_in = int(Decimal(amounts_in_sim[join_token_index]) * Decimal(1 + max_slippage))

        super().__init__(w3, pool_id, avatar, bpt_amount_out, token_in_address, max_amount_in, assets=assets)


class ExactSingleTokenJoinTx(ExactSingleTokenJoin):
    """Exact Single Token Join
    """

    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 token_in_address: Address,
                 amount_in: int,
                 max_slippage: float,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)
        join_token_index = assets.index(token_in_address)
        m = ExactSingleTokenQueryJoin(w3=w3,
                                      pool_id=pool_id,
                                      avatar=avatar,
                                      token_in_address=token_in_address,
                                      amount_in=amount_in)

        bpt_amount_out_sim, amounts_in = m.call(web3=w3)
        if not amount_in - 1 <= amounts_in[join_token_index] <= amounts_in + 1:
            raise ValueError(
                f"The amount_in = {amount_in} specified is not the same as the bpt_amount_out = {amounts_in[join_token_index]} calculated by the query contract."
            )
        min_bpt_amount_out = int(Decimal(bpt_amount_out_sim) * Decimal(1 - max_slippage))

        super().__init__(w3, pool_id, avatar, token_in_address, amount_in, min_bpt_amount_out, assets=assets)


class ExactBptProportionalJoinTx(ProportionalJoin):
    def __init__(self, w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_out: int,
                 max_slippage: float):
        m = ProportionalQueryJoin(w3=w3,
                                  pool_id=pool_id,
                                  avatar=avatar,
                                  bpt_amount_out=bpt_amount_out)

        bpt_amount_out_sim, amounts_in_sim = m.call(web3=w3)
        if not bpt_amount_out - 1 <= bpt_amount_out_sim <= bpt_amount_out + 1:
            raise ValueError(
                f"The bpt_amount_out = {bpt_amount_out} specified is not the same as the bpt_amount_out = {bpt_amount_out_sim} calculated by the query contract."
            )
        max_amounts_in = [int(Decimal(amount) * Decimal(1 + max_slippage)) for amount in amounts_in_sim]

        super().__init__(w3, pool_id, avatar, bpt_amount_out, max_amounts_in)


class ExactTokensJoinTx(ExactTokensJoin):

    def __init__(self,
                 w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 amounts_in: list[int],
                 max_slippage: float):
        m = ExactTokensQueryJoin(w3=w3,
                                 pool_id=pool_id,
                                 avatar=avatar,
                                 amounts_in=amounts_in)

        bpt_out, amounts_in = m.call(web3=w3)
        min_bpt_amount_out = int(Decimal(bpt_out) * Decimal(1 - max_slippage))

        super().__init__(w3, pool_id, avatar, amounts_in, min_bpt_amount_out)


class ExactSingleTokenProportionalJoinTx(ExactTokensJoin):
    def __init__(self, w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 token_in_address: Address,
                 amount_in: int,
                 max_slippage: float,
                 assets: list[Address] = None):
        if assets is None:
            assets = get_assets_from_pid(w3, pool_id)
        join_token_index = assets.index(token_in_address)
        balances = get_pool_balances_from_pid(w3, pool_id)
        amounts_in = [int(Decimal(balance) * Decimal(amount_in) / Decimal(balances[join_token_index])) for balance in
                      balances]

        m = ExactTokensQueryJoin(w3=w3,
                                 pool_id=pool_id,
                                 avatar=avatar,
                                 amounts_in=amounts_in)

        bpt_amount_out_sim, amounts_in_sim = m.call(web3=w3)
        if not amount_in - 1 <= amounts_in_sim[join_token_index] <= amount_in + 1:
            raise ValueError(
                f"The amount_in = {amount_in} specified is not the same as the amount_in = {amounts_in_sim[join_token_index]} calculated by the query contract."
            )
        min_bpt_amount_out = int(Decimal(bpt_amount_out_sim) * Decimal(1 - max_slippage))

        super().__init__(w3, pool_id, avatar, amounts_in, min_bpt_amount_out, assets=assets)