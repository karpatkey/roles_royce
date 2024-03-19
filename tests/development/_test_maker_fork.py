from decimal import Decimal

from defi_protocols.constants import ETHEREUM
from defi_protocols.functions import get_contract, get_decimals
from defi_protocols.Maker import underlying
from web3 import HTTPProvider, Web3

from tests.utils import LOCAL_NODE_PORT, fork_reset_state, fork_unlock_account

VAT = "0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B"
PROXY_REGISTRY = "0x4678f0a6958e4D2Bc4F1BAF7Bc52E8F3564f3fE4"
DSS_PROXY_ACTIONS = "0x82ecD135Dce65Fbc6DbdD0e4237E0AF93FFD5038"
DSS_CDP_MANAGER = "0x5ef30b9986345249bc32d8928B7ee64DE9435E39"
JUG = "0x19c0976f590D67707E62397C87829d896Dc0f1F1"
wstETH_JOIN = "0x10CD5fbe1b404B7E19Ef964B63939907bdaf42E2"  # GemJoin wstETH
DAI_JOIN = "0x9759A6Ac90977b93B58547b4A71c78317f391A28"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

ETH_JOIN_A = "0x2F0b23f53734252Bda2277357e97e1517d6B042A"

ABI_PROXY = '[{"constant":false,"inputs":[{"name":"_target","type":"address"},{"name":"_data","type":"bytes"}],"name":"execute","outputs":[{"name":"response","type":"bytes32"}],"payable":true,"stateMutability":"payable","type":"function"}]'


def get_draw_dart(wallet, wad, urn_handler, ilk, web3, block):
    RAY = 10**27

    jug_contract = get_contract(JUG, ETHEREUM, web3=web3, block=block)
    rate = jug_contract.functions.drip(ilk).call()
    jug_contract.functions.drip(ilk).transact({"from": wallet})
    rate = jug_contract.functions.drip(ilk).call()

    # Test to check if the rate after calling the drip() function is the same as the rate in the vat
    vat_contract = get_contract(VAT, ETHEREUM, web3=web3, block=block)
    dai_urn = vat_contract.functions.dai(urn_handler).call(block_identifier=block)
    rate1 = vat_contract.functions.ilks(ilk).call()[1]

    if dai_urn < (RAY * wad):
        dart = int(((Decimal(RAY) * Decimal(wad)) - dai_urn) / Decimal(rate))
        if dart * rate < RAY * wad:
            dart += 1

    return dart


def get_wipe_dart(dai_urn, urn_handler, ilk, web3, block):
    vat_contract = get_contract(VAT, ETHEREUM, web3=web3, block=block)
    rate = vat_contract.functions.ilks(ilk).call()[1]
    art = vat_contract.functions.urns(ilk, urn_handler).call(block_identifier=block)[1]

    dart = int(Decimal(dai_urn) / Decimal(rate))
    if dart < art:
        dart = -dart
    else:
        dart = -int(art)

    return dart


def get_wipe_all_wad(urn_handler, ilk, web3, block):
    RAY = 10**27

    vat_contract = get_contract(VAT, ETHEREUM, web3=web3, block=block)
    rate = vat_contract.functions.ilks(ilk).call()[1]
    art = vat_contract.functions.urns(ilk, urn_handler).call(block_identifier=block)[1]
    urn_dai = vat_contract.functions.dai(urn_handler).call(block_identifier=block)

    rad = int((Decimal(art) * Decimal(rate)) - Decimal(urn_dai))
    wad = int(Decimal(rad) / Decimal(RAY))

    if (wad * RAY) < rad:
        wad += 1

    return wad


def test_maker(wallet, gem_join, block="latest"):
    web3 = Web3(HTTPProvider(f"http://localhost:{LOCAL_NODE_PORT}"))
    fork_reset_state(web3, url="https://eth-mainnet.g.alchemy.com/v2/IyKoMQ6TujGvW64xPvNYsg4_7XutQfN_", block=block)
    fork_unlock_account(web3, wallet)
    print(web3.eth.block_number)

    # https://github.com/makerdao/developerguides/blob/master/vault/cdp-manager-guide/cdp-manager-guide.md#setup
    cdp_manager_contract = get_contract(DSS_CDP_MANAGER, ETHEREUM, web3=web3, block=block)

    gem_join_contract = get_contract(gem_join, ETHEREUM, web3=web3, block=block)
    gem = gem_join_contract.functions.gem().call()
    ilk = gem_join_contract.functions.ilk().call()

    # open cdp
    open_tx = cdp_manager_contract.functions.open(ilk, wallet).transact({"from": wallet})
    while True:
        try:
            open_receipt = web3.eth.get_transaction_receipt(open_tx.hex())
            break
        except:
            pass

    for log in open_receipt["logs"]:
        if log["topics"][0].hex() == "0xd6be0bc178658a382ff4f91c8c68b542aa6b71685b8fe427966b87745c3ea7a2":  # NewCdp
            cdp_id = int(log["topics"][3].hex(), 16)
            print("CDP ID: ", cdp_id)
            break

    if cdp_id is not None:
        urn_handler = cdp_manager_contract.functions.urns(cdp_id).call(block_identifier=block)
        print("Urn Handler: ", urn_handler)

    # Gem approval
    gem_contract = get_contract(gem, ETHEREUM, web3=web3, block=block)
    wad_gem = 1000000000000000000000
    if gem == WETH:
        # EthJoins have as gem() the WETH. If a user wants to lock ETH as collateral they have to manually wrap the ETH.
        gem_contract.functions.deposit().transact({"from": wallet, "value": wad_gem})

    gem_contract.functions.approve(gem_join, wad_gem).transact({"from": wallet})
    gem_allowance = gem_contract.functions.allowance(wallet, gem_join).call(block_identifier=block)
    print("Gem Allowance: ", gem_allowance / 10 ** (get_decimals(gem, ETHEREUM)))

    gem_join_contract = get_contract(gem_join, ETHEREUM, web3=web3, block=block)
    join_tx = gem_join_contract.functions.join(urn_handler, wad_gem).transact({"from": wallet})

    # lockGem
    dink = wad_gem
    dart = 0
    cdp_manager_contract.functions.frob(cdp_id, dink, dart).transact({"from": wallet})

    vat_contract = get_contract(VAT, ETHEREUM, web3=web3, block=block)
    urn_data = vat_contract.functions.urns(ilk, urn_handler).call(block_identifier=block)
    dai_urn = vat_contract.functions.dai(urn_handler).call(block_identifier=block)

    print("Urn Data: ", urn_data)
    print("Dai in Urn: ", dai_urn / 10**45)
    print("Underlying: ", underlying(cdp_id, block, web3=web3))

    # drawDAI
    wad_dai = 100000000000000000000000
    dart = get_draw_dart(wallet, wad_dai, urn_handler, ilk, web3, block)
    cdp_manager_contract.functions.frob(cdp_id, 0, dart).transact({"from": wallet})
    dai_urn = vat_contract.functions.dai(urn_handler).call(block_identifier=block)

    # variable that has 45 decimal places
    rad = wad_dai * 10**27  # 45 = 18 + 27
    cdp_manager_contract.functions.move(cdp_id, wallet, rad).transact({"from": wallet})
    vat_contract.functions.hope(DAI_JOIN).transact({"from": wallet})

    dai_join_contract = get_contract(DAI_JOIN, ETHEREUM, web3=web3, block=block)
    dai_join_contract.functions.exit(wallet, wad_dai).transact({"from": wallet})
    urn_data = vat_contract.functions.urns(ilk, urn_handler).call(block_identifier=block)

    dai_contract = get_contract(DAI, ETHEREUM, web3=web3, block=block)
    dai_balance = dai_contract.functions.balanceOf(wallet).call(block_identifier=block)
    dai_urn = vat_contract.functions.dai(urn_handler).call(block_identifier=block)

    print("Dai in Urn: ", dai_urn / 10**45)
    print("Dai Balance: ", dai_balance / 10 ** (get_decimals(DAI, ETHEREUM)))
    print("Urn Data: ", urn_data)
    print("Underlying: ", underlying(cdp_id, block, web3=web3))

    # wipeDAI / repayDAI
    wad_dai = 50000000000000000000000
    dai_contract.functions.approve(DAI_JOIN, wad_dai).transact({"from": wallet})
    print("DAI in Urn: ", vat_contract.functions.dai(urn_handler).call(block_identifier=block))
    dai_join_contract.functions.join(urn_handler, wad_dai).transact({"from": wallet})
    urn_dai = vat_contract.functions.dai(urn_handler).call(block_identifier=block)
    print("DAI in Urn: ", urn_dai)
    dart = get_wipe_dart(urn_dai, urn_handler, ilk, web3, block)
    cdp_manager_contract.functions.frob(cdp_id, 0, dart).transact({"from": wallet})
    urn_data = vat_contract.functions.urns(ilk, urn_handler).call(block_identifier=block)

    dai_balance = dai_contract.functions.balanceOf(wallet).call(block_identifier=block)
    dai_urn = vat_contract.functions.dai(urn_handler).call(block_identifier=block)

    print("Dai in Urn: ", dai_urn / 10**45)
    print("Dai Balance: ", dai_balance / 10 ** (get_decimals(DAI, ETHEREUM)))
    print("Urn Data: ", urn_data)
    print("Underlying: ", underlying(cdp_id, block, web3=web3))

    # wipeAll
    wad = get_wipe_all_wad(urn_handler, ilk, web3, block)
    dai_contract.functions.approve(DAI_JOIN, wad).transact({"from": wallet})
    dai_join_contract.functions.join(urn_handler, wad).transact({"from": wallet})
    art = vat_contract.functions.urns(ilk, urn_handler).call(block_identifier=block)[1]
    cdp_manager_contract.functions.frob(cdp_id, 0, -art).transact({"from": wallet})

    urn_data = vat_contract.functions.urns(ilk, urn_handler).call(block_identifier=block)
    dai_balance = dai_contract.functions.balanceOf(wallet).call(block_identifier=block)
    dai_urn = vat_contract.functions.dai(urn_handler).call(block_identifier=block)

    print("Dai in Urn: ", dai_urn / 10**45)
    print("Dai Balance: ", dai_balance / 10 ** (get_decimals(DAI, ETHEREUM)))
    print("Urn Data: ", urn_data)
    print("Underlying: ", underlying(cdp_id, block, web3=web3))

    # freeGem
    if gem == WETH:
        gem_balance = web3.eth.get_balance(wallet)
    else:
        gem_balance = gem_contract.functions.balanceOf(wallet).call(block_identifier=block)

    print("Gem Balance before Free: ", gem_balance / 10 ** (get_decimals(WETH, ETHEREUM)))

    cdp_manager_contract.functions.frob(cdp_id, wad_gem * -1, 0).transact({"from": wallet})
    cdp_manager_contract.functions.flux(cdp_id, wallet, wad_gem).transact({"from": wallet})
    gem_join_contract.functions.exit(wallet, wad_gem).transact({"from": wallet})

    urn_data = vat_contract.functions.urns(ilk, urn_handler).call(block_identifier=block)

    if gem == WETH:
        # If a user wants to withdraw ETH, they have to manually unwrap the ETH.
        gem_contract.functions.withdraw(wad_gem).transact({"from": wallet})
        gem_balance = web3.eth.get_balance(wallet)
    else:
        gem_balance = gem_contract.functions.balanceOf(wallet).call(block_identifier=block)

    dai_urn = vat_contract.functions.dai(urn_handler).call(block_identifier=block)

    print("Urn Data: ", urn_data)
    print("Gem Balance after Free: ", gem_balance / 10 ** (get_decimals(WETH, ETHEREUM)))
    print("Urn Data: ", urn_data)
    print("Underlying: ", underlying(cdp_id, block, web3=web3))


test_maker(wallet="0x6cE0F913F035ec6195bC3cE885aec4C66E485BC4", gem_join=wstETH_JOIN)
# test_maker(wallet='0x189B9cBd4AfF470aF2C0102f365FC1823d857965', gem_join=ETH_JOIN_A)
