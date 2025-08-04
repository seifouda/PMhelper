#!/usr/bin/env python3
"""
Test automatic mode detection functionality
"""

import sys
from pathlib import Path
import csv

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from pmhelper.gui.tabs.input_tab import InputTab

class MockMainWindow:
    def __init__(self):
        self.analysis_mode = None
    
    def set_analysis_mode(self, mode):
        self.analysis_mode = mode
        print(f"Mode set to: {mode}")
    
    def set_status(self, message):
        print(f"Status: {message}")

class MockNotebook:
    pass

def test_auto_detection():
    # Create mock objects
    notebook = MockNotebook()
    main_window = MockMainWindow()
    
    # Create InputTab instance
    input_tab = InputTab.__new__(InputTab)  # Create without calling __init__
    input_tab.notebook = notebook
    input_tab.main_window = main_window
    input_tab.current_mode = None
    
    # Test CPM headers
    cpm_headers = ['id', 'activity', 'duration', 'predecessors', 'min_duration', 'crash_cost']
    detected_mode = input_tab.auto_detect_mode(cpm_headers)
    print(f"CPM headers {cpm_headers} -> Detected mode: {detected_mode}")
    
    # Test PERT headers
    pert_headers = ['id', 'activity', 'optimistic', 'most_likely', 'pessimistic', 'predecessors']
    detected_mode = input_tab.auto_detect_mode(pert_headers)
    print(f"PERT headers {pert_headers} -> Detected mode: {detected_mode}")
    
    # Test mixed headers (should prefer PERT)
    mixed_headers = ['id', 'activity', 'duration', 'optimistic', 'most_likely', 'pessimistic']
    detected_mode = input_tab.auto_detect_mode(mixed_headers)
    print(f"Mixed headers {mixed_headers} -> Detected mode: {detected_mode}")
    
    # Test actual CSV files
    print("\nTesting actual CSV files:")
    
    # Test CPM CSV
    with open('test_cpm_auto_detect.csv', 'r') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        detected_mode = input_tab.auto_detect_mode(headers)
        print(f"test_cpm_auto_detect.csv headers {headers} -> Detected mode: {detected_mode}")
    
    # Test PERT CSV
    with open('test_pert_auto_detect.csv', 'r') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        detected_mode = input_tab.auto_detect_mode(headers)
        print(f"test_pert_auto_detect.csv headers {headers} -> Detected mode: {detected_mode}")

if __name__ == "__main__":
    test_auto_detection()
