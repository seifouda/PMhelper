#!/usr/bin/env python3
"""
Debug version of launch_app.py to diagnose the mode detection issue
"""

import sys
import os
from pathlib import Path

# Add the code directory to the path
project_root = Path(__file__).parent
code_path = project_root / "code"
sys.path.insert(0, str(code_path))

def debug_main():
    """Launch with debugging to see what's happening with mode detection"""
    try:
        print("Starting PMHelper - Project Management Analysis Tool...")
        print("Features available:")
        print("- Deterministic (CPM) analysis")
        print("- Probabilistic (PERT) analysis")
        print("- Resource-Constrained Project Scheduling (RCPS)")
        print("- Project crashing optimization")
        print("- Network diagrams and Gantt charts")
        print("- Probability analysis for PERT")
        print("- Risk analysis and Monte Carlo simulation")
        print("- CSV/Excel import/export functionality")
        print("- Command-line interface available")
        print("-" * 50)
        
        print("DEBUG: About to import cpm_app...")
        from cpm_app import CPMDesktopApp
        import tkinter as tk
        
        print("DEBUG: Creating tkinter root...")
        root = tk.Tk()
        
        print("DEBUG: Creating CPMDesktopApp instance...")
        app = CPMDesktopApp(root)
        
        print("DEBUG: Checking initial state...")
        print(f"  - analysis_mode: '{app.analysis_mode}'")
        print(f"  - mode_label: '{app.mode_label.cget('text')}'")
        print(f"  - activities count: {len(app.get_activities_data())}")
        
        if app.analysis_mode == 'deterministic':
            print("DEBUG: ✅ Mode is correctly set to 'deterministic'")
        else:
            print("DEBUG: ❌ Mode issue detected!")
            print(f"DEBUG:    Expected 'deterministic', got '{app.analysis_mode}'")
        
        if 'Mode: CPM' in app.mode_label.cget('text'):
            print("DEBUG: ✅ Label correctly shows CPM mode")
        else:
            print("DEBUG: ❌ Label issue detected!")
            print(f"DEBUG:    Expected label to contain 'Mode: CPM', got '{app.mode_label.cget('text')}'")
        
        activities_count = len(app.get_activities_data())
        if activities_count > 0:
            print(f"DEBUG: ✅ Sample data loaded ({activities_count} activities)")
        else:
            print("DEBUG: ❌ No sample data loaded")
        
        print("DEBUG: Starting main loop...")
        print("Application launched successfully!")
        print("Close the application window to exit.")
        
        root.mainloop()
        
        print("Application closed.")
        
    except ImportError as e:
        print(f"Error: Required modules not found: {e}")
        print("Please ensure all dependencies are installed:")
        print("- tkinter (usually included with Python)")
        print("- matplotlib")
        print("- pandas")
        print("- networkx")
        print("- numpy")
        print("- scipy")
        print("- tabulate")
        
    except Exception as e:
        print(f"Error launching application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_main()
