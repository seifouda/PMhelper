#!/usr/bin/env python3
"""
Test script to verify automatic mode detection in CPM application
"""

import tkinter as tk
from tkinter import messagebox
import csv
import os

# Import the main application
import sys
sys.path.append('code')
from cpm_app import CPMDesktopApp

# Create a test CSV file with deterministic data
test_csv_content = """activity,description,duration,predecessors,min_duration,crash_cost,resource_demand,normal_cost
A,Design Phase,5,,1,300,2,100
B,Requirements Analysis,3,,2,500,1,150
C,Architecture Design,7,"A, B",5,600,3,200
D,Database Design,5,C,4,400,1,120
E,Frontend Development,6,C,3,300,4,180
"""

test_csv_path = "test_deterministic.csv"

def create_test_csv():
    """Create a test CSV file for mode detection"""
    with open(test_csv_path, 'w', newline='') as f:
        f.write(test_csv_content)
    print(f"Created test CSV: {test_csv_path}")

def test_auto_detection():
    """Test the auto-detection functionality"""
    # Create test CSV
    create_test_csv()
    
    # Test the auto_detect_mode function directly
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    app = CPMDesktopApp(root)
    
    print(f"Initial state:")
    print(f"  analysis_mode: {app.analysis_mode}")
    print(f"  mode_label: {app.mode_label.cget('text')}")
    
    # Test auto-detection on the test CSV
    headers = ['activity', 'description', 'duration', 'predecessors', 'min_duration', 'crash_cost', 'resource_demand', 'normal_cost']
    detected_mode = app.auto_detect_mode(headers)
    print(f"\nAuto-detection result: {detected_mode}")
    
    # Simulate what happens when load_csv_auto_detect processes this file
    print(f"\nSimulating load_csv_auto_detect behavior:")
    print(f"1. Before clear_all: analysis_mode = {app.analysis_mode}")
    
    # Clear but preserve mode setting
    app.clear_all(reset_mode=False)
    print(f"2. After clear_all(reset_mode=False): analysis_mode = {app.analysis_mode}")
    
    # Set deterministic mode (as would happen in load_csv_auto_detect)
    app.analysis_mode = 'deterministic'
    app.current_analyzer = app.cpm_analyzer
    app.setup_deterministic_tree()
    app.mode_label.config(text="Mode: CPM (Auto-detected)", foreground="blue")
    
    print(f"3. After mode setup:")
    print(f"   analysis_mode: {app.analysis_mode}")
    print(f"   mode_label: {app.mode_label.cget('text')}")
    
    # Clean up
    root.destroy()
    if os.path.exists(test_csv_path):
        os.remove(test_csv_path)
        print(f"\nCleaned up test file: {test_csv_path}")

if __name__ == "__main__":
    test_auto_detection()
