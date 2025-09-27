#!/usr/bin/env python3
"""
cx_Freeze setup script for PMHelper
Creates a Windows executable with all dependencies and assets included.
"""

# Add src to sys.path so pmhelper can be found
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from cx_Freeze import setup, Executable
import shutil
from matplotlib import get_data_path
# Build options for cx_Freeze
include_files = [
    ("assets/", "assets/"),  # Include the assets directory
    ("src/pmhelper/", "lib/pmhelper/"),  # Include the source code
    (get_data_path(), "mpl-data"),  # Matplotlib data files
]
# Manually include scipy extra-dll if it exists
scipy_extra_dll = os.path.join(os.path.dirname(__import__('scipy').__file__), 'extra-dll')
if os.path.exists(scipy_extra_dll):
    include_files.append((scipy_extra_dll, "lib/scipy/extra-dll"))

build_exe_options = {
    # Packages to include explicitly
    "packages": [
        "numpy", 
        "pandas", 
        "matplotlib", 
        "networkx", 
        "scipy",
        "plotly",
        "openpyxl",
        "tabulate",
        # PMHelper modules
        "pmhelper",
    ],
    # Additional modules to include
    "includes": [
        "matplotlib.backends.backend_tkagg",
        "matplotlib.backends.backend_agg", 
        "matplotlib.figure",
        "matplotlib.pyplot",
        "matplotlib.patches",
        "matplotlib.colors",
        "numpy.core",
        "pandas.core",
        "tkinter.filedialog",
        "tkinter.messagebox", 
        "tkinter.ttk",
        "networkx.algorithms",
        "scipy.stats",
        # Web/network modules needed by dependencies
        "urllib",
        "urllib.request",
        "urllib.parse",
        "urllib.error",
        "http",
        "http.client",
        "xml",
        "xml.etree",
        "xml.etree.ElementTree",
        "pathlib",
        # Add pydoc as SciPy needs it
        "pydoc"
    ],
    # Files and directories to include with the executable
    "include_files": include_files,
    # Modules to exclude (to reduce size) - removed urllib, http, xml as they're needed
    "excludes": [
        "test", "tests", "pytest", "unittest",
        "email", "doctest",  # Removed pydoc as SciPy needs it
        "distutils", "setuptools", "pkg_resources"
    ],
    # Optimize for size
    "optimize": 2,
    # Zip includes to reduce file count
    "zip_include_packages": ["*"],
    "zip_exclude_packages": []
}
    # Remove None values from include_files (if scipy extra-dll does not exist)

# Base for GUI application (hides console window)
base = None
# TEMPORARILY ENABLE CONSOLE FOR DEBUGGING
# if sys.platform == "win32":
#     base = "Win32GUI"

# Define the executable
executables = [
    Executable(
        "launch_app.py",
        base=base,
        target_name="PMHelper.exe", 
        icon=None,  # Add icon path here if you have one
        copyright="PMHelper Project Management Tool"
    )
]

# Setup configuration
setup(
    name="PMHelper",
    version="1.0.0",
    description="Project Management Helper - CPM and PERT Analysis Tool",
    long_description="A comprehensive desktop application for project management analysis including CPM, PERT, project crashing, and resource scheduling capabilities.",
    author="PMHelper Development Team",
    options={"build_exe": build_exe_options},
    executables=executables,
)