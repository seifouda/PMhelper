#!/usr/bin/env python3
"""
Risk Analysis GUI Demo

Demonstrates the complete Risk Analysis tab functionality with sample PERT data.
Shows all four main features in action.
"""

import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pmhelper.gui.main_window import MainWindow
from pmhelper.core.pert_analyzer import PERTAnalyzer


def load_sample_pert_data():
    """Load sample PERT data for demonstration"""
    # Sample PERT network - medium complexity project
    data = {
        'Activity': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
        'Optimistic': [2, 3, 4, 2, 3, 2, 3, 4],
        'Most Likely': [4, 5, 6, 4, 5, 4, 5, 6],
        'Pessimistic': [6, 9, 10, 8, 9, 6, 9, 10],
        'Predecessors': ['', 'A', 'A', 'B', 'C,D', 'C', 'E,F', 'G']
    }
    
    df = pd.DataFrame(data)
    return df


def setup_demo_data(main_window):
    """Setup demo data in the main window"""
    try:
        # Load sample data
        df = load_sample_pert_data()
        
        # Convert to PERT format
        main_window.current_data = df
        main_window.analysis_mode = 'probabilistic'
        
        # Run PERT analysis
        if main_window.pert_analyzer:
            main_window.pert_analyzer.analyze(df)
            main_window.current_analyzer = main_window.pert_analyzer
            
            # Update status
            main_window.update_status("PERT analysis complete - Risk Analysis ready")
            main_window.mode_indicator.config(text="Mode: Probabilistic (PERT)")
            
            # Show instructions
            instructions = """Risk Analysis Demo Ready!

Sample PERT project loaded with 8 activities.

Try the Risk Analysis tab features:

1. DELAY RISK ANALYSIS
   - Contract Time: 15 weeks
   - Penalty Rate: $1000/week
   - Click "Calculate Delay Risk"

2. CONTINGENCY PLANNING
   - Use slider to adjust confidence level
   - Try 80%, 90%, 95%, 99%
   - Click "Calculate Contingency"

3. VARIANCE REDUCTION STRATEGIES
   - Compare Strategy A vs B vs Mixed
   - See ROI and net benefits
   - Click "Analyze Strategies"

4. ACTIVITY RISK PRIORITIZATION
   - Click "Calculate Risk Scores"
   - View color-coded risk levels
   - Click "Generate Mitigation Plan"

Navigate to the "Risk Analysis" tab to begin!"""
            
            messagebox.showinfo("Demo Ready", instructions)
            
            # Switch to Risk Analysis tab
            for i in range(main_window.notebook.index("end")):
                if main_window.notebook.tab(i, "text") == "Risk Analysis":
                    main_window.notebook.select(i)
                    break
            
            return True
        else:
            messagebox.showerror("Error", "PERT Analyzer not available!")
            return False
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to setup demo: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main demo function"""
    # Create main window
    root = tk.Tk()
    main_window = MainWindow(root)
    
    # Load demo data after a short delay (let GUI initialize)
    root.after(500, lambda: setup_demo_data(main_window))
    
    # Run the application
    root.mainloop()


if __name__ == "__main__":
    print("=" * 70)
    print("PMHelper Risk Analysis GUI Demo")
    print("=" * 70)
    print("\nStarting GUI with sample PERT data...")
    print("\nFeatures to explore:")
    print("  1. Delay Risk Analysis - Calculate delay probability and risk cost")
    print("  2. Contingency Planning - Estimate time buffers for confidence levels")
    print("  3. Variance Reduction - Compare optimization strategies")
    print("  4. Activity Risk Prioritization - Identify high-risk activities")
    print("\n" + "=" * 70 + "\n")
    
    main()
