API
===

Roles functions
---------------

.. module:: transaction_builder.roles


.. autofunction:: transaction_builder.roles.build

.. autofunction:: transaction_builder.roles.check

.. autofunction:: transaction_builder.roles.send


Transactable elements
---------------------

.. autoclass:: Transactable
   :members:
   :inherited-members:

.. autoclass:: transaction_builder.protocols.base.ContractMethod
   :members:
   :inherited-members:

Roles Modifier
--------------

.. autointenum:: transaction_builder.roles_modifier.Operation
    :members:

.. autoexception:: transaction_builder.roles_modifier.TransactionWouldBeReverted
    :members:

.. autoclass:: transaction_builder.roles_modifier.RolesMod
    :members:

Simulation
----------

Transactions can be simulated using Tenderly.

.. autofunction:: transaction_builder.utils.simulate_tx

.. autofunction:: transaction_builder.utils.tenderly_simulate

.. autofunction:: transaction_builder.utils.tenderly_share_simulation
