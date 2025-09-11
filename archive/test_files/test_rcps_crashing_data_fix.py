#!/usr/bin/env python3
"""
Test script to v        # Build the p        # Build the project graph and run CPM analysis first 
        try:
            # Convert input data to proper format
            activities_for_analysis = []
            for _, row in input_df.iterrows():
                activity = {
                    'id': row['id'],
                    'activity': row.get('activity', ''),
                    'duration': int(row['duration']),
                    'predecessors': row.get('predecessors', ''),
                    'resource': int(row.get('resource_demand', 1))  # Use resource_demand as resource
                }
                activities_for_analysis.append(activity)
            
            # Run normal CPM analysis
            project_graph, critical_path, project_duration = app.cpm_analyzer.run_cpm_analysis(activities_for_analysis)
            
            print(f"✅ CPM analysis completed: duration={project_duration}")
            
        except Exception as e:
            print(f"❌ CPM analysis failed: {e}")
            return
        
        # Access RCPS tab
        rcps_tab = app.rcps_tab
        
        # Load data into RCPS tab
        rcps_tab.load_data(cpm_analyzer=app.cpm_analyzer, input_data=input_df)aph and run CPM analysis first 
        try:
            # Convert input data to proper format
            activities_for_analysis = []
            for _, row in input_df.iterrows():
                activity = {
                    'id': row['id'],
                    'activity': row.get('activity', ''),
                    'duration': int(row['duration']),
                    'predecessors': row.get('predecessors', ''),
                    'resource': int(row.get('resource_demand', 1))  # Use resource_demand as resource
                }
                activities_for_analysis.append(activity)
            
            # Run normal CPM analysis
            project_graph, critical_path, project_duration = app.cpm_analyzer.run_cpm_analysis(activities_for_analysis)
            
            print(f"✅ CPM analysis completed: duration={project_duration}")
        
        except Exception as e:
            print(f"❌ CPM analysis failed: {e}")
            returnfy the RCPS crashing fix with proper attribute values
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from pmhelper.gui.main_window import MainWindow
import tkinter as tk

def test_rcps_crashing_data_fix():
    """Test that RCPS crashing uses proper attribute values from input data"""
    print("[DEBUG] Testing RCPS Crashing Data Fix")
    print("="*60)
    
    # Create main window
    root = tk.Tk()
    root.withdraw()  # Hide main window for testing
    
    try:
        app = MainWindow(root)
        app.analysis_mode = 'deterministic'
        
        print("✅ Main window created")
        
        # Load sample data which should have proper crashing attributes
        app.input_tab.load_sample_cpm()
        
        # Get the input data to verify what it contains
        input_activities = app.input_tab.get_activities_data()
        input_df = pd.DataFrame(input_activities)
        
        print(f"📊 Input data loaded: {len(input_df)} activities")
        print(f"📊 Input data columns: {list(input_df.columns)}")
        
        # Show sample of input data crashing attributes
        if 'min_duration' in input_df.columns and 'crash_cost' in input_df.columns:
            print("📊 Sample input data crashing attributes:")
            for i in range(min(3, len(input_df))):
                row = input_df.iloc[i]
                print(f"   {row['id']}: min_duration={row.get('min_duration')}, crash_cost={row.get('crash_cost')}")
        
        # Run CPM analysis first
        cpm_table, project_duration, critical_path = app.cpm_analyzer.build_cpm_schedule_table(input_df, resource_limit=5)
        app.current_data = cpm_table
        
        # Access RCPS tab
        rcps_tab = app.rcps_tab
        
        # Load data into RCPS tab
        rcps_tab.load_data(cpm_analyzer=app.cpm_analyzer, input_data=input_df)
        
        # Set resource limit and run RCPS analysis
        rcps_tab.resource_limit_var.set(5)  # Set high resource limit so it's not constraining
        print("📋 Running RCPS analysis...")
        
        # Run RCPS analysis
        rcps_tab.run_rcps_analysis()
        
        if rcps_tab.rcps_table_data is not None:
            print("✅ RCPS analysis completed successfully")
            
            # Test prepare_crashing_dataframe method
            print("📋 Testing prepare_crashing_dataframe...")
            crashing_df = rcps_tab.prepare_crashing_dataframe()
            
            if crashing_df is not None:
                print("✅ prepare_crashing_dataframe succeeded!")
                print(f"📊 Crashing DataFrame columns: {list(crashing_df.columns)}")
                
                # Check the actual values to see if they match input data
                if 'min_duration' in crashing_df.columns and 'crash_cost' in crashing_df.columns:
                    print("📊 Sample crashing data values:")
                    for i in range(min(3, len(crashing_df))):
                        row = crashing_df.iloc[i]
                        print(f"   {row['id']}: min_duration={row.get('min_duration')}, crash_cost={row.get('crash_cost')}")
                    
                    # Check if the values are using the original input data (not defaults)
                    sample_min_duration = crashing_df['min_duration'].tolist()[:3]
                    sample_crash_cost = crashing_df['crash_cost'].tolist()[:3]
                    
                    # Expected values from sample data (from file_handlers.py)
                    expected_min_durations = [1, 2, 5]  # A, B, C
                    expected_crash_costs = [300, 500, 600]  # A, B, C
                    
                    print(f"📊 Actual min_duration values: {sample_min_duration}")
                    print(f"📊 Expected min_duration values: {expected_min_durations}")
                    print(f"📊 Actual crash_cost values: {sample_crash_cost}")
                    print(f"📊 Expected crash_cost values: {expected_crash_costs}")
                    
                    # Check if values match (allowing for type differences)
                    min_duration_match = all(float(actual) == float(expected) for actual, expected in zip(sample_min_duration, expected_min_durations))
                    crash_cost_match = all(float(actual) == float(expected) for actual, expected in zip(sample_crash_cost, expected_crash_costs))
                    
                    if min_duration_match and crash_cost_match:
                        print("🎉 SUCCESS! Crashing attributes are using original input data values!")
                    else:
                        print("❌ FAIL! Crashing attributes are not using original input data values!")
                        if not min_duration_match:
                            print("   - min_duration values don't match")
                        if not crash_cost_match:
                            print("   - crash_cost values don't match")
                else:
                    print("❌ Missing required crashing attributes in DataFrame")
            else:
                print("❌ prepare_crashing_dataframe returned None")
        else:
            print("❌ RCPS analysis failed")
            
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
    test_rcps_crashing_data_fix()
