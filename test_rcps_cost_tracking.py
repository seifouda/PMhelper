#!/usr/bin/env python3
"""
Test script to verify RCPS crashing cost tracking fix
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up the application
import sys
import os
import tkinter as tk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import after path setup
try:
    from pmhelper.gui.main_app import MainApp
except ImportError:
    # Try alternative import path
    sys.path.insert(0, os.path.dirname(__file__))
    from src.pmhelper.gui.main_app import MainApp

def test_rcps_cost_tracking():
    """Test RCPS crashing to verify cost tracking is working"""
    print("Testing RCPS Crashing Cost Tracking...")
    
    # Create the main app
    root = tk.Tk()
    app = MainApp(root)
    
    try:
        # 1. First run RCPS analysis to get data
        print("\n1. Running RCPS analysis...")
        app.rcps_tab.resource_limit_var.set(5)
        app.rcps_tab.priority_var.set("minimum_slack")
        app.rcps_tab.run_rcps()
        
        # Wait a moment for processing
        root.update()
        
        # 2. Run RCPS crashing with target duration 25
        print("\n2. Running RCPS crashing with target 25...")
        app.rcps_crashing_tab.target_duration_var.set(25)
        app.rcps_crashing_tab.strategy_var.set("lowest_cost")
        app.rcps_crashing_tab.objective_var.set("minimize_cost")
        app.rcps_crashing_tab.run_rcps_crashing_with_table_data()
        
        # Wait for processing
        root.update()
        
        # 3. Get the results
        print("\n3. Checking results...")
        summary_content = app.rcps_crashing_tab.summary_text.get('1.0', tk.END)
        log_content = app.rcps_crashing_tab.log_text.get('1.0', tk.END)
        
        print("\n=== SUMMARY CONTENT ===")
        print(summary_content[:500] + "..." if len(summary_content) > 500 else summary_content)
        
        print("\n=== LOG CONTENT (first 800 chars) ===")
        print(log_content[:800] + "..." if len(log_content) > 800 else log_content)
        
        # 4. Check for cost tracking issues
        issues = []
        if "Crash Cost: $0.00" in log_content:
            issues.append("❌ Found $0.00 crash costs in log")
        else:
            print("✅ No $0.00 crash costs found")
            
        if "duration ?" in log_content or "duration N/A" in log_content:
            issues.append("❌ Found missing durations (?) in log")
        else:
            print("✅ No missing durations found")
            
        if "Total Crash Cost: $0.00" in summary_content:
            issues.append("❌ Total crash cost shows $0.00")
        else:
            print("✅ Total crash cost is non-zero")
            
        if issues:
            print(f"\n❌ ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print(f"\n✅ COST TRACKING APPEARS TO BE WORKING!")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()

if __name__ == "__main__":
    test_rcps_cost_tracking()
