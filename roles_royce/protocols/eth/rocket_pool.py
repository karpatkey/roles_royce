from defabipedia import Chain
from defabipedia.rocket_pool import ContractSpecs

from roles_royce.protocols.base import Address, BaseApprove, ContractMethod


class ApproveForSwapRouter(BaseApprove):
    """Approve rETH with Swap Router as spender"""

    fixed_arguments = {"spender": ContractSpecs[Chain.ETHEREUM].SwapRouter.address}
    token = ContractSpecs[Chain.ETHEREUM].rETH.address


class Deposit(ContractMethod):
    """sender deposits ETH and receives rETH"""

    name = "deposit"

    def __init__(self, deposit_pool: Address, value: int):
        super().__init__(value=value)
        self.target_address = deposit_pool


class Burn(ContractMethod):
    """Burns rETH in exchange for ETH"""

    name = "burn"
    target_address = ContractSpecs[Chain.ETHEREUM].rETH.address
    in_signature = [("_rethAmount", "uint256")]

    def __init__(self, amount: int):
        super().__init__()
        self.args._rethAmount = amount


class SwapTo(ContractMethod):
    """Swap ETH for rETH through SWAP_ROUTER.
    When there is not enough rETH in the DEPOSIT_POOL in exchange for
    the ETH you are depositing, the SWAP_ROUTER swaps the ETH for rETH
    in secondary markets (Balancer and Uniswap)"""

    name = "swapTo"
    target_address = ContractSpecs[Chain.ETHEREUM].SwapRouter.address
    in_signature = [
        ("_uniswapPortion", "uint256"),
        ("_balancerPortion", "uint256"),
        ("_minTokensOut", "uint256"),
        ("_idealTokensOut", "uint256"),
    ]

    def __init__(
        self, uniswap_portion: int, balancer_portion: int, min_tokens_out: int, ideal_tokens_out: int, value: int
    ):
        super().__init__(value=value)
        self.args._uniswapPortion = uniswap_portion
        self.args._balancerPortion = balancer_portion
        self.args._minTokensOut = min_tokens_out
        self.args._idealTokensOut = ideal_tokens_out


class SwapFrom(ContractMethod):
    """Swap rETH for ETH through SWAP_ROUTER.
    When there is not enough ETH in the DEPOSIT_POOL in exchange for
    the rETH you are withdrawing, the SWAP_ROUTER swaps the rETH for
    ETH in secondary markets (Balancer and Uniswap)"""

    name = "swapFrom"
    target_address = ContractSpecs[Chain.ETHEREUM].SwapRouter.address
    in_signature = [
        ("_uniswapPortion", "uint256"),
        ("_balancerPortion", "uint256"),
        ("_minTokensOut", "uint256"),
        ("_idealTokensOut", "uint256"),
        ("_tokensIn", "uint256"),
    ]

    def __init__(
        self, uniswap_portion: int, balancer_portion: int, min_tokens_out: int, ideal_tokens_out: int, tokens_in: int
    ):
        super().__init__()
        self.args._uniswapPortion = uniswap_portion
        self.args._balancerPortion = balancer_portion
        self.args._minTokensOut = min_tokens_out
        self.args._idealTokensOut = ideal_tokens_out
        self.args._tokensIn = tokens_in
