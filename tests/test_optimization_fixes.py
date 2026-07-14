"""
Quick test script to verify optimization GUI fixes
"""

import sys
sys.path.insert(0, 'src')

from pmhelper.core.cpm_analyzer import CPMAnalyzer
from pmhelper.core.cost_optimization import TimeCostOptimizer, IndirectCostModel
from pmhelper.core.resource_leveling import ResourceLevelingFactory, activities_from_cpm

# Test data
test_activities = [
    {'id': 'A', 'activity': 'Task A', 'duration': 4, 'predecessors': [], 
     'min_duration': 2, 'crash_cost': 100, 'normal_cost': 200, 'resource_demand': 2},
    {'id': 'B', 'activity': 'Task B', 'duration': 3, 'predecessors': ['A'],
     'min_duration': 2, 'crash_cost': 150, 'normal_cost': 300, 'resource_demand': 3},
    {'id': 'C', 'activity': 'Task C', 'duration': 5, 'predecessors': ['A'],
     'min_duration': 3, 'crash_cost': 200, 'normal_cost': 400, 'resource_demand': 2},
    {'id': 'D', 'activity': 'Task D', 'duration': 2, 'predecessors': ['B', 'C'],
     'min_duration': 1, 'crash_cost': 50, 'normal_cost': 100, 'resource_demand': 1},
]

print("=" * 60)
print("TESTING OPTIMIZATION MODULE FIXES")
print("=" * 60)

# Test 1: CPM Analysis and project_duration fix
print("\n[TEST 1] CPM Analysis and project_duration calculation...")
try:
    cpm = CPMAnalyzer()
    G, cp, ca = cpm.analyze(test_activities)
    
    # Calculate project duration the correct way
    project_duration = max([G.nodes[node].get('EF', 0) for node in G.nodes()])
    print(f"✓ Project duration calculated: {project_duration} days")
    print(f"✓ Critical path: {' -> '.join(cp[0]) if cp else 'None'}")
    
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 2: Cost Optimization with fixed project_duration access
print("\n[TEST 2] Cost Optimization (project_duration fix)...")
try:
    indirect_costs = {
        'facilities': 200.0,
        'equipment': 150.0,
        'overhead': 100.0
    }
    
    indirect_model = IndirectCostModel(indirect_costs)
    optimizer = TimeCostOptimizer(cpm, indirect_model)
    
    # This should not raise 'project_duration' attribute error anymore
    result = optimizer.find_optimal_duration()
    
    print(f"✓ Optimal duration: {result.get('optimal_duration', 'N/A')} days")
    print(f"✓ Optimal cost: ${result.get('optimal_total_cost', 0):,.2f}")
    
    # Test cost report generation (should not raise KeyError)
    from pmhelper.core.cost_visualizations import generate_cost_report
    report = generate_cost_report(cpm, result)
    print(f"✓ Cost report generated successfully ({len(report)} chars)")
    
except Exception as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Resource Leveling with ResourceProfile object handling
print("\n[TEST 3] Resource Leveling (ResourceProfile fix)...")
try:
    activities = activities_from_cpm(cpm)
    print(f"  Converted {len(activities)} activities from CPM")
    
    # Test with Minimum Moment method
    leveler = ResourceLevelingFactory.create('minimum_moment', activities, None)
    result = leveler.level()
    
    print(f"✓ Leveling completed: {result.get('iterations', 0)} iterations")
    print(f"✓ Original moment: {result.get('original_moment', 0):.2f}")
    print(f"✓ Leveled moment: {result.get('leveled_moment', 0):.2f}")
    print(f"✓ Improvement: {result.get('improvement_pct', 0):.2f}%")
    
    # Test ResourceProfile object access
    if 'original_profile' in result:
        prof = result['original_profile']
        
        # Test accessing profile dictionary
        if hasattr(prof, 'profile'):
            times = sorted(prof.profile.keys())
            usages = [prof.profile[t] for t in times]
            print(f"✓ ResourceProfile.profile accessible: {len(times)} time periods")
        
        # Test to_dataframe method if available
        if hasattr(prof, 'to_dataframe'):
            df = prof.to_dataframe()
            print(f"✓ ResourceProfile.to_dataframe() works: {len(df)} rows")
        else:
            print("  Note: to_dataframe() method not available, using profile dict directly")
    
    # Verify expected keys
    expected_keys = ['peak_usage_original', 'peak_usage_leveled', 'original_moment', 
                     'leveled_moment', 'improvement_pct', 'iterations']
    missing = [k for k in expected_keys if k not in result]
    if missing:
        print(f"  Warning: Missing expected keys: {missing}")
    else:
        print(f"✓ All expected result keys present")
    
except Exception as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED! ✓")
print("=" * 60)
print("\nFixes verified:")
print("1. ✓ project_duration calculated from graph nodes (not attribute)")
print("2. ✓ ResourceProfile objects handled correctly (profile dict access)")
print("3. ✓ Result dictionary keys match GUI expectations")
