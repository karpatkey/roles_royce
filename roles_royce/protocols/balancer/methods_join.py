from roles_royce.constants import ZERO, MAX_UINT256
from defabipedia.types import Blockchain, Chains
from roles_royce.protocols.base import Address
from web3 import Web3
from decimal import Decimal
from roles_royce.protocols.balancer.types_and_enums import StablePoolJoinKind
from .utils import Pool
from .contract_methods import Join


class _ExactBptSingleTokenJoin(Join):
    """
    A class representing a single asset join where the user sends an estimated but unknown (computed at run time) quantity of a single token, 
    and receives a precise quantity of BPT.

    Attributes:
        user_data_abi : (list[str]) The ABI of the user data.
        join_kind : (StablePoolJoinKind) The kind of join.
    """

    user_data_abi = ['uint256', 'uint256', 'uint256']
    join_kind = StablePoolJoinKind.TOKEN_IN_FOR_EXACT_BPT_OUT

    def __init__(self,
                blockchain: Blockchain,
                pool_id: str,
                avatar: Address,
                assets: list[Address],
                max_amounts_in: list[int],
                bpt_amount_out: int,
                join_token_index: int):
        """
        Constructs all the necessary attributes for the _ExactBptSingleTokenJoin object.

        Args:
            blockchain : (Blockchain) The blockchain instance.
            pool_id : (str) The id of the pool.
            avatar : (Address) The avatar address.
            assets : (list[Address]) A list of addresses of the assets.
            max_amounts_in : (list[int]) A list of maximum amounts of each token to be sent by the user.
            bpt_amount_out : (int) The amount of BPT to be minted.
            join_token_index : (int) The index of the token to enter the pool.
        """

        super().__init__(blockchain=blockchain,
                        pool_id=pool_id,
                        avatar=avatar,
                        assets=assets,
                        max_amounts_in=max_amounts_in,
                        user_data=[self.join_kind, bpt_amount_out, join_token_index])


class ExactBptSingleTokenJoin(_ExactBptSingleTokenJoin):
    """
    A class representing a single token join where the user sends a precise quantity of a single token, 
    and receives an estimated but unknown (computed at run time) quantity of BPT.

    Attributes:
        w3 : (Web3) The Web3 instance.
        pool_id : (str) The id of the pool.
        avatar : (Address) The avatar address.
        bpt_amount_out : (int) The amount of BPT to be minted.
        token_in_address : (Address) The address of the token to be sent by the user.
        max_amount_in : (int) The maximum amount of token to be sent by the user.
        assets : (list[Address]) A list of addresses of the assets.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                avatar: Address,
                bpt_amount_out: int,
                token_in_address: Address,
                max_amount_in: int,
                assets: list[Address] = None):
        """
        Constructs all the necessary attributes for the ExactBptSingleTokenJoin object.

        Args:
            w3 : (Web3) The Web3 instance.
            pool_id : (str) The id of the pool.
            avatar : (Address) The avatar address.
            bpt_amount_out : (int) The amount of BPT to be minted.
            token_in_address : (Address) The address of the token to be sent by the user.
            max_amount_in : (int) The maximum amount of token to be sent by the user.
            assets : (list[Address], optional) A list of addresses of the assets. If not provided, it will be fetched from the pool.
        """

        if assets is None:
            assets = Pool(w3, pool_id).assets()
        join_token_index = assets.index(token_in_address)
        max_amounts_in = [0] * join_token_index + [max_amount_in] + [0] * (len(assets) - join_token_index - 1)

        super().__init__(blockchain=Chains.get_blockchain_from_web3(w3),
                        pool_id=pool_id,
                        avatar=avatar,
                        assets=assets,
                        max_amounts_in=max_amounts_in,
                        bpt_amount_out=bpt_amount_out,
                        join_token_index=join_token_index)


class _ProportionalJoin(Join):
    """
    A class representing a proportional join where the user sends estimated but unknown (computed at run time) quantities of tokens, 
    and receives a precise quantity of BPT.

    Attributes:
        user_data_abi : (list[str]) The ABI of the user data.
        join_kind : (StablePoolJoinKind) The kind of join.
    """

    user_data_abi = ['uint256', 'uint256']
    join_kind = StablePoolJoinKind.ALL_TOKENS_IN_FOR_EXACT_BPT_OUT

    def __init__(self,
                blockchain: Blockchain,
                pool_id: str,
                avatar: Address,
                assets: list[Address],
                bpt_amount_out: int,
                max_amounts_in: list[int]):
        """
        Constructs all the necessary attributes for the _ProportionalJoin object.

        Args:
            blockchain : (Blockchain) The blockchain instance.
            pool_id : (str) The id of the pool.
            avatar : (Address) The avatar address.
            assets : (list[Address]) A list of addresses of the assets.
            bpt_amount_out : (int) The amount of BPT to be minted.
            max_amounts_in : (list[int]) A list of maximum amounts of each token to be sent by the user.
        """

        super().__init__(blockchain=blockchain,
                        pool_id=pool_id,
                        avatar=avatar,
                        assets=assets,
                        max_amounts_in=max_amounts_in,
                        user_data=[self.join_kind, bpt_amount_out])


class ProportionalJoin(_ProportionalJoin):
    def __init__(self, w3: Web3,
                 pool_id: str,
                 avatar: Address,
                 bpt_amount_out: int,
                 max_amounts_in: list[int],
                 assets: list[Address] = None):
        if assets is None:
            assets = Pool(w3, pool_id).assets()

        super().__init__(blockchain=Chains.get_blockchain_from_web3(w3),
                         pool_id=pool_id,
                         avatar=avatar,
                         assets=assets,
                         bpt_amount_out=bpt_amount_out,
                         max_amounts_in=max_amounts_in)


class _ExactTokensJoin(Join):
    """
    A class representing an exact tokens join where the user sends precise quantities of tokens, 
    and receives an estimated but unknown (computed at run time) quantity of BPT.

    Attributes:
        user_data_abi : (list[str]) The ABI of the user data.
        join_kind : (StablePoolJoinKind) The kind of join.
    """

    user_data_abi = ['uint256', 'uint256[]', 'uint256']
    join_kind = StablePoolJoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT

    def __init__(self,
                blockchain: Blockchain,
                pool_id: str,
                avatar: Address,
                assets: list[Address],
                amounts_in: list[int],
                min_bpt_amount_out: int):
        """
        Constructs all the necessary attributes for the _ExactTokensJoin object.

        Args:
            blockchain : (Blockchain) The blockchain instance.
            pool_id : (str) The id of the pool.
            avatar : (Address) The avatar address.
            assets : (list[Address]) A list of addresses of the assets.
            amounts_in : (list[int]) A list of precise amounts of each token to be sent by the user.
            min_bpt_amount_out : (int) The minimum amount of BPT to be minted.
        """

        super().__init__(blockchain=blockchain,
                        pool_id=pool_id,
                        avatar=avatar,
                        assets=assets,
                        max_amounts_in=amounts_in,
                        user_data=[self.join_kind, amounts_in, min_bpt_amount_out])


class ExactTokensJoin(_ExactTokensJoin):
    """
    A class representing an exact tokens join where the user sends precise quantities of tokens, 
    and receives an estimated but unknown (computed at run time) quantity of BPT.

    Attributes:
        w3 : (Web3) The Web3 instance.
        pool_id : (str) The id of the pool.
        avatar : (Address) The avatar address.
        amounts_in : (list[int]) A list of precise amounts of each token to be sent by the user.
        min_bpt_amount_out : (int) The minimum amount of BPT to be minted.
        assets : (list[Address]) A list of addresses of the assets.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                avatar: Address,
                amounts_in: list[int],
                min_bpt_amount_out: int,
                assets: list[Address] = None):
        """
        Constructs all the necessary attributes for the ExactTokensJoin object.

        Args:
            w3 : (Web3) The Web3 instance.
            pool_id : (str) The id of the pool.
            avatar : (Address) The avatar address.
            amounts_in : (list[int]) A list of precise amounts of each token to be sent by the user.
            min_bpt_amount_out : (int) The minimum amount of BPT to be minted.
            assets : (list[Address], optional) A list of addresses of the assets. If not provided, it will be fetched from the pool.
        """

        if assets is None:
            assets = Pool(w3, pool_id).assets()

        super().__init__(blockchain=Chains.get_blockchain_from_web3(w3),
                        pool_id=pool_id,
                        avatar=avatar,
                        assets=assets,
                        amounts_in=amounts_in,
                        min_bpt_amount_out=min_bpt_amount_out)


class ExactSingleTokenJoin(_ExactTokensJoin):
    """
    A class representing an exact single token join where the user sends a precise quantity of a single token, 
    and receives an estimated but unknown (computed at run time) quantity of BPT.

    Attributes:
        w3 : (Web3) The Web3 instance.
        pool_id : (str) The id of the pool.
        avatar : (Address) The avatar address.
        token_in_address : (Address) The address of the token to be sent by the user.
        amount_in : (int) The precise amount of token to be sent by the user.
        min_bpt_amount_out : (int) The minimum amount of BPT to be minted.
        assets : (list[Address]) A list of addresses of the assets.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                avatar: Address,
                token_in_address: Address,
                amount_in: int,
                min_bpt_amount_out: int,
                assets: list[Address] = None):
        """
        Constructs all the necessary attributes for the ExactSingleTokenJoin object.

        Args:
            w3 : (Web3) The Web3 instance.
            pool_id : (str) The id of the pool.
            avatar : (Address) The avatar address.
            token_in_address : (Address) The address of the token to be sent by the user.
            amount_in : (int) The precise amount of token to be sent by the user.
            min_bpt_amount_out : (int) The minimum amount of BPT to be minted.
            assets : (list[Address]), optional A list of addresses of the assets. If not provided, it will be fetched from the pool.
        """

        if assets is None:
            assets = Pool(w3, pool_id).assets()

        join_token_index = assets.index(token_in_address)
        amounts_in = [0] * join_token_index + [amount_in] + [0] * (len(assets) - join_token_index - 1)

        super().__init__(blockchain=Chains.get_blockchain_from_web3(w3),
                        pool_id=pool_id,
                        avatar=avatar,
                        assets=assets,
                        amounts_in=amounts_in,
                        min_bpt_amount_out=min_bpt_amount_out)

class QueryJoinMixin:
    """
    A mixin class for querying joins in a Balancer pool.

    Attributes:
        name : (str) The name of the mixin.
        out_signature : (list[tuple]) The output signature for the query join.
    """

    name = "queryJoin"
    out_signature = [("bpt_out", "uint256"), ("amounts_in", "uint256[]")]


class ExactBptSingleTokenQueryJoin(QueryJoinMixin, ExactBptSingleTokenJoin):
    """
    A class representing a query for an exact single token join where the user sends a precise quantity of a single token, 
    and receives an estimated but unknown (computed at run time) quantity of BPT.

    Attributes:
        w3 : (Web3) The Web3 instance.
        pool_id : (str) The id of the pool.
        bpt_amount_out : (int) The amount of BPT to be minted.
        token_in_address : (Address) The address of the token to be sent by the user.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                bpt_amount_out: int,
                token_in_address: Address):
        """
        Constructs all the necessary attributes for the ExactBptSingleTokenQueryJoin object.

        Args:
            w3 : (Web3) The Web3 instance.
            pool_id : (str) The id of the pool.
            bpt_amount_out : (int) The amount of BPT to be minted.
            token_in_address : (Address) The address of the token to be sent by the user.
        """

        super().__init__(w3=w3,
                        pool_id=pool_id,
                        avatar=ZERO,
                        bpt_amount_out=bpt_amount_out,
                        token_in_address=token_in_address,
                        max_amount_in=MAX_UINT256)


class ProportionalQueryJoin(QueryJoinMixin, ProportionalJoin):
    """
    A class representing a query for a proportional join where the user sends estimated but unknown (computed at run time) quantities of tokens, 
    and receives a precise quantity of BPT.
    This class is a subclass of QueryJoinMixin and ProportionalJoin.

    Attributes:
        w3 : (Web3) The Web3 instance.
        pool_id : (str) The id of the pool.
        bpt_amount_out : (int) The amount of BPT to be minted.
        assets : (list[Address]), optional A list of addresses of the assets. If not provided, it will be fetched from the pool.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                bpt_amount_out: int,
                assets: list[Address] = None):
        """
        Constructs all the necessary attributes for the ProportionalQueryJoin object.

        Args:
            w3 : (Web3) The Web3 instance.
            pool_id : (str) The id of the pool.
            bpt_amount_out : (int) The amount of BPT to be minted.
            assets : (list[Address]), optional A list of addresses of the assets. If not provided, it will be fetched from the pool.
        """

        if assets is None:
            assets = Pool(w3, pool_id).assets()
        max_amounts_in = [MAX_UINT256] * len(assets)

        super().__init__(w3=w3,
                        pool_id=pool_id,
                        avatar=ZERO,
                        bpt_amount_out=bpt_amount_out,
                        max_amounts_in=max_amounts_in,
                        assets=assets)


class ExactTokensQueryJoin(QueryJoinMixin, ExactTokensJoin):
    """
    A class representing a query for an exact tokens join where the user sends precise quantities of tokens, 
    and receives an estimated but unknown (computed at run time) quantity of BPT.

    Attributes:
        w3 : (Web3) The Web3 instance.
        pool_id : (str) The id of the pool.
        amounts_in : (list[int]) A list of precise amounts of each token to be sent by the user.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                amounts_in: list[int]):
        """
        Constructs all the necessary attributes for the ExactTokensQueryJoin object.

        Args:
            w3 : (Web3) The Web3 instance.
            pool_id : (str) The id of the pool.
            amounts_in : (list[int]) A list of precise amounts of each token to be sent by the user.
        """

        super().__init__(w3=w3,
                        pool_id=pool_id,
                        avatar=ZERO,
                        amounts_in=amounts_in,
                        min_bpt_amount_out=0)


class ExactSingleTokenQueryJoin(QueryJoinMixin, ExactSingleTokenJoin):
    """
    A class representing a query for an exact single token join where the user sends a precise quantity of a single token, 
    and receives an estimated but unknown (computed at run time) quantity of BPT.

    Attributes:
        w3 : (Web3) The Web3 instance.
        pool_id : (str) The id of the pool.
        token_in_address : (Address) The address of the token to be sent by the user.
        amount_in : (int) The precise amount of token to be sent by the user.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                token_in_address: Address,
                amount_in: int):
        """
        Constructs all the necessary attributes for the ExactSingleTokenQueryJoin object.

        Args:
            w3 : (Web3) The Web3 instance.
            pool_id : (str) The id of the pool.
            token_in_address : (Address) The address of the token to be sent by the user.
            amount_in : (int) The precise amount of token to be sent by the user.
        """

        super().__init__(w3=w3,
                        pool_id=pool_id,
                        avatar=ZERO,
                        token_in_address=token_in_address,
                        amount_in=amount_in,
                        min_bpt_amount_out=0)


class ExactBptSingleTokenJoinSlippage(ExactBptSingleTokenJoin):
    """
    A class representing an exact single token join where the user sends a precise quantity of a single token, 
    and receives a precise quantity of BPT, considering a specified maximum slippage.

    Attributes:
        w3 : (Web3) The Web3 instance.
        pool_id : (str) The id of the pool.
        avatar : (Address) The avatar address.
        bpt_amount_out : (int) The amount of BPT to be minted.
        token_in_address : (Address) The address of the token to be sent by the user.
        max_slippage : (float) The maximum slippage allowed for the transaction.
        assets : (list[Address]), optional A list of addresses of the assets. If not provided, it will be fetched from the pool.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                avatar: Address,
                bpt_amount_out: int,
                token_in_address: Address,
                max_slippage: float,
                assets: list[Address] = None):
        """
        Constructs all the necessary attributes for the ExactBptSingleTokenJoinSlippage object.

        Args:
            w3 : (Web3) The Web3 instance.
            pool_id : (str) The id of the pool.
            avatar : (Address) The avatar address.
            bpt_amount_out : (int) The amount of BPT to be minted.
            token_in_address : (Address) The address of the token to be sent by the user.
            max_slippage : (float) The maximum slippage allowed for the transaction.
            assets : (list[Address]), optional A list of addresses of the assets. If not provided, it will be fetched from the pool.
        """

        if assets is None:
            assets = Pool(w3, pool_id).assets()

        m = ExactBptSingleTokenQueryJoin(w3=w3,
                                        pool_id=pool_id,
                                        bpt_amount_out=bpt_amount_out,
                                        token_in_address=token_in_address)

        join_token_index = assets.index(token_in_address)
        bpt_amount_out_sim, amounts_in_sim = m.call(web3=w3)
        if not bpt_amount_out - 1 <= bpt_amount_out_sim <= bpt_amount_out + 1:
            raise ValueError(
                f"The bpt_amount_out = {bpt_amount_out} specified is not the same as the bpt_amount_out = {bpt_amount_out_sim} calculated by the query contract."
            )

        max_amount_in = int(Decimal(amounts_in_sim[join_token_index]) * Decimal(1 + max_slippage))

        super().__init__(w3=w3,
                        pool_id=pool_id,
                        avatar=avatar,
                        bpt_amount_out=bpt_amount_out,
                        token_in_address=token_in_address,
                        max_amount_in=max_amount_in,
                        assets=assets)

class ExactSingleTokenJoinSlippage(ExactSingleTokenJoin):
    """
    ExactSingleTokenJoinSlippage is a class that inherits from ExactSingleTokenJoin.
    It represents a join operation with a specified maximum slippage.

    Attributes:
        w3 : (Web3) An instance of Web3, used for interacting with the Ethereum blockchain.
        pool_id : (str) A string representing the ID of the pool.
        avatar : (Address) An instance of Address, representing the avatar of the pool.
        token_in_address : (Address) An instance of Address, representing the address of the token to be joined.
        amount_in : (int) An integer representing the amount of token to be joined.
        max_slippage : (float) A float representing the maximum slippage allowed for the join operation.
        assets : (list[Address]), optional A list of Address instances, representing the assets in the pool. This is optional and if not provided, the assets are fetched from the pool.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                avatar: Address,
                token_in_address: Address,
                amount_in: int,
                max_slippage: float,
                assets: list[Address] = None):
        """
        Constructs all the necessary attributes for the ExactSingleTokenJoinSlippage object.

        Args:
            w3 : (Web3) An instance of Web3, used for interacting with the Ethereum blockchain.
            pool_id : (str) A string representing the ID of the pool.
            avatar : (Address) An instance of Address, representing the avatar of the pool.
            token_in_address : (Address) An instance of Address, representing the address of the token to be joined.
            amount_in : (int) An integer representing the amount of token to be joined.
            max_slippage : (float) A float representing the maximum slippage allowed for the join operation.
            assets : (list[Address]), optional A list of Address instances, representing the assets in the pool. This is optional and if not provided, the assets are fetched from the pool.
        """

        if assets is None:
            assets = Pool(w3, pool_id).assets()
        join_token_index = assets.index(token_in_address)
        m = ExactSingleTokenQueryJoin(w3=w3,
                                    pool_id=pool_id,
                                    token_in_address=token_in_address,
                                    amount_in=amount_in)

        bpt_amount_out_sim, amounts_in = m.call(web3=w3)
        if not amount_in - 1 <= amounts_in[join_token_index] <= amounts_in + 1:
            raise ValueError(
                f"The amount_in = {amount_in} specified is not the same as the bpt_amount_out = {amounts_in[join_token_index]} calculated by the query contract."
            )
        min_bpt_amount_out = int(Decimal(bpt_amount_out_sim) * Decimal(1 - max_slippage))

        super().__init__(w3=w3,
                    pool_id=pool_id,
                    avatar=avatar,
                    token_in_address=token_in_address,
                    amount_in=amount_in,
                    min_bpt_amount_out=min_bpt_amount_out,
                    assets=assets)


class ExactBptProportionalJoinSlippage(ProportionalJoin):
    """
    ExactBptProportionalJoinSlippage is a class that inherits from ProportionalJoin.
    It represents a join operation with a specified maximum slippage.

    Attributes:
        w3 : (Web3) An instance of Web3, used for interacting with the Ethereum blockchain.
        pool_id : (str) A string representing the ID of the pool.
        avatar : (Address) An instance of Address, representing the avatar of the pool.
        bpt_amount_out : (int) An integer representing the amount of BPT to be minted.
        max_slippage : (float) A float representing the maximum slippage allowed for the join operation.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                avatar: Address,
                bpt_amount_out: int,
                max_slippage: float):
        """
        Constructs all the necessary attributes for the ExactBptProportionalJoinSlippage object.

        ArgsL
            w3 : (Web3) An instance of Web3, used for interacting with the Ethereum blockchain.
            pool_id : (str) A string representing the ID of the pool.
            avatar : (Address) An instance of Address, representing the avatar of the pool.
            bpt_amount_out : (int) An integer representing the amount of BPT to be minted.
            max_slippage : (float) A float representing the maximum slippage allowed for the join operation.
        """

        m = ProportionalQueryJoin(w3=w3,
                                    pool_id=pool_id,
                                    bpt_amount_out=bpt_amount_out)

        bpt_amount_out_sim, amounts_in_sim = m.call(web3=w3)
        if not bpt_amount_out - 1 <= bpt_amount_out_sim <= bpt_amount_out + 1:
            raise ValueError(
                f"The bpt_amount_out = {bpt_amount_out} specified is not the same as the bpt_amount_out = {bpt_amount_out_sim} calculated by the query contract."
            )
        max_amounts_in = [int(Decimal(amount) * Decimal(1 + max_slippage)) for amount in amounts_in_sim]

        super().__init__(w3=w3,
                        pool_id=pool_id,
                        avatar=avatar,
                        bpt_amount_out=bpt_amount_out,
                        max_amounts_in=max_amounts_in)


class ExactTokensJoinSlippage(ExactTokensJoin):
    """
    ExactTokensJoinSlippage is a class that inherits from ExactTokensJoin.
    It represents a join operation with a specified maximum slippage.

    Attributes:
        w3 : (Web3) An instance of Web3, used for interacting with the Ethereum blockchain.
        pool_id : (str) A string representing the ID of the pool.
        avatar : (Address) An instance of Address, representing the avatar of the pool.
        amounts_in : (list[int]) A list of integers representing the amounts of tokens to be joined.
        max_slippage : (float) A float representing the maximum slippage allowed for the join operation.
    """

    def __init__(self,
                w3: Web3,
                pool_id: str,
                avatar: Address,
                amounts_in: list[int],
                max_slippage: float):
        """
        Constructs all the necessary attributes for the ExactTokensJoinSlippage object.

        Args:
            w3 : (Web3) An instance of Web3, used for interacting with the Ethereum blockchain.
            pool_id : (str) A string representing the ID of the pool.
            avatar : (Address) An instance of Address, representing the avatar of the pool.
            amounts_in : (list[int]) A list of integers representing the amounts of tokens to be joined.
            max_slippage : (float) A float representing the maximum slippage allowed for the join operation.
        """

        m = ExactTokensQueryJoin(w3=w3,
                                    pool_id=pool_id,
                                    amounts_in=amounts_in)

        bpt_out, amounts_in = m.call(web3=w3)
        min_bpt_amount_out = int(Decimal(bpt_out) * Decimal(1 - max_slippage))

        super().__init__(w3=w3,
                        pool_id=pool_id,
                        avatar=avatar,
                        amounts_in=amounts_in,
                        min_bpt_amount_out=min_bpt_amount_out)

class ExactSingleTokenProportionalJoinSlippage(ExactTokensJoin):
    """
    ExactSingleTokenProportionalJoinSlippage is a class that inherits from ExactTokensJoin.
    It represents a join operation with a specified maximum slippage.

    Attributes:
        w3 : (Web3) An instance of Web3, used for interacting with the Ethereum blockchain.
        pool_id : (str) A string representing the ID of the pool.
        avatar : (Address) An instance of Address, representing the avatar of the pool.
        token_in_address : (Address) An instance of Address, representing the address of the token to be joined.
        amount_in : (int) An integer representing the amount of token to be joined.
        max_slippage : (float) A float representing the maximum slippage allowed for the join operation.
        assets : (list[Address]), optional A list of Address instances, representing the assets in the pool. This is optional and if not provided, the assets are fetched from the pool.
    """

    def __init__(self,
            w3: Web3,
            pool_id: str,
            avatar: Address,
            token_in_address: Address,
            amount_in: int,
            max_slippage: float,
            assets: list[Address] = None):
        """
        Constructs all the necessary attributes for the ExactSingleTokenProportionalJoinSlippage object.

        Args:
            w3 : (Web3) An instance of Web3, used for interacting with the Ethereum blockchain.
            pool_id : (str) A string representing the ID of the pool.
            avatar : (Address) An instance of Address, representing the avatar of the pool.
            token_in_address : (Address) An instance of Address, representing the address of the token to be joined.
            amount_in : (int) An integer representing the amount of token to be joined.
            max_slippage : (float) A float representing the maximum slippage allowed for the join operation.
            assets : (list[Address]), optional A list of Address instances, representing the assets in the pool. This is optional and if not provided, the assets are fetched from the pool.
        """

        if assets is None:
            assets = Pool(w3, pool_id).assets()
        join_token_index = assets.index(token_in_address)
        balances = Pool(w3, pool_id).pool_balances()
        amounts_in = [int(Decimal(balance) * Decimal(amount_in) / Decimal(balances[join_token_index])) for balance in
                        balances]

        m = ExactTokensQueryJoin(w3=w3,
                                    pool_id=pool_id,
                                    amounts_in=amounts_in)

        bpt_amount_out_sim, amounts_in_sim = m.call(web3=w3)
        if not amount_in - 1 <= amounts_in_sim[join_token_index] <= amount_in + 1:
            raise ValueError(
                f"The amount_in = {amount_in} specified is not the same as the amount_in = {amounts_in_sim[join_token_index]} calculated by the query contract."
            )
        min_bpt_amount_out = int(Decimal(bpt_amount_out_sim) * Decimal(1 - max_slippage))

        super().__init__(w3=w3,
                        pool_id=pool_id,
                        avatar=avatar,
                        amounts_in=amounts_in,
                        min_bpt_amount_out=min_bpt_amount_out,
                        assets=assets)
