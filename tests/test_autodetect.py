#!/usr/bin/env python3
"""
Simple test to check what happens during mode detection
"""

import sys
from pathlib import Path

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    # Test the auto-detection logic with different headers
    from pmhelper.gui.tabs.input_tab import InputTab
    import tkinter as tk
    from pmhelper.gui.main_window import MainWindow
    
    print("🔍 Testing auto-detection logic directly:")
    
    # Create a minimal input tab for testing
    root = tk.Tk()
    app = MainWindow(root)
    input_tab = app.input_tab
    
    # Test different header scenarios
    test_cases = [
        # Case 1: Clear CPM headers
        ['id', 'activity', 'duration', 'predecessors'],
        # Case 2: CPM headers with extra columns
        ['id', 'activity', 'duration', 'predecessors', 'min_duration', 'crash_cost'],
        # Case 3: PERT headers
        ['id', 'activity', 'optimistic', 'most_likely', 'pessimistic', 'predecessors'],
        # Case 4: Mixed/ambiguous headers  
        ['activity', 'description', 'start_date', 'end_date'],
        # Case 5: Headers with different casing
        ['ID', 'ACTIVITY', 'DURATION', 'PREDECESSORS'],
    ]
    
    for i, headers in enumerate(test_cases, 1):
        detected = input_tab.auto_detect_mode(headers)
        print(f"   Case {i}: {headers}")
        print(f"            → Detected: {detected}")
    
    root.destroy()
    print("✅ Auto-detection test completed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
