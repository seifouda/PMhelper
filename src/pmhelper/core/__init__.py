"""
Core analysis modules for PMHelper.

Contains the main analysis engines for CPM and PERT calculations.
"""

from .cpm_analyzer import CPMAnalyzer
from .network_builder import NetworkBuilder

# Try to import PERTAnalyzer, but handle SciPy import issues gracefully
try:
    from .pert_analyzer import PERTAnalyzer
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
