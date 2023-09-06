Welcome to Roles Royce's docs!
==============================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Roles Royce is a Python library designed to execute transactions using Zodiac
`Roles Modifier contracts <https://github.com/gnosis/zodiac-modifier-roles-v1>`_.
With support for many DeFi protocols this library serves as a versatile toolkit
for securing your decentralized finance operations through the use of the
Roles Modifier contracts.

.. warning::
    The project is currently undergoing active development, so we expect some
    backward incompatibility changes until we stabilize the API.
    We encourage you to stay engaged with the project's updates and contribute
    to its evolution.


Overview
--------

Roles Royce provides a way to declare protocol functions, called :class:`~roles_royce.protocols.base.ContractMethod`,
and some functions to interact with the Roles Modifier contract:

- :meth:`roles_royce.roles.check` to statically check if a transaction will go through or will fail.
- :meth:`roles_royce.roles.send` to actually send the transaction to the blockchain.
- :meth:`roles_royce.roles.build` to create a transaction to later be sent to the blockchain
  or other uses such as studying it or composing it with other contracts.

Many DeFi protocols are already implemented, ready to be used. See `Supported protocols`_.

Example
-------

The following example shows how to deposit GNO from a `Safe <https://app.safe.global/>`_
using an EOA, that has roles modifier preset with permissions, into the Spark protocol:

.. code-block:: python

    from roles_royce import roles
    from roles_royce.protocols.eth import spark
    from web3 import Web3, HTTPProvider

    safe_address = "0x..."
    eoa_private_key = os.getenv("EOA_PRIVATE_KEY")
    roles_mod_address = "0x..." # Role contract with a preset that allows the EOA to approve and deposit

    w3 = Web3(HTTPProvider("https://..."))

    # Start with some GNO balance in the Safe
    assert get_balance(w3, ETHAddr.GNO, safe_address) == 123_000_000

    # Create the transaction data for the aproval and deposit of GNO
    txs = [
        spark.ApproveToken(token=ETHAddr.GNO, amount=123_000_000),
        spark.DepositToken(token=ETHAddr.GNO, avatar=safe_address,
                           amount=123_000_000),
        spark.ApproveToken(token=ETHAddr.GNO, amount=0),
    ]

    # Through the Roles modifier contract deposit GNO to receive spGNO
    # It will be executed as a single transaction using a Multisend contract
    roles.send(txs,
               private_key=eoa_private_key,
               roles_mod_address=,
               role=1,
               web3=w3)

    # All the Safe's GNO tokens were converted into spGNO
    assert get_balance(w3, ETHAddr.GNO, safe_address) == 0
    assert get_balance(w3, ETHAddr.spGNO, safe_address) == 123_000_000



Supported protocols
-------------------

.. toctree::
   :maxdepth: 2

   protocols/index

How to add support for a new protocol
-------------------------------------

To add support for ``My Porotocol`` in Mainnet create a python module in
``roles_royce/protocols/eth/myproto.py``.
In that file create a subclass of :class:`~roles_royce.protocols.base.ContractMethod` per function
of the contract (or contracts of the protocols) that you want to support.

Example of a simple function from the Lido protocol:

.. code-block:: python

    from roles_royce.constants import ETHAddr
    from roles_royce.protocols.base import ContractMethod, Address

    class Wrap(ContractMethod):
        name = "wrap" # name of the function in the contract
        in_signature = [("amount", "uint256")] #
        target_address = ETHAddr.wstETH # address of the contract

        def __init__(self, amount: int):
            """Sender deposits stETH and receives wstETH.

            :param amount: amount of wstETH user receives after wrap.
            """
            super().__init__() # always call the init of the inherited class
            self.args.amount = amount # the value of the arguments for the method


A more involved example from Compound v3, using ``fixed_arguments``:

.. code-block:: python

    class BorrowETH(ContractMethod):
        name = "borrowETH"
        # the name of each element of the in_signature has to match the name used in ``self.args``
        in_signature = [
            ("address", "address"),
            ("amount", "uint256"),
            ("interest_rate_model", "uint256"),
            ("referral_code", "uint16")
        ]
        # when some arguments should be fixed (not just with a default value) they go in
        # the fixed_arguments dict.
        fixed_arguments = {
            "address": ETHAddr.AAVE_V2_LendingPool,
            "referral_code": 0
        }
        target_address  = ETHAddr.AAVE_V2_WrappedTokenGateway

        def __init__(self, amount: int, interest_rate_model: InterestRateModel):
            """"Sender receives ETH and debtETH (stable or variable debt) tokens.

            :param amount: amount the amount of ETH to borrow.
            :param interest_rate_model: the interest rate model.
            """
            super().__init__()
            self.args.amount = amount
            self.args.interest_rate_model = interest_rate_model

For more examples check out the code of the supported protocols.

Generic calls
-------------

Beside the provided protocol methods, generic calls can be performed.

.. toctree::
   :maxdepth: 1

   generic_calls

Simulation
----------

Transactions can be simulated using Tenderly.
Example:

.. code-block:: python

    from roles_royce import roles
    from roles_royce.protocols.eth import aura
    from roles_royce.utils import simulate_tx

    ROLES_MOD = "0x1cFB0CD7B1111bf2054615C7C491a15C4A3303cc"
    REVOKER_ROLE = "0xf099e0f6604BDE0AA860B39F7da75770B34aC804"
    LP80GNO20WETH = "0x32296969Ef14EB0c6d29669C550D4a0449130230"

    method = aura.ApproveForBooster(token=LP80GNO20WETH, amount=1000)

    tx = roles.build(txs=[method], role=1, account=REVOKER_ROLE, roles_mod_address=ROLES_MOD, web3=web3_eth)

    sim_data = simulate_tx(tx,
                           block=17994590,
                           account_id="foobarbaz-d123-4140-adfb-123978bc0ab9",
                           project="project",
                           api_token="MyAPiToken123123123",
                           sim_type='quick')

    assert sim_data['transaction']['status']  # False if transaction fails
    assert sim_data['simulation']['block_number'] == 17994590
    assert sim_data['transaction']['call_trace'][0] == {
        'call_type': 'CALL', 'from': '0xf099e0f6604bde0aa860b39f7da75770b34ac804',
        'to': '0x1cfb0cd7b1111bf2054615c7c491a15c4a3303cc',
        'gas': 96760, 'gas_used': 61660, 'subtraces': 1, 'type': 'CALL',
        'input': '0x6928e74b00000000000000000000000032296969ef14eb0c6d29669c550d4a0449130230000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000044095ea7b3000000000000000000000000a57b8d98dae62b26ec3bcc4a365338157060b23400000000000000000000000000000000000000000000000000000000000003e800000000000000000000000000000000000000000000000000000000',
        'output': '0x0000000000000000000000000000000000000000000000000000000000000001'
    }



Api
---

Roles methods
~~~~~~~~~~~~~

.. autofunction:: roles_royce.roles.build
    :noindex:

.. autofunction:: roles_royce.roles.check
    :noindex:

.. autofunction:: roles_royce.roles.send
    :noindex:

Reference
~~~~~~~~~

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
