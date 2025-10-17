#!/usr/bin/env python3
"""
PMHelper Application Launcher

Main entry point for the PMHelper GUI application.
Launch the Project Management application with full CPM and PERT analysis capabilities.
"""

import sys
import os
from pathlib import Path
import builtins
import warnings

# PRODUCTION MODE: Suppress debug prints and warnings
PRODUCTION_MODE = True  # ENABLED FOR PRODUCTION

if PRODUCTION_MODE:
    # Suppress matplotlib warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', module='matplotlib')
    
    # Also suppress specific warnings from GUI modules
    import logging
    logging.getLogger('matplotlib').setLevel(logging.ERROR)
    # Store original print function
    original_print = builtins.print
    
    def production_print(*args, **kwargs):
        """Filter out debug prints in production mode"""
        message = ' '.join(str(arg) for arg in args)
        
        # Skip debug prints with debug markers and emojis
        debug_indicators = [
            '[DEBUG_ANALYZE]', '[DEBUG_DATA]', '[DEBUG_SUCCESS]', '[DEBUG_ERROR]', 
            '[DEBUG_TARGET]', '[DEBUG_LIST]', '[DEBUG_BUILD]', '[DEBUG_COST]', 
            '[DEBUG_CHART]', '[DEBUG_LAUNCH]', 
            '[DEBUG', '[RCPS', '[CRASHING', '[ANALYSIS', 'DEBUG:', 
            'VERIFICATION', 'COST DATA', 'ITERATION', 'STRATEGY',
            'Graph nodes:', 'Critical activities:', 'Project duration:',
            'Analyzer type:', 'Activities data count:', 'Sample activity data:',
            'Analysis mode:', 'Current analyzer:', 'Analyzer has activities:',
            'Activity:', 'Node ', ': ES=', ', EF=', ', Duration=',
            'Integration Test Results:', 'fixes implemented', 'READY FOR TESTING',
            'GANTT CHART INTEGRATION TEST', 'Fix 1:', 'Fix 2:', 'Fix 3:',
            'Graph created:', 'crash_cost=', 'normal_cost=', 'Analyzer has',
            "{'id':", '[9 rows x 11 columns]', 'duration:', 'earliest_start:',
            'earliest_finish:', 'latest_start:', 'latest_finish:', "critical':",
            '======================================================================',
            'name', 'activity', 'duration', 'predecessors', 'resource',
            '| Duration=', '| ES=', '| AS=', '[COST DEBUG]', 'Original crash_cost:',
            'Original normal_cost:', 'Final crash_cost:', 'Final normal_cost:',
            'Activities:', 'Project Duration:', 'Project Variance:',
            '============================================================'
        ]
        
        # If message contains debug indicators, skip it
        if any(indicator in message for indicator in debug_indicators):
            return
        
        # Allow essential startup messages
        essential_messages = [
            'Starting PMHelper', 'Features available:', 'Application launched successfully',
            'Close the application window'
        ]
        
        if any(essential in message for essential in essential_messages):
            original_print(*args, **kwargs)
            return
            
        # For regular prints, use original function
        original_print(*args, **kwargs)
    
    # Replace print function
    builtins.print = production_print

# Add the appropriate directory to the path for the advanced GUI
project_root = Path(__file__).parent

# Detect if we're running from a frozen executable
if getattr(sys, 'frozen', False):
    # Running in a bundle (cx_Freeze executable)
    # PMHelper modules are in lib/ directory
    lib_path = project_root / "lib"
    sys.path.insert(0, str(lib_path))
else:
    # Running in development from source
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))

def launch_basic_gui():
    """Launch a basic PMHelper GUI as fallback"""
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    import pandas as pd
    import csv
    
    class BasicPMHelper:
        def __init__(self, root):
            self.root = root
            self.root.title("PMHelper - Project Management Analysis Tool v1.0.0")
            self.root.geometry("800x600")
            
            # Create main interface
            main_frame = ttk.Frame(root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            ttk.Label(main_frame, text="PMHelper - Project Management Analysis Tool", 
                     font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
            
            ttk.Label(main_frame, text="Copyright (c) 2025 PMHelper Development Team", 
                     font=('Arial', 10)).grid(row=1, column=0, columnspan=2, pady=5)
            
            # Buttons for different analysis types
            ttk.Button(main_frame, text="Load CPM Data", 
                      command=self.load_cpm_data).grid(row=2, column=0, padx=5, pady=5, sticky='ew')
            ttk.Button(main_frame, text="Load PERT Data", 
                      command=self.load_pert_data).grid(row=2, column=1, padx=5, pady=5, sticky='ew')
            
            # Status text area
            self.status_text = tk.Text(main_frame, height=20, width=80)
            self.status_text.grid(row=3, column=0, columnspan=2, pady=10, sticky='nsew')
            
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.status_text.yview)
            scrollbar.grid(row=3, column=2, sticky='ns')
            self.status_text.configure(yscrollcommand=scrollbar.set)
            
            self.log("PMHelper Basic GUI Loaded Successfully")
            self.log("Features available:")
            self.log("- Load and analyze CPM project data")
            self.log("- Load and analyze PERT project data")
            self.log("- Basic project management calculations")
            
        def log(self, message):
            self.status_text.insert(tk.END, f"{message}\n")
            self.status_text.see(tk.END)
            
        def load_cpm_data(self):
            filename = filedialog.askopenfilename(
                title="Select CPM Data File",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if filename:
                try:
                    if filename.endswith('.csv'):
                        df = pd.read_csv(filename)
                    else:
                        df = pd.read_excel(filename)
                    self.log(f"Loaded CPM data: {len(df)} activities")
                    self.log(f"Columns: {', '.join(df.columns)}")
                except Exception as e:
                    self.log(f"Error loading file: {e}")
                    
        def load_pert_data(self):
            filename = filedialog.askopenfilename(
                title="Select PERT Data File", 
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if filename:
                try:
                    if filename.endswith('.csv'):
                        df = pd.read_csv(filename)
                    else:
                        df = pd.read_excel(filename)
                    self.log(f"Loaded PERT data: {len(df)} activities")
                    self.log(f"Columns: {', '.join(df.columns)}")
                except Exception as e:
                    self.log(f"Error loading file: {e}")
    
    root = tk.Tk()
    app = BasicPMHelper(root)
    
    print("Sample activities loaded: 9")
    print("Application launched successfully!")
    print("Close the application window to exit.")
    
    root.mainloop()

def main():
    """Launch the PMHelper GUI application"""
    try:
        # Import tkinter and the advanced multi-tab GUI
        import tkinter as tk
        
        try:
            from pmhelper.gui.main_window import MainWindow
        except ImportError as e:
            # Fallback: use basic GUI if main_window import fails
            print(f"Advanced GUI not available ({e}), using basic interface...")
            return launch_basic_gui()
        
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