#!/usr/bin/env python3
"""
Test RCPS Debug Output Fixes
Validates the improvements to debug output formatting and calculations.
"""

import sys
import pandas as pd
from pathlib import Path

# Add the src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from pmhelper.core.rcps_analyzer import RCPSAnalyzer

def test_rcps_debug_output():
    """Test RCPS analysis with improved debug output"""
    
    print("🧪 Testing RCPS Debug Output Fixes")
    print("="*60)
    
    # Sample project data for testing
    test_data = [
        {'id': 'A', 'duration': 5, 'predecessors': [], 'resource': 1, 'min_duration': 1, 'crash_cost': 300},
        {'id': 'B', 'duration': 3, 'predecessors': [], 'resource': 1, 'min_duration': 2, 'crash_cost': 500},
        {'id': 'C', 'duration': 7, 'predecessors': ['A'], 'resource': 1, 'min_duration': 5, 'crash_cost': 600},
        {'id': 'D', 'duration': 5, 'predecessors': ['C'], 'resource': 1, 'min_duration': 4, 'crash_cost': 400},
        {'id': 'E', 'duration': 6, 'predecessors': ['C'], 'resource': 1, 'min_duration': 3, 'crash_cost': 300},
        {'id': 'F', 'duration': 8, 'predecessors': ['B'], 'resource': 1, 'min_duration': 5, 'crash_cost': 200},
        {'id': 'G', 'duration': 3, 'predecessors': ['D', 'E'], 'resource': 1, 'min_duration': 3, 'crash_cost': 800},
        {'id': 'H', 'duration': 4, 'predecessors': ['F'], 'resource': 1, 'min_duration': 2, 'crash_cost': 1000},
        {'id': 'I', 'duration': 3, 'predecessors': ['G', 'H'], 'resource': 1, 'min_duration': 2, 'crash_cost': 250}
    ]
    
    # Create DataFrame
    df_gantt = pd.DataFrame(test_data)
    resource_limit = 1
    
    print("📊 Input Data:")
    print(df_gantt[['id', 'duration', 'predecessors', 'resource', 'min_duration', 'crash_cost']])
    print()
    
    # Create analyzer and run RCPS analysis
    analyzer = RCPSAnalyzer()
    
    try:
        print("🔍 Running RCPS Analysis...")
        
        # Build CPM and RCPS schedules
        cmp_table, _, _ = analyzer.build_cmp_schedule_table(df_gantt, resource_limit)
        rcps_table, _, _ = analyzer.rcps_heuristic_schedule_table(df_gantt, resource_limit, priority_rule="SPT")
        
        print("\n📋 RCPS Table Results:")
        print(rcps_table[['id', 'duration', 'early_start', 'actual_start', 'late_finish', 'float']])
        
        print("\n✅ RCPS Analysis completed successfully!")
        print("The debug output above shows the improved formatting and calculations.")
        
    except Exception as e:
        print(f"❌ Error during RCPS analysis: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_rcps_debug_output()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
