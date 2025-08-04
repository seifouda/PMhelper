#!/usr/bin/env python3
"""
Test the exact user workflow described:
1. Launch app - should show Mode: CPM with sample data
2. Click "Load CPM Data" - should detect mode and keep it as CPM
3. Run analyze project - should work without errors
"""

import tkinter as tk
import tkinter.filedialog as filedialog
import csv
import sys
import os
sys.path.append('code')
from cpm_app import CPMDesktopApp

# Create a test deterministic CSV file
test_csv_content = """activity,description,duration,predecessors,min_duration,crash_cost,resource_demand,normal_cost
A,Design Phase,5,,1,300,2,100
B,Requirements Analysis,3,,2,500,1,150
C,Architecture Design,7,"A,B",5,600,3,200
D,Database Design,5,C,4,400,1,120
E,Frontend Development,6,C,3,300,4,180
"""

test_csv_path = "test_workflow.csv"

def create_test_csv():
    """Create a test CSV file"""
    with open(test_csv_path, 'w', newline='') as f:
        f.write(test_csv_content)

def test_user_workflow():
    """Test the exact workflow the user described"""
    print("=== Testing User Workflow ===")
    
    # Create test data
    create_test_csv()
    
    # Step 1: Launch app
    print("\n1. Launching application...")
    root = tk.Tk()
    root.withdraw()  # Hide the actual GUI
    app = CPMDesktopApp(root)
    
    print(f"   Initial state after launch:")
    print(f"   - analysis_mode: {app.analysis_mode}")
    print(f"   - mode_label: '{app.mode_label.cget('text')}'")
    print(f"   - activities count: {len(app.get_activities_data())}")
    
    if app.analysis_mode != 'deterministic':
        print("   ❌ ISSUE: Mode should be 'deterministic' but is:", app.analysis_mode)
    else:
        print("   ✅ Mode correctly set to 'deterministic'")
    
    if "Mode: CPM" not in app.mode_label.cget('text'):
        print("   ❌ ISSUE: Label should show 'Mode: CPM' but shows:", app.mode_label.cget('text'))
    else:
        print("   ✅ Label correctly shows 'Mode: CPM'")
    
    # Step 2: Simulate loading CPM data using the auto-detect method
    print("\n2. Simulating 'Load CPM Data' button click...")
    
    # Backup the original filedialog function
    original_askopenfilename = filedialog.askopenfilename
    
    # Mock the file dialog to return our test file
    def mock_filedialog(*args, **kwargs):
        return os.path.abspath(test_csv_path)
    
    filedialog.askopenfilename = mock_filedialog
    
    try:
        # This simulates clicking "Load CPM Data" button
        app.load_csv_auto_detect()
        
        print(f"   State after loading CSV:")
        print(f"   - analysis_mode: {app.analysis_mode}")
        print(f"   - mode_label: '{app.mode_label.cget('text')}'")
        print(f"   - activities count: {len(app.get_activities_data())}")
        
        if app.analysis_mode != 'deterministic':
            print("   ❌ ISSUE: Mode should be 'deterministic' after loading CPM data but is:", app.analysis_mode)
        else:
            print("   ✅ Mode correctly remains 'deterministic' after loading")
            
        if not app.mode_label.cget('text').startswith('Mode: CPM'):
            print("   ❌ ISSUE: Label should show 'Mode: CPM...' but shows:", app.mode_label.cget('text'))
        else:
            print("   ✅ Label correctly shows CPM mode")
            
    except Exception as e:
        print(f"   ❌ ERROR during CSV loading: {e}")
    finally:
        # Restore original filedialog
        filedialog.askopenfilename = original_askopenfilename
    
    # Step 3: Test analyze project
    print("\n3. Testing 'Analyze Project' functionality...")
    
    try:
        # Check conditions before analysis
        print(f"   Pre-analysis checks:")
        print(f"   - analysis_mode is truthy: {bool(app.analysis_mode)}")
        print(f"   - current_analyzer set: {app.current_analyzer is not None}")
        print(f"   - activities available: {len(app.get_activities_data())} activities")
        
        if not app.analysis_mode:
            print("   ❌ CRITICAL: analysis_mode is falsy - this will cause the error!")
            print("   This means analyze_project() will show 'Please load data first' error")
        else:
            print("   ✅ analysis_mode is set correctly")
            
        # Try to run a minimal version of analyze_project logic
        activities_data = app.get_activities_data()
        if not activities_data:
            print("   ❌ No activities data available")
        else:
            print(f"   ✅ {len(activities_data)} activities ready for analysis")
            
    except Exception as e:
        print(f"   ❌ ERROR during analysis test: {e}")
    
    # Cleanup
    root.destroy()
    if os.path.exists(test_csv_path):
        os.remove(test_csv_path)
    
    print("\n=== Workflow Test Complete ===")

if __name__ == "__main__":
    test_user_workflow()
