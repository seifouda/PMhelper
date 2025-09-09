#!/usr/bin/env python3
"""Simple test to verify the matplotlib artist fix"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

import tkinter as tk
from unittest.mock import Mock

# Test the NetworkTab import and initialization
try:
    from pmhelper.gui.tabs.network_tab import NetworkTab
    print("✓ NetworkTab import successful")
except Exception as e:
    print(f"✗ NetworkTab import failed: {e}")
    sys.exit(1)

# Create a mock parent window
root = tk.Tk()
root.withdraw()  # Hide the window

# Create a notebook mock
notebook = Mock()

try:
    # Initialize NetworkTab
    network_tab = NetworkTab(notebook)
    print("✓ NetworkTab initialization successful")
except Exception as e:
    print(f"✗ NetworkTab initialization failed: {e}")
    sys.exit(1)

# Test with mock results data
mock_graph = Mock()
mock_graph.nodes.return_value = ['A', 'B', 'C']
mock_graph.edges.return_value = [('A', 'B'), ('B', 'C')]

mock_results = {
    'graph': mock_graph,
    'critical_activities': ['A', 'B'],
    'project_duration': 10,
    'expected_duration': 10
}

try:
    # Set results data
    network_tab.results_data = mock_results
    network_tab.analysis_mode = 'deterministic'
    
    # Try to update diagram - this is where the artist reuse error would occur
    network_tab.update_diagram()
    print("✓ Network diagram update successful - no artist reuse error!")
    
except Exception as e:
    print(f"✗ Network diagram update failed: {e}")
    if "cannot put single artist in more than one figure" in str(e):
        print("  This is the artist reuse error we were trying to fix!")
    sys.exit(1)

print("\n🎉 All tests passed! The matplotlib artist reuse fix is working correctly.")
root.destroy()
