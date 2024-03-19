from defabipedia.types import Chain
from web3 import Web3

from roles_royce.constants import CrossChainAddr
from roles_royce.protocols.base import Address, BaseApproveForToken

from .contract_methods import StakeInGauge, UnstakeFromGauge


class ApproveForVault(BaseApproveForToken):
    """approve Token with BalancerVault as spender"""

    fixed_arguments = {"spender": CrossChainAddr.BalancerVault}


class Stake(StakeInGauge):
    def __init__(self, w3: Web3, gauge_address: Address, amount: int):
        super().__init__(blockchain=Chain.get_blockchain_from_web3(w3), gauge_address=gauge_address, amount=amount)


class Unstake(UnstakeFromGauge):
    def __init__(self, w3: Web3, gauge_address: Address, amount: int):
        super().__init__(blockchain=Chain.get_blockchain_from_web3(w3), gauge_address=gauge_address, amount=amount)
