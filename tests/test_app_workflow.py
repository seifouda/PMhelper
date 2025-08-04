#!/usr/bin/env python3
"""
Complete Application Test

Test the complete PMHelper application workflow to verify float values 
are displayed correctly in the ResultsTab.
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from pmhelper.gui.main_window import MainWindow


def test_application_workflow():
    """Test the complete application workflow programmatically"""
    print("=" * 80)
    print("COMPLETE APPLICATION TEST")
    print("=" * 80)
    
    # Create test data with known float values
    test_activities = [
        {'id': 'A', 'activity': 'Task A', 'duration': 3, 'predecessors': []},
        {'id': 'B', 'activity': 'Task B', 'duration': 2, 'predecessors': ['A']},
        {'id': 'C', 'activity': 'Task C', 'duration': 4, 'predecessors': ['A']},
        {'id': 'D', 'activity': 'Task D', 'duration': 1, 'predecessors': ['B', 'C']},
    ]
    
    print("Test Data:")
    for act in test_activities:
        print(f"  {act['id']}: {act['activity']}, Duration={act['duration']}, Predecessors={act['predecessors']}")
    
    print("\nExpected Results:")
    print("  Activity A: Float = 0 (Critical)")
    print("  Activity B: Float = 2 (Non-critical)")
    print("  Activity C: Float = 0 (Critical)")
    print("  Activity D: Float = 0 (Critical)")
    
    # Create application instance
    print("\nCreating application...")
    root = tk.Tk()
    root.withdraw()  # Hide the main window for testing
    
    app = MainWindow(root)
    
    # Set test data directly
    print("Loading test data...")
    app.current_analyzer = app.cpm_analyzer  # Set to CPM mode
    app.analysis_mode = 'deterministic'
    
    # Manually set activities data
    app.input_tab.activities_data = test_activities
    
    # Run analysis
    print("Running CPM analysis...")
    app.analyze_project()
    
    # Check results data
    if hasattr(app, 'results_data') and app.results_data:
        activities = app.results_data.get('activities', [])
        critical_activities = app.results_data.get('critical_activities', [])
        
        print(f"\nResults from MainWindow:")
        print(f"Critical Activities: {critical_activities}")
        
        success = True
        for activity in activities:
            act_id = activity.get('id')
            float_val = activity.get('float', 0)
            critical = activity.get('critical', False)
            es = activity.get('ES', 0)
            ls = activity.get('LS', 0)
            
            print(f"  {act_id}: ES={es}, LS={ls}, Float={float_val:.2f}, Critical={critical}")
            
            # Validate expected results
            if act_id == 'A' and (float_val != 0 or not critical):
                print(f"    ❌ Expected A to be critical with float=0, got float={float_val}, critical={critical}")
                success = False
            elif act_id == 'B' and (float_val != 2 or critical):
                print(f"    ❌ Expected B to be non-critical with float=2, got float={float_val}, critical={critical}")
                success = False
            elif act_id == 'C' and (float_val != 0 or not critical):
                print(f"    ❌ Expected C to be critical with float=0, got float={float_val}, critical={critical}")
                success = False
            elif act_id == 'D' and (float_val != 0 or not critical):
                print(f"    ❌ Expected D to be critical with float=0, got float={float_val}, critical={critical}")
                success = False
            else:
                print(f"    ✅ {act_id} results correct")
        
        total_float = sum(a.get('float', 0) for a in activities)
        non_critical_count = sum(1 for a in activities if not a.get('critical', True))
        
        print(f"\nSummary:")
        print(f"  Total system float: {total_float}")
        print(f"  Non-critical activities: {non_critical_count}")
        
        if success and total_float > 0 and non_critical_count > 0:
            print("\n🎉 APPLICATION TEST PASSED!")
            print("Float calculations are working correctly in the application!")
        else:
            print("\n❌ APPLICATION TEST FAILED!")
            print("Float calculations need further debugging.")
    else:
        print("❌ No results data generated from analysis")
        success = False
    
    # Test ResultsTab data format
    print("\nTesting ResultsTab data format...")
    if hasattr(app, 'results_tab') and app.results_data:
        # Update the results tab with the analysis data
        app.results_tab.update_results(app.results_data)
        
        # Check if the data is properly formatted for display
        print("ResultsTab updated successfully with analysis data")
    
    root.destroy()
    
    return success


if __name__ == "__main__":
    print("Testing Complete PMHelper Application Workflow...")
    
    success = test_application_workflow()
    
    print("\n" + "="*80)
    print("FINAL TEST RESULT")
    print("="*80)
    
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("PMHelper float calculation fix is working correctly!")
        print("\nTo verify in the GUI:")
        print("1. Run: python launch_app.py")
        print("2. Load test data or enter activities manually")
        print("3. Click 'Analyze Project'")
        print("4. Check Results tab - non-critical activities should show float > 0")
    else:
        print("❌ TESTS FAILED!")
        print("Additional debugging needed for float calculations.")
    print("="*80)
