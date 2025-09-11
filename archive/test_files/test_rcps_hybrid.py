#!/usr/bin/env python3
"""
Test script to verify RCPS hybrid layout is working
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import required modules
from src.pmhelper.gui.tabs.rcps_tab import RCPSTab

# Check if the key methods exist
print("=== RCPS Tab Investigation ===")
print(f"✓ RCPSTab class loaded from: {RCPSTab.__module__}")

# Check methods
methods = dir(RCPSTab)
key_methods = [
    'display_hybrid_schedule_view',
    'create_compact_table', 
    'display_compact_schedule_table',
    'display_gantt_chart',
    'run_rcps'
]

for method in key_methods:
    if method in methods:
        print(f"✓ {method} exists")
    else:
        print(f"✗ {method} missing")

# Check the run_rcps method source to see what it's calling
import inspect
try:
    source = inspect.getsource(RCPSTab.run_rcps)
    if 'display_hybrid_schedule_view' in source:
        print("✓ run_rcps calls display_hybrid_schedule_view")
    else:
        print("✗ run_rcps does NOT call display_hybrid_schedule_view")
        
    if 'display_schedule_table' in source:
        print("⚠ run_rcps still calls display_schedule_table (old method)")
    else:
        print("✓ run_rcps does not call old display_schedule_table")
        
except Exception as e:
    print(f"Error inspecting source: {e}")

print("\n=== Investigation Complete ===")
