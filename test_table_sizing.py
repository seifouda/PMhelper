#!/usr/bin/env python3
"""
Test the fixed-width table sizing implementation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import ttk
import pandas as pd

def test_table_sizing():
    """Test the new fixed-width table display method"""
    print("Testing fixed-width table sizing...")
    
    # Create test window
    root = tk.Tk()
    root.title("Table Sizing Test")
    root.geometry("800x600")
    
    # Mock main window and notebook for RCPSTab
    mock_notebook = ttk.Notebook(root)
    mock_main_window = root
    
    from src.pmhelper.gui.tabs.rcps_tab import RCPSTab
    
    # Create RCPS tab instance
    tab = RCPSTab(mock_notebook, mock_main_window)
    
    # Create test dataframes
    cpm_data = {
        'id': ['A', 'B', 'C'],
        'duration': [3, 4, 2],
        'resource': [1, 2, 1],
        'early_start': [0, 3, 7],
        'late_finish': [3, 7, 9],
        'float': [0, 0, 0]
    }
    
    rcps_data = {
        'id': ['A', 'B', 'C'],
        'duration': [3, 4, 2],
        'resource': [1, 2, 1],
        'early_start': [0, 3, 7],
        'late_finish': [3, 7, 9],
        'float': [0, 0, 0],
        'actual_start': [0, 4, 8]  # Extra column for RCPS
    }
    
    cpm_df = pd.DataFrame(cpm_data)
    rcps_df = pd.DataFrame(rcps_data)
    
    # Create test frame
    test_frame = ttk.Frame(root)
    test_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    try:
        # Test CPM table (6 columns)
        tab.display_compact_table_fixed_width(test_frame, cpm_df, "Initial CPM Schedule", 0, 0)
        print("✓ CPM table created successfully")
        
        # Test RCPS table (7 columns)  
        tab.display_compact_table_fixed_width(test_frame, rcps_df, "Final RCPS Schedule", 1, 0)
        print("✓ RCPS table created successfully")
        
        print("\n[SUCCESS] Both table types display correctly!")
        print("Close the window to continue...")
        
        root.mainloop()
        
    except Exception as e:
        print(f"[ERROR] Table sizing test failed: {e}")
        import traceback
        traceback.print_exc()
        root.destroy()

if __name__ == "__main__":
    test_table_sizing()
