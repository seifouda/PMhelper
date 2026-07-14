"""
Command-line interface modules for PMHelper.

Contains CLI tools for CPM, PERT analysis, and Project Selection.
"""

try:
    from pmhelper.cli.selection_cli import selection  # noqa: F401
    __all__ = ['selection']
except ImportError:
    __all__ = []
