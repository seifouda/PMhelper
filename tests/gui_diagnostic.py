#!/usr/bin/env python3
"""
GUI Data Flow Diagnostic

Test to check if the timing data is flowing correctly from MainWindow to ResultsTab.
"""

import sys
from pathlib import Path
import tkinter as tk

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from pmhelper.gui.main_window import MainWindow


def test_gui_data_flow():
    """Test the data flow from MainWindow analysis to ResultsTab display"""
    print("=" * 80)
    print("GUI DATA FLOW DIAGNOSTIC")
    print("=" * 80)
    
    # Create application instance (hidden window)
    root = tk.Tk()
    root.withdraw()  # Hide the main window for testing
    
    try:
        app = MainWindow(root)
        
        # Set to CPM mode
        app.analysis_mode = 'deterministic'
        app.current_analyzer = app.cpm_analyzer
        
        print("Application created successfully")
        print(f"Analysis mode: {app.analysis_mode}")
        
        # Get sample data
        activities_data = app.get_activities_data()
        print(f"Sample activities loaded: {len(activities_data)}")
        
        print("\nSample activities:")
        for i, act in enumerate(activities_data[:3]):  # Show first 3
            print(f"  {i+1}. {act}")
        
        # Run analysis
        print("\nRunning analysis...")
        app.analyze_project()
        
        # Check if results_data exists
        if hasattr(app, 'results_data') and app.results_data:
            print("\n✅ Results data created by MainWindow")
            results_data = app.results_data
            
            activities = results_data.get('activities', [])
            print(f"Number of activities in results: {len(activities)}")
            
            print("\nFirst few activity results:")
            for i, activity in enumerate(activities[:3]):
                act_id = activity.get('id', 'Unknown')
                name = activity.get('name', 'MISSING')
                es = activity.get('ES', 'MISSING')
                ef = activity.get('EF', 'MISSING')
                ls = activity.get('LS', 'MISSING')
                lf = activity.get('LF', 'MISSING')
                float_val = activity.get('float', 'MISSING')
                critical = activity.get('critical', 'MISSING')
                
                print(f"  {i+1}. {act_id}: ES={es}, EF={ef}, LS={ls}, LF={lf}, Float={float_val}, Critical={critical}")
                print(f"     Name='{name}', ES_type={type(es)}, Float_type={type(float_val)}, Dict_keys={list(activity.keys())}")
                
                # Check if any values are missing
                missing = [key for key, val in [('ES', es), ('EF', ef), ('LS', ls), ('LF', lf), ('float', float_val)] 
                          if val == 'MISSING']
                if missing:
                    print(f"     ❌ MISSING: {missing}")
                else:
                    print(f"     ✅ All timing values present")
            
            # Check ResultsTab data reception
            print(f"\nChecking ResultsTab...")
            if hasattr(app, 'results_tab'):
                print("✅ ResultsTab exists")
                
                # Try to update ResultsTab with the data
                try:
                    app.results_tab.update_results(results_data, 'deterministic')
                    print("✅ ResultsTab.update_results() called successfully")
                    
                    # Check if activities tree was populated
                    tree = app.results_tab.activities_tree
                    tree_items = tree.get_children()
                    print(f"Activities tree items: {len(tree_items)}")
                    
                    if tree_items:
                        print("✅ Activities tree has items")
                        
                        # Check first few items
                        print("Tree item values:")
                        for i, item in enumerate(tree_items[:3]):
                            values = tree.item(item)['values']
                            print(f"  Row {i+1}: {values}")
                    else:
                        print("❌ Activities tree is empty")
                        
                except Exception as e:
                    print(f"❌ Error updating ResultsTab: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ ResultsTab not found")
        else:
            print("❌ No results data created by MainWindow")
            
        # Check update methods
        print(f"\nChecking update methods...")
        if hasattr(app, 'update_all_tabs'):
            try:
                app.update_all_tabs()
                print("✅ update_all_tabs() called successfully")
            except Exception as e:
                print(f"❌ Error in update_all_tabs(): {e}")
        
    except Exception as e:
        print(f"❌ Error in GUI test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()


def test_results_tab_directly():
    """Test ResultsTab directly with known data"""
    print("\n" + "=" * 80)
    print("DIRECT RESULTSTAB TEST")
    print("=" * 80)
    
    # Create test data with known timing values
    test_results_data = {
        'project_duration': 8,
        'critical_path': ['START', 'A', 'C', 'D', 'END'],
        'critical_activities': ['A', 'C', 'D'],
        'activities': [
            {
                'id': 'A',
                'name': 'Task A', 
                'duration': 3,
                'ES': 0,
                'EF': 3,
                'LS': 0,
                'LF': 3,
                'float': 0,
                'critical': True
            },
            {
                'id': 'B',
                'name': 'Task B',
                'duration': 2, 
                'ES': 3,
                'EF': 5,
                'LS': 5,
                'LF': 7,
                'float': 2,
                'critical': False
            },
            {
                'id': 'C',
                'name': 'Task C',
                'duration': 4,
                'ES': 3,
                'EF': 7,
                'LS': 3,
                'LF': 7,
                'float': 0,
                'critical': True
            }
        ]
    }
    
    root = tk.Tk()
    root.withdraw()
    
    try:
        from pmhelper.gui.tabs.results_tab import ResultsTab
        
        # Create ResultsTab directly
        results_tab = ResultsTab(root)
        results_tab.analysis_mode = 'deterministic'
        
        print("ResultsTab created")
        
        # Update with test data
        results_tab.update_results(test_results_data)
        print("ResultsTab updated with test data")
        
        # Check tree content
        tree_items = results_tab.activities_tree.get_children()
        print(f"Tree items after update: {len(tree_items)}")
        
        if tree_items:
            print("Tree contents:")
            for i, item in enumerate(tree_items):
                values = results_tab.activities_tree.item(item)['values']
                print(f"  Row {i+1}: {values}")
        else:
            print("❌ Tree is still empty")
            
    except Exception as e:
        print(f"❌ Error in direct ResultsTab test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()


if __name__ == "__main__":
    print("Running GUI Data Flow Diagnostic...")
    
    test_gui_data_flow()
    test_results_tab_directly()
    
    print("\nDiagnostic complete.")
