#!/usr/bin/env python3
"""
Test script to reproduce the specific mode detection issue:
- Load CPM data first (mode should change to CPM but doesn't)
- Load PERT data (mode changes to PERT - works)
- Load CPM data again (mode changes to CPM - works)
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_specific_mode_issue():
    """Test the specific mode detection issue described by user"""
    
    print("=" * 70)
    print("REPRODUCING SPECIFIC MODE DETECTION ISSUE")
    print("=" * 70)
    
    try:
        import tkinter as tk
        from pmhelper.gui.main_window import MainWindow
        
        print("✅ Successfully imported required modules")
        
        # Create application
        root = tk.Tk()
        app = MainWindow(root)
        
        # Check initial state
        print(f"\n📍 INITIAL STATE:")
        print(f"   MainWindow.analysis_mode: {app.analysis_mode}")
        print(f"   InputTab.current_mode: {app.input_tab.current_mode}")
        print(f"   Mode indicator text: {app.mode_indicator.cget('text')}")
        print(f"   Input tab mode label: {app.input_tab.mode_label.cget('text')}")
        
        # Test 1: Load CPM data first (this should work but user says it doesn't)
        print(f"\n🔍 TEST 1: Load CPM Data (User reports this doesn't work)")
        app.input_tab.load_sample_cpm()
        
        print(f"   After load_sample_cmp():")
        print(f"   MainWindow.analysis_mode: {app.analysis_mode}")
        print(f"   InputTab.current_mode: {app.input_tab.current_mode}")
        print(f"   Mode indicator text: {app.mode_indicator.cget('text')}")
        print(f"   Input tab mode label: {app.input_tab.mode_label.cget('text')}")
        
        if app.analysis_mode == 'deterministic' and "CPM" in app.mode_indicator.cget('text'):
            print("   ✅ RESULT: CPM mode set correctly")
        else:
            print("   ❌ RESULT: CPM mode NOT set correctly - REPRODUCED ISSUE!")
        
        # Test 2: Load PERT data (user says this works)
        print(f"\n🔍 TEST 2: Load PERT Data (User reports this works)")
        app.input_tab.load_sample_pert()
        
        print(f"   After load_sample_pert():")
        print(f"   MainWindow.analysis_mode: {app.analysis_mode}")
        print(f"   InputTab.current_mode: {app.input_tab.current_mode}")
        print(f"   Mode indicator text: {app.mode_indicator.cget('text')}")
        print(f"   Input tab mode label: {app.input_tab.mode_label.cget('text')}")
        
        if app.analysis_mode == 'probabilistic' and "PERT" in app.mode_indicator.cget('text'):
            print("   ✅ RESULT: PERT mode set correctly")
        else:
            print("   ❌ RESULT: PERT mode NOT set correctly")
        
        # Test 3: Load CPM data again (user says this works after loading PERT first)
        print(f"\n🔍 TEST 3: Load CPM Data Again (User reports this works after PERT)")
        app.input_tab.load_sample_cpm()
        
        print(f"   After second load_sample_cpm():")
        print(f"   MainWindow.analysis_mode: {app.analysis_mode}")
        print(f"   InputTab.current_mode: {app.input_tab.current_mode}")
        print(f"   Mode indicator text: {app.mode_indicator.cget('text')}")
        print(f"   Input tab mode label: {app.input_tab.mode_label.cget('text')}")
        
        if app.analysis_mode == 'deterministic' and "CPM" in app.mode_indicator.cget('text'):
            print("   ✅ RESULT: CPM mode set correctly after PERT")
        else:
            print("   ❌ RESULT: CPM mode NOT set correctly after PERT")
        
        # Test 4: Reset and try with fresh app instance to simulate CSV loading
        print(f"\n🔍 TEST 4: Fresh App - Simulate CSV Loading Issue")
        root.destroy()
        
        # Create new instance
        root2 = tk.Tk()
        app2 = MainWindow(root2)
        
        print(f"   Fresh app initial state:")
        print(f"   MainWindow.analysis_mode: {app2.analysis_mode}")
        print(f"   InputTab.current_mode: {app2.input_tab.current_mode}")
        print(f"   Mode indicator text: {app2.mode_indicator.cget('text')}")
        
        # Simulate CSV loading by calling the auto-detect method
        app2.input_tab.clear_all_without_confirmation()
        app2.input_tab.set_mode('deterministic')  # This is what CSV loading does
        app2.set_analysis_mode('deterministic')  # This is what CSV loading does
        
        print(f"   After simulated CSV loading:")
        print(f"   MainWindow.analysis_mode: {app2.analysis_mode}")
        print(f"   InputTab.current_mode: {app2.input_tab.current_mode}")
        print(f"   Mode indicator text: {app2.mode_indicator.cget('text')}")
        print(f"   Input tab mode label: {app2.input_tab.mode_label.cget('text')}")
        
        if app2.analysis_mode == 'deterministic' and "CPM" in app2.mode_indicator.cget('text'):
            print("   ✅ RESULT: CSV CPM loading simulation works correctly")
        else:
            print("   ❌ RESULT: CSV CPM loading simulation FAILED - ISSUE REPRODUCED!")
        
        root2.destroy()
        
        print("\n" + "=" * 70)
        print("ISSUE REPRODUCTION TEST COMPLETED")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_specific_mode_issue()
    if success:
        print("\n🔍 Check the results above to see if the issue was reproduced.")
    else:
        print("\n💥 Test failed with errors.")
