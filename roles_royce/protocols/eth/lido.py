from defabipedia.cowswap_signer import ContractSpecs as CowswapSignerContractSpecs
from defabipedia.tokens import EthereumTokenAddr as ETHAddr
from defabipedia.types import Chain

from roles_royce.protocols.base import Address, AvatarAddress, BaseApprove, ContractMethod


class ApproveRelayerStETH(BaseApprove):
    """approve relayer to spend stETH"""

    fixed_arguments = {"spender": CowswapSignerContractSpecs[Chain.ETHEREUM].CowswapRelayer.address}
    token = ETHAddr.stETH


class ApproveRelayerWstETH(BaseApprove):
    """approve relayer to spend wstETH"""

    fixed_arguments = {"spender": CowswapSignerContractSpecs[Chain.ETHEREUM].CowswapRelayer.address}
    token = ETHAddr.wstETH


class ApproveWithdrawalStETHwithWstETH(BaseApprove):
    """approve stETH withdrawal with wstETH as spender"""

    fixed_arguments = {"spender": ETHAddr.wstETH}
    token = ETHAddr.stETH


class ApproveWithdrawalStETHWithUnstETH(BaseApprove):
    """approve stETH withdrawal with unstETH as spender"""

    fixed_arguments = {"spender": ETHAddr.unstETH}
    token = ETHAddr.stETH


class ApproveWithdrawalWstETH(BaseApprove):
    """approve wstETH withdrawal with unstETH as spender"""

    fixed_arguments = {"spender": ETHAddr.unstETH}
    token = ETHAddr.wstETH


class Deposit(ContractMethod):
    """sender deposits ETH and receives stETH"""

    name = "submit"
    in_signature = [("referral", "address")]
    fixed_arguments = {"referral": ETHAddr.ZERO}
    target_address = ETHAddr.stETH

    def __init__(self, eth_amount: int):
        super().__init__(value=eth_amount)


class Wrap(ContractMethod):
    name = "wrap"
    in_signature = [("amount", "uint256")]
    target_address = ETHAddr.wstETH

    def __init__(self, amount: int):
        """Sender deposits stETH and receives wstETH.

        Args:
            amount: amount of wstETH user receives after wrap.
        """
        super().__init__()
        self.args.amount = amount


class Unwrap(ContractMethod):
    """Sender redeems wstETH and receives stETH."""

    name = "unwrap"
    in_signature = [("amount", "uint256")]
    target_address = ETHAddr.wstETH

    def __init__(self, amount: int):
        """Amount of stETH user receives after unwrap"""
        super().__init__()
        self.args.amount = amount


class RequestWithdrawalsStETH(ContractMethod):
    """Sender requests a claim on his ETH from stETH.

    Locks your stETH in the queue. In exchange, you receive an NFT that represents your position in the queue
    """

    name = "requestWithdrawals"
    in_signature = [("amounts", "uint256[]"), ("owner", "address")]
    fixed_arguments = {"owner": AvatarAddress}
    target_address = ETHAddr.unstETH

    def __init__(self, amounts: list, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.amounts = amounts


# TODO: the amounts is a list, because it has a max of 1000 stETH per element, should built that in


class RequestWithdrawalsWithPermitStETH(ContractMethod):
    """Sender requests a claim on his ETH from wstETH.

    When the unstETH has no allowance over the owner's stETH locks your stETH in the queue.
    In exchange, you receive an NFT that represents your position in the queue
    """

    name = "requestWithdrawalsWithPermit"
    in_signature = [
        ("amounts", "uint256[]"),
        ("owner", "address"),
        ("permit", ("value", "uint256"), ("deadline", "uint256"), ("v", "uint8"), ("r", "bytes32"), ("s", "bytes32")),
    ]
    fixed_arguments = {"owner": AvatarAddress}
    target_address = ETHAddr.unstETH

    def __init__(self, amounts: list, avatar: Address):
        super().__init__(avatar=avatar)
        self.args.amounts = amounts


class RequestWithdrawalsWstETH(RequestWithdrawalsStETH):
    """Transfers the wstETH to the unstETH to be burned in exchange for stETH

    Then it locks your stETH in the queue. In exchange, you receive an NFT that represents your position in the queue
    """

    name = "requestWithdrawalsWstETH"


class RequestWithdrawalsWithPermitWstETH(RequestWithdrawalsWithPermitStETH):
    """when the unstETH has no allowance over the owner's wstETH transfers the wstETH to the unstETH to be burned in exchange for stETH.

    Then it locks your stETH in the queue. In exchange, you receive an NFT that represents your position in the queue
    """

    name = "requestWithdrawalsWithPermitWstETH"


class GetWithdrawalRequests(ContractMethod):
    name = "getWithdrawalRequests"
    in_signature = [("owner", "address")]
    out_signature = [("ids", "uint256[]")]
    target_address = ETHAddr.unstETH

    def __init__(self, owner: Address):
        super().__init__()
        self.args.owner = owner


class ClaimWithdrawal(ContractMethod):
    """Sender wants to claim his ETH.

    Once the request is finalized by the oracle report and becomes claimable,
    this function claims your ether and burns the NFT.
    """

    name = "claimWithdrawals"
    in_signature = [("request_id", "uint256")]
    target_address = ETHAddr.unstETH

    def __init__(self, request_id: int):
        super().__init__()
        self.args.request_id = request_id


class ClaimWithdrawals(ContractMethod):
    """sender wants to claim his ETH in batches or optimize on hint search"""

    name = "claimWithdrawals"
    in_signature = [("request_ids", "uint256[]"), ("hints", "uint256[]")]
    target_address = ETHAddr.unstETH

    def __init__(self, request_ids: list, hints: list):
        super().__init__()
        self.args.request_ids = request_ids
        self.args.hints = hints


class GetWithdrawalStatus(ContractMethod):
    name = "getWithdrawalStatus"
    in_signature = [("request_ids", "uint256[]")]
    out_signature = [
        (
            "statuses",
            [
                (  # an array of structs
                    ("amount_of_stETH", "uint256"),
                    ("amount_of_shares", "uint256"),
                    ("owner", "address"),
                    ("timestamp", "uint256"),
                    ("is_finalized", "bool"),
                    ("is_claimed", "bool"),
                ),
                "tuple[]",
            ],
        )
    ]
    target_address = ETHAddr.unstETH

    def __init__(self, request_ids: list[int]):
        super().__init__()
        self.args.request_ids = request_ids
