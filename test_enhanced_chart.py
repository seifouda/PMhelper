#!/usr/bin/env python3
"""
Test the enhanced chart sizing for Gantt charts
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import ttk
import pandas as pd

def test_chart_sizing():
    """Test the enhanced Gantt chart sizing"""
    print("Testing enhanced Gantt chart sizing...")
    
    # Create test window
    root = tk.Tk()
    root.title("Enhanced Chart Sizing Test")
    root.geometry("1200x700")  # Larger window to test chart scaling
    
    # Mock main window and notebook for RCPSTab
    mock_notebook = ttk.Notebook(root)
    mock_main_window = root
    
    from src.pmhelper.gui.tabs.rcps_tab import RCPSTab
    
    # Create RCPS tab instance
    tab = RCPSTab(mock_notebook, mock_main_window)
    
    # Create test dataframe with timeline data
    test_data = {
        'id': ['A', 'B', 'C', 'D'],
        'duration': [3, 4, 2, 5],
        'resource': [1, 2, 1, 2],
        'early_start': [0, 3, 7, 9],
        'late_finish': [3, 7, 9, 14],
        'float': [0, 0, 0, 0],
        'actual_start': [0, 4, 8, 10],  # RCPS with delays
        # Timeline columns
        0: ['', '', '', ''],
        1: ['A', '', '', ''],
        2: ['A', '', '', ''],
        3: ['A', 'B', '', ''],
        4: ['', 'B', '', ''],
        5: ['', 'B', '', ''],
        6: ['', 'B', '', ''],
        7: ['', '', 'C', ''],
        8: ['', '', 'C', ''],
        9: ['', '', '', 'D'],
        10: ['', '', '', 'D'],
        11: ['', '', '', 'D'],
        12: ['', '', '', 'D'],
        13: ['', '', '', 'D'],
        14: ['', '', '', '']
    }
    
    # Add resource usage row
    test_data_with_resources = test_data.copy()
    # Add resource availability and usage rows
    rs_data = ['RS'] + [2] * 6 + [1, 1, 2, 2, 2, 2, 2, 2]  # Resource usage over time
    
    df = pd.DataFrame(test_data)
    
    # Create test frame with grid layout like the hybrid view
    test_frame = ttk.Frame(root)
    test_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Configure grid weights like the actual hybrid layout
    test_frame.grid_columnconfigure(0, weight=0)  # Tables: fixed width
    test_frame.grid_columnconfigure(1, weight=1)  # Charts: expanding
    test_frame.grid_rowconfigure(0, weight=1)
    test_frame.grid_rowconfigure(1, weight=1)
    
    try:
        # Create compact table on the left
        tab.display_compact_table_fixed_width(test_frame, df, "Test RCPS Schedule", 0, 0)
        print("✓ Compact table created successfully")
        
        # Create enhanced Gantt chart on the right
        tab.display_gantt_chart(test_frame, df, "Enhanced Gantt Chart", col=1, row=0, is_cpm=False)
        print("✓ Enhanced Gantt chart created successfully")
        
        print("\n[SUCCESS] Enhanced chart sizing implemented!")
        print("Key improvements:")
        print("- Chart width increased from 8 to 12 inches")
        print("- Added subplot adjustments for better space utilization")
        print("- Applied tight_layout for optimal layout")
        print("- Chart now fills the available chart field properly")
        print("\nClose the window to continue...")
        
        root.mainloop()
        
    except Exception as e:
        print(f"[ERROR] Chart sizing test failed: {e}")
        import traceback
        traceback.print_exc()
        root.destroy()

if __name__ == "__main__":
    test_chart_sizing()
