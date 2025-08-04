#!/usr/bin/env python3
"""
PMHelper Application Launcher

Main entry point for the PMHelper GUI application.
Launch the Project Management application with full CPM and PERT analysis capabilities.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path for the advanced GUI
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Launch the PMHelper GUI application"""
    try:
        # Import tkinter and the advanced multi-tab GUI
        import tkinter as tk
        from pmhelper.gui.main_window import MainWindow
        
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
        
        # Create and run the application directly
        root = tk.Tk()
        app = MainWindow(root)
        
        # Verify initial state
        print(f"Application initialized with mode: {app.analysis_mode}")
        if hasattr(app, 'input_tab') and hasattr(app.input_tab, 'get_activities_data'):
            print(f"Sample activities loaded: {len(app.input_tab.get_activities_data())}")
        else:
            print("Sample activities loaded: [InputTab or get_activities_data not found]")

        print("Application launched successfully!")
        print("Close the application window to exit.")

        root.mainloop()
        
        print("Application closed.")
        
        # # Create and run the application
        # root = tk.Tk()
        # app = MainWindow(root)
        
        # print("Application launched successfully!")
        # print("Close the application window to exit.")
        
        # root.mainloop()
        
        # print("Application closed.")
        
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
        print("\nAlternatively, you can run the CLI version:")
        print("python -m pmhelper.cli.cpm_cli --help")
        print("python -m pmhelper.cli.pert_cli --help")
        
    except Exception as e:
        print(f"Error launching application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
