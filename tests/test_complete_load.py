#!/usr/bin/env python3
"""
Test the complete load_csv_auto_detect method with exception handling
"""

import tkinter as tk
import tkinter.filedialog as filedialog
import csv
import sys
import os
sys.path.append('code')
from cpm_app import CPMDesktopApp

# Create a test CSV
test_csv_content = """id,activity,duration,predecessors,min_duration,crash_cost,resource_demand,normal_cost
A,Design Phase,5,,1,300,2,100
B,Requirements Analysis,3,,2,500,1,150
C,Architecture Design,7,"A,B",5,600,3,200
"""

test_csv_path = "complete_test.csv"

def test_complete_load_csv_auto_detect():
    """Test the complete load_csv_auto_detect method"""
    # Create test CSV
    with open(test_csv_path, 'w', newline='') as f:
        f.write(test_csv_content)
    
    root = tk.Tk()
    root.withdraw()
    app = CPMDesktopApp(root)
    
    print("=== Testing Complete load_csv_auto_detect Method ===")
    
    # Mock the file dialog
    original_askopenfilename = filedialog.askopenfilename
    def mock_filedialog(*args, **kwargs):
        return os.path.abspath(test_csv_path)
    filedialog.askopenfilename = mock_filedialog
    
    try:
        print(f"Before load_csv_auto_detect:")
        print(f"  - mode: {app.analysis_mode}")
        print(f"  - activities: {len(app.get_activities_data())}")
        
        # Call the actual method
        app.load_csv_auto_detect()
        
        print(f"After load_csv_auto_detect:")
        print(f"  - mode: {app.analysis_mode}")
        print(f"  - mode_label: '{app.mode_label.cget('text')}'")
        print(f"  - activities: {len(app.get_activities_data())}")
        
        # Test if analyze_project would work
        print(f"\nTesting analyze_project conditions:")
        print(f"  - analysis_mode truthy: {bool(app.analysis_mode)}")
        if not app.analysis_mode:
            print("  ❌ This would trigger 'Please load data first' error")
        else:
            print("  ✅ Mode check would pass")
            
        activities_data = app.get_activities_data()
        if not activities_data:
            print("  ❌ No activities - would trigger 'Please enter some activities' error")
        else:
            print(f"  ✅ {len(activities_data)} activities available for analysis")
            
            # Print first few activities for verification
            for i, activity in enumerate(activities_data[:3]):
                print(f"    Activity {i+1}: {activity}")
        
    except Exception as e:
        print(f"ERROR in load_csv_auto_detect: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        filedialog.askopenfilename = original_askopenfilename
        root.destroy()
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)

if __name__ == "__main__":
    test_complete_load_csv_auto_detect()
