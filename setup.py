"""
PMHelper - A comprehensive Project Management Analysis Tool

This is the setuptools-based setup.py for PyPI distribution.
For the cx_Freeze Windows executable build, see build_setup.py.
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements (pyproject.toml is the source of truth for `pip install`; this
# is only used if setup.py is invoked directly)
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() 
        for line in fh.read().splitlines() 
        if line.strip() and not line.startswith("#") and not line.startswith("tkinter")
    ]

# Read version from __init__.py
version = {}
version_file = os.path.join("src", "pmhelper", "__init__.py")
with open(version_file, "r", encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("__version__"):
            version["__version__"] = line.split("=")[1].strip().strip('"')

setup(
    name="pmhelper",
    version=version["__version__"],
    author="PMHelper Team",
    author_email="support@pmhelper.dev",
    description="A comprehensive toolkit for Critical Path Method (CPM) and PERT analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seifouda/PMhelper",
    project_urls={
        "Bug Reports": "https://github.com/seifouda/PMhelper/issues",
        "Source": "https://github.com/seifouda/PMhelper",
        "Documentation": "https://github.com/seifouda/PMhelper/blob/main/README.md",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "pmhelper": [
            "assets/*.csv",
            "assets/*.xlsx",
            "config/*.ini",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Other Audience",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
        "full": [
            "plotly>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pmhelper=pmhelper.cli.cpm_cli:main",
            "pmhelper-cpm=pmhelper.cli.cpm_cli:main",
            "pmhelper-pert=pmhelper.cli.pert_cli:main",
        ],
        "gui_scripts": [
            "pmhelper-gui=pmhelper.gui.main_window:main",
        ],
    },
    keywords="project management, cpm, pert, critical path, scheduling, gantt, network analysis",
    license="MIT",
    zip_safe=False,  # Due to data files
)