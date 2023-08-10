from web3 import Web3
import time
from datetime import datetime
import requests
import json
import sys
import traceback
from web3.exceptions import TransactionNotFound
from decouple import config

BOT_ADDRESS = config('BOT_ADDRESS')
PRIVATE_KEYS = config('PRIVATE_KEYS')
FIXER_API_ACCESS_KEY = config('FIXER_ACCESS_API_KEY')

URL_SLACK_BOTS_NOTIFICATIONS = config('URL_SLACK_BOTS_NOTIFICATIONS')
URL_SLACK_ALERTS_TEST = config('URL_SLACK_ALERTS_TEST')
URL_TELEGRAM_TESTING_ALERTS = config('URL_TELEGRAM_TESTING_ALERTS')

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# GENERAL PARAMETERS & CONSTANTS
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Roles Module Data
ROLES_CONTRACT_ADDRESS = config('ROLES_CONTRACT_ADDRESS')
ROLES_CONTRACT_ABI = '[{"type":"constructor","stateMutability":"nonpayable","inputs":[{"type":"address","name":"_owner","internalType":"address"},{"type":"address","name":"_avatar","internalType":"address"},{"type":"address","name":"_target","internalType":"address"}]},{"type":"error","name":"ArraysDifferentLength","inputs":[]},{"type":"error","name":"ModuleTransactionFailed","inputs":[]},{"type":"error","name":"NoMembership","inputs":[]},{"type":"error","name":"SetUpModulesAlreadyCalled","inputs":[]},{"type":"event","name":"AssignRoles","inputs":[{"type":"address","name":"module","internalType":"address","indexed":false},{"type":"uint16[]","name":"roles","internalType":"uint16[]","indexed":false},{"type":"bool[]","name":"memberOf","internalType":"bool[]","indexed":false}],"anonymous":false},{"type":"event","name":"AvatarSet","inputs":[{"type":"address","name":"previousAvatar","internalType":"address","indexed":true},{"type":"address","name":"newAvatar","internalType":"address","indexed":true}],"anonymous":false},{"type":"event","name":"ChangedGuard","inputs":[{"type":"address","name":"guard","internalType":"address","indexed":false}],"anonymous":false},{"type":"event","name":"DisabledModule","inputs":[{"type":"address","name":"module","internalType":"address","indexed":false}],"anonymous":false},{"type":"event","name":"EnabledModule","inputs":[{"type":"address","name":"module","internalType":"address","indexed":false}],"anonymous":false},{"type":"event","name":"OwnershipTransferred","inputs":[{"type":"address","name":"previousOwner","internalType":"address","indexed":true},{"type":"address","name":"newOwner","internalType":"address","indexed":true}],"anonymous":false},{"type":"event","name":"RolesModSetup","inputs":[{"type":"address","name":"initiator","internalType":"address","indexed":true},{"type":"address","name":"owner","internalType":"address","indexed":true},{"type":"address","name":"avatar","internalType":"address","indexed":true},{"type":"address","name":"target","internalType":"address","indexed":false}],"anonymous":false},{"type":"event","name":"SetDefaultRole","inputs":[{"type":"address","name":"module","internalType":"address","indexed":false},{"type":"uint16","name":"defaultRole","internalType":"uint16","indexed":false}],"anonymous":false},{"type":"event","name":"SetMultisendAddress","inputs":[{"type":"address","name":"multisendAddress","internalType":"address","indexed":false}],"anonymous":false},{"type":"event","name":"TargetSet","inputs":[{"type":"address","name":"previousTarget","internalType":"address","indexed":true},{"type":"address","name":"newTarget","internalType":"address","indexed":true}],"anonymous":false},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"allowTarget","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"uint8","name":"options","internalType":"enum ExecutionOptions"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"assignRoles","inputs":[{"type":"address","name":"module","internalType":"address"},{"type":"uint16[]","name":"_roles","internalType":"uint16[]"},{"type":"bool[]","name":"memberOf","internalType":"bool[]"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"avatar","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint16","name":"","internalType":"uint16"}],"name":"defaultRoles","inputs":[{"type":"address","name":"","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"disableModule","inputs":[{"type":"address","name":"prevModule","internalType":"address"},{"type":"address","name":"module","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"enableModule","inputs":[{"type":"address","name":"module","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"success","internalType":"bool"}],"name":"execTransactionFromModule","inputs":[{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"value","internalType":"uint256"},{"type":"bytes","name":"data","internalType":"bytes"},{"type":"uint8","name":"operation","internalType":"enum Enum.Operation"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"","internalType":"bool"},{"type":"bytes","name":"","internalType":"bytes"}],"name":"execTransactionFromModuleReturnData","inputs":[{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"value","internalType":"uint256"},{"type":"bytes","name":"data","internalType":"bytes"},{"type":"uint8","name":"operation","internalType":"enum Enum.Operation"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"success","internalType":"bool"}],"name":"execTransactionWithRole","inputs":[{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"value","internalType":"uint256"},{"type":"bytes","name":"data","internalType":"bytes"},{"type":"uint8","name":"operation","internalType":"enum Enum.Operation"},{"type":"uint16","name":"role","internalType":"uint16"},{"type":"bool","name":"shouldRevert","internalType":"bool"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"success","internalType":"bool"},{"type":"bytes","name":"returnData","internalType":"bytes"}],"name":"execTransactionWithRoleReturnData","inputs":[{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"value","internalType":"uint256"},{"type":"bytes","name":"data","internalType":"bytes"},{"type":"uint8","name":"operation","internalType":"enum Enum.Operation"},{"type":"uint16","name":"role","internalType":"uint16"},{"type":"bool","name":"shouldRevert","internalType":"bool"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"_guard","internalType":"address"}],"name":"getGuard","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"address[]","name":"array","internalType":"address[]"},{"type":"address","name":"next","internalType":"address"}],"name":"getModulesPaginated","inputs":[{"type":"address","name":"start","internalType":"address"},{"type":"uint256","name":"pageSize","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"guard","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"isModuleEnabled","inputs":[{"type":"address","name":"_module","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"multisend","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"owner","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"renounceOwnership","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"revokeTarget","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeAllowFunction","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"uint8","name":"options","internalType":"enum ExecutionOptions"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeFunction","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"bool[]","name":"isParamScoped","internalType":"bool[]"},{"type":"uint8[]","name":"paramType","internalType":"enum ParameterType[]"},{"type":"uint8[]","name":"paramComp","internalType":"enum Comparison[]"},{"type":"bytes[]","name":"compValue","internalType":"bytes[]"},{"type":"uint8","name":"options","internalType":"enum ExecutionOptions"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeFunctionExecutionOptions","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"uint8","name":"options","internalType":"enum ExecutionOptions"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeParameter","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"uint256","name":"paramIndex","internalType":"uint256"},{"type":"uint8","name":"paramType","internalType":"enum ParameterType"},{"type":"uint8","name":"paramComp","internalType":"enum Comparison"},{"type":"bytes","name":"compValue","internalType":"bytes"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeParameterAsOneOf","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"uint256","name":"paramIndex","internalType":"uint256"},{"type":"uint8","name":"paramType","internalType":"enum ParameterType"},{"type":"bytes[]","name":"compValues","internalType":"bytes[]"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeRevokeFunction","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeTarget","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setAvatar","inputs":[{"type":"address","name":"_avatar","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setDefaultRole","inputs":[{"type":"address","name":"module","internalType":"address"},{"type":"uint16","name":"role","internalType":"uint16"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setGuard","inputs":[{"type":"address","name":"_guard","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setMultisend","inputs":[{"type":"address","name":"_multisend","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setTarget","inputs":[{"type":"address","name":"_target","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setUp","inputs":[{"type":"bytes","name":"initParams","internalType":"bytes"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"target","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"transferOwnership","inputs":[{"type":"address","name":"newOwner","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"unscopeParameter","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"uint8","name":"paramIndex","internalType":"uint8"}]}]'


# Safe Address
SAFE_ADDRESS = config('SAFE_ADDRESS')

CHAINLINK_FEED_ADDRESS = '0xab70BCB260073d036d1660201e9d5405F5829b7a'
CHAINLINK_FEED_ABI = '[{"inputs":[{"internalType":"address","name":"_aggregator","type":"address"},{"internalType":"address","name":"_accessController","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"int256","name":"current","type":"int256"},{"indexed":true,"internalType":"uint256","name":"roundId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"updatedAt","type":"uint256"}],"name":"AnswerUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"roundId","type":"uint256"},{"indexed":true,"internalType":"address","name":"startedBy","type":"address"},{"indexed":false,"internalType":"uint256","name":"startedAt","type":"uint256"}],"name":"NewRound","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"OwnershipTransferRequested","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"inputs":[],"name":"acceptOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"accessController","outputs":[{"internalType":"contract AccessControllerInterface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"aggregator","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_aggregator","type":"address"}],"name":"confirmAggregator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_roundId","type":"uint256"}],"name":"getAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_roundId","type":"uint256"}],"name":"getTimestamp","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRound","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestTimestamp","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address payable","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint16","name":"","type":"uint16"}],"name":"phaseAggregators","outputs":[{"internalType":"contract AggregatorV2V3Interface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"phaseId","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_aggregator","type":"address"}],"name":"proposeAggregator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"proposedAggregator","outputs":[{"internalType":"contract AggregatorV2V3Interface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"proposedGetRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"proposedLatestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_accessController","type":"address"}],"name":"setController","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

decimalsEURe = 18
decimalsWXDAI = 18

CURVE_POOL_ADDRESS = '0x056C6C5e684CeC248635eD86033378Cc444459B0'
CURVE_POOL_ABI = '[{"name":"TokenExchange","inputs":[{"name":"buyer","type":"address","indexed":true},{"name":"sold_id","type":"uint256","indexed":false},{"name":"tokens_sold","type":"uint256","indexed":false},{"name":"bought_id","type":"uint256","indexed":false},{"name":"tokens_bought","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"AddLiquidity","inputs":[{"name":"provider","type":"address","indexed":true},{"name":"token_amounts","type":"uint256[2]","indexed":false},{"name":"fee","type":"uint256","indexed":false},{"name":"token_supply","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"RemoveLiquidity","inputs":[{"name":"provider","type":"address","indexed":true},{"name":"token_amounts","type":"uint256[2]","indexed":false},{"name":"token_supply","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"RemoveLiquidityOne","inputs":[{"name":"provider","type":"address","indexed":true},{"name":"token_amount","type":"uint256","indexed":false},{"name":"coin_index","type":"uint256","indexed":false},{"name":"coin_amount","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"CommitNewAdmin","inputs":[{"name":"deadline","type":"uint256","indexed":true},{"name":"admin","type":"address","indexed":true}],"anonymous":false,"type":"event"},{"name":"NewAdmin","inputs":[{"name":"admin","type":"address","indexed":true}],"anonymous":false,"type":"event"},{"name":"CommitNewParameters","inputs":[{"name":"deadline","type":"uint256","indexed":true},{"name":"admin_fee","type":"uint256","indexed":false},{"name":"mid_fee","type":"uint256","indexed":false},{"name":"out_fee","type":"uint256","indexed":false},{"name":"fee_gamma","type":"uint256","indexed":false},{"name":"allowed_extra_profit","type":"uint256","indexed":false},{"name":"adjustment_step","type":"uint256","indexed":false},{"name":"ma_half_time","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"NewParameters","inputs":[{"name":"admin_fee","type":"uint256","indexed":false},{"name":"mid_fee","type":"uint256","indexed":false},{"name":"out_fee","type":"uint256","indexed":false},{"name":"fee_gamma","type":"uint256","indexed":false},{"name":"allowed_extra_profit","type":"uint256","indexed":false},{"name":"adjustment_step","type":"uint256","indexed":false},{"name":"ma_half_time","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"RampAgamma","inputs":[{"name":"initial_A","type":"uint256","indexed":false},{"name":"future_A","type":"uint256","indexed":false},{"name":"initial_gamma","type":"uint256","indexed":false},{"name":"future_gamma","type":"uint256","indexed":false},{"name":"initial_time","type":"uint256","indexed":false},{"name":"future_time","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"StopRampA","inputs":[{"name":"current_A","type":"uint256","indexed":false},{"name":"current_gamma","type":"uint256","indexed":false},{"name":"time","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"name":"ClaimAdminFee","inputs":[{"name":"admin","type":"address","indexed":true},{"name":"tokens","type":"uint256","indexed":false}],"anonymous":false,"type":"event"},{"stateMutability":"nonpayable","type":"constructor","inputs":[{"name":"owner","type":"address"},{"name":"admin_fee_receiver","type":"address"},{"name":"A","type":"uint256"},{"name":"gamma","type":"uint256"},{"name":"mid_fee","type":"uint256"},{"name":"out_fee","type":"uint256"},{"name":"allowed_extra_profit","type":"uint256"},{"name":"fee_gamma","type":"uint256"},{"name":"adjustment_step","type":"uint256"},{"name":"admin_fee","type":"uint256"},{"name":"ma_half_time","type":"uint256"},{"name":"initial_price","type":"uint256"},{"name":"_token","type":"address"},{"name":"_coins","type":"address[2]"}],"outputs":[]},{"stateMutability":"view","type":"function","name":"token","inputs":[],"outputs":[{"name":"","type":"address"}]},{"stateMutability":"view","type":"function","name":"coins","inputs":[{"name":"i","type":"uint256"}],"outputs":[{"name":"","type":"address"}]},{"stateMutability":"view","type":"function","name":"A","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"gamma","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"fee","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"get_virtual_price","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"price_oracle","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"exchange","inputs":[{"name":"i","type":"uint256"},{"name":"j","type":"uint256"},{"name":"dx","type":"uint256"},{"name":"min_dy","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"exchange","inputs":[{"name":"i","type":"uint256"},{"name":"j","type":"uint256"},{"name":"dx","type":"uint256"},{"name":"min_dy","type":"uint256"},{"name":"receiver","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"exchange_extended","inputs":[{"name":"i","type":"uint256"},{"name":"j","type":"uint256"},{"name":"dx","type":"uint256"},{"name":"min_dy","type":"uint256"},{"name":"sender","type":"address"},{"name":"receiver","type":"address"},{"name":"cb","type":"bytes"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"get_dy","inputs":[{"name":"i","type":"uint256"},{"name":"j","type":"uint256"},{"name":"dx","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"add_liquidity","inputs":[{"name":"amounts","type":"uint256[2]"},{"name":"min_mint_amount","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"add_liquidity","inputs":[{"name":"amounts","type":"uint256[2]"},{"name":"min_mint_amount","type":"uint256"},{"name":"receiver","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"remove_liquidity","inputs":[{"name":"_amount","type":"uint256"},{"name":"min_amounts","type":"uint256[2]"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"remove_liquidity","inputs":[{"name":"_amount","type":"uint256"},{"name":"min_amounts","type":"uint256[2]"},{"name":"receiver","type":"address"}],"outputs":[]},{"stateMutability":"view","type":"function","name":"calc_token_amount","inputs":[{"name":"amounts","type":"uint256[2]"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"calc_withdraw_one_coin","inputs":[{"name":"token_amount","type":"uint256"},{"name":"i","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"remove_liquidity_one_coin","inputs":[{"name":"token_amount","type":"uint256"},{"name":"i","type":"uint256"},{"name":"min_amount","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"remove_liquidity_one_coin","inputs":[{"name":"token_amount","type":"uint256"},{"name":"i","type":"uint256"},{"name":"min_amount","type":"uint256"},{"name":"receiver","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"claim_admin_fees","inputs":[],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"ramp_A_gamma","inputs":[{"name":"future_A","type":"uint256"},{"name":"future_gamma","type":"uint256"},{"name":"future_time","type":"uint256"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"stop_ramp_A_gamma","inputs":[],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"commit_new_parameters","inputs":[{"name":"_new_mid_fee","type":"uint256"},{"name":"_new_out_fee","type":"uint256"},{"name":"_new_admin_fee","type":"uint256"},{"name":"_new_fee_gamma","type":"uint256"},{"name":"_new_allowed_extra_profit","type":"uint256"},{"name":"_new_adjustment_step","type":"uint256"},{"name":"_new_ma_half_time","type":"uint256"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"apply_new_parameters","inputs":[],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"revert_new_parameters","inputs":[],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"commit_transfer_ownership","inputs":[{"name":"_owner","type":"address"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"apply_transfer_ownership","inputs":[],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"revert_transfer_ownership","inputs":[],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"kill_me","inputs":[],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"unkill_me","inputs":[],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"set_admin_fee_receiver","inputs":[{"name":"_admin_fee_receiver","type":"address"}],"outputs":[]},{"stateMutability":"view","type":"function","name":"lp_price","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"price_scale","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"last_prices","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"last_prices_timestamp","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"initial_A_gamma","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"future_A_gamma","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"initial_A_gamma_time","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"future_A_gamma_time","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"allowed_extra_profit","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"future_allowed_extra_profit","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"fee_gamma","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"future_fee_gamma","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"adjustment_step","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"future_adjustment_step","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"ma_half_time","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"future_ma_half_time","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"mid_fee","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"out_fee","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"admin_fee","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"future_mid_fee","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"future_out_fee","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"future_admin_fee","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"balances","inputs":[{"name":"arg0","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"D","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"owner","inputs":[],"outputs":[{"name":"","type":"address"}]},{"stateMutability":"view","type":"function","name":"future_owner","inputs":[],"outputs":[{"name":"","type":"address"}]},{"stateMutability":"view","type":"function","name":"xcp_profit","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"xcp_profit_a","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"virtual_price","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"is_killed","inputs":[],"outputs":[{"name":"","type":"bool"}]},{"stateMutability":"view","type":"function","name":"kill_deadline","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"transfer_ownership_deadline","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"admin_actions_deadline","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"admin_fee_receiver","inputs":[],"outputs":[{"name":"","type":"address"}]}]'

CURVE_ZAP_ADDRESS = '0xE3FFF29d4DC930EBb787FeCd49Ee5963DADf60b6'
CURVE_ZAP_ABI = '[{"stateMutability":"nonpayable","type":"constructor","inputs":[{"name":"pool","type":"address"},{"name":"base_pool","type":"address"}],"outputs":[]},{"stateMutability":"view","type":"function","name":"coins","inputs":[{"name":"i","type":"uint256"}],"outputs":[{"name":"","type":"address"}]},{"stateMutability":"view","type":"function","name":"underlying_coins","inputs":[{"name":"i","type":"uint256"}],"outputs":[{"name":"","type":"address"}]},{"stateMutability":"view","type":"function","name":"pool","inputs":[],"outputs":[{"name":"","type":"address"}]},{"stateMutability":"view","type":"function","name":"base_pool","inputs":[],"outputs":[{"name":"","type":"address"}]},{"stateMutability":"view","type":"function","name":"token","inputs":[],"outputs":[{"name":"","type":"address"}]},{"stateMutability":"view","type":"function","name":"price_oracle","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"price_scale","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"lp_price","inputs":[],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"add_liquidity","inputs":[{"name":"_amounts","type":"uint256[4]"},{"name":"_min_mint_amount","type":"uint256"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"add_liquidity","inputs":[{"name":"_amounts","type":"uint256[4]"},{"name":"_min_mint_amount","type":"uint256"},{"name":"_receiver","type":"address"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"exchange_underlying","inputs":[{"name":"i","type":"uint256"},{"name":"j","type":"uint256"},{"name":"_dx","type":"uint256"},{"name":"_min_dy","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"exchange_underlying","inputs":[{"name":"i","type":"uint256"},{"name":"j","type":"uint256"},{"name":"_dx","type":"uint256"},{"name":"_min_dy","type":"uint256"},{"name":"_receiver","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"nonpayable","type":"function","name":"remove_liquidity","inputs":[{"name":"_amount","type":"uint256"},{"name":"_min_amounts","type":"uint256[4]"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"remove_liquidity","inputs":[{"name":"_amount","type":"uint256"},{"name":"_min_amounts","type":"uint256[4]"},{"name":"_receiver","type":"address"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"remove_liquidity_one_coin","inputs":[{"name":"_token_amount","type":"uint256"},{"name":"i","type":"uint256"},{"name":"_min_amount","type":"uint256"}],"outputs":[]},{"stateMutability":"nonpayable","type":"function","name":"remove_liquidity_one_coin","inputs":[{"name":"_token_amount","type":"uint256"},{"name":"i","type":"uint256"},{"name":"_min_amount","type":"uint256"},{"name":"_receiver","type":"address"}],"outputs":[]},{"stateMutability":"view","type":"function","name":"get_dy_underlying","inputs":[{"name":"i","type":"uint256"},{"name":"j","type":"uint256"},{"name":"_dx","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"calc_token_amount","inputs":[{"name":"_amounts","type":"uint256[4]"}],"outputs":[{"name":"","type":"uint256"}]},{"stateMutability":"view","type":"function","name":"calc_withdraw_one_coin","inputs":[{"name":"token_amount","type":"uint256"},{"name":"i","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]}]'

WXDAI_ADDRESS = '0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d'
WXDAI_ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'

EURe_ADDRESS = '0xcB444e90D8198415266c6a2724b7900fb12FC56E'
EURe_ABI = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes3","name":"ticker","type":"bytes3"},{"indexed":true,"internalType":"address","name":"old","type":"address"},{"indexed":true,"internalType":"address","name":"current","type":"address"}],"name":"Controller","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"}],"name":"OwnershipRenounced","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"data","type":"bytes"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"stateMutability":"nonpayable","type":"fallback"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PREDICATE_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"who","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes32","name":"h","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"burnFrom","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"claimOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getController","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mintTo","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_contractAddr","type":"address"}],"name":"reclaimContract","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"reclaimEther","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract ERC20Basic","name":"_token","type":"address"}],"name":"reclaimToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes32","name":"h","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"recover","outputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"renounceRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"address_","type":"address"}],"name":"setController","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"ticker","outputs":[{"internalType":"bytes3","name":"","type":"bytes3"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_from","type":"address"},{"internalType":"uint256","name":"_value","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"tokenFallback","outputs":[],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"transferAndCall","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

# Transaction Fixed Arguments
OPERATION = 0
ROLE = 1
SHOULD_REVERT = False


# Transactions Gas Parameters
CHAIN_ID = 100
GAS_LIMIT = 5000000  # Maximum gas amount approved for the transaction
MAX_FEE_PER_GAS = 2000000000  # Maximum total amount per unit of gas we are willing to pay, including base fee and priority fee
MAX_PRIORITY_FEE_PER_GAS = 1000000000  # Maximum fee (tip) per unit of gas paid to validator for transaction prioritization


web3 = Web3(Web3.HTTPProvider('https://rpc.gnosischain.com/'))

roles_contract = web3.eth.contract(address=ROLES_CONTRACT_ADDRESS, abi=ROLES_CONTRACT_ABI)

SLIPPAGE = config('SLIPPAGE')
DRIFT = config('DRIFT')
AMOUNT = config('AMOUNT')
COOLDOWN = config('COOLDOWN') # minutes
SLACK_TEST_MODE = config('SLACK_TEST_MODE')
EXEC_TRANSACTIONS = config('EXEC_TRANSACTIONS')




# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# send_slack_message
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def send_slack_message(txn_message, txn_hash_message, status):
    color = ''
    title = ''
    url = ''

    if status == 1:
        title = ':loudspeaker:' + 'Transaction executed by the EURe arbitrage bot'
        color = '#00FF00'
    elif status == 2:
        title = 'Warning:heavy_exclamation_mark:' + 'I need funds'
        color = '#FF0000'
    elif status == 3:
        title = 'Warning:heavy_exclamation_mark:' + 'Error'
        color = '#FF0000'
    elif status == 0:
        title = 'Warning:heavy_exclamation_mark:' + 'The EURe arbitrage bot failed to execute transaction'
        color = '#FF0000'

    if SLACK_TEST_MODE is False:
        url = URL_SLACK_BOTS_NOTIFICATIONS
    else:
        url = URL_SLACK_ALERTS_TEST

    if status == 2 or status == 3:
        slack_message = '*' + txn_message + '*'
    else:
        slack_message = '*' + txn_message + '*' + '\n' + txn_hash_message

    # if __name__ == '__main__':
    slack_data = {
        # 'username': 'NotificationBot',
        # 'icon_emoji': ':satellite:',
        # 'channel' : '#somerandomcahnnel',
        'attachments': [
            {
                'mrkdwn_in': ['text'],
                'color': color,
                'title': title,
                'text': slack_message
                # 'image_url': image_url,
                # 'fields': [
                #     {
                #         'title': title,
                #         'value': txns_message,
                #         #'short': 'false',
                #     }
                # ]
            }
        ]
    }

    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': 'application/json', 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)


def get_EUR_oracle_price():
    data_from_api = requests.get(
        'https://data.fixer.io/api/latest?access_key=%s&base=EUR&symbols=USD' % FIXER_API_ACCESS_KEY)
    if data_from_api.status_code == 200:
        response = json.loads(data_from_api.content.decode('utf-8'))
        if response['success']:
            return response['rates']['USD']
    contract = web3.eth.contract(address=CHAINLINK_FEED_ADDRESS, abi=CHAINLINK_FEED_ABI)
    chainlink_price = contract.functions.latestAnswer().call() / (10 ** 8)
    return chainlink_price


def get_EURe_to_USD(amount):
    contract = web3.eth.contract(address=CURVE_ZAP_ADDRESS, abi=CURVE_ZAP_ABI)
    amount_int = int(amount * (10 ** decimalsEURe))
    if amount_int == 0:
        raise ValueError('Amount of EURe too small. Amount of EURe: %f.' % (amount * (10 ** decimalsEURe)))
    rate = contract.functions.get_dy_underlying(0, 1, amount_int).call()
    return rate / (10 ** decimalsEURe)


def get_USD_to_EURe(amount):
    contract = web3.eth.contract(address=CURVE_ZAP_ADDRESS, abi=CURVE_ZAP_ABI)
    amount_int = int(amount * (10 ** decimalsWXDAI))
    if amount_int == 0:
        raise ValueError('Amount of WXDAI too small. Amount of WXDAI: %f.' % (amount * (10 ** decimalsWXDAI)))
    rate = contract.functions.get_dy_underlying(1, 0, amount_int).call()
    return rate / (10 ** decimalsWXDAI)


def exec(to_address, data, value):
    txn = roles_contract.functions.execTransactionWithRole(to_address, value, data, OPERATION, ROLE,
                                                           SHOULD_REVERT).build_transaction({
        'chainId': CHAIN_ID,
        'gas': GAS_LIMIT,
        'maxFeePerGas': MAX_FEE_PER_GAS,
        'maxPriorityFeePerGas': MAX_PRIORITY_FEE_PER_GAS,
        'nonce': web3.eth.get_transaction_count(BOT_ADDRESS),
    })

    # Creates signed transaction object
    signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEYS)

    # Executes transaction
    executed_txn = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    txn_exists = False
    attempt = 0#attempt to get receipt
    txn_receipt = None
    while txn_exists is False:
        try:
            txn_receipt = web3.eth.get_transaction_receipt(executed_txn.hex())
            txn_exists = True

        except TransactionNotFound:
            time.sleep(5)
            attempt += 1
        if attempt == 12 * 10:
            txn_hash_message_slack = '*Unable to get Txn receipt:* <https://gnosisscan.io/tx/%s|%s>\n' % (
                executed_txn.hex(), executed_txn.hex())
            txn_hash_message = 'Unable to get Txn receipt: https://gnosisscan.io/tx/%s\n' % (executed_txn.hex())
            return txn_receipt, txn_hash_message_slack, txn_hash_message

    if txn_receipt.status == 1:
        txn_hash_message_slack = '*Txn hash (Success):* <https://gnosisscan.io/tx/%s|%s>\n' % (
            executed_txn.hex(), executed_txn.hex())
        txn_hash_message = 'Txn hash (Success): https://gnosisscan.io/tx/%s\n' % (
            executed_txn.hex())
    else:
        txn_hash_message_slack = '*Txn hash (Fail):* <https://gnosisscan.io/tx/%s|%s>\n' % (
            executed_txn.hex(), executed_txn.hex())
        txn_hash_message = 'Txn hash (Fail): https://gnosisscan.io/tx/%s\n' % (
            executed_txn.hex())
    return txn_receipt, txn_hash_message_slack, txn_hash_message


def wrap_xDAI(amount):
    balance = web3.eth.get_balance(SAFE_ADDRESS)
    amount_int = int(amount * (10 ** decimalsWXDAI))
    if balance < amount_int:
        raise ValueError("Insufficient xDAI balance. Balance: %.3f, Amount to wrap: %.3f" % (
        balance / (10 ** decimalsWXDAI), amount))

    contract = web3.eth.contract(address=WXDAI_ADDRESS, abi=WXDAI_ABI)
    data = contract.encodeABI(fn_name='deposit', args=[])
    to_address = WXDAI_ADDRESS
    txn_receipt, txn_hash_message_slack, txn_hash_message = exec(to_address, data, amount_int)
    if txn_receipt.status == 1:
        send_slack_message('%.2f XDAI was wrapped' % amount, txn_hash_message_slack, txn_receipt.status)
    else:
        send_slack_message('Failed to wrap%.2f XDAI' % amount, txn_hash_message_slack, 0)


def unwrap_xDAI(amount):
    contract = web3.eth.contract(address=WXDAI_ADDRESS, abi=WXDAI_ABI)
    amount_int = int(amount * (10 ** decimalsWXDAI))
    balance = contract.functions.balanceOf(SAFE_ADDRESS).call()
    if balance < amount_int:
        raise ValueError("Insufficient WXDAI balance. WXDAI Balance: %.3f, Amount to unwrap: %.3f" % (
        balance / (10 ** decimalsWXDAI), amount))
    data = contract.encodeABI(fn_name='withdraw', args=[amount_int])
    to_address = WXDAI_ADDRESS
    txn_receipt, txn_hash_message_slack, txn_hash_message = exec(to_address, data, 0)
    if txn_receipt.status == 1:
        send_slack_message('%.2f WXDAI was unwrapped' % amount, txn_hash_message_slack, txn_receipt.status)
    else:
        send_slack_message('Failed to wrap%.2f XDAI' % amount, txn_hash_message_slack, txn_receipt.status)


def swap_EURe_for_WXDAI(amount):
    EURe_contract = web3.eth.contract(address=EURe_ADDRESS, abi=EURe_ABI)
    balance = EURe_contract.functions.balanceOf(SAFE_ADDRESS).call()
    if balance < amount * (10 ** decimalsEURe):
        raise ValueError('Not enough EURe to swap. Current EURe balance: %.3f.' % (balance / (10 ** decimalsEURe)))
    contract = web3.eth.contract(address=CURVE_ZAP_ADDRESS, abi=CURVE_ZAP_ABI)
    amount_int = int(amount * (10 ** decimalsEURe))
    if amount_int == 0:
        raise ValueError('Amount to swap is too small. Amount of EURe to swap: %f.' % (amount * (10 ** decimalsEURe)))
    amount_out = contract.functions.get_dy_underlying(0, 1, amount_int).call()
    min_amount_out = int((1 - SLIPPAGE) * amount_out)
    data = contract.encodeABI(fn_name='exchange_underlying', args=[0, 1, amount_int, min_amount_out])
    to_address = CURVE_ZAP_ADDRESS
    txn_receipt, txn_hash_message_slack, txn_hash_message = exec(to_address, data, 0)
    logs = txn_receipt.logs
    amount_received = 0
    if txn_receipt is not None:
        for element in logs:
            if element['topics'] == [bytes.fromhex('ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
                                     bytes.fromhex('000000000000000000000000e3fff29d4dc930ebb787fecd49ee5963dadf60b6'),
                                     bytes.fromhex('00000000000000000000000051d34416593a8acf4127dc4a40625a8efab9940c')]:
                amount_received = int(element['data'].hex(), base=16) / (10 ** decimalsWXDAI)
        if txn_receipt.status == 1 and amount_received != 0:
            msg = '%.2f EURe was swapped for %.2f WXDAI' % (amount, amount_received)
            status = 1
        else:
            msg = 'Failed to swap %.2f EURe' % amount
            status = 0
        send_slack_message(msg, txn_hash_message_slack, status)
        return msg + '.' + txn_hash_message
    else:
        send_slack_message('', txn_hash_message_slack, 3)
        return txn_hash_message

def swap_WXDAI_for_EURe(amount):
    WXDAI_contract = web3.eth.contract(address=WXDAI_ADDRESS, abi=WXDAI_ABI)
    balance = WXDAI_contract.functions.balanceOf(SAFE_ADDRESS).call()
    if balance < amount * (10 ** decimalsWXDAI):
        raise ValueError('Not enough WXDAI to swap. Current WXDAI balance: %.3f.' % (balance / (10 ** decimalsWXDAI)))
    contract = web3.eth.contract(address=CURVE_ZAP_ADDRESS, abi=CURVE_ZAP_ABI)
    amount_int = int(amount * (10 ** decimalsWXDAI))
    if amount_int == 0:
        raise ValueError('Amount to swap is too small. Amount of WXDAI to swap: %f.' % amount)
    amount_out = contract.functions.get_dy_underlying(1, 0, amount_int).call()
    min_amount_out = int((1 - SLIPPAGE) * amount_out)
    data = contract.encodeABI(fn_name='exchange_underlying', args=[1, 0, amount_int, min_amount_out])
    to_address = CURVE_ZAP_ADDRESS
    txn_receipt, txn_hash_message_slack, txn_hash_message = exec(to_address, data, 0)
    if txn_receipt is not None:
        logs = txn_receipt.logs
        amount_received = 0
        for element in logs:
            if element['topics'] == [bytes.fromhex('ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
                                     bytes.fromhex('000000000000000000000000e3fff29d4dc930ebb787fecd49ee5963dadf60b6'),
                                     bytes.fromhex('00000000000000000000000051d34416593a8acf4127dc4a40625a8efab9940c')]:
                amount_received = int(element['data'].hex(), base=16) / (10 ** decimalsEURe)
        if txn_receipt.status == 1 and amount_received != 0:
            msg = '%.2f WXDAI was swapped for %.2f EURe' % (amount, amount_received)
            status = 1
        else:
            msg = 'Failed to swap %.2f WXDAI' % amount
            status = 0
        send_slack_message(msg, txn_hash_message_slack, status)
        return msg + '.' + txn_hash_message
    else:
        send_slack_message('', txn_hash_message_slack, 3)
        return txn_hash_message


# wrap_xDAI(0.00000001)
# swap_WXDAI_for_EURe(0.00000001)
# swap_EURe_for_WXDAI(0.00000001)
# unwrap_xDAI(0.00000001)

amount_WXDAI = AMOUNT
amount_EURe = AMOUNT
lack_of_gas_warning = False
lack_of_WXDAI = False
lack_of_EURe = False
while True:
    txn_executed = False
    EURe_to_USD = get_EURe_to_USD(amount_EURe)
    USD_to_EURe = get_USD_to_EURe(amount_WXDAI)
    EURe_price = get_EUR_oracle_price()
    dict_log = {
        'Date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'EURe to USD oracle': '%.3f EURe ---> %.3f USD' % (amount_EURe, amount_EURe * EURe_price),
        'USD to EURe oracle': '%.3f USD ---> %.3f EURe' % (amount_WXDAI, amount_WXDAI / EURe_price),
        'EURe to WXDAI Curve': '%.3f EURe ---> %.3f WXDAI' % (amount_EURe, EURe_to_USD),
        'WXDAI to EURe Curve': '%.3f WXDAI ---> %.3f EURe' % (amount_WXDAI, USD_to_EURe),
        'EURe to WXDAI drift': '%.5f' % (EURe_to_USD / (EURe_price * amount_EURe) - 1),
        'WXDAI to EURe drift': '%.5f' % (USD_to_EURe / (amount_WXDAI / EURe_price) - 1),
        'Drift threshold': '%.5f' % DRIFT,
    }
    if EURe_to_USD > (1 + DRIFT) * EURe_price * amount_EURe and lack_of_EURe is False and EXEC_TRANSACTIONS is True:
        try:
            msg = swap_EURe_for_WXDAI(amount_EURe)
            dict_log['Execution'] = msg
            txn_executed = True
        except ValueError as e:
            traceback.print_exc()
            requests.post(URL_TELEGRAM_TESTING_ALERTS % (e.args[0]))
            send_slack_message(e.args[0], '', 3)

    elif USD_to_EURe > (1 + DRIFT) * amount_WXDAI / EURe_price and lack_of_WXDAI is False and EXEC_TRANSACTIONS is True:
        try:
            msg = swap_WXDAI_for_EURe(amount_WXDAI)
            dict_log['Execution'] = msg
            txn_executed = True
        except ValueError as e:
            traceback.print_exc()
            requests.post(URL_TELEGRAM_TESTING_ALERTS % (e.args[0]))
            send_slack_message(e.args[0], '', 3)

    if txn_executed:
        time.sleep(5)
        EURe_to_USD = get_EURe_to_USD(amount_EURe)
        USD_to_EURe = get_USD_to_EURe(amount_WXDAI)
        dict_log['New EURe to WXDAI Curve'] = '%.3f EURe ---> %.3f WXDAI' % (amount_EURe, EURe_to_USD)
        dict_log['New WXDAI to EURe Curve'] = '%.3f WXDAI ---> %.3f EURe' % (amount_WXDAI, USD_to_EURe)
        dict_log['New EURe to WXDAI drift'] = '%.5f' % (EURe_to_USD / (EURe_price * amount_EURe) - 1)
        dict_log['New WXDAI to EURe drift'] = '%.5f' % (USD_to_EURe / (amount_WXDAI / EURe_price) - 1)

    requests.post(URL_TELEGRAM_TESTING_ALERTS % dict_log)

    print(dict_log)

    WXDAI_contract = web3.eth.contract(address=WXDAI_ADDRESS, abi=WXDAI_ABI)
    balance = WXDAI_contract.functions.balanceOf(SAFE_ADDRESS).call()
    if 10 * amount_WXDAI * (10 ** decimalsWXDAI) < balance and amount_WXDAI < AMOUNT:
        while 10 * amount_WXDAI * (10 ** decimalsWXDAI) < balance and 10 * amount_WXDAI <= AMOUNT:
            amount_WXDAI = amount_WXDAI * 10
    elif amount_WXDAI * (10 ** decimalsWXDAI) < balance < 10 * amount_WXDAI * (10 ** decimalsWXDAI):
        pass
    elif balance < amount_WXDAI * (10 ** decimalsWXDAI):
        if lack_of_WXDAI is False:
            message = 'Im running outta WXDAI! Only %.5f left.' % (balance / (10 ** decimalsWXDAI))
            send_slack_message(message, '', 2)
            requests.post(URL_TELEGRAM_TESTING_ALERTS % message)
            print(message)
        while balance < amount_WXDAI * (10 ** decimalsWXDAI) and amount_WXDAI > 1:
            amount_WXDAI = amount_WXDAI / 10
        if amount_WXDAI <= 1:
            lack_of_WXDAI = True


    EURe_contract = web3.eth.contract(address=EURe_ADDRESS, abi=EURe_ABI)
    balance = EURe_contract.functions.balanceOf(SAFE_ADDRESS).call()
    if 10 * amount_EURe * (10 ** decimalsEURe) < balance and amount_EURe < AMOUNT:
        while 10 * amount_EURe * (10 ** decimalsEURe) < balance and 10 * amount_EURe <= AMOUNT:
            amount_EURe = amount_EURe * 10
    elif amount_EURe * (10 ** decimalsEURe) < balance < 10 * amount_EURe * (10 ** decimalsEURe):
        pass
    elif balance < amount_EURe * (10 ** decimalsEURe):
        if lack_of_EURe is False:
            message = 'Im running outta EURe! Only %.5f left.' % (balance / (10 ** decimalsEURe))
            send_slack_message(message, '', 2)
            requests.post(URL_TELEGRAM_TESTING_ALERTS % message)
            print(message)
        while balance < amount_EURe * (10 ** decimalsEURe) and amount_EURe > 1:
            amount_EURe = amount_EURe / 10
        if amount_EURe <= 1:
            lack_of_EURe = True


    balance = web3.eth.get_balance(BOT_ADDRESS)
    if balance < 0.001 and lack_of_gas_warning is False:
        message = 'Im running outta XDAI for gas! Only %.3f left.' % (balance / (10 ** 18))
        send_slack_message(message, '', 2)
        requests.post(URL_TELEGRAM_TESTING_ALERTS % message)
        print(message)
        lack_of_gas_warning = True

    time.sleep(60 * COOLDOWN)