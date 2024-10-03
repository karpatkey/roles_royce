from .disassembler import Disassembler, validate_percentage
from .disassembling_aura import AuraDisassembler
from .disassembling_balancer import BalancerDisassembler
from .disassembling_dsr import DSRDisassembler
from .disassembling_lido import LidoDisassembler
from .disassembling_spark import SparkDisassembler
from .disassembling_swaps import SwapDisassembler

DISASSEMBLERS = {
    "balancer": BalancerDisassembler,
    "aura": AuraDisassembler,
    "lido": LidoDisassembler,
    "swaps": SwapDisassembler,
    "dsr": DSRDisassembler,
    "spark": SparkDisassembler,
}
