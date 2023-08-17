Welcome to Roles Royce's documentation!
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

The ``roles_royce`` package is a DeFi library that allows you to easily execute
transactions using Zodiac Roles Modifier contracts `ZodiacRoles`_
for mulitple DeFi protocols.

This project is currently being actively developed and it is in alpha state
so expect backwards incompatible changes.

.. _ZodiacRoles: https://github.com/gnosis/zodiac-modifier-roles-v1

Usage
-----

The main functions that are provided are:

- :meth:`~roles_royce.check` to statically check if a transaction will go through or will fail.
- :meth:`~roles_royce.send` to actually send the transaction to the blockchain.
- :meth:`~roles_royce.build` to create a transaction to later be sent to the blockchain or other uses such as studying it or composing it with other contracts.



Example
-------


Deposit GNO into the Spark protocol:

.. code-block:: python

    from roles_royce.protocols.eth import spark
    from roles_royce import send
    from web3 import Web3, HTTPProvider

    w3 = Web3(HTTPProvider("https://..."))
    safe_address = "0xabc.."
    assert get_balance(w3, ETHAddr.GNO, safe_address) == 123_000_000

    # Create the transaction data for the aproval and deposit of GNO
    txs = [
        spark.ApproveToken(token=ETHAddr.GNO, amount=123_000_000),
        spark.DepositToken(token=ETHAddr.GNO, avatar=safe.address,
                           amount=123_000_000),
        spark.ApproveToken(token=ETHAddr.GNO, amount=0),
    ]

    # Through the Roles modifier contract deposit GNO to receive spGNO
    # It will be executed as only one transaction using a Multisend contract
    send(txs,
         account="0x...",
         roles_mod_address="0x...",
         web3=w3)

    assert get_balance(w3, ETHAddr.GNO, safe_address) == 0
    assert get_balance(w3, ETHAddr.spGNO, safe_address) == 123_000_000


Generic calls
-------------

Beside the provided protocol methods, generic calls can be performed.

.. toctree::
   :maxdepth: 1

   generic_calls



Protocols supported
-------------------

.. toctree::
   :maxdepth: 2

   protocols/index


Api
---

Main methods
~~~~~~~~~~~~

.. autofunction:: roles_royce.build
    :noindex:

.. autofunction:: roles_royce.check
    :noindex:

.. autofunction:: roles_royce.send
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
