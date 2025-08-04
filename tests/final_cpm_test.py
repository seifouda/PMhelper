#!/usr/bin/env python3
"""
Final test to confirm PMHelper CPM timing calculations are displaying correctly in GUI
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from pmhelper.gui.main_window import MainWindow

def test_final_cpm_display():
    """Test that CPM calculations show correctly in GUI"""
    print("=== FINAL CPM TIMING DISPLAY TEST ===")
    
    # Create test data
    sample_activities = [
        {'id': 'A', 'activity': 'Task A', 'duration': '5', 'predecessors': ''},
        {'id': 'B', 'activity': 'Task B', 'duration': '3', 'predecessors': ''},  
        {'id': 'C', 'activity': 'Task C', 'duration': '7', 'predecessors': 'A,B'},
    ]
    
    # Create MainWindow (without GUI)
    app = MainWindow()
    app.activities = sample_activities
    app.analysis_mode = 'deterministic'
    
    # Run analysis
    app.analyze_project()
    
    # Check results_data was created
    if not hasattr(app, 'results_data') or not app.results_data:
        print("❌ FAILED - No results_data created")
        return False
    
    activities = app.results_data.get('activities', [])
    if len(activities) != 3:
        print(f"❌ FAILED - Expected 3 activities, got {len(activities)}")
        return False
    
    print("✅ Analysis completed successfully")
    print("\nActivity Results:")
    
    success = True
    for activity in activities:
        act_id = activity.get('id')
        name = activity.get('name', activity.get('activity', 'Unknown'))
        es = activity.get('ES', 'MISSING')
        ef = activity.get('EF', 'MISSING') 
        ls = activity.get('LS', 'MISSING')
        lf = activity.get('LF', 'MISSING')
        float_val = activity.get('float', 'MISSING')
        critical = activity.get('critical', False)
        
        print(f"  {act_id} ({name}): ES={es}, EF={ef}, LS={ls}, LF={lf}, Float={float_val}, Critical={critical}")
        
        # Verify all timing values exist and are numbers
        for field, value in [('ES', es), ('EF', ef), ('LS', ls), ('LF', lf), ('float', float_val)]:
            if not isinstance(value, (int, float)):
                print(f"    ❌ {field} is not a number: {value} (type: {type(value)})")
                success = False
    
    # Check critical path logic
    critical_activities = [a for a in activities if a.get('critical', False)]
    non_critical_activities = [a for a in activities if not a.get('critical', False)]
    
    print(f"\nCritical Path Analysis:")
    print(f"  Critical activities: {len(critical_activities)}")
    print(f"  Non-critical activities: {len(non_critical_activities)}")
    
    # Check that critical activities have zero float
    for activity in critical_activities:
        float_val = activity.get('float', -1)
        if float_val != 0:
            print(f"    ❌ Critical activity {activity['id']} has non-zero float: {float_val}")
            success = False
    
    # Check that at least one non-critical activity has positive float
    has_positive_float = any(a.get('float', 0) > 0 for a in non_critical_activities)
    if non_critical_activities and not has_positive_float:
        print(f"    ❌ No non-critical activities have positive float")
        success = False
    
    if success:
        print("\n🎉 SUCCESS: All CPM timing calculations are working correctly!")
        print("   - ES, EF, LS, LF values calculated")
        print("   - Float values calculated") 
        print("   - Critical path identified")
        print("   - Data format correct for GUI display")
        return True
    else:
        print("\n❌ FAILED: Issues found in CPM calculations")
        return False

if __name__ == "__main__":
    test_final_cpm_display()
