from .disassembler import Disassembler, validate_percentage
from .disassembling_aura import AuraDisassembler
from .disassembling_balancer import BalancerDisassembler
from .disassembling_lido import LidoDisassembler
from .disassembling_swaps import SwapDisassembler
from .disassembling_dsr import DSRDisassembler
from .disassembling_spark import SparkDisassembler

DISASSEMBLERS = {
    "balancer": BalancerDisassembler,
    "aura": AuraDisassembler,
    "lido": LidoDisassembler,
    "swaps": SwapDisassembler,
    "dsr": DSRDisassembler,
    "spark": SparkDisassembler,
}
