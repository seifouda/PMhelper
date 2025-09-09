#!/usr/bin/env python3
"""
Test script to verify enhanced RCPS crashing cost calculations
"""

def test_enhanced_cost_calculations():
    """Test the enhanced cost calculation formulas"""
    print("Testing Enhanced RCPS Cost Calculations")
    print("="*50)
    
    # Sample activity data
    activities = [
        {'id': 'A', 'duration': 5, 'resource': 2},
        {'id': 'B', 'duration': 3, 'resource': 1},
        {'id': 'C', 'duration': 7, 'resource': 3},
        {'id': 'E', 'duration': 6, 'resource': 4},
        {'id': 'F', 'duration': 8, 'resource': 5},
    ]
    
    print("Enhanced Cost Calculations:")
    print("-" * 30)
    
    total_step_normal_cost = 0
    
    for activity in activities:
        duration = activity['duration']
        resource_count = activity['resource']
        
        # Enhanced formulas
        base_crash_cost = 50 + (resource_count * 25)  # $50 base + $25 per resource unit
        crash_cost_per_unit = base_crash_cost * (1 + duration * 0.1)  # Longer activities cost more to crash
        normal_cost_per_unit = resource_count * 20  # $20 per resource unit per time unit
        
        total_step_normal_cost += normal_cost_per_unit
        
        print(f"Activity {activity['id']}:")
        print(f"  Duration: {duration}, Resources: {resource_count}")
        print(f"  Base crash cost: ${base_crash_cost}")
        print(f"  Crash cost per unit: ${crash_cost_per_unit:.2f}")
        print(f"  Normal cost per unit: ${normal_cost_per_unit}")
        print()
    
    print(f"Total step normal cost (all activities): ${total_step_normal_cost}")
    print()
    
    # Simulate crashing scenario
    print("Simulation: Crashing Activity A from 5 to 4 duration")
    print("-" * 45)
    
    activity_a = activities[0]
    original_duration = activity_a['duration']
    new_duration = 4
    resource_count = activity_a['resource']
    
    # Calculate costs
    base_crash_cost = 50 + (resource_count * 25)
    crash_cost_per_unit = base_crash_cost * (1 + original_duration * 0.1)
    step_normal_cost = total_step_normal_cost  # Cost of running all activities for this step
    
    print(f"Crash cost for reducing A by 1 unit: ${crash_cost_per_unit:.2f}")
    print(f"Step normal cost (all activities): ${step_normal_cost}")
    print(f"Step total cost: ${crash_cost_per_unit + step_normal_cost:.2f}")
    print()
    
    # Compare with old system
    print("Comparison with Old System:")
    print("-" * 30)
    print(f"Old system: Flat $100 crash cost, $0 normal cost")
    print(f"New system: ${crash_cost_per_unit:.2f} crash cost, ${step_normal_cost} normal cost")
    print(f"Improvement: Realistic variable costs based on resources and duration")
    
    return True

if __name__ == "__main__":
    test_enhanced_cost_calculations()
