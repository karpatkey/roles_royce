from defi_protocols.Maker import underlying
from web3 import HTTPProvider, Web3

from roles_royce import roles
from roles_royce.constants import ETHAddr
from roles_royce.protocols.eth import maker
from roles_royce.utils import to_checksum_address
from tests.roles import apply_presets, deploy_roles, setup_common_roles
from tests.utils import (
    LOCAL_NODE_PORT,
    accounts,
    create_simple_safe,
    gen_test_accounts,
    get_balance,
    local_node,
    steal_token,
)

wstETH_JOIN = "0x10CD5fbe1b404B7E19Ef964B63939907bdaf42E2"  # GemJoin wstETH
ABI_GEM_JOIN = '[{"constant":true,"inputs":[],"name":"gem","outputs":[{"internalType":"contract GemLike_3","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"ilk","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"}]'
ABI_TOKEN = '[{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
ABI_CDP_MANAGER = '[{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"urns","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]'
ABI_VAT = '[{"constant":true,"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"},{"internalType":"address","name":"","type":"address"}],"name":"urns","outputs":[{"internalType":"uint256","name":"ink","type":"uint256"},{"internalType":"uint256","name":"art","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'


def test_maker_cdp_module_proxy():
    w3 = Web3(HTTPProvider(f"http://localhost:{LOCAL_NODE_PORT}"))
    accounts = gen_test_accounts()
    safe = create_simple_safe(w3=w3, owner=accounts[0])
    roles_ctract = deploy_roles(avatar=safe.address, w3=w3)
    setup_common_roles(safe, roles_ctract)

    # Build proxy
    build_receipt = safe.send([maker.Build()]).receipt
    for log in build_receipt["logs"]:
        if log["topics"][0].hex() == "0x259b30ca39885c6d801a0b5dbc988640f3c25e2f37531fe138c5c5af8955d41b":  # Created
            proxy_address = to_checksum_address("0x" + log["data"].hex()[26:66])
            break

    gem_join_contract = w3.eth.contract(address=wstETH_JOIN, abi=ABI_GEM_JOIN)
    gem = gem_join_contract.functions.gem().call()
    ilk = gem_join_contract.functions.ilk().call()

    presets = """{"version": "1.0","chainId": "1","meta":{ "description": "","txBuilderVersion": "1.8.0"},"createdAt": 1695904723785,"transactions": [
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x5e82669500000000000000000000000000000000000000000000000000000000000000010000000000000000000000006b175474e89094c44da98b954eedeac495271d0f","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x33a0480c00000000000000000000000000000000000000000000000000000000000000010000000000000000000000006b175474e89094c44da98b954eedeac495271d0f095ea7b30000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000140000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000001c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000020000000000000000000000000d758500ddec05172aaa035911387c8e0e789cf6a","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000001000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x33a0480c0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2095ea7b30000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000140000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000001c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000020000000000000000000000000d758500ddec05172aaa035911387c8e0e789cf6a","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x5e8266950000000000000000000000000000000000000000000000000000000000000001000000000000000000000000d758500ddec05172aaa035911387c8e0e789cf6a","value": "0"},
    {"to": "0x1ffAdc16726dd4F91fF275b4bF50651801B06a86","data": "0x33a0480c0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000d758500ddec05172aaa035911387c8e0e789cf6a1cff79cd0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000140000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000001c0000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002000000000000000000000000082ecd135dce65fbc6dbdd0e4237e0af93ffd5038","value": "0"}
    ]}"""
    apply_presets(
        safe,
        roles_ctract,
        json_data=presets,
        replaces=[
            ("c01318bab7ee1f5ba734172bf7718b5dc6ec90e1", safe.address[2:]),
            ("c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", gem[2:]),
            ("d758500ddec05172aaa035911387c8e0e789cf6a", proxy_address[2:]),
        ],
    )

    # steal wstETH
    steal_token(
        w3,
        token=ETHAddr.wstETH,
        holder="0x6cE0F913F035ec6195bC3cE885aec4C66E485BC4",
        to=safe.address,
        amount=1000_000_000_000_000_000_000,
    )
    # approve gem
    approve_gem = maker.ApproveGem(gem=gem, proxy=proxy_address, amount=1000_000_000_000_000_000_000)
    # send gem approval
    send_approve_gem = roles.send(
        [approve_gem], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3
    )

    gem_contract = w3.eth.contract(address=gem, abi=ABI_TOKEN)
    gem_allowance = gem_contract.functions.allowance(safe.address, proxy_address).call()
    assert gem_allowance == 1000_000_000_000_000_000_000

    # open cdp
    open_cdp = maker.ProxyActionOpen(proxy=proxy_address, ilk=ilk)
    send_open_cdp = roles.send(
        [open_cdp], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3
    )

    cdp_id = None
    for log in send_open_cdp["logs"]:
        if log["topics"][0].hex() == "0xd6be0bc178658a382ff4f91c8c68b542aa6b71685b8fe427966b87745c3ea7a2":  # NewCdp
            cdp_id = int(log["topics"][3].hex(), 16)
            print("CDP ID: ", cdp_id)
            break

    assert cdp_id

    # lockGem
    lock_gem = maker.ProxyActionLockGem(
        proxy=proxy_address, gem_join=wstETH_JOIN, cdp_id=cdp_id, wad=1000_000_000_000_000_000_000
    )
    send_lock_gem = roles.send(
        [lock_gem], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3
    )
    cdp_manager_contract = w3.eth.contract(address=ETHAddr.MakerCDPManager, abi=ABI_CDP_MANAGER)
    urn_handler = cdp_manager_contract.functions.urns(cdp_id).call()
    vat_contract = w3.eth.contract(address=ETHAddr.MakerVat, abi=ABI_VAT)
    locked_gem = vat_contract.functions.urns(ilk, urn_handler).call()[0]
    assert locked_gem == 1000_000_000_000_000_000_000
    print(underlying(cdp_id, "latest", web3=w3))

    # draw DAI
    draw_dai = maker.ProxyActionDraw(proxy=proxy_address, cdp_id=cdp_id, wad=100_000_000_000_000_000_000_000)
    send_draw_dai = roles.send(
        [draw_dai], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3
    )
    dai_balance = get_balance(w3=w3, token=ETHAddr.DAI, address=safe.address)
    assert dai_balance == 100_000_000_000_000_000_000_000
    print(underlying(cdp_id, "latest", web3=w3))

    # approve DAI
    approve_dai = maker.ApproveDAI(proxy=proxy_address, amount=100_000_000_000_000_000_000_000)
    send_approve_dai = roles.send(
        [approve_dai], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3
    )
    dai_contract = w3.eth.contract(address=ETHAddr.DAI, abi=ABI_TOKEN)
    dai_allowance = dai_contract.functions.allowance(safe.address, proxy_address).call()
    assert dai_allowance == 100_000_000_000_000_000_000_000

    # wipe DAI
    wipe_dai = maker.ProxyActionWipe(proxy=proxy_address, cdp_id=cdp_id, wad=100_000_000_000_000_000_000_000)
    send_wipe_dai = roles.send(
        [wipe_dai], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3
    )
    dai_balance = get_balance(w3=w3, token=ETHAddr.DAI, address=safe.address)
    assert dai_balance == 0
    print(underlying(cdp_id, "latest", web3=w3))

    # freeGem
    free_gem = maker.ProxyActionFreeGem(
        proxy=proxy_address, gem_join=wstETH_JOIN, cdp_id=cdp_id, wad=1000_000_000_000_000_000_000
    )
    send_free_gem = roles.send(
        [free_gem], role=1, private_key=accounts[1].key, roles_mod_address=roles_ctract.address, web3=w3
    )
    locked_gem = vat_contract.functions.urns(ilk, urn_handler).call()[0]
    assert locked_gem == 0
    print(underlying(cdp_id, "latest", web3=w3))


test_maker_cdp_module_proxy()
