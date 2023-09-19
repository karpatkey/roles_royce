from web3 import Web3
import time
from datetime import datetime
import requests
import json
import sys
import traceback
from web3.exceptions import TransactionNotFound
from decouple import config
import math
from utils import ENV
from roles_royce.toolshed.arbitrage.curve.addresses_and_abis import GnosisChainAddressesAndAbis


URL_SLACK_ALERTS_TEST = config('URL_SLACK_ALERTS_TEST')
URL_TELEGRAM_TESTING_ALERTS = config('URL_TELEGRAM_TESTING_ALERTS')

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# GENERAL PARAMETERS & CONSTANTS
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Roles Module Data
ROLES_CONTRACT_ABI = '[{"type":"constructor","stateMutability":"nonpayable","inputs":[{"type":"address","name":"_owner","internalType":"address"},{"type":"address","name":"_avatar","internalType":"address"},{"type":"address","name":"_target","internalType":"address"}]},{"type":"error","name":"ArraysDifferentLength","inputs":[]},{"type":"error","name":"ModuleTransactionFailed","inputs":[]},{"type":"error","name":"NoMembership","inputs":[]},{"type":"error","name":"SetUpModulesAlreadyCalled","inputs":[]},{"type":"event","name":"AssignRoles","inputs":[{"type":"address","name":"module","internalType":"address","indexed":false},{"type":"uint16[]","name":"roles","internalType":"uint16[]","indexed":false},{"type":"bool[]","name":"memberOf","internalType":"bool[]","indexed":false}],"anonymous":false},{"type":"event","name":"AvatarSet","inputs":[{"type":"address","name":"previousAvatar","internalType":"address","indexed":true},{"type":"address","name":"newAvatar","internalType":"address","indexed":true}],"anonymous":false},{"type":"event","name":"ChangedGuard","inputs":[{"type":"address","name":"guard","internalType":"address","indexed":false}],"anonymous":false},{"type":"event","name":"DisabledModule","inputs":[{"type":"address","name":"module","internalType":"address","indexed":false}],"anonymous":false},{"type":"event","name":"EnabledModule","inputs":[{"type":"address","name":"module","internalType":"address","indexed":false}],"anonymous":false},{"type":"event","name":"OwnershipTransferred","inputs":[{"type":"address","name":"previousOwner","internalType":"address","indexed":true},{"type":"address","name":"newOwner","internalType":"address","indexed":true}],"anonymous":false},{"type":"event","name":"RolesModSetup","inputs":[{"type":"address","name":"initiator","internalType":"address","indexed":true},{"type":"address","name":"owner","internalType":"address","indexed":true},{"type":"address","name":"avatar","internalType":"address","indexed":true},{"type":"address","name":"target","internalType":"address","indexed":false}],"anonymous":false},{"type":"event","name":"SetDefaultRole","inputs":[{"type":"address","name":"module","internalType":"address","indexed":false},{"type":"uint16","name":"defaultRole","internalType":"uint16","indexed":false}],"anonymous":false},{"type":"event","name":"SetMultisendAddress","inputs":[{"type":"address","name":"multisendAddress","internalType":"address","indexed":false}],"anonymous":false},{"type":"event","name":"TargetSet","inputs":[{"type":"address","name":"previousTarget","internalType":"address","indexed":true},{"type":"address","name":"newTarget","internalType":"address","indexed":true}],"anonymous":false},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"allowTarget","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"uint8","name":"options","internalType":"enum ExecutionOptions"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"assignRoles","inputs":[{"type":"address","name":"module","internalType":"address"},{"type":"uint16[]","name":"_roles","internalType":"uint16[]"},{"type":"bool[]","name":"memberOf","internalType":"bool[]"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"avatar","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint16","name":"","internalType":"uint16"}],"name":"defaultRoles","inputs":[{"type":"address","name":"","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"disableModule","inputs":[{"type":"address","name":"prevModule","internalType":"address"},{"type":"address","name":"module","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"enableModule","inputs":[{"type":"address","name":"module","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"success","internalType":"bool"}],"name":"execTransactionFromModule","inputs":[{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"value","internalType":"uint256"},{"type":"bytes","name":"data","internalType":"bytes"},{"type":"uint8","name":"operation","internalType":"enum Enum.Operation"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"","internalType":"bool"},{"type":"bytes","name":"","internalType":"bytes"}],"name":"execTransactionFromModuleReturnData","inputs":[{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"value","internalType":"uint256"},{"type":"bytes","name":"data","internalType":"bytes"},{"type":"uint8","name":"operation","internalType":"enum Enum.Operation"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"success","internalType":"bool"}],"name":"execTransactionWithRole","inputs":[{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"value","internalType":"uint256"},{"type":"bytes","name":"data","internalType":"bytes"},{"type":"uint8","name":"operation","internalType":"enum Enum.Operation"},{"type":"uint16","name":"role","internalType":"uint16"},{"type":"bool","name":"shouldRevert","internalType":"bool"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"bool","name":"success","internalType":"bool"},{"type":"bytes","name":"returnData","internalType":"bytes"}],"name":"execTransactionWithRoleReturnData","inputs":[{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"value","internalType":"uint256"},{"type":"bytes","name":"data","internalType":"bytes"},{"type":"uint8","name":"operation","internalType":"enum Enum.Operation"},{"type":"uint16","name":"role","internalType":"uint16"},{"type":"bool","name":"shouldRevert","internalType":"bool"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"_guard","internalType":"address"}],"name":"getGuard","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"address[]","name":"array","internalType":"address[]"},{"type":"address","name":"next","internalType":"address"}],"name":"getModulesPaginated","inputs":[{"type":"address","name":"start","internalType":"address"},{"type":"uint256","name":"pageSize","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"guard","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"isModuleEnabled","inputs":[{"type":"address","name":"_module","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"multisend","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"owner","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"renounceOwnership","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"revokeTarget","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeAllowFunction","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"uint8","name":"options","internalType":"enum ExecutionOptions"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeFunction","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"bool[]","name":"isParamScoped","internalType":"bool[]"},{"type":"uint8[]","name":"paramType","internalType":"enum ParameterType[]"},{"type":"uint8[]","name":"paramComp","internalType":"enum Comparison[]"},{"type":"bytes[]","name":"compValue","internalType":"bytes[]"},{"type":"uint8","name":"options","internalType":"enum ExecutionOptions"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeFunctionExecutionOptions","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"uint8","name":"options","internalType":"enum ExecutionOptions"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeParameter","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"uint256","name":"paramIndex","internalType":"uint256"},{"type":"uint8","name":"paramType","internalType":"enum ParameterType"},{"type":"uint8","name":"paramComp","internalType":"enum Comparison"},{"type":"bytes","name":"compValue","internalType":"bytes"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeParameterAsOneOf","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"uint256","name":"paramIndex","internalType":"uint256"},{"type":"uint8","name":"paramType","internalType":"enum ParameterType"},{"type":"bytes[]","name":"compValues","internalType":"bytes[]"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeRevokeFunction","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"scopeTarget","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setAvatar","inputs":[{"type":"address","name":"_avatar","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setDefaultRole","inputs":[{"type":"address","name":"module","internalType":"address"},{"type":"uint16","name":"role","internalType":"uint16"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setGuard","inputs":[{"type":"address","name":"_guard","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setMultisend","inputs":[{"type":"address","name":"_multisend","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setTarget","inputs":[{"type":"address","name":"_target","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setUp","inputs":[{"type":"bytes","name":"initParams","internalType":"bytes"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"target","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"transferOwnership","inputs":[{"type":"address","name":"newOwner","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"unscopeParameter","inputs":[{"type":"uint16","name":"role","internalType":"uint16"},{"type":"address","name":"targetAddress","internalType":"address"},{"type":"bytes4","name":"functionSig","internalType":"bytes4"},{"type":"uint8","name":"paramIndex","internalType":"uint8"}]}]'


CHAINLINK_FEED_ADDRESS = '0xab70BCB260073d036d1660201e9d5405F5829b7a'
CHAINLINK_FEED_ABI = '[{"inputs":[{"internalType":"address","name":"_aggregator","type":"address"},{"internalType":"address","name":"_accessController","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"int256","name":"current","type":"int256"},{"indexed":true,"internalType":"uint256","name":"roundId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"updatedAt","type":"uint256"}],"name":"AnswerUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"roundId","type":"uint256"},{"indexed":true,"internalType":"address","name":"startedBy","type":"address"},{"indexed":false,"internalType":"uint256","name":"startedAt","type":"uint256"}],"name":"NewRound","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"OwnershipTransferRequested","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"inputs":[],"name":"acceptOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"accessController","outputs":[{"internalType":"contract AccessControllerInterface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"aggregator","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_aggregator","type":"address"}],"name":"confirmAggregator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_roundId","type":"uint256"}],"name":"getAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_roundId","type":"uint256"}],"name":"getTimestamp","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRound","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestTimestamp","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address payable","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint16","name":"","type":"uint16"}],"name":"phaseAggregators","outputs":[{"internalType":"contract AggregatorV2V3Interface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"phaseId","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_aggregator","type":"address"}],"name":"proposeAggregator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"proposedAggregator","outputs":[{"internalType":"contract AggregatorV2V3Interface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"proposedGetRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"proposedLatestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_accessController","type":"address"}],"name":"setController","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

decimalsEURe = 18
decimalsWXDAI = 18


WXDAI_ADDRESS = '0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d'
WXDAI_ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'

EURe_ADDRESS = '0xcB444e90D8198415266c6a2724b7900fb12FC56E'
EURe_ABI = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes3","name":"ticker","type":"bytes3"},{"indexed":true,"internalType":"address","name":"old","type":"address"},{"indexed":true,"internalType":"address","name":"current","type":"address"}],"name":"Controller","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"}],"name":"OwnershipRenounced","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"data","type":"bytes"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"stateMutability":"nonpayable","type":"fallback"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PREDICATE_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"who","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes32","name":"h","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"burnFrom","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"claimOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getController","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mintTo","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_contractAddr","type":"address"}],"name":"reclaimContract","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"reclaimEther","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract ERC20Basic","name":"_token","type":"address"}],"name":"reclaimToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes32","name":"h","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"recover","outputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"renounceRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"address_","type":"address"}],"name":"setController","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"ticker","outputs":[{"internalType":"bytes3","name":"","type":"bytes3"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_from","type":"address"},{"internalType":"uint256","name":"_value","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"tokenFallback","outputs":[],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"transferAndCall","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"ok","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

# Transaction Fixed Arguments
OPERATION = 0
ROLE = 1
SHOULD_REVERT = False


VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
# ABI Vault - batchSwap
ABI_VAULT = '[{"inputs":[{"internalType":"enum IVault.SwapKind","name":"kind","type":"uint8"},{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"uint256","name":"assetInIndex","type":"uint256"},{"internalType":"uint256","name":"assetOutIndex","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"internalType":"struct IVault.BatchSwapStep[]","name":"swaps","type":"tuple[]"},{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.FundManagement","name":"funds","type":"tuple"},{"internalType":"int256[]","name":"limits","type":"int256[]"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"batchSwap","outputs":[{"internalType":"int256[]","name":"assetDeltas","type":"int256[]"}],"stateMutability":"payable","type":"function"}]'

BALANCER_QUERIES = '0x0F3e0c4218b7b0108a3643cFe9D3ec0d4F57c54e'
# ABI Balancer Queries - queryExit, queryJoin, querySwap, queryBatchSwap
ABI_BALANCER_QUERIES = '[{"inputs":[{"internalType":"contract IVault","name":"_vault","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"enum IVault.SwapKind","name":"kind","type":"uint8"},{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"uint256","name":"assetInIndex","type":"uint256"},{"internalType":"uint256","name":"assetOutIndex","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"internalType":"struct IVault.BatchSwapStep[]","name":"swaps","type":"tuple[]"},{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.FundManagement","name":"funds","type":"tuple"}],"name":"queryBatchSwap","outputs":[{"internalType":"int256[]","name":"assetDeltas","type":"int256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"minAmountsOut","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.ExitPoolRequest","name":"request","type":"tuple"}],"name":"queryExit","outputs":[{"internalType":"uint256","name":"bptIn","type":"uint256"},{"internalType":"uint256[]","name":"amountsOut","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"components":[{"internalType":"contract IAsset[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"maxAmountsIn","type":"uint256[]"},{"internalType":"bytes","name":"userData","type":"bytes"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"}],"internalType":"struct IVault.JoinPoolRequest","name":"request","type":"tuple"}],"name":"queryJoin","outputs":[{"internalType":"uint256","name":"bptOut","type":"uint256"},{"internalType":"uint256[]","name":"amountsIn","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"enum IVault.SwapKind","name":"kind","type":"uint8"},{"internalType":"contract IAsset","name":"assetIn","type":"address"},{"internalType":"contract IAsset","name":"assetOut","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"internalType":"struct IVault.SingleSwap","name":"singleSwap","type":"tuple"},{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.FundManagement","name":"funds","type":"tuple"}],"name":"querySwap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"vault","outputs":[{"internalType":"contract IVault","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'

EURe = "0xcB444e90D8198415266c6a2724b7900fb12FC56E"
bb_ag_USD = "0xFEdb19Ec000d38d92Af4B21436870F115db22725"
bb_ag_WXDAI = "0x41211BBa6d37F5a74b22e667533F080C7C7f3F13"
WXDAI = "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"
EURe_bb_ag_USD_POOL_ID = '0xa611a551b95b205ccd9490657acf7899daee5db700000000000000000000002e'
bb_ag_USD_POOL_ID = '0xfedb19ec000d38d92af4b21436870f115db22725000000000000000000000010'
bb_ag_WXDAI_POOL_ID = '0x41211bba6d37f5a74b22e667533f080c7c7f3f1300000000000000000000000b'
XDAI = 'xdai'

ENV = ENV()

# Transactions Gas Parameters
CHAIN_ID = 100
GAS_LIMIT = 5000000  # Maximum gas amount approved for the transaction
MAX_FEE_PER_GAS = 2000000000  # Maximum total amount per unit of gas we are willing to pay, including base fee and priority fee
MAX_PRIORITY_FEE_PER_GAS = 1000000000  # Maximum fee (tip) per unit of gas paid to validator for transaction prioritization


web3 = Web3(Web3.HTTPProvider(ENV.RPC_ENDPOINT))

roles_contract = web3.eth.contract(address=ENV.ROLES_MOD_ADDRESS, abi=ROLES_CONTRACT_ABI)

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
        url = ENV.SLACK_WEBHOOK_URL
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
        'https://data.fixer.io/api/latest?access_key=%s&base=EUR&symbols=USD' % ENV.FIXER_API_ACCESS_KEY)
    if data_from_api.status_code == 200:
        response = json.loads(data_from_api.content.decode('utf-8'))
        if response['success']:
            return response['rates']['USD']
    contract = web3.eth.contract(address=CHAINLINK_FEED_ADDRESS, abi=CHAINLINK_FEED_ABI)
    chainlink_price = contract.functions.latestAnswer().call() / (10 ** 8)
    return chainlink_price

def get_EURe_to_USD_balancer(amount):

    amount = int(amount * 10 ** decimalsEURe)

    batch_swap_steps = []

    swap_kind = 0 # 0 = "Out Given Exact In" or 1 = "In Given Exact Out"
    user_data = '0x'

    # Step 1: Swap EURe for bb-ag-USD
    index_asset_in = 0
    index_asset_out = 1
    batch_swap_steps.append([EURe_bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, amount, user_data])

    # Step 2: Swap bb-ag-USD for bb-ag-WXDAI
    index_asset_in = 1
    index_asset_out = 2
    batch_swap_steps.append([bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Step 3: Swap bb-ag-WXDAI for WXDAI
    index_asset_in = 2
    index_asset_out = 3
    batch_swap_steps.append([bb_ag_WXDAI_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Assets
    assets = [EURe, bb_ag_USD, bb_ag_WXDAI, WXDAI]

    # FundsManagement
    funds_management = [ENV.AVATAR_SAFE_ADDRESS, False, ENV.AVATAR_SAFE_ADDRESS, False]

    balancer_queries = web3.eth.contract(BALANCER_QUERIES, abi=ABI_BALANCER_QUERIES)

    # try:
    swap = balancer_queries.functions.queryBatchSwap(int(swap_kind), batch_swap_steps, assets, funds_management).call()

    amount_out = abs(swap[3]) / 10 ** decimalsEURe

    return amount_out

def get_USD_to_EURe_balancer(amount):

    amount = int(amount * 10 ** decimalsWXDAI)

    batch_swap_steps = []

    swap_kind = 0 # 0 = "Out Given Exact In" or 1 = "In Given Exact Out"
    user_data = '0x'

    # Step 1: Swap WXDAI for bb-ag-WXDAI  
    index_asset_in = 0
    index_asset_out = 1
    batch_swap_steps.append([bb_ag_WXDAI_POOL_ID, index_asset_in, index_asset_out, amount, user_data])

    # Step 2: Swap bb-ag-WXDAI for bb-ag-USD 
    index_asset_in = 1
    index_asset_out = 2
    batch_swap_steps.append([bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Step 1: Swap bb-ag-USD for EURe
    index_asset_in = 2
    index_asset_out = 3
    batch_swap_steps.append([EURe_bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Assets
    assets = [WXDAI, bb_ag_WXDAI, bb_ag_USD, EURe]

    # FundsManagement
    funds_management = [ENV.AVATAR_SAFE_ADDRESS, False, ENV.AVATAR_SAFE_ADDRESS, False]

    balancer_queries = web3.eth.contract(BALANCER_QUERIES, abi=ABI_BALANCER_QUERIES)

    # try:
    swap = balancer_queries.functions.queryBatchSwap(int(swap_kind), batch_swap_steps, assets, funds_management).call()

    amount_out = abs(swap[0]) / 10 ** decimalsWXDAI

    return amount_out


def get_EURe_to_USD_curve(amount):
    contract = web3.eth.contract(address=GnosisChainAddressesAndAbis.DepositZap.address, abi=GnosisChainAddressesAndAbis.DepositZap.abi)
    amount_int = int(amount * (10 ** decimalsEURe))
    if amount_int == 0:
        raise ValueError('Amount of EURe too small. Amount of EURe: %f.' % (amount * (10 ** decimalsEURe)))
    rate = contract.functions.get_dy_underlying(0, 1, amount_int).call()
    return rate / (10 ** decimalsEURe)


def get_USD_to_EURe_curve(amount):
    contract = web3.eth.contract(address=GnosisChainAddressesAndAbis.DepositZap.address, abi=GnosisChainAddressesAndAbis.DepositZap.abi)
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
        'nonce': web3.eth.get_transaction_count(ENV.BOT_ADDRESS),
    })

    # Creates signed transaction object
    signed_txn = web3.eth.account.sign_transaction(txn, ENV.PRIVATE_KEY)

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
    balance = web3.eth.get_balance(ENV.AVATAR_SAFE_ADDRESS)
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
    balance = contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
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


def swap_EURe_for_WXDAI_balancer(amount):

    EURe_contract = web3.eth.contract(address=EURe_ADDRESS, abi=EURe_ABI)
    balance = EURe_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
    if balance < amount * (10 ** decimalsEURe):
        raise ValueError('Not enough EURe to swap. Current EURe balance: %.3f.' % (balance / (10 ** decimalsEURe)))
    vault = web3.eth.contract(address=VAULT, abi=ABI_VAULT)
    amount_int = int(amount * (10 ** decimalsEURe))
    if amount_int == 0:
        raise ValueError('Amount to swap is too small. Amount of EURe to swap: %f.' % (amount * (10 ** decimalsEURe)))
    
    amount_out = get_EURe_to_USD_balancer(amount)
    min_amount_out = ((1 - float(ENV.MAX_SLIPPAGE)) * amount_out) * -1

    batch_swap_steps = []

    swap_kind = 0 # 0 = "Out Given Exact In" or 1 = "In Given Exact Out"
    user_data = '0x'

    # Step 1: Swap EURe for bb-ag-USD
    index_asset_in = 0
    index_asset_out = 1
    batch_swap_steps.append([EURe_bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, amount_int, user_data])

    # Step 2: Swap bb-ag-USD for bb-ag-WXDAI
    index_asset_in = 1
    index_asset_out = 2
    batch_swap_steps.append([bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Step 3: Swap bb-ag-WXDAI for WXDAI
    index_asset_in = 2
    index_asset_out = 3
    batch_swap_steps.append([bb_ag_WXDAI_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Assets
    assets = [EURe, bb_ag_USD, bb_ag_WXDAI, WXDAI]

    # FundsManagement
    funds_management = [ENV.AVATAR_SAFE_ADDRESS, False, ENV.AVATAR_SAFE_ADDRESS, False]

    # Limits
    limits = [int(amount * (10 ** decimalsEURe)), 0, 0, int(min_amount_out * (10 ** decimalsWXDAI))]

    # Deadline
    deadline = math.floor(datetime.now().timestamp()+1800)

    data = vault.encodeABI(fn_name='batchSwap', args=[swap_kind, batch_swap_steps, assets, funds_management, limits, deadline])
    to_address = VAULT
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


def swap_WXDAI_for_EURe_balancer(amount):

    WXDAI_contract = web3.eth.contract(address=WXDAI_ADDRESS, abi=WXDAI_ABI)
    balance = WXDAI_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
    if balance < amount * (10 ** decimalsWXDAI):
        raise ValueError('Not enough WXDAI to swap. Current WXDAI balance: %.3f.' % (balance / (10 ** decimalsWXDAI)))
    vault = web3.eth.contract(address=VAULT, abi=ABI_VAULT)
    amount_int = int(amount * (10 ** decimalsWXDAI))
    if amount_int == 0:
        raise ValueError('Amount to swap is too small. Amount of WXDAI to swap: %f.' % amount)
    
    amount_out = get_USD_to_EURe_balancer(amount)
    min_amount_out = ((1 - float(ENV.MAX_SLIPPAGE)) * amount_out) * -1

    batch_swap_steps = []

    swap_kind = 0 # 0 = "Out Given Exact In" or 1 = "In Given Exact Out"
    user_data = '0x'

    # Step 1: Swap WXDAI for bb-ag-WXDAI  
    index_asset_in = 0
    index_asset_out = 1
    batch_swap_steps.append([bb_ag_WXDAI_POOL_ID, index_asset_in, index_asset_out, amount_int, user_data])

    # Step 2: Swap bb-ag-WXDAI for bb-ag-USD 
    index_asset_in = 1
    index_asset_out = 2
    batch_swap_steps.append([bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Step 1: Swap bb-ag-USD for EURe
    index_asset_in = 2
    index_asset_out = 3
    batch_swap_steps.append([EURe_bb_ag_USD_POOL_ID, index_asset_in, index_asset_out, 0, user_data])

    # Assets
    assets = [WXDAI, bb_ag_WXDAI, bb_ag_USD, EURe]

    # FundsManagement
    funds_management = [ENV.AVATAR_SAFE_ADDRESS, False, ENV.AVATAR_SAFE_ADDRESS, False]

    # Limits
    limits = [int(amount * (10 ** decimalsWXDAI)), 0, 0, int(min_amount_out * (10 ** decimalsEURe))]

    # Deadline
    deadline = math.floor(datetime.now().timestamp()+1800)

    data = vault.encodeABI(fn_name='batchSwap', args=[swap_kind, batch_swap_steps, assets, funds_management, limits, deadline])
    to_address = VAULT
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


def swap_EURe_for_WXDAI_curve(amount):
    EURe_contract = web3.eth.contract(address=EURe_ADDRESS, abi=EURe_ABI)
    balance = EURe_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
    if balance < amount * (10 ** decimalsEURe):
        raise ValueError('Not enough EURe to swap. Current EURe balance: %.3f.' % (balance / (10 ** decimalsEURe)))
    contract = web3.eth.contract(address=GnosisChainAddressesAndAbis.DepositZap.address, abi=GnosisChainAddressesAndAbis.DepositZap.abi)
    amount_int = int(amount * (10 ** decimalsEURe))
    if amount_int == 0:
        raise ValueError('Amount to swap is too small. Amount of EURe to swap: %f.' % (amount * (10 ** decimalsEURe)))
    amount_out = contract.functions.get_dy_underlying(0, 1, amount_int).call()
    min_amount_out = int((1 - ENV.MAX_SLIPPAGE) * amount_out)
    data = contract.encodeABI(fn_name='exchange_underlying', args=[0, 1, amount_int, min_amount_out])
    to_address = GnosisChainAddressesAndAbis.DepositZap.address
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

def swap_WXDAI_for_EURe_curve(amount):
    WXDAI_contract = web3.eth.contract(address=WXDAI_ADDRESS, abi=WXDAI_ABI)
    balance = WXDAI_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
    if balance < amount * (10 ** decimalsWXDAI):
        raise ValueError('Not enough WXDAI to swap. Current WXDAI balance: %.3f.' % (balance / (10 ** decimalsWXDAI)))
    contract = web3.eth.contract(address=GnosisChainAddressesAndAbis.DepositZap.address, abi=GnosisChainAddressesAndAbis.DepositZap.abi)
    amount_int = int(amount * (10 ** decimalsWXDAI))
    if amount_int == 0:
        raise ValueError('Amount to swap is too small. Amount of WXDAI to swap: %f.' % amount)
    amount_out = contract.functions.get_dy_underlying(1, 0, amount_int).call()
    min_amount_out = int((1 - ENV.MAX_SLIPPAGE) * amount_out)
    data = contract.encodeABI(fn_name='exchange_underlying', args=[1, 0, amount_int, min_amount_out])
    to_address = GnosisChainAddressesAndAbis.DepositZap.address
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

amount_WXDAI = ENV.AMOUNT
amount_EURe = ENV.AMOUNT
lack_of_gas_warning = False
lack_of_WXDAI = False
lack_of_EURe = False
while True:
    txn_executed = False
    EURe_to_USD = get_EURe_to_USD_curve(amount_EURe)
    USD_to_EURe = get_USD_to_EURe_curve(amount_WXDAI)
    EURe_price = get_EUR_oracle_price()
    dict_log = {
        'Date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'EURe to USD oracle': '%.3f EURe ---> %.3f USD' % (amount_EURe, amount_EURe * EURe_price),
        'USD to EURe oracle': '%.3f USD ---> %.3f EURe' % (amount_WXDAI, amount_WXDAI / EURe_price),
        'EURe to WXDAI Curve': '%.3f EURe ---> %.3f WXDAI' % (amount_EURe, EURe_to_USD),
        'WXDAI to EURe Curve': '%.3f WXDAI ---> %.3f EURe' % (amount_WXDAI, USD_to_EURe),
        'EURe to WXDAI drift': '%.5f' % (EURe_to_USD / (EURe_price * amount_EURe) - 1),
        'WXDAI to EURe drift': '%.5f' % (USD_to_EURe / (amount_WXDAI / EURe_price) - 1),
        'Drift threshold': '%.5f' % ENV.DRIFT_THRESHOLD,
    }
    if EURe_to_USD > (1 + ENV.DRIFT_THRESHOLD) * EURe_price * amount_EURe and lack_of_EURe is False and EXEC_TRANSACTIONS is True:
        try:
            msg = swap_EURe_for_WXDAI_curve(amount_EURe)
            dict_log['Execution'] = msg
            txn_executed = True
        except ValueError as e:
            traceback.print_exc()
            requests.post(URL_TELEGRAM_TESTING_ALERTS % (e.args[0]))
            send_slack_message(e.args[0], '', 3)

    elif USD_to_EURe > (1 + ENV.DRIFT_THRESHOLD) * amount_WXDAI / EURe_price and lack_of_WXDAI is False and EXEC_TRANSACTIONS is True:
        try:
            msg = swap_WXDAI_for_EURe_curve(amount_WXDAI)
            dict_log['Execution'] = msg
            txn_executed = True
        except ValueError as e:
            traceback.print_exc()
            requests.post(URL_TELEGRAM_TESTING_ALERTS % (e.args[0]))
            send_slack_message(e.args[0], '', 3)

    if txn_executed:
        time.sleep(5)
        EURe_to_USD = get_EURe_to_USD_curve(amount_EURe)
        USD_to_EURe = get_USD_to_EURe_curve(amount_WXDAI)
        dict_log['New EURe to WXDAI Curve'] = '%.3f EURe ---> %.3f WXDAI' % (amount_EURe, EURe_to_USD)
        dict_log['New WXDAI to EURe Curve'] = '%.3f WXDAI ---> %.3f EURe' % (amount_WXDAI, USD_to_EURe)
        dict_log['New EURe to WXDAI drift'] = '%.5f' % (EURe_to_USD / (EURe_price * amount_EURe) - 1)
        dict_log['New WXDAI to EURe drift'] = '%.5f' % (USD_to_EURe / (amount_WXDAI / EURe_price) - 1)

    requests.post(URL_TELEGRAM_TESTING_ALERTS % dict_log)

    print(dict_log)

    WXDAI_contract = web3.eth.contract(address=WXDAI_ADDRESS, abi=WXDAI_ABI)
    balance = WXDAI_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
    if 10 * amount_WXDAI * (10 ** decimalsWXDAI) < balance and amount_WXDAI < ENV.AMOUNT:
        while 10 * amount_WXDAI * (10 ** decimalsWXDAI) < balance and 10 * amount_WXDAI <= ENV.AMOUNT:
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
    balance = EURe_contract.functions.balanceOf(ENV.AVATAR_SAFE_ADDRESS).call()
    if 10 * amount_EURe * (10 ** decimalsEURe) < balance and amount_EURe < ENV.AMOUNT:
        while 10 * amount_EURe * (10 ** decimalsEURe) < balance and 10 * amount_EURe <= ENV.AMOUNT:
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


    balance = web3.eth.get_balance(ENV.BOT_ADDRESS)
    if balance < 0.001 and lack_of_gas_warning is False:
        message = 'Im running outta XDAI for gas! Only %.3f left.' % (balance / (10 ** 18))
        send_slack_message(message, '', 2)
        requests.post(URL_TELEGRAM_TESTING_ALERTS % message)
        print(message)
        lack_of_gas_warning = True

    time.sleep(60 * ENV.COOLDOWN_MINUTES)