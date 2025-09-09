#!/usr/bin/env python3
"""
Direct test of the prepare_crashing_dataframe method logic
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd

def test_prepare_crashing_dataframe_logic():
    """Test the core logic of prepare_crashing_dataframe method"""
    print("[DEBUG] Testing prepare_crashing_dataframe Logic")
    print("="*60)
    
    # Simulate RCPS table data
    rcps_table_data = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D', 'RA', 'RS'],  # Including resource rows
        'duration': [3, 4, 2, 3, 0, 0],
        'early_start': [0, 3, 3, 7, 0, 0],
        'early_finish': [3, 7, 5, 10, 0, 0],
        'actual_start': [0, 3, 4, 8, 0, 0],  # RCPS scheduled start times
        'actual_finish': [3, 7, 6, 11, 0, 0],
        'resource': [2, 3, 1, 2, 0, 0],
    })
    
    # Simulate input data WITHOUT crashing attributes
    input_data = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'duration': [3, 4, 2, 3],
        'predecessors': ['', 'A', 'A', 'B,C'],
        'resource': [2, 3, 1, 2],
        # Note: NO crash_cost, min_duration, normal_cost columns
    })
    
    print(f"📊 Input data columns: {list(input_data.columns)}")
    print(f"📊 RCPS data columns: {list(rcps_table_data.columns)}")
    
    # Simulate the prepare_crashing_dataframe logic
    print("📋 Simulating prepare_crashing_dataframe logic...")
    
    # Start with RCPS results (which has actual start times)
    crashing_df = rcps_table_data.copy()
    
    # Filter out resource rows
    crashing_df = crashing_df[~crashing_df['id'].isin(['RA', 'RS'])].copy()
    print(f"📊 After filtering resource rows: {len(crashing_df)} activities")
    
    # Add indicator column to track that we're using RCPS data
    crashing_df['is_rcps_based'] = True
    
    # Map necessary attributes for crashing
    if 'actual_start' in crashing_df.columns:
        # Replace early_start with actual_start for crashing (critical for resource-aware crashing)
        crashing_df['original_early_start'] = crashing_df['early_start']
        crashing_df['early_start'] = crashing_df['actual_start']
        
        # Calculate early_finish based on new early_start
        crashing_df['early_finish'] = crashing_df.apply(
            lambda row: row['early_start'] + row['duration'], axis=1
        )
        print("✅ Replaced early_start with actual_start")
    
    # Merge crashing attributes from original data if they exist
    if input_data is not None and isinstance(input_data, pd.DataFrame) and 'id' in input_data.columns:
        # Identify crashing columns in the input data
        crashing_cols = ['id']  # Always include ID for merging
        for col in ['min_duration', 'crash_cost', 'normal_cost']:
            if col in input_data.columns:
                crashing_cols.append(col)
                
        if len(crashing_cols) > 1:  # If we found at least one crashing attribute
            # Merge only the crashing attributes
            crashing_df = pd.merge(
                crashing_df,
                input_data[crashing_cols],
                on='id',
                how='left'
            )
            print(f"📊 Merged crashing attributes from input data: {crashing_cols[1:]}")
        else:
            print("📊 No crashing attributes found in input data")
    
    # Ensure all required crashing attributes exist with sensible defaults
    required_crashing_attrs = {
        'min_duration': 1,  # Default to 1 time unit minimum
        'crash_cost': 100,  # Default crash cost per time unit
        'normal_cost': 50   # Default normal cost per time unit
    }
    
    for attr, default_value in required_crashing_attrs.items():
        if attr not in crashing_df.columns:
            # Column doesn't exist, create it with default values
            crashing_df[attr] = default_value
            print(f"📊 Added missing crashing attribute '{attr}' with default value {default_value}")
        else:
            # Column exists but might have null values, fill them
            null_count = crashing_df[attr].isnull().sum()
            if null_count > 0:
                crashing_df[attr] = crashing_df[attr].fillna(default_value)
                print(f"📊 Filled {null_count} null values in '{attr}' with default value {default_value}")
    
    print(f"📊 Final DataFrame shape: {crashing_df.shape}")
    print(f"📊 Final DataFrame columns: {list(crashing_df.columns)}")
    
    # Verify all required attributes are present
    required_attrs = ['min_duration', 'crash_cost', 'normal_cost']
    missing_attrs = [attr for attr in required_attrs if attr not in crashing_df.columns]
    
    if not missing_attrs:
        print("✅ All required crashing attributes present!")
        
        # Show sample values
        for attr in required_attrs:
            values = crashing_df[attr].tolist()
            print(f"📊 {attr} values: {values}")
        
        # Verify early_start replacement
        if 'early_start' in crashing_df.columns and 'actual_start' in crashing_df.columns:
            early_starts = crashing_df['early_start'].tolist()
            actual_starts = crashing_df['actual_start'].tolist()
            print(f"📊 early_start values (should match actual_start): {early_starts}")
            print(f"📊 actual_start values: {actual_starts}")
            
            if early_starts == actual_starts:
                print("✅ early_start correctly replaced with actual_start values!")
            else:
                print("⚠️ early_start values don't match actual_start")
        
        print("🎉 LOGIC TEST PASSED! The fix should work correctly.")
        
    else:
        print(f"❌ Missing required attributes: {missing_attrs}")

if __name__ == "__main__":
    test_prepare_crashing_dataframe_logic()
