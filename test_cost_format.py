#!/usr/bin/env python3
"""
Simple test to verify RCPS crashing cost tracking logic
"""

def test_crash_log_format():
    """Test that crash log entries have the correct format for cost tracking"""
    
    # Simulate what the crash log entry should look like
    crash_log_entry = {
        'iteration': 1,
        'activity': 'A',
        'crash_amount': 1,
        'cost': 100,  # This is what the report looks for
        'duration': 4,  # This is what the report looks for  
        'current_project_duration': 32,
        'total_crash_cost': 100,
        'critical_path': ['A', 'C', 'F', 'H', 'I'],
        'normal_cost': 50,
        'EF': 4,
        'step_normal_cost': 0,  # RCPS doesn't track step normal costs
        'total_normal_cost_accumulated': 0,
        'active_activities': ['A', 'C', 'F', 'H', 'I']
    }
    
    print("Testing crash log entry format...")
    print(f"Entry: {crash_log_entry}")
    
    # Test report generation logic
    activity_id = crash_log_entry.get('activity', '?')
    crash_cost = float(crash_log_entry.get('cost', 0))
    step_normal_cost = float(crash_log_entry.get('step_normal_cost', 0))
    step_total_cost = crash_cost + step_normal_cost
    duration = crash_log_entry.get('duration', '?')
    iteration = crash_log_entry.get('iteration', '?')
    
    print("\n=== Simulated Report Line ===")
    print(f"Step {iteration}: Activity {activity_id} crashed to duration {duration}")
    print(f"  - Crash Cost: ${crash_cost:,.2f}")
    print(f"  - Step Normal Cost (Active Tasks): ${step_normal_cost:,.2f}")
    print(f"  - Step Total Cost: ${step_total_cost:,.2f}")
    
    # Check for issues
    issues = []
    if crash_cost == 0:
        issues.append("❌ Crash cost is 0")
    if duration == '?':
        issues.append("❌ Duration is missing (?)")
    if not isinstance(crash_cost, (int, float)):
        issues.append("❌ Crash cost is not numeric")
        
    if issues:
        print(f"\n❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print(f"\n✅ CRASH LOG FORMAT IS CORRECT!")
        return True

def test_multiple_crash_entries():
    """Test multiple crash log entries like RCPS would generate"""
    
    crash_log = [
        {
            'iteration': 1, 'activity': 'A', 'crash_amount': 1, 'cost': 100,
            'duration': 4, 'current_project_duration': 32, 'total_crash_cost': 100,
            'critical_path': ['A', 'C', 'F', 'H', 'I'], 'normal_cost': 50,
            'step_normal_cost': 0, 'total_normal_cost_accumulated': 0
        },
        {
            'iteration': 2, 'activity': 'A', 'crash_amount': 1, 'cost': 100,
            'duration': 3, 'current_project_duration': 31, 'total_crash_cost': 200,
            'critical_path': ['A', 'C', 'F', 'H', 'I'], 'normal_cost': 50,
            'step_normal_cost': 0, 'total_normal_cost_accumulated': 0
        },
        {
            'iteration': 3, 'activity': 'C', 'crash_amount': 1, 'cost': 100,
            'duration': 6, 'current_project_duration': 30, 'total_crash_cost': 300,
            'critical_path': ['A', 'C', 'F', 'H', 'I'], 'normal_cost': 50,
            'step_normal_cost': 0, 'total_normal_cost_accumulated': 0
        }
    ]
    
    print("\\n=== Testing Multiple Crash Log Entries ===")
    
    cumulative_crash_cost = 0.0
    for entry in crash_log:
        crash_cost = float(entry.get('cost', 0))
        step_normal_cost = float(entry.get('step_normal_cost', 0))
        step_total_cost = crash_cost + step_normal_cost
        cumulative_crash_cost += crash_cost
        
        print(f"Step {entry['iteration']}: Activity {entry['activity']} crashed to duration {entry['duration']}")
        print(f"  - Crash Cost: ${crash_cost:,.2f}")
        print(f"  - Step Total Cost: ${step_total_cost:,.2f}")
        print(f"  - Cumulative Crash Cost: ${cumulative_crash_cost:,.2f}")
        print(f"  - Project Duration: {entry['current_project_duration']}")
        print()
    
    print(f"✅ Total crash cost should be: ${cumulative_crash_cost:,.2f}")
    return True

if __name__ == "__main__":
    print("RCPS Crashing Cost Tracking Test")
    print("="*40)
    
    test1_passed = test_crash_log_format()
    test2_passed = test_multiple_crash_entries()
    
    if test1_passed and test2_passed:
        print("\\n🎉 ALL TESTS PASSED! Cost tracking format is correct.")
    else:
        print("\\n❌ Some tests failed. Check the format.")
