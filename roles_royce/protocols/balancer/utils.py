from defabipedia.balancer import Abis, ContractSpecs
from defabipedia.types import Chain
from web3 import Web3
from web3.exceptions import ContractLogicError

from .types_and_enums import PoolKind


class Pool:
    def __init__(self, w3: Web3, pool_id: str):
        self.w3 = w3
        self.pool_id = pool_id
        blockchain = Chain.get_blockchain_from_web3(self.w3)
        self.vault_contract = ContractSpecs[blockchain].Vault.contract(self.w3)
        bpt_address = self.vault_contract.functions.getPool(self.pool_id).call()[0]
        self.bpt_contract = self.w3.eth.contract(address=bpt_address, abi=Abis[blockchain].UniversalBPT.abi)

    def pool_kind(self) -> PoolKind:
        """
        Returns the kind of pool
        """
        try:
            self.bpt_contract.functions.getNormalizedWeights().call()
            return PoolKind.WeightedPool
        except (ContractLogicError, ValueError):
            try:
                self.bpt_contract.functions.getBptIndex().call()
                return PoolKind.ComposableStablePool
            except (ContractLogicError, ValueError):
                try:
                    self.bpt_contract.functions.inRecoveryMode().call()
                    return PoolKind.StablePool
                except (ContractLogicError, ValueError):
                    return PoolKind.MetaStablePool

    def assets(self) -> list[str]:
        """
        Returns the assets of a pool given a pool id
        """
        return self.vault_contract.functions.getPoolTokens(self.pool_id).call()[0]

    def pool_balances(self) -> list[int]:
        """
        Returns the token balances of a pool given a pool id
        """
        return self.vault_contract.functions.getPoolTokens(self.pool_id).call()[1]

    def bpt_index_from_composable(self) -> int:
        """
        Returns the bpt index of a composable pool given a pool id
        """
        pool_kind = self.pool_kind()
        if pool_kind != PoolKind.ComposableStablePool:
            raise ValueError("Pool is not a composable stable pool")
        else:
            return self.bpt_contract.functions.getBptIndex().call()

    def bpt_balance(self, address: str) -> int:
        return self.bpt_contract.functions.balanceOf(address).call()
