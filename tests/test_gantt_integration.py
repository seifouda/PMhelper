#!/usr/bin/env python3
"""
Gantt Integration Test Script

Tests the three critical fixes:
1. Automatic chart display after analysis
2. Enhanced data integration 
3. Tab communication events
"""

import sys
import os
from pathlib import Path
import tkinter as tk

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_gantt_integration():
    """Test the Gantt chart integration fixes"""
    
    print("=" * 80)
    print("GANTT CHART INTEGRATION TESTING")
    print("=" * 80)
    
    try:
        # Import and create the application
        from pmhelper.gui.main_window import MainWindow
        
        root = tk.Tk()
        app = MainWindow(root)
        
        print(f"✓ Application created successfully")
        print(f"✓ Mode: {app.analysis_mode}")
        print(f"✓ Sample activities: {len(app.get_activities_data())}")
        
        # Test Fix 1: Automatic chart display method
        if hasattr(app, 'update_gantt_chart_after_analysis'):
            print("✓ Fix 1: Automatic chart display method exists")
        else:
            print("✗ Fix 1: Missing automatic chart display method")
        
        # Test Fix 2: Enhanced data integration
        if hasattr(app.gantt_tab, 'update_data'):
            print("✓ Fix 2: Enhanced data integration method exists")
        else:
            print("✗ Fix 2: Missing enhanced data integration")
        
        # Test Fix 3: Tab communication
        if hasattr(app, 'on_tab_selected'):
            print("✓ Fix 3: Tab communication event handler exists")
        else:
            print("✗ Fix 3: Missing tab communication handler")
        
        print("\n" + "=" * 80)
        print("TESTING ANALYSIS WORKFLOW")
        print("=" * 80)
        
        # Run analysis to test automatic integration
        print("Running CPM analysis...")
        app.analyze_project()
        
        # Verify results were stored
        if hasattr(app, 'results_data') and app.results_data:
            print("✓ Analysis completed and results stored")
            
            # Check if gantt tab received data
            if hasattr(app.gantt_tab, 'results_data') and app.gantt_tab.results_data:
                print("✓ Gantt tab received analysis data")
            else:
                print("⚠ Gantt tab may not have received data yet")
            
            print(f"✓ Graph nodes: {len(app.results_data.get('graph', {}).nodes())}")
            print(f"✓ Critical activities: {len(app.results_data.get('critical_activities', []))}")
            
        else:
            print("✗ Analysis failed or no results stored")
        
        print("\n" + "=" * 80)
        print("TESTING TAB SWITCHING")
        print("=" * 80)
        
        # Test switching to Gantt tab
        for i in range(app.notebook.index("end")):
            tab_text = app.notebook.tab(i, "text")
            if "Gantt" in tab_text:
                print(f"✓ Found Gantt tab at index {i}: {tab_text}")
                app.notebook.select(i)
                print("✓ Successfully switched to Gantt tab")
                break
        else:
            print("✗ Gantt tab not found")
        
        print("\n" + "=" * 80)
        print("INTEGRATION TEST COMPLETED")
        print("=" * 80)
        print("Close the application window to complete the test.")
        
        # Run the application
        root.mainloop()
        
        print("Application closed successfully.")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gantt_integration()
