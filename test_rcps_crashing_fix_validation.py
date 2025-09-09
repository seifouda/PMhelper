#!/usr/bin/env python3
"""
Test script            print("✅ Main window created")
        
        # Debug what attributes are available
        print(f"[DEBUG] Available attributes: {[attr for attr in dir(app) if 'analyzer' in attr.lower()]}")
        
        # Initialize CPM analyzer (required for RCPS)
        if hasattr(app, 'cpm_analyzer'):
            print("✅ CPM analyzer found")
            # Build CPM schedule table to get properly formatted data
            cpm_table, project_duration, critical_path = app.cpm_analyzer.build_cpm_schedule_table(test_data, resource_limit=5)
            app.current_data = cpm_table
            print("✅ CPM analysis completed")nitialize CPM analyzer (required for RCPS)
        if hasattr(app, 'cpm_analyzer'):
            # Build CPM schedule table to get properly formatted data
            cpm_table, project_duration, critical_path = app.cpm_analyzer.build_cpm_schedule_table(test_data, resource_limit=5)
            app.current_data = cpm_table
            print("✅ CPM analysis completed")idate the RCPS crashing fix for missing attributes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from pmhelper.gui.main_window import MainWindow
import tkinter as tk

def test_rcps_crashing_missing_attributes():
    """Test RCPS crashing with data missing crashing attributes"""
    print("[DEBUG] Testing RCPS Crashing Fix for Missing Attributes")
    print("="*60)
    
    # Create test data WITHOUT crashing attributes (simulating real user data)
    test_data = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'duration': [3, 4, 2, 3],
        'predecessors': ['', 'A', 'A', 'B,C'],
        'resource': [2, 3, 1, 2],  # Max resource is 3
        # Note: NO crash_cost, min_duration, normal_cost columns
    })
    
    print(f"📊 Test data columns: {list(test_data.columns)}")
    print(f"📊 Missing crashing attributes: min_duration, crash_cost, normal_cost")
    
    # Create main window
    root = tk.Tk()
    root.withdraw()  # Hide main window for testing
    
    try:
        app = MainWindow(root)
        app.input_data = test_data  # Set as input data
        app.analysis_mode = 'deterministic'
        
        print("✅ Main window created")
        
        # Initialize CPM analyzer (required for RCPS)
        if hasattr(app, 'cmp_analyzer'):
            # Build CPM schedule table to get properly formatted data
            cpm_table, project_duration, critical_path = app.cmp_analyzer.build_cpm_schedule_table(test_data, resource_limit=5)
            app.current_data = cpm_table
            print("✅ CPM analysis completed")
            
            # Access RCPS tab and RCPS Crashing tab
            rcps_tab = app.rcps_tab
            rcps_crashing_tab = app.rcps_crashing_tab_manager
            
            # Simulate loading data into RCPS tab
            rcps_tab.load_data(cpm_analyzer=app.cpm_analyzer, input_data=test_data)
            
            # Set the resource limit and run RCPS analysis
            rcps_tab.resource_limit_var.set(3)  # Set resource limit to 3
            print("📋 Running RCPS analysis...")
            
            # Run RCPS analysis
            rcps_tab.run_rcps_analysis()
            
            # Check if RCPS analysis succeeded
            if rcps_tab.rcps_table_data is not None:
                print("✅ RCPS analysis completed successfully")
                print(f"📊 RCPS table shape: {rcps_tab.rcps_table_data.shape}")
                
                # Test prepare_crashing_dataframe method
                print("📋 Testing prepare_crashing_dataframe with missing attributes...")
                crashing_df = rcps_tab.prepare_crashing_dataframe()
                
                if crashing_df is not None:
                    print("✅ prepare_crashing_dataframe succeeded!")
                    print(f"📊 Crashing DataFrame shape: {crashing_df.shape}")
                    print(f"📊 Crashing DataFrame columns: {list(crashing_df.columns)}")
                    
                    # Check if required crashing attributes are present
                    required_attrs = ['min_duration', 'crash_cost', 'normal_cost']
                    missing_attrs = [attr for attr in required_attrs if attr not in crashing_df.columns]
                    
                    if not missing_attrs:
                        print("✅ All required crashing attributes present!")
                        print(f"📊 min_duration values: {crashing_df['min_duration'].tolist()}")
                        print(f"📊 crash_cost values: {crashing_df['crash_cost'].tolist()}")
                        print(f"📊 normal_cost values: {crashing_df['normal_cost'].tolist()}")
                        
                        # Now test RCPS crashing functionality
                        print("📋 Testing RCPS crashing analysis...")
                        
                        # Set up bidirectional references
                        rcps_tab.set_rcps_crashing_tab(rcps_crashing_tab)
                        rcps_crashing_tab.set_rcps_tab_reference(rcps_tab)
                        
                        # Test the get_rcps_data method in crashing tab
                        rcps_data = rcps_crashing_tab.get_rcps_data()
                        
                        if rcps_data is not None:
                            print("✅ RCPS Crashing data retrieval succeeded!")
                            print(f"📊 Retrieved data shape: {rcps_data.shape}")
                            print("🎉 ALL TESTS PASSED! RCPS crashing fix validated.")
                        else:
                            print("❌ RCPS Crashing data retrieval failed")
                            
                    else:
                        print(f"❌ Missing required attributes: {missing_attrs}")
                        
                else:
                    print("❌ prepare_crashing_dataframe returned None")
                    
            else:
                print("❌ RCPS analysis failed")
                
        else:
            print("❌ CPM analyzer not available")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    test_rcps_crashing_missing_attributes()
