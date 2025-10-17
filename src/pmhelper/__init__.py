"""
PMHelper - Project Management Analysis Tool

A comprehensive toolkit for Critical Path Method (CPM) and PERT analysis.
"""

__version__ = "1.0.0"
__author__ = "PMHelper Team"

from .core.cpm_analyzer import CPMAnalyzer
from .core.network_builder import NetworkBuilder

# Try to import PERTAnalyzer, but handle SciPy import issues gracefully
try:
    from .core.pert_analyzer import PERTAnalyzer
    PERT_AVAILABLE = True
except ImportError:
    PERTAnalyzer = None
    PERT_AVAILABLE = False

__all__ = [
    "CPMAnalyzer",
    "NetworkBuilder"
]

if PERT_AVAILABLE:
    __all__.append("PERTAnalyzer")
