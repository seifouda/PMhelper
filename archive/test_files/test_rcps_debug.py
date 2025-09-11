#!/usr/bin/env python3
"""
Debug script to test RCPS duration issue with detailed output
"""

import sys
sys.path.append('src')

from pmhelper.gui.main_window import MainWindow
import tkinter as tk

def test_rcps_debug():
    print("[DEBUG] Testing RCPS with Debug Output")
    print("=" * 60)
    
    # Create the main window
    root = tk.Tk()
    root.withdraw()  # Hide the window for testing
    app = MainWindow(root)
    
    # Load sample data
    app.input_tab.load_sample_data()
    print("✅ Sample data loaded")
    
    # Run CPM analysis first
    app.run_cpm_analysis()
    print("✅ CPM analysis completed")
    
    # Create RCPS tab if needed
    if not hasattr(app, 'rcps_tab') or app.rcps_tab is None:
        from pmhelper.gui.tabs.rcps_tab import RCPSTab
        app.rcps_tab = RCPSTab(app.notebook, app)
    
    # Run RCPS analysis with resource limit 5
    print("\n🔧 Running RCPS Analysis...")
    app.rcps_tab.resource_limit_var.set(5)
    app.rcps_tab.run_rcps()
    print("✅ RCPS analysis completed")
    
    # Now test RCPS Crashing
    print("\n🚀 Testing RCPS Crashing...")
    
    # Test the crashing data preparation
    crashing_df = app.rcps_tab.prepare_crashing_dataframe()
    if crashing_df is not None:
        print(f"✅ RCPS Crashing DataFrame prepared with {len(crashing_df)} activities")
    
    # Test running RCPS crashing
    if hasattr(app, 'rcps_crashing_tab') and app.rcps_crashing_tab:
        print("\n🔥 Running RCPS Crashing Analysis...")
        try:
            # Set target duration to 30 (less than expected 33)
            app.rcps_crashing_tab.target_duration_var.set(30)
            
            # Trigger crashing analysis
            app.rcps_crashing_tab.run_crashing()
            
        except Exception as e:
            print(f"❌ RCPS Crashing failed: {e}")
            import traceback
            traceback.print_exc()
    
    root.destroy()
    print(f"\n🎉 Debug test completed!")

if __name__ == "__main__":
    test_rcps_debug()
