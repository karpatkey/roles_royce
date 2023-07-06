# Roles Royce


The `roles_royce` package is a DeFi library that allows you to easily execute 
transactions using Zodiac Roles Modifier contracts (https://github.com/gnosis/zodiac-modifier-roles-v1)
for mulitple DeFi protocols. 

This project is currently being actively developed and it is in alpha state 
so expect backwards incompatible changes.

## Protocols supported

* AAVE
* Lido


## Usage

Two main functions are provided: `check` to statically check if a transaction will go through or will fail 
and `send` to actually send the transaction to the blockchain.

### Examples for supported protocols

```python 
from roles_royce.protocols.eth import aave_v2
from roles_royce import check, send, Chain
from web3 import Web3, HTTPProvider

claim = aave.ClaimAAVERewards(avatar="0x...", amount=10)

w3 = Web3(HTTPProvider("https://..."))
status = check([claim],
               role=1,
               account="0x...",
               roles_mod_address="0x...",
               web3=w3,
               blockchain=Chain.ETHEREUM)

```

Send the tx to the blockchain
```python

send([claim], 
     role=1, 
     private_key="xxx", 
     roles_mod_address="0x...", 
     web3=w3, 
     blockchain=Chain.ETHEREUM)
```

### Multisend transactions

Multisend transactions are supported: `send([tx1, tx2, tx3], ...)`

### Generic calls

Beside the provided protocol methods, generic calls can be performed:

```python

from roles_royce import check, send, GenericMethodTransaction, Operation, Chain

CURVE_USDC_USDT_REWARD_GAUGE = "0x7f90122BF0700F9E7e1F688fe926940E8839F353"

approve = GenericMethodTransaction(
    function_name="approve",
    function_args=[CURVE_USDC_USDT_REWARD_GAUGE, 1000],
    contract_address=GCAddr.USDT,
    contract_abi='[{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve",'
                 '"outputs":[{"name":"result","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]',
    operation=Operation.CALL,
    value=0,
)
add_liquidity = GenericMethodTransaction(
    function_name="add_liquidity",
    function_args=[[0, 0, 100], 0],
    contract_address=CURVE_USDC_USDT_REWARD_GAUGE,
    contract_abi='[{"stateMutability":"nonpayable","type":"function","name":"add_liquidity","inputs":[{"name":"_amounts","type":"uint256[3]"},'
                 '{"name":"_min_mint_amount","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}],"gas":7295966}]',
    operation=Operation.CALL,
    value=0,
)


ROLES_MOD_ADDRESS = "0xB6CeDb9603e7992A5d42ea2246B3ba0a21342503"
ACCOUNT = "0x7e19DE37A31E40eec58977CEA36ef7fB70e2c5CD"
status = check(txs=[approve, add_liquidity], 
               role=2, 
               account=ACCOUNT, 
               roles_mod_address=ROLES_MOD_ADDRESS,
               web3=w3, 
               blockchain=Chain.GC)

...
```

## Development

* Install the python dev dependencies: `pip install -r requirements-dev.txt`
* Install rolls_royce in editable mode: `pip install -e .`
* Install Hardhat by running `npm install` in the project's root directory.


If the tests are not working it may be due to hardhat not being correctly installed or some
other incompatibility. In this case run hardhat manually in fork mode on port 8546 with:

`npx hardhat node --show-stack-traces --fork 'URL' --port 8546`

and then run the tests with `RR_HARDHAT_STANDALONE=1 pytest`.
