# Roles Royce


The `roles_royce` package is a DeFi library that allows you to easily execute 
transactions using Zodiac Roles Modifier contracts (https://github.com/gnosis/zodiac-modifier-roles-v1)
for mulitple DeFi protocols. 

This project is currently being actively developed and it is in alpha state 
so expect backwards incompatible changes.

Some protocols supported:

* AAVEv2
* Lido
* Compound v2, v3
* Balancer


## Documentation

Check the docs in TODO

### Quick usage example

Send a tx to the blockchain through a Roles Modifier contract:

```python 
from roles_royce.protocols.eth import aave_v2
from roles_royce import send
from web3 import Web3, HTTPProvider

w3 = Web3(HTTPProvider("https://..."))
claim = aave_v2.ClaimAAVERewards(avatar="0x...", amount=10)
status = send([claim],
               role=1,
               private_key="xxx",
               roles_mod_address="0x...",
               web3=w3)

```

## Development

* Install the python dev dependencies: `pip install -r requirements-dev.txt`
* Install rolls_royce in editable mode: `pip install -e .`
* Install anvil by downloading it from https://github.com/foundry-rs/foundry.


To run the tests start anvil in a terminal in fork mode on port 8546 with:

`anvil --accounts 15 -f 'URL' --port 8546`

and then run the tests with `pytest -vs`.

### Building the docs

With sphinx installed run `sphinx-build  -b html docs/ docs/_build/`