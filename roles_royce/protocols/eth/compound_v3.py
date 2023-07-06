import eth_abi
from web3 import Web3
from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Method, Address, BaseApproveForToken


class Comet:
    cUSDCv3 = "0xc3d688B66703497DAA19211EEdff47f25384cdc3"
    cWETHv3 = "0xA17581A9E3356d9A858b789D68B4d866e593aE94"


ACTION_SUPPLY_NATIVE_TOKEN = "0x" + b'ACTION_SUPPLY_NATIVE_TOKEN'.hex().ljust(64, '0')


class Approve(BaseApproveForToken):
    fixed_arguments = {"spender": ETHAddr.AURABooster}

    def __init__(self, comet: Address, token: Address, amount: int):
        super().__init__(token=token, amount=amount)
        self.args.spender = comet


class Allow(Method):
    """Allow

    The approval for the MainnetBulker is done once per wallet.
    """
    name = "allow"
    in_signature = [("manager", "address"), ("is_allowed", "bool")]
    fixed_arguments = {"manager": ETHAddr.COMPOUND_Bulker, "is_allowed": True}

    def __init__(self, comet: Address):
        self.target_address = comet
        super().__init__()


class Supply(Method):
    """Supply token.

    If the supplied asset is the underlying token of the Comet then you get in exchange approximately
    the same amount of Comet token. Otherwise, the supplied amount of asset is transfered to the Comet as collateral.
    """
    name = "supply"
    in_signature = [("asset", "address"), ("amount", "uint256")]

    def __init__(self, comet: Address, token: Address, amount: int):
        super().__init__()
        self.target_address = comet
        self.args.asset = token
        self.args.amount = amount


class SupplyETH(Method):
    """Supply ETH"""
    name = "invoke"
    in_signature = [("actions", "bytes32[]"), ("data", "bytes[]")]
    fixed_arguments = {"actions": [ACTION_SUPPLY_NATIVE_TOKEN]}
    target_address = ETHAddr.COMPOUND_Bulker

    def __init__(self, comet: Address, avatar: Address, amount: int):
        super().__init__(value=amount)
        self.args.data = [eth_abi.encode(types=('address', 'address', 'uint256'), args=[comet, avatar, amount])]


"""
### Deployments:

- Comets:
    - `cUSDCv3`:
        - mainnet: 0xc3d688B66703497DAA19211EEdff47f25384cdc3
    - `cWETHv3`:
        - mainnet: 0xA17581A9E3356d9A858b789D68B4d866e593aE94
- `MainnetBulker`:
    - mainnet: 0xa397a8C2086C554B531c02E29f3291c9704B00c7
- `CometRewards`:
    - mainnet: 0x1B0e765F6224C21223AeA2af16c1C46E38885a40

### Categorized Methods:

- Withdraw:
    1. Method 1: `withdraw`
        - Description: if the withdrawn asset is the underlying token of the Comet then you burn the amount of Comet token for the same amount of underlying token. Otherwise the withdrawn amount of asset is removed from the Comet as collateral
        - Target Address: `Comet`
        - Function signature: `withdraw(address,uint256)`
        - Parameters:
            1. asset: `Token` (not ETH)
            2. amount: unconstrained
    2. Method 2: `withdrawETH`
        - Description: withdraw ETH → Every transaction with ETH uses the metafunction `invoke(bytes32[],bytes[])`
        - Target Address: `MainnetBulker`
        - Function signature: `invoke(bytes32[],bytes[])`
        - Parameters:
            1. actions: `["0x414354494f4e5f57495448445241575f4e41544956455f544f4b454e00000000"]` (ACTION_WITHDRAW_NATIVE_TOKEN)
            2. data: `[(address comet, address to, uint amount)]` → (`Comet`, `AVATAR`, amount)
- Borrow: same as Withdraw but you can ONLY borrow the Comets’ underlying token
    
    See Withdraw
    
- Repay: same as Deposit but you can ONLY repay the Comets’ underlying token
    
    See Deposit
    
- Claim:
    1. Method 1: `claim`
        - Description: claim COMP rewards
        - Target Address: `CometRewards`
        - Function signature: `claim(address,address,bool)`
        - Parameters:
            1. comet: `Comet`
            2. src: `AVATAR`
            3. shouldAccrue
"""
