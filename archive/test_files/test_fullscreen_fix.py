#!/usr/bin/env python3
"""
Quick test for the fixed fullscreen comparison feature
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_fullscreen_fix():
    """Test the fullscreen comparison feature with proper root window handling"""
    
    # Create test window
    root = tk.Tk()
    root.title("RCPS Fullscreen Fix Test")
    root.geometry("600x400")
    
    # Import the fixed RCPS tab
    try:
        from src.pmhelper.gui.tabs.rcps_tab import FullscreenComparisonWindow
        print("✅ Successfully imported FullscreenComparisonWindow")
    except ImportError as e:
        print(f"❌ Failed to import FullscreenComparisonWindow: {e}")
        return False
    
    # Create sample test data
    sample_cpm_data = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'duration': [3, 2, 4, 1],
        'resource': [2, 1, 3, 1],
        'early_start': [0, 3, 5, 9],
        'late_finish': [3, 5, 9, 10],
        'float': [0, 0, 0, 0],
        1: ['', '', '', ''],
        2: ['', '', '', ''],
        3: [2, '', '', ''],
        4: ['', 1, '', ''],
        5: ['', '', '', ''],
        6: ['', '', 3, ''],
        7: ['', '', 3, ''],
        8: ['', '', 3, ''],
        9: ['', '', 3, ''],
        10: ['', '', '', 1]
    })
    
    sample_rcps_data = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'duration': [3, 2, 4, 1],
        'resource': [2, 1, 3, 1],
        'early_start': [0, 3, 5, 9],
        'late_finish': [3, 5, 9, 10],
        'float': [0, 0, 0, 0],
        'actual_start': [0, 3, 6, 10],  # C and D are delayed
        1: ['', '', '', ''],
        2: ['', '', '', ''],
        3: [2, '', '', ''],
        4: ['', 1, '', ''],
        5: ['', '', '', ''],
        6: ['', '', '', ''],
        7: ['', '', 3, ''],
        8: ['', '', 3, ''],
        9: ['', '', 3, ''],
        10: ['', '', 3, ''],
        11: ['', '', '', 1]
    })
    
    sample_gantt_data = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'duration': [3, 2, 4, 1],
        'resource': [2, 1, 3, 1]
    })
    
    print("✅ Created sample test data")
    
    def open_fullscreen_test():
        """Open the fullscreen comparison window with test data using proper root"""
        try:
            # This should now work with the fix
            fullscreen_window = FullscreenComparisonWindow(
                root,  # Pass the actual tkinter root window
                sample_cpm_data, 
                sample_rcps_data, 
                sample_gantt_data
            )
            print("✅ Successfully opened fullscreen comparison window")
        except Exception as e:
            print(f"❌ Error opening fullscreen window: {e}")
            import traceback
            traceback.print_exc()
    
    # Create test interface
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    title_label = tk.Label(main_frame, text="RCPS Fullscreen Fix Test", 
                          font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 20))
    
    status_label = tk.Label(main_frame, 
                         text="Fixed: Using proper root window for tk.Toplevel()\\n" +
                              "Now the fullscreen window should open correctly!")
    status_label.pack(pady=(0, 20))
    
    test_btn = ttk.Button(main_frame, text="Test Fullscreen Comparison", 
                         command=open_fullscreen_test)
    test_btn.pack(pady=10)
    
    close_btn = ttk.Button(main_frame, text="Close Test", command=root.quit)
    close_btn.pack(pady=10)
    
    print("✅ Test interface created successfully")
    print("\\n🚀 Starting fullscreen fix test...")
    print("Click 'Test Fullscreen Comparison' to test the fixed feature")
    
    # Start the test interface
    root.mainloop()
    
    return True

if __name__ == "__main__":
    print("=== RCPS Fullscreen Fix Test ===")
    success = test_fullscreen_fix()
    if success:
        print("\\n✅ Test completed successfully!")
    else:
        print("\\n❌ Test failed!")
