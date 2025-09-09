#!/usr/bin/env python3
"""
Simple test to verify the RCPS crashing fix with proper attribute values
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from pmhelper.gui.main_window import MainWindow
import tkinter as tk

def test_rcps_crashing_simple():
    """Simple test of the RCPS crashing data fix"""
    print("[DEBUG] Testing RCPS Crashing Data Fix (Simple)")
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
        
        # Debug: Show all IDs to understand the duplication
        print(f"📊 Input data IDs: {input_df['id'].tolist()}")
        
        # Show sample of input data crashing attributes
        if 'min_duration' in input_df.columns and 'crash_cost' in input_df.columns:
            print("📊 Sample input data crashing attributes:")
            for i in range(min(5, len(input_df))):
                row = input_df.iloc[i]
                print(f"   {row['id']}: min_duration={row.get('min_duration')}, crash_cost={row.get('crash_cost')}")
            
            # Check for unique activities only
            unique_df = input_df.drop_duplicates(subset=['id'])
            print(f"📊 Unique activities in input data: {len(unique_df)}")
            print(f"📊 Unique IDs: {unique_df['id'].tolist()}")
        
        # Access RCPS tab (create it if it doesn't exist)
        if app.rcps_tab is None:
            app.show_rcps_tab()  # This should create the RCPS tab
        
        rcps_tab = app.rcps_tab
        
        if rcps_tab is None:
            print("❌ Could not create RCPS tab")
            return
        
        # Create mock RCPS table data (simulate RCPS analysis results)
        # Use all 9 activities to match the input data
        rcps_table_data = pd.DataFrame({
            'id': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
            'duration': [5, 3, 7, 5, 6, 8, 3, 4, 3],
            'early_start': [0, 0, 5, 12, 12, 12, 17, 20, 24],
            'early_finish': [5, 3, 12, 17, 18, 20, 20, 24, 27],
            'actual_start': [0, 0, 5, 12, 12, 12, 17, 20, 24],  # RCPS scheduled start times
            'actual_finish': [5, 3, 12, 17, 18, 20, 20, 24, 27],
            'resource': [2, 1, 3, 1, 4, 5, 2, 1, 2],
        })
        
        # Set the mock data on the RCPS tab
        rcps_tab.rcps_table_data = rcps_table_data
        
        print("✅ Mock RCPS data created")
        
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
                sample_min_duration = crashing_df['min_duration'].tolist()
                sample_crash_cost = crashing_df['crash_cost'].tolist()
                
                # Expected values from sample data (from file_handlers.py)
                expected_min_durations = [1, 2, 5, 4, 3, 5, 3, 2, 2]  # A through I
                expected_crash_costs = [300, 500, 600, 400, 300, 200, 800, 1000, 250]  # A through I
                
                # But we need to account for duplicates in input data, so each value appears twice
                expected_min_durations_with_dups = [1, 1, 2, 2, 5, 5, 4, 4, 3, 3, 5, 5, 3, 3, 2, 2, 2, 2]
                expected_crash_costs_with_dups = [300, 300, 500, 500, 600, 600, 400, 400, 300, 300, 200, 200, 800, 800, 1000, 1000, 250, 250]
                
                print(f"📊 Actual min_duration values: {sample_min_duration}")
                print(f"📊 Expected min_duration values (with dups): {expected_min_durations_with_dups}")
                print(f"📊 Actual crash_cost values: {sample_crash_cost}")
                print(f"📊 Expected crash_cost values (with dups): {expected_crash_costs_with_dups}")
                
                # Check if values match (allowing for type differences)
                min_duration_match = len(sample_min_duration) == len(expected_min_durations_with_dups) and all(float(actual) == float(expected) for actual, expected in zip(sample_min_duration, expected_min_durations_with_dups))
                crash_cost_match = len(sample_crash_cost) == len(expected_crash_costs_with_dups) and all(float(actual) == float(expected) for actual, expected in zip(sample_crash_cost, expected_crash_costs_with_dups))
                
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
    test_rcps_crashing_simple()
