from web3 import Web3
from enum import IntEnum
from roles_royce.constants import Chain
from roles_royce.protocols.balancer.addresses_and_abis import AddressesAndAbis
from web3.exceptions import ContractLogicError
from .types_and_enums import PoolKind
from dataclasses import dataclass

@dataclass
class Pool:
    w3: Web3
    pool_id: str

    def pool_kind(self) -> PoolKind:
        """
        Returns the kind of pool
        """
        blockchain = Chain.get_blockchain_from_web3(self.w3)
        vault_contract = self.w3.eth.contract(address=AddressesAndAbis[blockchain].Vault.address,
                                         abi=AddressesAndAbis[blockchain].Vault.abi)
        bpt_address = vault_contract.functions.getPool(self.pool_id).call()[0]
        bpt_contract = self.w3.eth.contract(address=bpt_address, abi=AddressesAndAbis[blockchain].UniversalBPT.abi)
        try:
            bpt_contract.functions.getNormalizedWeights().call()
            return PoolKind.WeightedPool
        except ContractLogicError:
            try:
                bpt_contract.functions.getBptIndex().call()
                return PoolKind.ComposableStablePool
            except ContractLogicError:
                try:
                    bpt_contract.functions.inRecoveryMode().call()
                    return PoolKind.StablePool
                except ContractLogicError:
                    return PoolKind.MetaStablePool


    def assets(self) -> list[str]:
        """
        Returns the assets of a pool given a pool id
        """
        blockchain = Chain.get_blockchain_from_web3(self.w3)
        vault_contract = self.w3.eth.contract(address=AddressesAndAbis[blockchain].Vault.address,
                                         abi=AddressesAndAbis[blockchain].Vault.abi)
        return vault_contract.functions.getPoolTokens(self.pool_id).call()[0]


    def pool_balances(self) -> list[int]:
        """
        Returns the token balances of a pool given a pool id
        """
        blockchain = Chain.get_blockchain_from_web3(self.w3)
        vault_contract = self.w3.eth.contract(address=AddressesAndAbis[blockchain].Vault.address,
                                         abi=AddressesAndAbis[blockchain].Vault.abi)
        return vault_contract.functions.getPoolTokens(self.pool_id).call()[1]


    def bpt_index_from_composable(self) -> int:
        """
        Returns the bpt index of a composable pool given a pool id
        """
        pool_kind = self.pool_kind()
        if pool_kind != PoolKind.ComposableStablePool:
            raise ValueError("Pool is not a composable stable pool")
        else:
            blockchain = Chain.get_blockchain_from_web3(self.w3)
            vault_contract = self.w3.eth.contract(address=AddressesAndAbis[blockchain].Vault.address,
                                             abi=AddressesAndAbis[blockchain].Vault.abi)
            bpt_address = vault_contract.functions.getPool(self.pool_id).call()[0]
            bpt_contract = self.w3.eth.contract(address=bpt_address, abi=AddressesAndAbis[blockchain].UniversalBPT.abi)
            return bpt_contract.functions.getBptIndex().call()

    def bpt_balance(self, address: str) -> int:
        blockchain = Chain.get_blockchain_from_web3(self.w3)
        vault_contract = self.w3.eth.contract(address=AddressesAndAbis[blockchain].Vault.address,
                                         abi=AddressesAndAbis[blockchain].Vault.abi)
        bpt_address = vault_contract.functions.getPool(self.pool_id).call()[0]
        bpt_contract = self.w3.eth.contract(address=bpt_address, abi=AddressesAndAbis[blockchain].UniversalBPT.abi)
        return bpt_contract.functions.balanceOf(address).call()