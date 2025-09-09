#!/usr/bin/env python3
"""
Test script to reproduce               # Build CPM schedule table to get properly formatted data
            cpm_table, project_duration, critical_path = app.cmp_analyzer.build_cpm_schedule_table(test_data, resource_limit=5)
            app.current_data = cpm_table       # Build CPM schedule table to get properly formatted data
            cpm_table, project_duration, critical_path = app.cmp_analyzer.build_cpm_schedule_table(test_data, resource_limit=5)
            app.current_data = cpm_table RCPS Crashing "no RCPS data available" bug
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from pmhelper.gui.main_window import MainWindow
import tkinter as tk

def test_rcps_crashing_bug():
    """Test the RCPS crashing bug scenario"""
    print("[DEBUG] Testing RCPS Crashing Bug Reproduction")
    print("="*60)
    
    # Create test data with all required columns for RCPS
    test_data = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'duration': [3, 4, 2, 3],
        'predecessors': ['', 'A', 'A', 'B,C'],
        'resource': [2, 3, 1, 2],  # Max resource is 3
        'crash_cost': [100, 150, 80, 120],
        'min_duration': [2, 2, 1, 2],
        # Add required columns for RCPS validation
        'early_start': [0, 3, 3, 7],
        'late_finish': [3, 7, 5, 10],
        'float': [0, 0, 2, 0]
    })
    
    print(f"📊 Test data max resource: {test_data['resource'].max()}")
    
    # Create main window
    root = tk.Tk()
    root.withdraw()  # Hide main window for testing
    
    try:
        app = MainWindow(root)
        app.current_data = test_data
        app.analysis_mode = 'deterministic'
        
        print("✅ Main window created")
        
        # Initialize CPM analyzer (required for RCPS)
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        app.cmp_analyzer = CPMAnalyzer()
        print("✅ CPM analyzer initialized")
        
        # Set the test data directly since it already has required columns
        app.current_data = test_data
        print(f"✅ Test data set. Shape: {app.current_data.shape}")
        print(f"   Columns: {list(app.current_data.columns)}")
        
        # Create RCPS tab (done on-demand)
        app.show_rcps_tab()
        print("✅ RCPS tab created")
        
        # Check RCPS tab attributes before RCPS analysis
        print(f"🔍 Debugging RCPS tab access:")
        print(f"   - app.rcps_tab exists: {hasattr(app, 'rcps_tab')}")
        print(f"   - app.rcps_tab type: {type(getattr(app, 'rcps_tab', None))}")
        
        rcps_tab = app.rcps_tab
        if rcps_tab is None:
            print("❌ Could not find RCPS tab")
            return False
            
        # Check RCPS tab attributes before RCPS analysis
        print(f"🔍 Before RCPS analysis:")
        print(f"   - rcps_network_graph: {getattr(rcps_tab, 'rcps_network_graph', 'NOT SET')}")
        print(f"   - rcps_analyzer: {getattr(rcps_tab, 'rcps_analyzer', 'NOT SET')}")
        
        # Simulate RCPS analysis
        print("📊 Running RCPS analysis...")
        try:
            # Add some debug prints to trace execution
            import logging
            logging.basicConfig(level=logging.DEBUG)
            
            rcps_tab.resource_limit_var.set(5)
            rcps_tab.priority_rule_var.set("earliest_start")  # Use valid priority rule
            
            # Hook into the run_rcps method to trace execution
            original_run_rcps = rcps_tab.run_rcps
            def debug_run_rcps():
                print("[DEBUG TEST] run_rcps called")
                try:
                    result = original_run_rcps()
                    print("[DEBUG TEST] run_rcps completed normally")
                    return result
                except Exception as e:
                    print(f"[DEBUG TEST] run_rcps exception: {e}")
                    raise
            
            rcps_tab.run_rcps = debug_run_rcps
            rcps_tab.run_rcps()
            print("✅ RCPS analysis completed")
        except Exception as e:
            print(f"❌ RCPS analysis failed: {e}")
            return False
        
        # Check RCPS tab attributes after RCPS analysis
        print(f"🔍 After RCPS analysis:")
        print(f"   - rcps_network_graph: {getattr(rcps_tab, 'rcps_network_graph', 'NOT SET')}")
        print(f"   - rcps_analyzer: {getattr(rcps_tab, 'rcps_analyzer', 'NOT SET')}")
        
        # Test RCPS crashing data access
        print("🎯 Testing RCPS Crashing data access...")
        try:
            rcps_crashing_gui = app.rcps_crashing_tab.gui_manager
            
            # Test the methods that are failing
            try:
                rcps_graph = rcps_crashing_gui.get_rcps_data()
                print(f"✅ get_rcps_data() succeeded: {type(rcps_graph)}")
            except Exception as e:
                print(f"❌ get_rcps_data() failed: {e}")
                return False
                
            try:
                rcps_analyzer = rcps_crashing_gui.get_rcps_analyzer()
                print(f"✅ get_rcps_analyzer() succeeded: {type(rcps_analyzer)}")
            except Exception as e:
                print(f"❌ get_rcps_analyzer() failed: {e}")
                return False
                
            try:
                resource_limit = rcps_crashing_gui.get_resource_limit()
                print(f"✅ get_resource_limit() succeeded: {resource_limit}")
            except Exception as e:
                print(f"❌ get_resource_limit() failed: {e}")
                return False
                
        except Exception as e:
            print(f"❌ RCPS Crashing tab access failed: {e}")
            return False
        
        print("🎉 All tests passed - bug should be fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    finally:
        root.destroy()

if __name__ == "__main__":
    success = test_rcps_crashing_bug()
    print("="*60)
    if success:
        print("✅ TEST PASSED - RCPS Crashing should work correctly")
    else:
        print("❌ TEST FAILED - Bug still exists")
