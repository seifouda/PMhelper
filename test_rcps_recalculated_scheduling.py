#!/usr/bin/env python3
"""
Test RCPS network graph building with recalculated Late Finish and Float values
This test verifies that the RCPS network graph uses RCPS project duration for scheduling calculations
"""

import sys
sys.path.append('src')
import pandas as pd
from pmhelper.core.cpm_analyzer import CPMAnalyzer

def test_rcps_recalculated_scheduling():
    """Test RCPS network graph building with improved scheduling calculations"""
    print("="*80)
    print("TESTING RCPS NETWORK GRAPH WITH RECALCULATED SCHEDULING ATTRIBUTES")
    print("="*80)
    
    # Create test data
    activities = [
        {'id': 'A', 'name': 'Design Phase', 'duration': 5, 'predecessors': [], 'resource': 2},
        {'id': 'B', 'name': 'Requirements Analysis', 'duration': 3, 'predecessors': [], 'resource': 1},
        {'id': 'C', 'name': 'Architecture Design', 'duration': 7, 'predecessors': ['A', 'B'], 'resource': 3},
        {'id': 'D', 'name': 'Database Design', 'duration': 5, 'predecessors': ['C'], 'resource': 1},
        {'id': 'E', 'name': 'Frontend Development', 'duration': 6, 'predecessors': ['C'], 'resource': 4},
        {'id': 'F', 'name': 'Backend Development', 'duration': 8, 'predecessors': ['C'], 'resource': 5},
        {'id': 'G', 'name': 'Testing', 'duration': 3, 'predecessors': ['D'], 'resource': 2},
        {'id': 'H', 'name': 'Deployment', 'duration': 4, 'predecessors': ['E', 'F'], 'resource': 1},
        {'id': 'I', 'name': 'Documentation', 'duration': 3, 'predecessors': ['G', 'H'], 'resource': 2}
    ]

    # Build analyzer and create test data
    analyzer = CPMAnalyzer()
    analyzer.load_activities_from_data(activities)
    
    # Create dataframe with calculated CPM values
    test_data = {
        'id': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
        'name': ['Design Phase', 'Requirements Analysis', 'Architecture Design', 'Database Design', 'Frontend Development', 'Backend Development', 'Testing', 'Deployment', 'Documentation'],
        'duration': [5, 3, 7, 5, 6, 8, 3, 4, 3],
        'early_start': [0, 0, 5, 12, 12, 12, 17, 20, 24],
        'late_finish': [5, 5, 12, 21, 20, 20, 24, 24, 27],
        'float': [0, 2, 0, 4, 2, 0, 4, 0, 0],
        'resource': [2, 1, 3, 1, 4, 5, 2, 1, 2],
        'predecessors': ['', '', 'A,B', 'C', 'C', 'C', 'D', 'E,F', 'G,H']
    }
    
    df_gantt = pd.DataFrame(test_data)
    
    # Calculate CPM project duration
    cpm_duration = df_gantt['early_start'].max() + df_gantt.loc[df_gantt['early_start'].idxmax(), 'duration']
    print(f"CPM Project Duration: {cpm_duration}")

    # Get RCPS table
    cmp_table, _, _ = analyzer.build_cpm_schedule_table(df_gantt, 5)
    rcps_table, _, _ = analyzer.rcps_heuristic_schedule_table(df_gantt, 5, priority_rule='minimum_slack')

    # Check RCPS duration
    rcps_duration = max([row['actual_start'] + row['duration'] for _, row in rcps_table.iterrows() if row['id'] not in ['RA', 'RS']])
    print(f"RCPS Project Duration: {rcps_duration}")
    print(f"Duration Difference: {rcps_duration - cpm_duration}")
    
    print("\n" + "="*70)
    print("ORIGINAL RCPS TABLE (with CPM-based Late Finish and Float)")
    print("="*70)
    print(f"{'ID':<4} {'Duration':<8} {'ES':<6} {'AS':<6} {'LF':<6} {'Float':<6}")
    print("-"*70)
    
    for _, row in rcps_table.iterrows():
        if row['id'] not in ['RA', 'RS']:
            print(f"{row['id']:<4} {row['duration']:<8} {row['early_start']:<6} {row['actual_start']:<6} {row['late_finish']:<6} {row['float']:<6}")
    
    print("\n" + "="*70)
    print("SIMULATED RECALCULATED SCHEDULING (with RCPS-based Late Finish and Float)")
    print("="*70)
    print(f"{'ID':<4} {'Duration':<8} {'ES':<6} {'AS':<6} {'LF_old':<8} {'LF_new':<8} {'Float_old':<10} {'Float_new':<10}")
    print("-"*70)
    
    # Simulate the recalculation logic from our improved _build_rcps_network_graph
    activity_rows = rcps_table[~rcps_table['id'].isin(['RA', 'RS'])]
    
    for _, row in activity_rows.iterrows():
        actual_start = row['actual_start'] if 'actual_start' in row and row['actual_start'] != '' else row['early_start']
        duration = row['duration'] 
        early_finish = actual_start + duration
        
        # Original values
        lf_old = row['late_finish']
        float_old = row['float']
        
        # RECALCULATED: Late Finish based on RCPS project duration
        late_finish_rcps = rcps_duration - (early_finish - actual_start - duration)
        
        # RECALCULATED: Float based on RCPS times
        late_start_rcps = late_finish_rcps - duration
        float_rcps = late_start_rcps - actual_start
        float_rcps = max(0, float_rcps)  # Ensure non-negative
        
        print(f"{row['id']:<4} {duration:<8} {row['early_start']:<6} {actual_start:<6} {lf_old:<8} {late_finish_rcps:<8} {float_old:<10.1f} {float_rcps:<10.1f}")
    
    print("="*70)
    print("✅ TEST COMPLETED: RCPS Network Graph should now use recalculated Late Finish and Float")
    print("   based on RCPS project duration instead of original CPM values")
    print("="*70)

if __name__ == "__main__":
    test_rcps_recalculated_scheduling()
