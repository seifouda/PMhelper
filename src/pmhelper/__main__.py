#!/usr/bin/env python3
"""
PMHelper package main entry point.

Allows the package to be executed with: python -m pmhelper
"""

import sys
from pmhelper.cli.cpm_cli import main

if __name__ == "__main__":
    sys.exit(main())
