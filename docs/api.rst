API
===

Roles functions
---------------

.. module:: roles_royce.roles


.. autofunction:: roles_royce.roles.build

.. autofunction:: roles_royce.roles.check

.. autofunction:: roles_royce.roles.send


Transactable elements
---------------------

.. autoclass:: Transactable
   :members:
   :inherited-members:

.. autoclass:: roles_royce.protocols.base.ContractMethod
   :members:
   :inherited-members:

Roles Modifier
--------------

.. autointenum:: roles_royce.roles_modifier.Operation
    :members:

.. autoexception:: roles_royce.roles_modifier.TransactionWouldBeReverted
    :members:

.. autoclass:: roles_royce.roles_modifier.RolesMod
    :members:

Simulation
----------

Transactions can be simulated using Tenderly.

.. autofunction:: roles_royce.utils.simulate_tx

.. autofunction:: roles_royce.utils.tenderly_simulate

.. autofunction:: roles_royce.utils.tenderly_share_simulation
