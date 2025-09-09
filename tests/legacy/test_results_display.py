#!/usr/bin/env python3
"""Test ResultsTab display with fixed data structure"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

def test_results_display():
    """Test the ResultsTab display functionality"""
    print("=== TESTING RESULTSTAB DISPLAY FUNCTIONALITY ===")
    
    try:
        # Import required modules
        import tkinter as tk
        from pmhelper.gui.main_window import MainWindow
        
        # Create application
        root = tk.Tk()
        root.withdraw()  # Hide for testing
        
        print("1. Creating MainWindow...")
        app = MainWindow(root)
        print("✅ MainWindow created successfully")
        
        # Get sample data
        print("\n2. Getting sample activities data...")
        activities_data = app.get_activities_data()
        print(f"✅ Sample data: {len(activities_data)} activities")
        
        # Create analyzer
        print(f"\n3. Creating analyzer for mode: {app.analysis_mode}")
        if app.analysis_mode == 'deterministic':
            from pmhelper.core.cpm_analyzer import CPMAnalyzer
            analyzer = CPMAnalyzer()
        else:
            from pmhelper.core.pert_analyzer import PERTAnalyzer
            analyzer = PERTAnalyzer()
        
        app.current_analyzer = analyzer
        print("✅ Analyzer created")
        
        # Run analysis through the main window method (this should now work)
        print("\n4. Running analyze_project()...")
        try:
            app.analyze_project()
            print("✅ analyze_project() completed successfully")
            
            # Check if results_tab was updated
            if hasattr(app.results_tab, 'results_data') and app.results_tab.results_data:
                print("✅ ResultsTab has results_data")
                print(f"   Results keys: {list(app.results_tab.results_data.keys())}")
                print(f"   Project duration: {app.results_tab.results_data.get('project_duration')}")
                print(f"   Critical path: {app.results_tab.results_data.get('critical_path')}")
                print(f"   Activities count: {len(app.results_tab.results_data.get('activities', []))}")
            else:
                print("❌ ResultsTab has no results_data")
                
        except Exception as e:
            print(f"❌ analyze_project() failed: {e}")
            import traceback
            traceback.print_exc()
        
        root.destroy()
        print("\n🎉 Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_results_display()
