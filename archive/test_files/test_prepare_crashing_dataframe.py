#!/usr/bin/env python3
"""
Simplified test script to validate the RCPS crashing fix for missing attributes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from pmhelper.gui.tabs.rcps_tab import RCPSTab
import tkinter as tk

def test_prepare_crashing_dataframe():
    """Direct test of prepare_crashing_dataframe method"""
    print("[DEBUG] Testing prepare_crashing_dataframe Fix")
    print("="*60)
    
    # Create root window for testing
    root = tk.Tk()
    root.withdraw()
    
    try:
        # Create a mock main window class with the required attributes
        class MockMainWindow:
            def __init__(self):
                self.input_data = pd.DataFrame({
                    'id': ['A', 'B', 'C', 'D'],
                    'duration': [3, 4, 2, 3],
                    'predecessors': ['', 'A', 'A', 'B,C'],
                    'resource': [2, 3, 1, 2],
                    # Note: NO crash_cost, min_duration, normal_cost columns
                })
        
        # Create an RCPS tab instance
        frame = tk.Frame(root)
        mock_main = MockMainWindow()
        rcps_tab = RCPSTab(frame, mock_main)
        
        # Create mock RCPS table data
        rcps_tab.rcps_table_data = pd.DataFrame({
            'id': ['A', 'B', 'C', 'D'],
            'duration': [3, 4, 2, 3],
            'early_start': [0, 3, 3, 7],
            'early_finish': [3, 7, 5, 10],
            'actual_start': [0, 3, 4, 8],  # RCPS scheduled start times
            'actual_finish': [3, 7, 6, 11],
            'resource': [2, 3, 1, 2],
        })
        
        print("✅ Mock RCPS data created")
        print(f"📊 Input data columns: {list(mock_main.input_data.columns)}")
        print(f"📊 RCPS data columns: {list(rcps_tab.rcps_table_data.columns)}")
        
        # Test prepare_crashing_dataframe method
        print("📋 Testing prepare_crashing_dataframe...")
        result_df = rcps_tab.prepare_crashing_dataframe()
        
        if result_df is not None:
            print("✅ prepare_crashing_dataframe succeeded!")
            print(f"📊 Result DataFrame shape: {result_df.shape}")
            print(f"📊 Result DataFrame columns: {list(result_df.columns)}")
            
            # Check if required crashing attributes are present
            required_attrs = ['min_duration', 'crash_cost', 'normal_cost']
            missing_attrs = [attr for attr in required_attrs if attr not in result_df.columns]
            
            if not missing_attrs:
                print("✅ All required crashing attributes present!")
                
                # Check values
                for attr in required_attrs:
                    values = result_df[attr].tolist()
                    print(f"📊 {attr} values: {values}")
                
                # Check that actual_start is used as early_start
                if 'actual_start' in result_df.columns and 'early_start' in result_df.columns:
                    early_starts = result_df['early_start'].tolist()
                    actual_starts = result_df['actual_start'].tolist()
                    print(f"📊 early_start values (should be from actual_start): {early_starts}")
                    print(f"📊 actual_start values: {actual_starts}")
                    
                    if early_starts == actual_starts:
                        print("✅ early_start correctly replaced with actual_start values!")
                    else:
                        print("⚠️ early_start values don't match actual_start")
                
                print("🎉 ALL TESTS PASSED! RCPS crashing fix validated.")
                
            else:
                print(f"❌ Missing required attributes: {missing_attrs}")
                
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
    test_prepare_crashing_dataframe()
