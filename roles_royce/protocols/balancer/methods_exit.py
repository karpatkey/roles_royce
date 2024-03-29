from decimal import Decimal

from defabipedia.types import Blockchain, Chain
from web3 import Web3

from roles_royce.constants import MAX_UINT256, ZERO
from roles_royce.protocols.balancer.types_and_enums import (
    ComposableStablePoolExitKind,
    StablePoolExitKind,
    StablePoolv2ExitKind,
)
from roles_royce.protocols.base import Address

from .contract_methods import Exit
from .types_and_enums import PoolKind
from .utils import Pool


class _ExactBptSingleTokenExit(Exit):
    """Single Asset Exit

    User sends a precise quantity of BPT, and receives an estimated but unknown (computed at run time) quantity of a single token.
    """

    user_data_abi = ["uint256", "uint256", "uint256"]

    def __init__(
        self,
        blockchain: Blockchain,
        pool_kind: PoolKind,
        pool_id: str,
        avatar: Address,
        assets: list[Address],
        bpt_amount_in: int,
        exit_token_index: int,
        min_amounts_out: list[int],
    ):
        if pool_kind == PoolKind.ComposableStablePool:
            self.exit_kind = ComposableStablePoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT
        else:
            self.exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT

        super().__init__(
            blockchain=blockchain,
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            min_amounts_out=min_amounts_out,
            user_data=[self.exit_kind, bpt_amount_in, exit_token_index],
        )


class ExactBptSingleTokenExit(_ExactBptSingleTokenExit):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        bpt_amount_in: int,
        token_out_address: Address,
        min_amount_out: int,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()
        pool_kind = Pool(w3, pool_id).pool_kind()
        exit_token_index = assets.index(token_out_address)
        min_amounts_out = [0] * exit_token_index + [min_amount_out] + [0] * (len(assets) - exit_token_index - 1)

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            pool_kind=pool_kind,
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            bpt_amount_in=bpt_amount_in,
            exit_token_index=exit_token_index,
            min_amounts_out=min_amounts_out,
        )


class _ExactBptProportionalExit(Exit):
    """Proportional Exit

    User sends a precise quantity of BPT, and receives an estimated but unknown (computed at run time) quantities of all tokens.
    """

    user_data_abi = ["uint256", "uint256"]

    def __init__(
        self,
        blockchain: Blockchain,
        pool_kind: PoolKind,
        pool_id: str,
        avatar: Address,
        assets: list[Address],
        bpt_amount_in: int,
        min_amounts_out: list[int],
    ):
        """
        :param bpt_amount_in: the amount of BPT to burn in exchange for withdrawn tokens
        """
        if pool_kind == PoolKind.ComposableStablePool:
            exit_kind = ComposableStablePoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT
        else:
            exit_kind = StablePoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT

        super().__init__(
            blockchain=blockchain,
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            min_amounts_out=min_amounts_out,
            user_data=[exit_kind, bpt_amount_in],
        )


class ExactBptProportionalExit(_ExactBptProportionalExit):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        bpt_amount_in: int,
        min_amounts_out: list[int],
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()
        pool_kind = Pool(w3, pool_id).pool_kind()

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            pool_kind=pool_kind,
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            bpt_amount_in=bpt_amount_in,
            min_amounts_out=min_amounts_out,
        )


class _ExactTokensExit(Exit):
    """Custom Exit

    User sends an estimated but unknown (computed at run time) quantity of BPT, and receives precise quantities of specified tokens.
    """

    user_data_abi = ["uint256", "uint256[]", "uint256"]

    def __init__(
        self,
        blockchain: Blockchain,
        pool_kind: PoolKind,
        pool_id: str,
        avatar: Address,
        assets: list[Address],
        amounts_out: list[int],
        max_bpt_amount_in: int,
    ):
        """

        :param amounts_out: are the amounts of each token to be withdrawn from the pool
        :param max_bpt_amount_in: is the minimum acceptable BPT to burn in return for withdrawn tokens
        """

        if pool_kind == PoolKind.ComposableStablePool:
            exit_kind = ComposableStablePoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT
        else:
            exit_kind = StablePoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT

        super().__init__(
            blockchain=blockchain,
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            min_amounts_out=amounts_out,
            user_data=[exit_kind, amounts_out, max_bpt_amount_in],
        )


class ExactTokensExit(_ExactTokensExit):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        amounts_out: list[int],
        max_bpt_amount_in: int,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()
        pool_kind = Pool(w3, pool_id).pool_kind()

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            pool_kind=pool_kind,
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            amounts_out=amounts_out,
            max_bpt_amount_in=max_bpt_amount_in,
        )


class ExactSingleTokenExit(ExactTokensExit):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        token_out_address: Address,
        amount_out: int,
        max_bpt_amount_in: int,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        exit_token_index = assets.index(token_out_address)
        amounts_out = [0] * exit_token_index + [amount_out] + [0] * (len(assets) - exit_token_index - 1)

        super().__init__(
            w3=w3,
            pool_id=pool_id,
            avatar=avatar,
            amounts_out=amounts_out,
            max_bpt_amount_in=max_bpt_amount_in,
            assets=assets,
        )


class _ExactBptRecoveryModeExit(Exit):
    user_data_abi = ["uint256", "uint256"]

    def __init__(
        self,
        blockchain: Blockchain,
        pool_id: str,
        avatar: Address,
        assets: list[Address],
        bpt_amount_in: int,
        min_amounts_out: list[int],
    ):
        """
        :param bpt_amount_in: the amount of BPT to burn in exchange for withdrawn tokens
        """
        exit_kind = StablePoolv2ExitKind.RECOVERY_MODE_EXIT_KIND

        super().__init__(
            blockchain=blockchain,
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            min_amounts_out=min_amounts_out,
            user_data=[exit_kind, bpt_amount_in],
        )


class ExactBptRecoveryModeExit(_ExactBptRecoveryModeExit):
    def __init__(self, w3: Web3, pool_id: str, avatar: Address, bpt_amount_in: int, assets: list[Address] = None):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        min_amounts_out = [0] * len(assets)

        super().__init__(
            blockchain=Chain.get_blockchain_from_web3(w3),
            pool_id=pool_id,
            avatar=avatar,
            assets=assets,
            bpt_amount_in=bpt_amount_in,
            min_amounts_out=min_amounts_out,
        )


# -----------------------------------------------------------------------------------------------------------------------
# Query Exit


class QueryExitMixin:
    name = "queryExit"
    out_signature = [("bpt_in", "uint256"), ("amounts_out", "uint256[]")]


class ExactBptSingleTokenQueryExit(QueryExitMixin, ExactBptSingleTokenExit):
    def __init__(self, w3: Web3, pool_id: str, bpt_amount_in: int, token_out_address: Address):
        super().__init__(
            w3=w3,
            pool_id=pool_id,
            avatar=ZERO,
            bpt_amount_in=bpt_amount_in,
            token_out_address=token_out_address,
            min_amount_out=0,
        )


class ExactBptProportionalQueryExit(QueryExitMixin, ExactBptProportionalExit):
    def __init__(self, w3: Web3, pool_id: str, bpt_amount_in: int, assets: list[Address] = None):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        super().__init__(
            w3=w3,
            pool_id=pool_id,
            avatar=ZERO,
            bpt_amount_in=bpt_amount_in,
            min_amounts_out=[0] * len(assets),
            assets=assets,
        )


class ExactTokensQueryExit(QueryExitMixin, ExactTokensExit):
    def __init__(self, w3: Web3, pool_id: str, amounts_out: list[int], assets: list[Address] = None):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        super().__init__(
            w3=w3, pool_id=pool_id, avatar=ZERO, amounts_out=amounts_out, max_bpt_amount_in=MAX_UINT256, assets=assets
        )


class ExactSingleTokenQueryExit(QueryExitMixin, ExactSingleTokenExit):
    def __init__(self, w3: Web3, pool_id: str, token_out_address: Address, amount_out: int):
        super().__init__(
            w3=w3,
            pool_id=pool_id,
            avatar=ZERO,
            token_out_address=token_out_address,
            amount_out=amount_out,
            max_bpt_amount_in=MAX_UINT256,
        )


# -----------------------------------------------------------------------------------------------------------------------
# The next are the classes ready to be used inputting max slippage


class ExactBptSingleTokenExitSlippage(ExactBptSingleTokenExit):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        bpt_amount_in: int,
        token_out_address: Address,
        max_slippage: float,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        m = ExactBptSingleTokenQueryExit(
            w3=w3, pool_id=pool_id, bpt_amount_in=bpt_amount_in, token_out_address=token_out_address
        )
        exit_token_index = assets.index(token_out_address)
        bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)

        if not bpt_amount_in - 1 <= bpt_amount_in_sim <= bpt_amount_in + 1:
            raise ValueError(
                f"The bpt_amount_in = {bpt_amount_in} specified is not the same as the bpt_amount_in = {bpt_amount_in_sim} calculated by the query contract."
            )

        min_amount_out = int(Decimal(amounts_out_sim[exit_token_index]) * Decimal(1 - max_slippage))

        super().__init__(w3, pool_id, avatar, bpt_amount_in, token_out_address, min_amount_out, assets=assets)


class ExactSingleTokenExitSlippage(ExactSingleTokenExit):
    """Exact Single Token Exit"""

    def __init__(
        self, w3: Web3, pool_id: str, avatar: Address, token_out_address: Address, amount_out: int, max_slippage: float
    ):
        m = ExactSingleTokenQueryExit(
            w3=w3, pool_id=pool_id, token_out_address=token_out_address, amount_out=amount_out
        )
        assets = Pool(w3, pool_id).assets()
        exit_token_index = assets.index(token_out_address)
        bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)

        if amount_out - 1 <= amounts_out_sim[exit_token_index] <= amount_out + 1:
            raise ValueError(
                f"The amount_out = {amount_out} specified is not the same as the amount_out = {amounts_out_sim[exit_token_index]} calculated by the query contract."
            )
        max_bpt_amount_in = int(Decimal(bpt_amount_in_sim) * Decimal(1 + max_slippage))

        super().__init__(w3, pool_id, avatar, token_out_address, amount_out, max_bpt_amount_in, assets=assets)


class ExactBptProportionalExitSlippage(ExactBptProportionalExit):
    def __init__(self, w3: Web3, pool_id: str, avatar: Address, bpt_amount_in: int, max_slippage: float):
        m = ExactBptProportionalQueryExit(w3=w3, pool_id=pool_id, bpt_amount_in=bpt_amount_in)

        bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)

        if not bpt_amount_in_sim - 1 <= bpt_amount_in_sim <= bpt_amount_in + 1:
            raise ValueError(
                f"The bpt_amount_in = {bpt_amount_in} specified is not the same as the bpt_amount_in = {bpt_amount_in_sim} calculated by the query contract."
            )

        min_amounts_out = [int(Decimal(amount) * Decimal(1 - max_slippage)) for amount in amounts_out_sim]

        super().__init__(w3, pool_id, avatar, bpt_amount_in, min_amounts_out)


class ExactTokensExitSlippage(ExactTokensExit):
    def __init__(self, w3: Web3, pool_id: str, avatar: Address, amounts_out: list[int], max_slippage: float):
        m = ExactTokensQueryExit(w3=w3, pool_id=pool_id, amounts_out=amounts_out)
        bpt_in, amounts_out_sim = m.call(web3=w3)

        # If the pool is composable stable, remove the amount corresponding to the bpt
        pool_kind = Pool(w3, pool_id).pool_kind()
        if pool_kind == PoolKind.ComposableStablePool:
            bpt_index = Pool(w3, pool_id).bpt_index_from_composable()
            del amounts_out_sim[bpt_index]

        for index in range(len(amounts_out)):
            if not amounts_out[index] - 1 <= amounts_out_sim[index] <= amounts_out[index] + 1:
                raise ValueError(
                    f"The amounts_out = {amounts_out} specified are not the same as the amounts_out = {amounts_out_sim} calculated by the query contract."
                )

        max_bpt_amount_in = int(Decimal(bpt_in) * Decimal(1 + max_slippage))

        super().__init__(w3, pool_id, avatar, amounts_out, max_bpt_amount_in)


class ExactSingleTokenProportionalExitSlippage(ExactTokensExit):
    def __init__(
        self,
        w3: Web3,
        pool_id: str,
        avatar: Address,
        token_out_address: Address,
        amount_out: int,
        max_slippage: float,
        assets: list[Address] = None,
    ):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        token_index = assets.index(token_out_address)
        balances = Pool(w3, pool_id).pool_balances()

        # Get the corresponding proportional amounts out
        amounts_out = [
            int(Decimal(balance) * Decimal(amount_out) / Decimal(balances[token_index])) for balance in balances
        ]

        # If the pool is composable stable, remove the amount corresponding to the bpt
        pool_kind = Pool(w3, pool_id).pool_kind()
        if pool_kind == PoolKind.ComposableStablePool:
            bpt_index = Pool(w3, pool_id).bpt_index_from_composable()
            del amounts_out[bpt_index]

        m = ExactTokensQueryExit(w3=w3, pool_id=pool_id, amounts_out=amounts_out)

        bpt_amount_in_sim, amounts_out_sim = m.call(web3=w3)
        if not amount_out - 1 <= amounts_out_sim[token_index] <= amount_out + 1:
            raise ValueError(
                f"The amount_out = {amount_out} specified is not the same as the amount_out = {amounts_out_sim[token_index]} calculated by the query contract."
            )

        max_bpt_amount_in = int(Decimal(bpt_amount_in_sim) * Decimal(1 + max_slippage))

        super().__init__(w3, pool_id, avatar, amounts_out, max_bpt_amount_in, assets=assets)
