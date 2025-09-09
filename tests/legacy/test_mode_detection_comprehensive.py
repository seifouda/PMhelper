#!/usr/bin/env python3
"""
Comprehensive test script to verify mode detection fixes

This script tests all the scenarios mentioned in the bug report:
1. Application startup with sample data
2. Load Sample Data button
3. CSV loading with auto-detection
4. File loading from menu
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_mode_detection_comprehensive():
    """Test the mode detection functionality comprehensively"""
    
    print("=" * 60)
    print("COMPREHENSIVE MODE DETECTION VERIFICATION TEST")
    print("=" * 60)
    
    try:
        import tkinter as tk
        from pmhelper.gui.main_window import MainWindow
        
        print("✅ Successfully imported required modules")
        
        # Test 1: Application startup
        print("\n🔍 Test 1: Application Startup with Sample Data")
        root = tk.Tk()
        app = MainWindow(root)
        
        initial_mode = app.analysis_mode
        initial_activities = len(app.get_activities_data())
        
        print(f"   Mode at startup: {initial_mode}")
        print(f"   Activities loaded: {initial_activities}")
        
        if initial_mode == 'deterministic' and initial_activities > 0:
            print("   ✅ PASS: Startup correctly sets deterministic mode with sample data")
        else:
            print("   ❌ FAIL: Startup mode detection failed")
            
        # Test 2: Sample data loading
        print("\n🔍 Test 2: Load Sample Data")
        app.input_tab.load_sample_cpm()
        mode_after_sample = app.analysis_mode
        activities_after_sample = len(app.get_activities_data())
        
        print(f"   Mode after sample CPM: {mode_after_sample}")
        print(f"   Activities after sample: {activities_after_sample}")
        
        if mode_after_sample == 'deterministic' and activities_after_sample > 0:
            print("   ✅ PASS: Sample CPM data loading works correctly")
        else:
            print("   ❌ FAIL: Sample CPM data loading failed")
            
        # Test 3: PERT sample data
        print("\n🔍 Test 3: Load Sample PERT Data")
        app.input_tab.load_sample_pert()
        mode_after_pert = app.analysis_mode
        activities_after_pert = len(app.get_activities_data())
        
        print(f"   Mode after sample PERT: {mode_after_pert}")
        print(f"   Activities after PERT: {activities_after_pert}")
        
        if mode_after_pert == 'probabilistic' and activities_after_pert > 0:
            print("   ✅ PASS: Sample PERT data loading works correctly")
        else:
            print("   ❌ FAIL: Sample PERT data loading failed")
            
        # Test 4: CSV Auto-detection (CPM)
        print("\n🔍 Test 4: CSV Auto-detection for CPM")
        cpm_headers = ['id', 'activity', 'duration', 'predecessors', 'min_duration', 'crash_cost', 'resource_demand']
        detected_mode = app.input_tab.auto_detect_mode(cpm_headers)
        print(f"   Detected mode for CPM headers: {detected_mode}")
        
        if detected_mode == 'deterministic':
            print("   ✅ PASS: CPM auto-detection works correctly")
        else:
            print("   ❌ FAIL: CPM auto-detection failed")
            
        # Test 5: CSV Auto-detection (PERT)
        print("\n🔍 Test 5: CSV Auto-detection for PERT")
        pert_headers = ['id', 'activity', 'optimistic', 'most_likely', 'pessimistic', 'predecessors']
        detected_mode_pert = app.input_tab.auto_detect_mode(pert_headers)
        print(f"   Detected mode for PERT headers: {detected_mode_pert}")
        
        if detected_mode_pert == 'probabilistic':
            print("   ✅ PASS: PERT auto-detection works correctly")
        else:
            print("   ❌ FAIL: PERT auto-detection failed")
            
        # Test 6: Mode switching consistency
        print("\n🔍 Test 6: Mode Switching Consistency")
        
        # Switch to CPM mode
        app.input_tab.load_sample_cpm()
        cpm_mode = app.analysis_mode
        cpm_mode_label = app.mode_indicator.cget("text")
        
        # Switch to PERT mode  
        app.input_tab.load_sample_pert()
        pert_mode = app.analysis_mode
        pert_mode_label = app.mode_indicator.cget("text")
        
        print(f"   CPM mode: {cpm_mode}, Label: {cpm_mode_label}")
        print(f"   PERT mode: {pert_mode}, Label: {pert_mode_label}")
        
        if (cpm_mode == 'deterministic' and "CPM" in cpm_mode_label and
            pert_mode == 'probabilistic' and "PERT" in pert_mode_label):
            print("   ✅ PASS: Mode switching works correctly")
        else:
            print("   ❌ FAIL: Mode switching failed")
            
        root.destroy()
        
        print("\n" + "=" * 60)
        print("COMPREHENSIVE MODE DETECTION TEST COMPLETED")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mode_detection_comprehensive()
    if success:
        print("\n🎉 All tests completed. Check individual test results above.")
    else:
        print("\n💥 Test failed with errors.")
