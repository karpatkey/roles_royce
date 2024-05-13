# Roles Royce

Roles Royce is a Python library designed to execute transactions using Zodiac
Roles Modifier contracts (https://github.com/gnosis/zodiac-modifier-roles-v1).
With support for many DeFi protocols this library serves as a versatile toolkit
for securing your decentralized finance operations through the use of the
Roles Modifier contracts.

The project is currently undergoing active development, so we expect some backward
incompatibility changes until we stabilize the API. We encourage you to stay engaged
with the project’s updates and contribute to its evolution.

Some protocols supported: AAVEv2, Lido, Compound v2 and v3, Balancer, and more.

## Documentation

Check the docs in TODO

### Quick usage example

Send a tx to the blockchain through a Roles Modifier contract:

```python 
from roles_royce.protocols.eth import aave_v2
from roles_royce import roles
from web3 import Web3, HTTPProvider

w3 = Web3(HTTPProvider("https://..."))
claim = aave_v2.ClaimAAVERewards(avatar="0x...", amount=10)
status = roles.send([claim],
                    role=1,
                    private_key="xxx",
                    roles_mod_address="0x...",
                    web3=w3)

```

## Install

When using `roleroyce` as a library, you have two way to install it:
```sh
pip install . 'roleroyce[all]'
```
or, if you experiment dependencies conflicts, you can take control over some dependencies version by removing `[all]`
but specifying each missing dependencie.
```sh
pip install . 'roleroyce'
pip install "karpatkit @ git+https://github.com/karpatkey/karpatkit.git@another_specific_version"
```
where `another_specific_version` should be a git reference (tag, hash, branch).

Have a look `all` in the [pyproject.toml](pyproject.toml) file, `[project.optional-dependencies]` section.

> Take into account that installing just `roleroyce` without `roleroyce[all]` is an incompleted instalation.


## Development

* Install the python dev dependencies: `pip install -r requirements-dev.txt`
* Install rolls_royce in editable mode: `pip install -e . 'rolesroyce[all]'`
* Install anvil by downloading it from https://github.com/foundry-rs/foundry.

To run the tests start anvil in a terminal in fork mode on ports 8546 and 8547 with:

`anvil --accounts 15 -f 'mainnet_RPC_endpoint_URL' --port 8546`

`anvil --accounts 15 -f 'gnosis_RPC_endpoint_URL' --port 8547`

and then run the tests with `pytest -vs`.

### Building the docs

With sphinx installed `cd` into the `docs` dir and run `make html`. The output will be in `_build`.
