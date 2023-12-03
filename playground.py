from web3 import Web3

poep = Web3.keccak(text="santi_the_best")
print(poep.hex())

b'{"errorType":"AppDataHashMismatch","description":"calculated app data hash 0x970eb15ab11f171c843c2d1fa326b7f8f6bf06ac7f84bb1affcc86511c783f12 doesn\'t match order app data field 0xac657dc52b86f5c106d0f8f35a962c15e8d7c969cac7966c9fb03809064b5eef"}'