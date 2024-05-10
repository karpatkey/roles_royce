API
===

Roles functions
---------------

.. module:: artemis.roles


.. autofunction:: artemis.roles.build

.. autofunction:: artemis.roles.check

.. autofunction:: artemis.roles.send


Transactable elements
---------------------

.. autoclass:: Transactable
   :members:
   :inherited-members:

.. autoclass:: artemis.protocols.base.ContractMethod
   :members:
   :inherited-members:

Roles Modifier
--------------

.. autointenum:: artemis.roles_modifier.Operation
    :members:

.. autoexception:: artemis.roles_modifier.TransactionWouldBeReverted
    :members:

.. autoclass:: artemis.roles_modifier.RolesMod
    :members:

Simulation
----------

Transactions can be simulated using Tenderly.

.. autofunction:: artemis.utils.simulate_tx

.. autofunction:: artemis.utils.tenderly_simulate

.. autofunction:: artemis.utils.tenderly_share_simulation
