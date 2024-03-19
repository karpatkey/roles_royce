from decimal import Decimal

from defi_protocols.Balancer import ABI_VEBAL_FEE_DISTRIBUTOR, VEBAL_FEE_DISTRIBUTORS, VEBAL_REWARD_TOKENS
from defi_protocols.constants import ETHEREUM
from defi_protocols.functions import get_decimals, last_block
from web3 import HTTPProvider, Web3

from tests.utils import ETH_FORK_NODE_URL, LOCAL_NODE_PORT, fork_reset_state, fork_unlock_account


def test_balancer_vebal(wallet, block, decimals=True):
    if isinstance(block, str):
        if block == "latest":
            block = last_block(ETHEREUM)
        else:
            raise ValueError("Incorrect block.")
    else:
        block = block - 1

    w3 = Web3(HTTPProvider(f"http://localhost:{LOCAL_NODE_PORT}"))
    fork_reset_state(w3, url=ETH_FORK_NODE_URL, block=block)
    fork_unlock_account(w3, wallet)

    vebal_rewards_dict = {}

    fee_distributor_blocks = list(VEBAL_FEE_DISTRIBUTORS.keys())[::-1]
    # Continues only if the block is greater than the first fee distributor block
    if block >= int(fee_distributor_blocks[-1]):
        vebal_reward_tokens_blocks = list(VEBAL_REWARD_TOKENS.keys())

        i = 0
        # Obtains the block to determine the reward tokens
        while i < len(vebal_reward_tokens_blocks):
            if block >= int(vebal_reward_tokens_blocks[i]):
                vebal_reward_tokens_block = vebal_reward_tokens_blocks[i]
            i += 1

        for fee_distributor_block in fee_distributor_blocks:
            if block >= int(fee_distributor_block):
                fee_distributor_contract = w3.eth.contract(
                    address=VEBAL_FEE_DISTRIBUTORS[fee_distributor_block], abi=ABI_VEBAL_FEE_DISTRIBUTOR
                )
                tx = fee_distributor_contract.functions.claimTokens(
                    wallet, VEBAL_REWARD_TOKENS[vebal_reward_tokens_block]
                ).transact({"from": wallet})
                while True:
                    try:
                        txn = w3.eth.get_transaction_receipt(tx.hex())
                        break
                    except:
                        pass

                while txn["logs"] != []:
                    for log in txn["logs"]:
                        if (
                            log["topics"][0].hex()
                            == "0xff097c7d8b1957a4ff09ef1361b5fb54dcede3941ba836d0beb9d10bec725de6"
                        ):
                            claim_token = "0x" + log["data"].hex()[90:130]
                            token_amount = int(log["data"].hex()[130:194], 16)

                            if decimals:
                                token_decimals = get_decimals(claim_token, ETHEREUM)
                            else:
                                token_decimals = 0

                            if claim_token not in vebal_rewards_dict:
                                vebal_rewards_dict[claim_token] = token_amount / Decimal(10**token_decimals)
                            else:
                                vebal_rewards_dict[claim_token] += token_amount / Decimal(10**token_decimals)

                    tx = fee_distributor_contract.functions.claimTokens(
                        wallet, VEBAL_REWARD_TOKENS[vebal_reward_tokens_block]
                    ).transact({"from": wallet})
                    while True:
                        try:
                            txn = w3.eth.get_transaction_receipt(tx.hex())
                            break
                        except:
                            pass

    return vebal_rewards_dict


ABI_GAUGE: str = '[{"name":"Deposit","inputs":[{"name":"provider","type":"address","indexed":true},{"name":"value","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"Withdraw","inputs":[{"name":"provider","type":"address","indexed":true},{"name":"value","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"UpdateLiquidityLimit","inputs":[{"name":"user","type":"address","indexed":false},{"name":"original_balance","type":"uint256","indexed":false},{"name":"original_supply","type":"uint256","indexed":false},{"name":"working_balance","type":"uint256","indexed":false},{"name":"working_supply","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"CommitOwnership","inputs":[{"name":"admin","type":"address","indexed":false}],"anonymous":false,"type":"event"},{"name":"ApplyOwnership","inputs":[{"name":"admin","type":"address","indexed":false}],"anonymous":false,"type":"event"},{"name":"Transfer","inputs":[{"name":"_from","type":"address","indexed":true},{"name":"_to","type":"address","indexed":true},{"name":"_value","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"Approval","inputs":[{"name":"_owner","type":"address","indexed":true},{"name":"_spender","type":"address","indexed":true},{"name":"_value","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"stateMutability":"nonpayable","type":"constructor","inputs":[{"name":"_lp_token","type":"address"},{"name":"_distributor_proxy","type":"address"},{"name":"_admin","type":"address"}],"outputs":[]},{"stateMutability":"view","type":"function","name":"decimals","inputs":[],"outputs":[{"name":"","type":"uint256"}],"gas":288},{"stateMutability":"view","type":"function","name":"integrate_checkpoint","inputs":[],"outputs":[{"name":"","type":"uint256"}],"gas":4560},{"stateMutability":"nonpayable","type":"function","name":"user_checkpoint","inputs":[{"name":"addr","type":"address"}],"outputs":[{"name":"","type":"bool"}],"gas":3133382},{"stateMutability":"nonpayable","type":"function","name":"claimable_tokens","inputs":[{"name":"addr","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":3046449},{"stateMutability":"view","type":"function","name":"reward_contract","inputs":[],"outputs":[{"name":"","type":"address"}],"gas":2718},{"stateMutability":"view","type":"function","name":"last_claim","inputs":[],"outputs":[{"name":"","type":"uint256"}],"gas":2544},{"stateMutability":"view","type":"function","name":"claimed_reward","inputs":[{"name":"_addr","type":"address"},{"name":"_token","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":3066},{"stateMutability":"view","type":"function","name":"claimable_reward","inputs":[{"name":"_addr","type":"address"},{"name":"_token","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":3034},{"stateMutability":"nonpayable","type":"function","name":"claimable_reward_write","inputs":[{"name":"_addr","type":"address"},{"name":"_token","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":1209922},{"stateMutability":"nonpayable","type":"function","name":"set_rewards_receiver","inputs":[{"name":"_receiver","type":"address"}],"outputs":[],"gas":35733},{"stateMutability":"nonpayable","type":"function","name":"claim_rewards","inputs":[],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"claim_rewards","inputs":[{"name":"_addr","type":"address"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"claim_rewards","inputs":[{"name":"_addr","type":"address"},{"name":"_receiver","type":"address"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"kick","inputs":[{"name":"addr","type":"address"}],"outputs":[],"gas":3147973},{"stateMutability":"nonpayable","type":"function","name":"deposit","inputs":[{"name":"_value","type":"uint256"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"deposit","inputs":[{"name":"_value","type":"uint256"},{"name":"_addr","type":"address"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"deposit","inputs":[{"name":"_value","type":"uint256"},{"name":"_addr","type":"address"},{"name":"_claim_rewards","type":"bool"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"withdraw","inputs":[{"name":"_value","type":"uint256"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"withdraw","inputs":[{"name":"_value","type":"uint256"},{"name":"_claim_rewards","type":"bool"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"transfer","inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"outputs":[{"name":"","type":"bool"}],"gas":17167132},{"stateMutability":"nonpayable","type":"function","name":"transferFrom","inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"outputs":[{"name":"","type":"bool"}],"gas":17205082},{"stateMutability":"nonpayable","type":"function","name":"approve","inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"outputs":[{"name":"","type":"bool"}],"gas":38211},{"stateMutability":"nonpayable","type":"function","name":"increaseAllowance","inputs":[{"name":"_spender","type":"address"},{"name":"_added_value","type":"uint256"}],"outputs":[{"name":"","type":"bool"}],"gas":40755},{"stateMutability":"nonpayable","type":"function","name":"decreaseAllowance","inputs":[{"name":"_spender","type":"address"},{"name":"_subtracted_value","type":"uint256"}],"outputs":[{"name":"","type":"bool"}],"gas":40779},{"stateMutability":"nonpayable","type":"function","name":"set_rewards","inputs":[{"name":"_reward_contract","type":"address"},{"name":"_sigs","type":"bytes32"},{"name":"_reward_tokens","type":"address[8]"}],"outputs":[],"gas":2740447},{"stateMutability":"nonpayable","type":"function","name":"set_killed","inputs":[{"name":"_is_killed","type":"bool"}],"outputs":[],"gas":38145},{"stateMutability":"nonpayable","type":"function","name":"commit_transfer_ownership","inputs":[{"name":"addr","type":"address"}],"outputs":[],"gas":39525},{"stateMutability":"nonpayable","type":"function","name":"accept_transfer_ownership","inputs":[],"outputs":[],"gas":39470},{"stateMutability":"view","type":"function","name":"distributor_proxy","inputs":[],"outputs":[{"name":"","type":"address"}],"gas":3078},{"stateMutability":"view","type":"function","name":"distributor","inputs":[],"outputs":[{"name":"","type":"address"}],"gas":3108},{"stateMutability":"view","type":"function","name":"lp_token","inputs":[],"outputs":[{"name":"","type":"address"}],"gas":3138},{"stateMutability":"view","type":"function","name":"controller","inputs":[],"outputs":[{"name":"","type":"address"}],"gas":3168},{"stateMutability":"view","type":"function","name":"voting_escrow","inputs":[],"outputs":[{"name":"","type":"address"}],"gas":3198},{"stateMutability":"view","type":"function","name":"future_epoch_time","inputs":[],"outputs":[{"name":"","type":"uint256"}],"gas":3228},{"stateMutability":"view","type":"function","name":"balanceOf","inputs":[{"name":"arg0","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":3473},{"stateMutability":"view","type":"function","name":"totalSupply","inputs":[],"outputs":[{"name":"","type":"uint256"}],"gas":3288},{"stateMutability":"view","type":"function","name":"allowance","inputs":[{"name":"arg0","type":"address"},{"name":"arg1","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":3748},{"stateMutability":"view","type":"function","name":"name","inputs":[],"outputs":[{"name":"","type":"string"}],"gas":13578},{"stateMutability":"view","type":"function","name":"symbol","inputs":[],"outputs":[{"name":"","type":"string"}],"gas":11331},{"stateMutability":"view","type":"function","name":"working_balances","inputs":[{"name":"arg0","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":3623},{"stateMutability":"view","type":"function","name":"working_supply","inputs":[],"outputs":[{"name":"","type":"uint256"}],"gas":3438},{"stateMutability":"view","type":"function","name":"period","inputs":[],"outputs":[{"name":"","type":"int128"}],"gas":3468},{"stateMutability":"view","type":"function","name":"period_timestamp","inputs":[{"name":"arg0","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}],"gas":3543},{"stateMutability":"view","type":"function","name":"integrate_inv_supply","inputs":[{"name":"arg0","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}],"gas":3573},{"stateMutability":"view","type":"function","name":"integrate_inv_supply_of","inputs":[{"name":"arg0","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":3773},{"stateMutability":"view","type":"function","name":"integrate_checkpoint_of","inputs":[{"name":"arg0","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":3803},{"stateMutability":"view","type":"function","name":"integrate_fraction","inputs":[{"name":"arg0","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":3833},{"stateMutability":"view","type":"function","name":"inflation_rate","inputs":[],"outputs":[{"name":"","type":"uint256"}],"gas":3648},{"stateMutability":"view","type":"function","name":"reward_tokens","inputs":[{"name":"arg0","type":"uint256"}],"outputs":[{"name":"","type":"address"}],"gas":3723},{"stateMutability":"view","type":"function","name":"rewards_receiver","inputs":[{"name":"arg0","type":"address"}],"outputs":[{"name":"","type":"address"}],"gas":3923},{"stateMutability":"view","type":"function","name":"reward_integral","inputs":[{"name":"arg0","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":3953},{"stateMutability":"view","type":"function","name":"reward_integral_for","inputs":[{"name":"arg0","type":"address"},{"name":"arg1","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":4198},{"stateMutability":"view","type":"function","name":"admin","inputs":[],"outputs":[{"name":"","type":"address"}],"gas":3798},{"stateMutability":"view","type":"function","name":"future_admin","inputs":[],"outputs":[{"name":"","type":"address"}],"gas":3828},{"stateMutability":"view","type":"function","name":"is_killed","inputs":[],"outputs":[{"name":"","type":"bool"}],"gas":3858}]'


def test(wallet, block, value, decimals=True):
    if isinstance(block, str):
        if block == "latest":
            block = last_block(ETHEREUM)
        else:
            raise ValueError("Incorrect block.")
    else:
        block = block - 1

    w3 = Web3(HTTPProvider(f"http://localhost:{LOCAL_NODE_PORT}"))
    fork_reset_state(w3, url=ETH_FORK_NODE_URL, block=block)
    fork_unlock_account(w3, wallet)

    gauge_contract = w3.eth.contract(address="0x675eC042325535F6e176638Dd2d4994F645502B9", abi=ABI_GAUGE)

    tx = gauge_contract.functions.withdraw(value).transact({"from": wallet})
    while True:
        try:
            txn = w3.eth.get_transaction_receipt(tx.hex())
            break
        except:
            pass


test("0x542256Ef33279C5545AA71f4b3B6298990f30Ffc", "latest", 6024149996523491930)
# print(test_balancer_vebal('0x849D52316331967b6fF1198e5E32A0eB168D039d', 17420616))
