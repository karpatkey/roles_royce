from roles_royce.constants import Chain
from roles_royce.abi_utils import load_abi, AddressOrAbi


class EthereumAddressesAndAbis:
    Storage = AddressOrAbi(address='0x1d8f8f00cfa6758d7bE78336684788Fb0ee0Fa46',
                            abi=load_abi('storage.json'),
                            name='Storage')
    DepositPool = AddressOrAbi(abi=load_abi('deposit_pool.json'),
                                name='DepositPool')
    ProtocolSettingsDeposit = AddressOrAbi(abi=load_abi('protocol_settings_deposit.json'),
                                name='ProtocolSettingsDeposit')
    SwapRouter = AddressOrAbi(address="0x16D5A408e807db8eF7c578279BEeEe6b228f1c1C",
                            abi=load_abi('swap_router.json'),
                            name='SwapRouter')
    rETH = AddressOrAbi(address="0xae78736Cd615f374D3085123A210448E74Fc6393",
                        abi=load_abi('rETH.json'),
                        name='rETH')

AddressesAndAbis = {
    Chain.Ethereum: EthereumAddressesAndAbis
}