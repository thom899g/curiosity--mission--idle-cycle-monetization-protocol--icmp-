"""
CURIOSITY ICMP - Autonomous Capital Cortex
Core package for idle cycle monetization protocol.
"""
__version__ = "1.0.0-alpha"
__author__ = "Evolution Ecosystem"

from .logger import setup_logger
from .config import SystemConfig
from .exceptions import (
    CuriosityError,
    DataValidationError,
    StrategyExecutionError,
    CapitalAllocationError,
    MEVProtectionError
)

__all__ = [
    'setup_logger',
    'SystemConfig',
    'CuriosityError',
    'DataValidationError',
    'StrategyExecutionError',
    'CapitalAllocationError',
    'MEVProtectionError'
]