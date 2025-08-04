#!/usr/bin/env python3
"""
Quick test to launch the actual GUI and check the mode state
"""

import tkinter as tk
import sys
sys.path.append('code')
from cpm_app import CPMDesktopApp

def quick_gui_test():
    """Launch GUI briefly to check mode state"""
    root = tk.Tk()
    app = CPMDesktopApp(root)
    
    # Check mode immediately after initialization
    print(f"After GUI creation:")
    print(f"  analysis_mode: {app.analysis_mode}")
    print(f"  mode_label text: '{app.mode_label.cget('text')}'")
    
    # Check if we can analyze project right away
    try:
        print(f"\nTesting analyze_project()...")
        print(f"  analysis_mode check: {bool(app.analysis_mode)}")
        if not app.analysis_mode:
            print("  ❌ analysis_mode is falsy - this is the problem!")
        else:
            print(f"  ✅ analysis_mode is truthy: '{app.analysis_mode}'")
            
        # Also check what activities_data looks like
        activities_data = app.get_activities_data()
        print(f"  activities_data count: {len(activities_data) if activities_data else 0}")
        
    except Exception as e:
        print(f"  Error during test: {e}")
    
    # Don't actually show the GUI, just destroy it
    root.after(100, root.destroy)  # Close after 100ms
    root.mainloop()

if __name__ == "__main__":
    quick_gui_test()
