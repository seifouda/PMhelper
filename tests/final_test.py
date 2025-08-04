#!/usr/bin/env python3
"""
Final test to confirm PMHelper CPM timing calculations work correctly
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from pmhelper.core.cpm_analyzer import CPMAnalyzer
from pmhelper.core.network_builder import NetworkBuilder

def test_final_cpm_calculations():
    """Test that CPM calculations work correctly end-to-end"""
    print("=== FINAL CPM CALCULATIONS TEST ===")
    
    # Test data - simple project
    activities_data = [
        {'id': 'A', 'activity': 'Task A', 'duration': 5, 'predecessors': []},
        {'id': 'B', 'activity': 'Task B', 'duration': 3, 'predecessors': []},  
        {'id': 'C', 'activity': 'Task C', 'duration': 7, 'predecessors': ['A', 'B']},
    ]
    
    # Create analyzer
    analyzer = CPMAnalyzer()
    
    # Load activities
    analyzer.load_activities_from_data(activities_data)
    print(f"✅ Loaded {len(activities_data)} activities")
    
    # Run analysis  
    result = analyzer.analyze()
    if not result:
        print("❌ FAILED - Analysis returned False")
        return False
    
    # Get network builder
    builder = analyzer.network_builder
    G = builder.G
    
    print("✅ Analysis completed successfully")
    print(f"Project Duration: {result.get('project_duration', 'Unknown')}")
    print(f"Critical Path: {' → '.join(result.get('critical_path', []))}")
    
    print("\nActivity Timing Results:")
    success = True
    
    expected_results = {
        'A': {'ES': 0, 'EF': 5, 'LS': 0, 'LF': 5, 'Float': 0, 'Critical': True},
        'B': {'ES': 0, 'EF': 3, 'LS': 2, 'LF': 5, 'Float': 2, 'Critical': False}, 
        'C': {'ES': 5, 'EF': 12, 'LS': 5, 'LF': 12, 'Float': 0, 'Critical': True},
    }
    
    for activity_id in ['A', 'B', 'C']:
        if activity_id not in G.nodes:
            print(f"❌ Activity {activity_id} not found in graph")
            success = False
            continue
            
        node_data = G.nodes[activity_id]
        expected = expected_results[activity_id]
        
        # Check each timing value
        for field in ['ES', 'EF', 'LS', 'LF']:
            actual = node_data.get(field, 'MISSING')
            expected_val = expected[field]
            if actual != expected_val:
                print(f"❌ {activity_id}.{field}: Expected {expected_val}, got {actual}")
                success = False
        
        # Check float
        actual_float = node_data.get('float', 'MISSING')
        expected_float = expected['Float']
        if actual_float != expected_float:
            print(f"❌ {activity_id}.Float: Expected {expected_float}, got {actual_float}")
            success = False
        
        # Check critical status
        critical_activities = result.get('critical_activities', [])
        is_critical = activity_id in critical_activities
        expected_critical = expected['Critical']
        if is_critical != expected_critical:
            print(f"❌ {activity_id}.Critical: Expected {expected_critical}, got {is_critical}")
            success = False
        
        if success:
            print(f"  ✅ {activity_id}: ES={node_data.get('ES')}, EF={node_data.get('EF')}, LS={node_data.get('LS')}, LF={node_data.get('LF')}, Float={actual_float}, Critical={is_critical}")
    
    if success:
        print("\n🎉 SUCCESS: All CPM timing calculations are perfect!")
        print("   - Forward pass calculations correct")
        print("   - Backward pass calculations correct") 
        print("   - Float calculations correct")
        print("   - Critical path identification correct")
        print("   - Activity B has float=2 (non-critical)")
        print("   - Activities A,C have float=0 (critical)")
        return True
    else:
        print("\n❌ FAILED: Issues found in CPM calculations")
        return False

if __name__ == "__main__":
    test_final_cpm_calculations()
