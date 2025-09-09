#!/usr/bin/env python3
"""
Test script to verify Network tab matplotlib toolbar visibility and functionality
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pmhelper.gui.main_window import MainWindow
from pmhelper.core.cpm_analyzer import CPMAnalyzer

def test_toolbar_visibility():
    """Test that the Network tab toolbar is visible and functional"""
    print("=" * 60)
    print("NETWORK TAB TOOLBAR VISIBILITY TEST")
    print("=" * 60)
    
    # Create test application
    root = tk.Tk()
    app = MainWindow(root)
    
    # Wait for the application to initialize
    root.update()
    root.after(200)  # Give time for geometry management
    root.update_idletasks()
    
    # Access the network tab
    network_tab = app.network_tab
    
    # Check if toolbar exists
    if hasattr(network_tab, 'toolbar') and network_tab.toolbar:
        print("✓ Toolbar widget exists")
        
        # Check toolbar frame geometry
        if hasattr(network_tab, 'toolbar'):
            toolbar_parent = network_tab.toolbar.master
            toolbar_height = toolbar_parent.winfo_height()
            toolbar_geometry = toolbar_parent.winfo_geometry()
            
            print(f"✓ Toolbar frame height: {toolbar_height}")
            print(f"✓ Toolbar frame geometry: {toolbar_geometry}")
            
            if toolbar_height > 1:
                print("✓ TOOLBAR IS VISIBLE!")
                
                # Test toolbar buttons
                toolbar_children = network_tab.toolbar.winfo_children()
                button_count = len([w for w in toolbar_children if isinstance(w, tk.Button)])
                print(f"✓ Toolbar buttons found: {button_count}")
                
                if button_count > 0:
                    print("✓ TOOLBAR FUNCTIONALITY CONFIRMED!")
                    test_result = "PASS"
                else:
                    print("✗ No toolbar buttons found")
                    test_result = "FAIL"
            else:
                print("✗ TOOLBAR IS NOT VISIBLE (height = 1)")
                test_result = "FAIL"
        else:
            print("✗ Toolbar frame not accessible")
            test_result = "FAIL"
    else:
        print("✗ Toolbar widget does not exist")
        test_result = "FAIL"
    
    # Clean up
    root.destroy()
    
    print("=" * 60)
    print(f"TEST RESULT: {test_result}")
    print("=" * 60)
    
    return test_result == "PASS"

if __name__ == "__main__":
    success = test_toolbar_visibility()
    sys.exit(0 if success else 1)
