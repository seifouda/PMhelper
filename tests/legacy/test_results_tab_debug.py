#!/usr/bin/env python3
"""Debug test for ResultsTab issue"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

def debug_results_tab():
    """Debug the ResultsTab display issue"""
    print("=== DEBUGGING RESULTSTAB DISPLAY ISSUE ===")
    
    try:
        # Import required modules
        import tkinter as tk
        from pmhelper.gui.main_window import MainWindow
        
        # Create a hidden root window for testing
        root = tk.Tk()
        root.withdraw()
        
        # Create the main window
        print("1. Creating MainWindow...")
        app = MainWindow(root)
        print(f"✅ MainWindow created")
        print(f"   Analysis mode: {app.analysis_mode}")
        print(f"   Has results_tab: {hasattr(app, 'results_tab')}")
        
        # Check if results_tab is properly initialized
        if hasattr(app, 'results_tab'):
            results_tab = app.results_tab
            print(f"   ResultsTab type: {type(results_tab)}")
            print(f"   Has results_frame: {hasattr(results_tab, 'results_frame')}")
            print(f"   Has activities_tree: {hasattr(results_tab, 'activities_tree')}")
            print(f"   Results data: {results_tab.results_data}")
        
        # Try to get sample data and run analysis
        print("\n2. Getting sample data...")
        activities_data = app.get_activities_data()
        print(f"✅ Sample data loaded: {len(activities_data)} activities")
        
        # Simulate analysis
        print("\n3. Testing analysis execution...")
        
        # Get the analyzer
        if app.analysis_mode == 'deterministic':
            from pmhelper.core.cpm_analyzer import CPMAnalyzer
            analyzer = CPMAnalyzer()
        else:
            from pmhelper.core.pert_analyzer import PERTAnalyzer  
            analyzer = PERTAnalyzer()
        
        # Run analysis
        results = analyzer.analyze_from_data(activities_data)
        print(f"✅ Analysis completed")
        print(f"   Results type: {type(results)}")
        print(f"   Results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
        
        # Test results_tab.update_results directly
        print("\n4. Testing ResultsTab.update_results()...")
        try:
            results_tab.update_results(results, app.analysis_mode)
            print("✅ update_results() called successfully")
        except Exception as e:
            print(f"❌ update_results() failed: {e}")
            import traceback
            traceback.print_exc()
        
        root.destroy()
        print("\n🎉 Debug test completed!")
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_results_tab()
