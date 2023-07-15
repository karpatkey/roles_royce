from enum import Enum
from roles_royce.constants import ETHAddr
from roles_royce.protocols.base import Method, Address, AvatarAddress, BaseApproveForToken


class Ctoken(Enum):
    cAAVE = "0xe65cdB6479BaC1e22340E4E755fAE7E509EcD06c"
    cBAT = "0x6C8c6b02E7b2BE14d4fA6022Dfd6d75921D90E4E"
    cCOMP = "0x70e36f6BF80a52b3B46b3aF8e106CC0ed743E8e4"
    cDAI = "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643"
    cETH = "0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5"
    cFEI = "0x7713DD9Ca933848F6819F38B8352D9A15EA73F67"
    cLINK = "0xFAce851a4921ce59e912d19329929CE6da6EB0c7"
    cMKR = "0x95b4eF2869eBD94BEb4eEE400a99824BF5DC325b"
    cREP = "0x158079Ee67Fce2f58472A96584A73C7Ab9AC95c1"
    cSAI = "0xF5DCe57282A584D2746FaF1593d3121Fcac444dC"
    cSUSHI = "0x4B0181102A0112A2ef11AbEE5563bb4a3176c9d7"
    cTUSD = "0x12392F67bdf24faE0AF363c24aC620a2f67DAd86"
    cUNI = "0x35A18000230DA775CAc24873d00Ff85BccdeD550"
    cUSDC = "0x39AA39c021dfbaE8faC545936693aC917d5E7563"
    cUSDP = "0x041171993284df560249B57358F931D9eB7b925D"
    cUSDT = "0xf650C3d88D12dB855b8bf7D11Be6C55A4e07dCC9"
    cWBTC = "0xC11b1268C1A384e55C48c2391d8d480264A3A7F4"
    cWBTC2 = "0xccF4429DB6322D5C611ee964527D42E5d685DD6a"
    cYFI = "0x80a2AE356fc9ef4305676f7a3E2Ed04e12C33946"
    cZRX = "0xB3319f5D18Bc0D84dD1b4825Dcde5d5f7266d407"


class Approve(BaseApproveForToken):
    def __init__(self, ctoken: Ctoken, token: Address, amount: int):
        super().__init__(token=token, amount=amount)
        self.args.spender = ctoken.value


class Mint(Method):
    """Deposit asset.

    Sender deposits a specified amount of underlying asset in exchange for cTokens
    """
    name = "mint"
    in_signature = [("amount", "uint256")]

    def __init__(self, ctoken: Ctoken, amount: int):
        super().__init__()
        self.target_address = ctoken.value
        self.args.amount = amount


class Redeem(Method):
    """Withdraw asset.

    It is called when MAX underlying amount is withdrawn
    """
    name = "redeem"
    in_signature = [("amount", "uint256")]

    def __init__(self, ctoken: Ctoken, amount: int):
        super().__init__()
        self.target_address = ctoken.value
        self.args.amount = amount


class RedeemUnderlying(Method):
    """Withdraw asset.

    It is called when MAX underlying amount is withdrawn
    """
    name = "redeemUnderlying"
    in_signature = [("amount", "uint256")]

    def __init__(self, ctoken: Ctoken, amount: int):
        super().__init__()
        self.target_address = ctoken.value
        self.args.amount = amount


class EnterMarkets(Method):
    """

    Set asset as collateral
    """
    name = "enterMarkets"
    in_signature = [("ctokens", "address[]")]
    target_address = ETHAddr.COMPOUND_V2_Comptroller

    def __init__(self, ctokens: list[Ctoken]):
        super().__init__()
        self.args.ctokens = [ctoken.value for ctoken in ctokens]


class ExitMarket(Method):
    """

    Unset asset as collateral
    """
    name = "exitMarkets"
    in_signature = [("ctoken", "address")]
    target_address = ETHAddr.COMPOUND_V2_Comptroller

    def __init__(self, ctoken: Ctoken):
        super().__init__()
        self.args.ctoken = ctoken.value


class Borrow(Method):
    """

    Borrow underlying asset amount.
    """
    name = "borrow"
    in_signature = [("amount", "uint256")]

    def __init__(self, ctoken: Ctoken, amount: int):
        super().__init__()
        self.target_address = ctoken.value
        self.args.amount = amount


class Repay(Method):
    """

    Repay underlying asset amount.
    """
    name = "repayBorrow"
    in_signature = [("amount", "uint256")]

    def __init__(self, ctoken: Ctoken, amount: int):
        super().__init__()
        self.target_address = ctoken.value
        self.args.amount = amount


class RepayETH(Method):
    """

    Repay ETH amount
    """
    name = "repayBehalf"
    in_signature = [("borrower", "address")]
    target_address = ETHAddr.COMPOUND_V2_Maximillion
    fixed_arguments = {"borrower": AvatarAddress}

    def __init__(self, avatar: Address):
        super().__init__(avatar=avatar)


class ClaimCOMP(Method):
    """

    Claim COMP rewards.
    """
    name = "claimComp"
    in_signature = [("holder", "address"), ("ctokens", "address[]")]
    target_address = ETHAddr.COMPOUND_V2_Comptroller
    fixed_arguments = {"holder": AvatarAddress}

    def __init__(self, avatar: Address, ctokens: list[Ctoken]):
        super().__init__(avatar=avatar)
        self.args.ctokens = [ctoken.value for ctoken in ctokens]

