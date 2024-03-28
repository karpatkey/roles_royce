from defi_protocols.constants import ETHEREUM, ZERO_ADDRESS
from defi_protocols.functions import get_contract, get_data, get_decimals
from defi_protocols.Maker import get_vault_data, underlying
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


def test_maker(wallet, gem_join, block="latest"):
    web3 = Web3(HTTPProvider(f"http://localhost:{LOCAL_NODE_PORT}"))
    fork_reset_state(web3, url="https://eth-mainnet.g.alchemy.com/v2/IyKoMQ6TujGvW64xPvNYsg4_7XutQfN_", block=block)
    fork_unlock_account(web3, wallet)

    proxy_registry_contract = get_contract(PROXY_REGISTRY, ETHEREUM, web3=web3, block=block)

    build_tx = proxy_registry_contract.functions.build().transact({"from": wallet})
    while True:
        try:
            build_receipt = web3.eth.get_transaction_receipt(build_tx.hex())
            break
        except:
            pass

    proxy_address = ZERO_ADDRESS
    for log in build_receipt["logs"]:
        if log["topics"][0].hex() == "0x259b30ca39885c6d801a0b5dbc988640f3c25e2f37531fe138c5c5af8955d41b":  # Created
            proxy_address = web3.to_checksum_address("0x" + log["data"].hex()[26:66])
            break

    if proxy_address == ZERO_ADDRESS:
        raise ValueError("Proxy address not found.")
    else:
        gem_join_contract = get_contract(gem_join, ETHEREUM, web3=web3, block=block)
        gem = gem_join_contract.functions.gem().call()
        ilk = gem_join_contract.functions.ilk().call()

        # Gem approval
        gem_allowance = 0
        gem_contract = get_contract(gem, ETHEREUM, web3=web3, block=block)
        wad_gem = 1000000000000000000000

        if gem != WETH:
            gem_contract.functions.approve(proxy_address, wad_gem).transact({"from": wallet})
            gem_allowance = gem_contract.functions.allowance(wallet, proxy_address).call(block_identifier=block)
            print("Gem Allowance: ", gem_allowance / 10 ** (get_decimals(gem, ETHEREUM)))

        if gem_allowance > 0 or gem == WETH:
            proxy_contract = web3.eth.contract(address=proxy_address, abi=ABI_PROXY)
            dai_contract = get_contract(DAI, ETHEREUM, web3=web3, block=block)
            wad_dai = 100000000000000000000000

            # # Open a Vault, lock collateral, and draw DAI in one transaction
            # dai_balance = dai_contract.functions.balanceOf(wallet).call(block_identifier=block)
            # print('Dai Balance before Draw: ', dai_balance / 10**(get_decimals(DAI, ETHEREUM)))
            # if gem == WETH:
            #     gem_balance = web3.eth.get_balance(wallet)
            #     print('Gem Balance before Lock: ', gem_balance / 10**(get_decimals(gem, ETHEREUM)))
            #     data = get_data(DSS_PROXY_ACTIONS, "openLockETHAndDraw",
            #                     [DSS_CDP_MANAGER,
            #                     JUG,
            #                     gem_join,
            #                     DAI_JOIN,
            #                     ilk,
            #                     wad_dai], ETHEREUM, web3=web3, block=block)
            #     action_tx = proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact({"from": wallet, "value": wad_gem})
            # else:
            #     gem_balance = gem_contract.functions.balanceOf(wallet).call(block_identifier=block)
            #     print('Gem Balance before Lock: ', gem_balance / 10**(get_decimals(gem, ETHEREUM)))
            #     data = get_data(DSS_PROXY_ACTIONS, "openLockGemAndDraw",
            #                     [DSS_CDP_MANAGER,
            #                     JUG,
            #                     gem_join,
            #                     DAI_JOIN,
            #                     ilk,
            #                     wad_gem,
            #                     wad_dai,
            #                     True], ETHEREUM, web3=web3, block=block)
            #     action_tx = proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact({"from": wallet})

            # while True:
            #     try:
            #         action_receipt = web3.eth.get_transaction_receipt(action_tx.hex())
            #         break
            #     except:
            #         pass

            # cdp_id = None
            # for log in action_receipt["logs"]:
            #     if log["topics"][0].hex() == "0xd6be0bc178658a382ff4f91c8c68b542aa6b71685b8fe427966b87745c3ea7a2": # NewCdp
            #         cdp_id = int(log["topics"][3].hex(), 16)
            #         print('CDP ID: ', cdp_id)
            #         break

            # print(underlying(cdp_id, block, web3=web3))

            # dai_balance = dai_contract.functions.balanceOf(wallet).call(block_identifier=block)
            # print('Dai Balance after Draw: ', dai_balance / 10**(get_decimals(DAI, ETHEREUM)))

            # open cdp
            data = get_data(
                DSS_PROXY_ACTIONS, "open", [DSS_CDP_MANAGER, ilk, proxy_address], ETHEREUM, web3=web3, block=block
            )
            action_tx = proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact({"from": wallet})

            while True:
                try:
                    action_receipt = web3.eth.get_transaction_receipt(action_tx.hex())
                    break
                except:
                    pass

            cdp_id = None
            for log in action_receipt["logs"]:
                if (
                    log["topics"][0].hex() == "0xd6be0bc178658a382ff4f91c8c68b542aa6b71685b8fe427966b87745c3ea7a2"
                ):  # NewCdp
                    cdp_id = int(log["topics"][3].hex(), 16)
                    print("CDP ID: ", cdp_id)
                    break

            print(underlying(cdp_id, block, web3=web3))

            if cdp_id is not None:
                # lockGem
                if gem == WETH:
                    gem_balance = web3.eth.get_balance(wallet)
                    print("Gem Balance before Lock: ", gem_balance / 10 ** (get_decimals(gem, ETHEREUM)))
                    data = get_data(
                        DSS_PROXY_ACTIONS,
                        "lockETH",
                        [DSS_CDP_MANAGER, ETH_JOIN_A, cdp_id],
                        ETHEREUM,
                        web3=web3,
                        block=block,
                    )
                    action_tx = proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact(
                        {"from": wallet, "value": wad_gem}
                    )
                    gem_balance = web3.eth.get_balance(wallet)
                    print("Gem Balance before Lock: ", gem_balance / 10 ** (get_decimals(gem, ETHEREUM)))
                else:
                    gem_balance = gem_contract.functions.balanceOf(wallet).call(block_identifier=block)
                    print("Gem Balance before Lock: ", gem_balance / 10 ** (get_decimals(gem, ETHEREUM)))
                    data = get_data(
                        DSS_PROXY_ACTIONS,
                        "lockGem",
                        [DSS_CDP_MANAGER, gem_join, cdp_id, gem_allowance, True],
                        ETHEREUM,
                        web3=web3,
                        block=block,
                    )
                    action_tx = proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact({"from": wallet})
                    gem_balance = gem_contract.functions.balanceOf(wallet).call(block_identifier=block)
                    print("Gem Balance after Lock: ", gem_balance / 10 ** (get_decimals(gem, ETHEREUM)))

                print(underlying(cdp_id, block, web3=web3))

                # drawDAI
                # cdp_manager_contract = get_contract(DSS_CDP_MANAGER, ETHEREUM, web3=web3, block=block)
                # urn_handler  = cdp_manager_contract.functions.urns(cdp_id).call(block_identifier=block)
                # vat_contract = get_contract(VAT, ETHEREUM, web3=web3, block=block)
                # rate = vat_contract.functions.ilks(ilk).call(block_identifier=block)[1]
                # urn_data = vat_contract.functions.urns(ilk, urn_handler).call(block_identifier=block)
                # dai_urn = vat_contract.functions.dai(urn_handler).call(block_identifier=block)
                data = get_data(
                    DSS_PROXY_ACTIONS,
                    "draw",
                    [DSS_CDP_MANAGER, JUG, DAI_JOIN, cdp_id, wad_dai],
                    ETHEREUM,
                    web3=web3,
                    block=block,
                )
                action_tx = proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact({"from": wallet})

                print(underlying(cdp_id, block, web3=web3))

                # cdp_manager_contract = get_contract(DSS_CDP_MANAGER, ETHEREUM, web3=web3, block=block)
                # urn_handler  = cdp_manager_contract.functions.urns(cdp_id).call(block_identifier=block)
                # vat_contract = get_contract(VAT, ETHEREUM, web3=web3, block=block)
                # rate = vat_contract.functions.ilks(ilk).call(block_identifier=block)[1]
                # urn_data = vat_contract.functions.urns(ilk, urn_handler).call(block_identifier=block)
                # dai_urn = vat_contract.functions.dai(urn_handler).call(block_identifier=block)
                dai_balance = dai_contract.functions.balanceOf(wallet).call(block_identifier=block)
                print("Dai Balance: ", dai_balance / 10 ** (get_decimals(DAI, ETHEREUM)))

                # # lockGemAndDraw
                # if gem == WETH:
                #     gem_balance = web3.eth.get_balance(wallet)
                #     print('Gem Balance before Lock: ', gem_balance / 10**(get_decimals(gem, ETHEREUM)))
                #     data = get_data(DSS_PROXY_ACTIONS, "lockETHAndDraw",
                #                     [DSS_CDP_MANAGER,
                #                     JUG,
                #                     gem_join,
                #                     DAI_JOIN,
                #                     cdp_id,
                #                     wad_dai], ETHEREUM, web3=web3, block=block)
                #     proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact({"from": wallet, "value": wad_gem})
                #     gem_balance = web3.eth.get_balance(wallet)
                #     print('Gem Balance after Lock: ', gem_balance / 10**(get_decimals(gem, ETHEREUM)))
                # else:
                #     gem_balance = gem_contract.functions.balanceOf(wallet).call(block_identifier=block)
                #     print('Gem Balance before Lock: ', gem_balance / 10**(get_decimals(gem, ETHEREUM)))
                #     data = get_data(DSS_PROXY_ACTIONS, "lockGemAndDraw",
                #                     [DSS_CDP_MANAGER,
                #                     JUG,
                #                     gem_join,
                #                     DAI_JOIN,
                #                     cdp_id,
                #                     wad_gem,
                #                     wad_dai,
                #                     True], ETHEREUM, web3=web3, block=block)
                #     proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact({"from": wallet})
                #     gem_balance = gem_contract.functions.balanceOf(wallet).call(block_identifier=block)
                #     print('Gem Balance after Lock: ', gem_balance / 10**(get_decimals(gem, ETHEREUM)))

                # print(underlying(cdp_id, block, web3=web3))

                # freeGem
                if gem == WETH:
                    gem_balance = web3.eth.get_balance(wallet)
                    print("Gem Balance before Lock: ", gem_balance / 10 ** (get_decimals(gem, ETHEREUM)))
                    data = get_data(
                        DSS_PROXY_ACTIONS,
                        "freeETH",
                        [DSS_CDP_MANAGER, gem_join, cdp_id, 500000000000000000000],
                        ETHEREUM,
                        web3=web3,
                        block=block,
                    )
                    proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact({"from": wallet})
                    gem_balance = web3.eth.get_balance(wallet)
                    print("Gem Balance: ", gem_balance / 10 ** (get_decimals(gem, ETHEREUM)))
                else:
                    gem_balance = gem_contract.functions.balanceOf(wallet).call(block_identifier=block)
                    print("Gem Balance before Lock: ", gem_balance / 10 ** (get_decimals(gem, ETHEREUM)))
                    data = get_data(
                        DSS_PROXY_ACTIONS,
                        "freeGem",
                        [DSS_CDP_MANAGER, gem_join, cdp_id, 500000000000000000000],
                        ETHEREUM,
                        web3=web3,
                        block=block,
                    )
                    proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact({"from": wallet})
                    gem_balance = gem_contract.functions.balanceOf(wallet).call(block_identifier=block)
                    print("Gem Balance: ", gem_balance / 10 ** (get_decimals(gem, ETHEREUM)))

                print(underlying(cdp_id, block, web3=web3))

                # wipe
                # DAI approval
                wad_dai = 50000000000000000000000
                dai_contract.functions.approve(proxy_address, wad_dai).transact({"from": wallet})
                wad_dai = dai_contract.functions.allowance(wallet, proxy_address).call(block_identifier=block)
                print("DAI Allowance: ", wad_dai / 10 ** (get_decimals(DAI, ETHEREUM)))
                dai_balance = dai_contract.functions.balanceOf(wallet).call(block_identifier=block)
                print("Dai Balance before Wipe: ", dai_balance / 10 ** (get_decimals(DAI, ETHEREUM)))
                data = get_data(
                    DSS_PROXY_ACTIONS,
                    "wipe",
                    [DSS_CDP_MANAGER, DAI_JOIN, cdp_id, wad_dai],
                    ETHEREUM,
                    web3=web3,
                    block=block,
                )
                action_tx = proxy_contract.functions.execute(DSS_PROXY_ACTIONS, data).transact({"from": wallet})
                print(underlying(cdp_id, block, web3=web3))
                dai_balance = dai_contract.functions.balanceOf(wallet).call(block_identifier=block)
                print("Dai Balance after Wipe: ", dai_balance / 10 ** (get_decimals(DAI, ETHEREUM)))

                vault_data = get_vault_data(cdp_id, block, web3=web3)
                collateral_ratio = int(
                    round(
                        vault_data["ink"]
                        * vault_data["spot"]
                        * vault_data["mat"]
                        / vault_data["art"]
                        / vault_data["rate"]
                        * 100
                    )
                )
                print("Collateral Ratio: ", collateral_ratio)


# test_maker(wallet='0x6cE0F913F035ec6195bC3cE885aec4C66E485BC4', gem_join=wstETH_JOIN)
# test_maker(wallet='0x189B9cBd4AfF470aF2C0102f365FC1823d857965', gem_join=ETH_JOIN_A)
