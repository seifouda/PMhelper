#!/usr/bin/env python3
"""
Test Float Calculation Fix

Test script to verify that CPM analysis correctly calculates float values
for non-critical activities.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from pmhelper.core.cpm_analyzer import CPMAnalyzer


def test_float_calculation():
    """Test float calculation with known expected results"""
    print("=" * 80)
    print("FLOAT CALCULATION TEST")
    print("=" * 80)
    
    # Test case with known float values
    # Expected: A→C→D = 8 days (critical path)
    # Expected: A→B→D = 6 days (non-critical, 2 days slack)
    # Activity B should have float = 2 days
    test_activities = [
        {'id': 'A', 'duration': 3, 'predecessors': []},           # Should be critical
        {'id': 'B', 'duration': 2, 'predecessors': ['A']},       # Should have float = 2
        {'id': 'C', 'duration': 4, 'predecessors': ['A']},       # Should be critical  
        {'id': 'D', 'duration': 1, 'predecessors': ['B', 'C']},  # Should be critical
    ]
    
    print("Test Activities:")
    for act in test_activities:
        print(f"  {act['id']}: Duration={act['duration']}, Predecessors={act['predecessors']}")
    
    print("\nExpected Results:")
    print("  Critical Path: A→C→D (8 days)")
    print("  Non-critical Path: A→B→D (6 days)")
    print("  Activity A: Float = 0 (critical)")
    print("  Activity B: Float = 2 (non-critical)")  
    print("  Activity C: Float = 0 (critical)")
    print("  Activity D: Float = 0 (critical)")
    
    # Run CPM analysis
    print("\n" + "="*50)
    print("RUNNING CPM ANALYSIS")
    print("="*50)
    
    analyzer = CPMAnalyzer()
    G, critical_paths, critical_activities = analyzer.analyze(test_activities)
    
    print(f"\nCritical Path: {critical_paths[0] if critical_paths else 'None'}")
    print(f"Critical Activities: {critical_activities}")
    
    print("\nDetailed Node Data:")
    for node in ['START', 'A', 'B', 'C', 'D', 'END']:
        if G.has_node(node):
            node_data = G.nodes[node]
            es = node_data.get('ES', 0)
            ef = node_data.get('EF', 0)
            ls = node_data.get('LS', 0)
            lf = node_data.get('LF', 0)
            float_val = node_data.get('float', 0)
            duration = node_data.get('duration', 0)
            is_critical = node in critical_activities
            
            print(f"  {node}: ES={es}, EF={ef}, LS={ls}, LF={lf}, Float={float_val}, Duration={duration}, Critical={is_critical}")
    
    # Validate results
    print("\n" + "="*50)
    print("VALIDATION")
    print("="*50)
    
    success = True
    
    # Check Activity A (should be critical, float=0)
    if G.has_node('A'):
        a_float = G.nodes['A'].get('float', -1)
        a_critical = 'A' in critical_activities
        if a_float == 0 and a_critical:
            print("✅ Activity A: Float=0, Critical=True (PASS)")
        else:
            print(f"❌ Activity A: Float={a_float}, Critical={a_critical} (FAIL)")
            success = False
    
    # Check Activity B (should be non-critical, float=2)
    if G.has_node('B'):
        b_float = G.nodes['B'].get('float', -1)
        b_critical = 'B' in critical_activities
        if b_float == 2 and not b_critical:
            print("✅ Activity B: Float=2, Critical=False (PASS)")
        else:
            print(f"❌ Activity B: Float={b_float}, Critical={b_critical} (FAIL)")
            success = False
    
    # Check Activity C (should be critical, float=0)
    if G.has_node('C'):
        c_float = G.nodes['C'].get('float', -1)
        c_critical = 'C' in critical_activities
        if c_float == 0 and c_critical:
            print("✅ Activity C: Float=0, Critical=True (PASS)")
        else:
            print(f"❌ Activity C: Float={c_float}, Critical={c_critical} (FAIL)")
            success = False
    
    # Check Activity D (should be critical, float=0)
    if G.has_node('D'):
        d_float = G.nodes['D'].get('float', -1)
        d_critical = 'D' in critical_activities
        if d_float == 0 and d_critical:
            print("✅ Activity D: Float=0, Critical=True (PASS)")
        else:
            print(f"❌ Activity D: Float={d_float}, Critical={d_critical} (FAIL)")
            success = False
    
    # Check total system float
    total_float = sum(G.nodes[node].get('float', 0) for node in G.nodes() if node not in ['START', 'END'])
    if total_float > 0:
        print(f"✅ Total System Float: {total_float} > 0 (PASS)")
    else:
        print(f"❌ Total System Float: {total_float} = 0 (FAIL)")
        success = False
    
    print("\n" + "="*80)
    if success:
        print("🎉 ALL TESTS PASSED - Float calculation working correctly!")
    else:
        print("❌ TESTS FAILED - Float calculation needs debugging")
    print("="*80)
    
    return success


def test_complex_network():
    """Test float calculations in a more complex network"""
    print("\n" + "="*80)
    print("COMPLEX NETWORK TEST")
    print("="*80)
    
    # More complex test case with multiple non-critical paths
    complex_activities = [
        {'id': 'A', 'duration': 4, 'predecessors': []},
        {'id': 'B', 'duration': 2, 'predecessors': []},          # Should have float
        {'id': 'C', 'duration': 3, 'predecessors': ['A']},       # Should be critical
        {'id': 'D', 'duration': 1, 'predecessors': ['B']},       # Should have float
        {'id': 'E', 'duration': 2, 'predecessors': ['C', 'D']},  # Should be critical
    ]
    
    print("Complex Activities:")
    for act in complex_activities:
        print(f"  {act['id']}: Duration={act['duration']}, Predecessors={act['predecessors']}")
    
    print("\nExpected Results:")
    print("  Critical Path: A→C→E (9 days)")
    print("  Non-critical Path: B→D→E (5 days)")
    print("  Activities B and D should have float > 0")
    
    # Run analysis
    analyzer = CPMAnalyzer()
    G, critical_paths, critical_activities = analyzer.analyze(complex_activities)
    
    print(f"\nCritical Path: {critical_paths[0] if critical_paths else 'None'}")
    print(f"Critical Activities: {critical_activities}")
    
    # Check for non-critical activities with float > 0
    non_critical_count = 0
    total_float = 0
    
    print("\nActivity Analysis:")
    for node in G.nodes():
        if node not in ['START', 'END']:
            float_val = G.nodes[node].get('float', 0)
            is_critical = node in critical_activities
            total_float += float_val
            
            if not is_critical and float_val > 0:
                non_critical_count += 1
                print(f"  ✅ {node}: Float={float_val} (Non-critical with positive float)")
            elif is_critical and float_val == 0:
                print(f"  ✅ {node}: Float={float_val} (Critical activity)")
            else:
                print(f"  ❌ {node}: Float={float_val}, Critical={is_critical} (Unexpected)")
    
    success = non_critical_count >= 2 and total_float > 0
    
    print(f"\nSummary:")
    print(f"  Non-critical activities with float > 0: {non_critical_count}")
    print(f"  Total system float: {total_float}")
    print(f"  Test Result: {'PASS' if success else 'FAIL'}")
    
    return success


if __name__ == "__main__":
    print("Testing PMHelper Float Calculation Fix...")
    
    test1_result = test_float_calculation()
    test2_result = test_complex_network()
    
    print("\n" + "="*80)
    print("FINAL TEST RESULTS")
    print("="*80)
    print(f"Simple Network Test: {'PASS' if test1_result else 'FAIL'}")
    print(f"Complex Network Test: {'PASS' if test2_result else 'FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED!")
        print("Float calculation is working correctly.")
    else:
        print("\n❌ TESTS FAILED!")
        print("Float calculation needs to be fixed.")
    print("="*80)
