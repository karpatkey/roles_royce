from decimal import Decimal

from defabipedia.types import Blockchain, Chain
from web3 import Web3

from roles_royce.constants import MAX_UINT256, ZERO
from roles_royce.protocols.balancer.types_and_enums import StablePoolJoinKind
from roles_royce.protocols.base import Address

from .contract_methods import Join
from .utils import Pool


class _ExactBptSingleTokenJoin(Join):
    """Single Asset Join

    User sends an estimated but unknown (computed at run time) quantity of a single token, and receives a precise quantity of BPT.
    """

    user_data_abi = ["uint256", "uint256", "uint256"]
    join_kind = StablePoolJoinKind.TOKEN_IN_FOR_EXACT_BPT_OUT

    def __init__(
        self,
        blockchain: Blockchain,
        pool_id: str,
        avatar: Address,
        assets: list[Address],
        max_amounts_in: list[int],
        bpt_amount_out: int,
        join_token_index: int,
    ):
        """

        :param bpt_amount_out: the amount of BPT to be minted
        :param join_token_index: the index of the token to enter the pool
        """
        super().__init__(
            blockchain=blockchain,
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            max_amounts_in=max_amounts_in,
            user_data=[self.join_kind, bpt_amount_out, join_token_index],
        )


class ExactBptSingleTokenJoin(_ExactBptSingleTokenJoin):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        bpt_amount_out: int,
        token_in_address: Address,
        max_amount_in: int,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()
        join_token_index = assets.index(token_in_address)
        max_amounts_in = [0] * join_token_index + [max_amount_in] + [0] * (len(assets) - join_token_index - 1)

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            max_amounts_in=max_amounts_in,
            bpt_amount_out=bpt_amount_out,
            join_token_index=join_token_index,
        )


class _ProportionalJoin(Join):
    """
    Proportional Join

    User sends estimated but unknown (computed at run time) quantities of tokens, and receives precise quantity of BPT.
    """

    user_data_abi = ["uint256", "uint256"]
    join_kind = StablePoolJoinKind.ALL_TOKENS_IN_FOR_EXACT_BPT_OUT

    def __init__(
        self,
        blockchain: Blockchain,
        pool_id: str,
        avatar: Address,
        assets: list[Address],
        bpt_amount_out: int,
        max_amounts_in: list[int],
    ):
        """
        :param max_amounts_in: the maximum amounts of each token to be deposited into the pool
        :param bpt_amount_out: the amount of BPT to be minted
        """

        super().__init__(
            blockchain=blockchain,
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            max_amounts_in=max_amounts_in,
            user_data=[self.join_kind, bpt_amount_out],
        )


class ProportionalJoin(_ProportionalJoin):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        bpt_amount_out: int,
        max_amounts_in: list[int],
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            bpt_amount_out=bpt_amount_out,
            max_amounts_in=max_amounts_in,
        )


class _ExactTokensJoin(Join):
    """Exact Tokens Join

    User sends precise quantities of tokens, and receives an estimated but unknown (computed at run time) quantity of BPT.
    """

    user_data_abi = ["uint256", "uint256[]", "uint256"]
    join_kind = StablePoolJoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT

    def __init__(
        self,
        blockchain: Blockchain,
        pool_id: str,
        avatar: Address,
        assets: list[Address],
        amounts_in: list[int],
        min_bpt_amount_out: int,
    ):
        super().__init__(
            blockchain=blockchain,
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            max_amounts_in=amounts_in,
            user_data=[self.join_kind, amounts_in, min_bpt_amount_out],
        )


class ExactTokensJoin(_ExactTokensJoin):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        amounts_in: list[int],
        min_bpt_amount_out: int,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            amounts_in=amounts_in,
            min_bpt_amount_out=min_bpt_amount_out,
        )


class ExactSingleTokenJoin(_ExactTokensJoin):
    """Exact Single Token Join"""

    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        token_in_address: Address,
        amount_in: int,
        min_bpt_amount_out: int,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        join_token_index = assets.index(token_in_address)
        amounts_in = [0] * join_token_index + [amount_in] + [0] * (len(assets) - join_token_index - 1)

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            amounts_in=amounts_in,
            min_bpt_amount_out=min_bpt_amount_out,
        )


class QueryJoinMixin:
    name = "queryJoin"
    out_signature = [("bpt_out", "uint256"), ("amounts_in", "uint256[]")]


class ExactBptSingleTokenQueryJoin(QueryJoinMixin, ExactBptSingleTokenJoin):
    def __init__(self, w3: Web3, pool_id: str, bpt_amount_out: int, token_in_address: Address):
        super().__init__(
            w3=w3,
            pool_id=pool_id,
            avatar=ZERO,
            bpt_amount_out=bpt_amount_out,
            token_in_address=token_in_address,
            max_amount_in=MAX_UINT256,
        )


class ProportionalQueryJoin(QueryJoinMixin, ProportionalJoin):
    def __init__(self, w3: Web3, pool_id: str, bpt_amount_out: int, assets: list[Address] = None):
        if assets is None:
            assets = Pool(w3, pool_id).assets()
        max_amounts_in = [MAX_UINT256] * len(assets)

        super().__init__(
            w3=w3,
            pool_id=pool_id,
            avatar=ZERO,
            bpt_amount_out=bpt_amount_out,
            max_amounts_in=max_amounts_in,
            assets=assets,
        )


class ExactTokensQueryJoin(QueryJoinMixin, ExactTokensJoin):
    def __init__(self, w3: Web3, pool_id: str, amounts_in: list[int]):
        super().__init__(w3=w3, pool_id=pool_id, avatar=ZERO, amounts_in=amounts_in, min_bpt_amount_out=0)


class ExactSingleTokenQueryJoin(QueryJoinMixin, ExactSingleTokenJoin):
    def __init__(self, w3: Web3, pool_id: str, token_in_address: Address, amount_in: int):
        super().__init__(
            w3=w3,
            pool_id=pool_id,
            avatar=ZERO,
            token_in_address=token_in_address,
            amount_in=amount_in,
            min_bpt_amount_out=0,
        )


class ExactBptSingleTokenJoinSlippage(ExactBptSingleTokenJoin):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        bpt_amount_out: int,
        token_in_address: Address,
        max_slippage: float,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        m = ExactBptSingleTokenQueryJoin(
            w3=w3, pool_id=pool_id, bpt_amount_out=bpt_amount_out, token_in_address=token_in_address
        )

        join_token_index = assets.index(token_in_address)
        bpt_amount_out_sim, amounts_in_sim = m.call(web3=w3)
        if not bpt_amount_out - 1 <= bpt_amount_out_sim <= bpt_amount_out + 1:
            raise ValueError(
                f"The bpt_amount_out = {bpt_amount_out} specified is not the same as the bpt_amount_out = {bpt_amount_out_sim} calculated by the query contract."
            )

        max_amount_in = int(Decimal(amounts_in_sim[join_token_index]) * Decimal(1 + max_slippage))

        super().__init__(
            w3=w3,
            pool_id=pool_id,
            avatar=avatar,
            bpt_amount_out=bpt_amount_out,
            token_in_address=token_in_address,
            max_amount_in=max_amount_in,
            assets=assets,
        )


class ExactSingleTokenJoinSlippage(ExactSingleTokenJoin):
    """Exact Single Token Join"""

    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        token_in_address: Address,
        amount_in: int,
        max_slippage: float,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()
        join_token_index = assets.index(token_in_address)
        m = ExactSingleTokenQueryJoin(w3=w3, pool_id=pool_id, token_in_address=token_in_address, amount_in=amount_in)

        bpt_amount_out_sim, amounts_in = m.call(web3=w3)
        if not amount_in - 1 <= amounts_in[join_token_index] <= amounts_in + 1:
            raise ValueError(
                f"The amount_in = {amount_in} specified is not the same as the bpt_amount_out = {amounts_in[join_token_index]} calculated by the query contract."
            )
        min_bpt_amount_out = int(Decimal(bpt_amount_out_sim) * Decimal(1 - max_slippage))

        super().__init__(
            w3=w3,
            pool_id=pool_id,
            avatar=avatar,
            token_in_address=token_in_address,
            amount_in=amount_in,
            min_bpt_amount_out=min_bpt_amount_out,
            assets=assets,
        )


class ExactBptProportionalJoinSlippage(ProportionalJoin):
    def __init__(self, w3: Web3, pool_id: str, avatar: Address, bpt_amount_out: int, max_slippage: float):
        m = ProportionalQueryJoin(w3=w3, pool_id=pool_id, bpt_amount_out=bpt_amount_out)

        bpt_amount_out_sim, amounts_in_sim = m.call(web3=w3)
        if not bpt_amount_out - 1 <= bpt_amount_out_sim <= bpt_amount_out + 1:
            raise ValueError(
                f"The bpt_amount_out = {bpt_amount_out} specified is not the same as the bpt_amount_out = {bpt_amount_out_sim} calculated by the query contract."
            )
        max_amounts_in = [int(Decimal(amount) * Decimal(1 + max_slippage)) for amount in amounts_in_sim]

        super().__init__(
            w3=w3, pool_id=pool_id, avatar=avatar, bpt_amount_out=bpt_amount_out, max_amounts_in=max_amounts_in
        )


class ExactTokensJoinSlippage(ExactTokensJoin):
    def __init__(self, w3: Web3, pool_id: str, avatar: Address, amounts_in: list[int], max_slippage: float):
        m = ExactTokensQueryJoin(w3=w3, pool_id=pool_id, amounts_in=amounts_in)

        bpt_out, amounts_in = m.call(web3=w3)
        min_bpt_amount_out = int(Decimal(bpt_out) * Decimal(1 - max_slippage))

        super().__init__(
            w3=w3, pool_id=pool_id, avatar=avatar, amounts_in=amounts_in, min_bpt_amount_out=min_bpt_amount_out
        )


class ExactSingleTokenProportionalJoinSlippage(ExactTokensJoin):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        token_in_address: Address,
        amount_in: int,
        max_slippage: float,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()
        join_token_index = assets.index(token_in_address)
        balances = Pool(w3, pool_id).pool_balances()
        amounts_in = [
            int(Decimal(balance) * Decimal(amount_in) / Decimal(balances[join_token_index])) for balance in balances
        ]

        m = ExactTokensQueryJoin(w3=w3, pool_id=pool_id, amounts_in=amounts_in)

        bpt_amount_out_sim, amounts_in_sim = m.call(web3=w3)
        if not amount_in - 1 <= amounts_in_sim[join_token_index] <= amount_in + 1:
            raise ValueError(
                f"The amount_in = {amount_in} specified is not the same as the amount_in = {amounts_in_sim[join_token_index]} calculated by the query contract."
            )
        min_bpt_amount_out = int(Decimal(bpt_amount_out_sim) * Decimal(1 - max_slippage))

        super().__init__(
            w3=w3,
            pool_id=pool_id,
            avatar=avatar,
            amounts_in=amounts_in,
            min_bpt_amount_out=min_bpt_amount_out,
            assets=assets,
        )
