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
PRODUCTION_MODE = True

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
        
        # Skip debug prints with emojis or debug markers
        debug_indicators = [
            '🔍', '📊', '✅', '❌', '🎯', '📋', '🔨', '💰', '📈', '🚀', 
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
