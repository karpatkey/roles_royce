Generic calls
=============

Beside the provided protocol methods, generic calls can be performed.

Example
-------

.. code-block:: python

    from transaction_builder import roles, GenericMethodTransaction, Operation, Chain

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
    status = roles.check(txs=[approve, add_liquidity],
						 role=2,
						 account=ACCOUNT,
						 roles_mod_address=ROLES_MOD_ADDRESS,
						 web3=w3,
						 blockchain=Chain.GC)

    ...

