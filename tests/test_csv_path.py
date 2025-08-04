#!/usr/bin/env python3
"""
Test specifically the CSV loading button path that user reports is broken
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_csv_loading_path():
    """Test the specific CSV loading button that user reports is broken"""
    
    print("=" * 70)
    print("TESTING CSV LOADING PATH - LOAD CPM DATA BUTTON")
    print("=" * 70)
    
    try:
        import tkinter as tk
        from pmhelper.gui.main_window import MainWindow
        
        # Create application
        root = tk.Tk()
        app = MainWindow(root)
        
        print(f"📍 INITIAL STATE:")
        print(f"   MainWindow.analysis_mode: {app.analysis_mode}")
        print(f"   Mode indicator: '{app.mode_indicator.cget('text')}'")
        
        # Test the auto-detection logic directly
        print(f"\n🔍 TEST AUTO-DETECTION LOGIC:")
        
        # CPM headers (what would be in a CPM CSV)
        cpm_headers = ['id', 'activity', 'duration', 'predecessors', 'min_duration', 'crash_cost']
        detected_mode = app.input_tab.auto_detect_mode(cpm_headers)
        print(f"   CPM headers: {cpm_headers}")
        print(f"   Detected mode: {detected_mode}")
        
        # PERT headers (what would be in a PERT CSV)  
        pert_headers = ['id', 'activity', 'optimistic', 'most_likely', 'pessimistic', 'predecessors']
        detected_mode_pert = app.input_tab.auto_detect_mode(pert_headers)
        print(f"   PERT headers: {pert_headers}")
        print(f"   Detected mode: {detected_mode_pert}")
        
        # Test manual mode setting (simulating what CSV loading does)
        print(f"\n🔍 TEST MANUAL MODE SETTING (CSV Path):")
        
        # Clear first (like CSV loading does)
        app.input_tab.clear_all_without_confirmation()
        print(f"   After clear - Mode indicator: '{app.mode_indicator.cget('text')}'")
        
        # Set mode to deterministic (like CSV loading does)
        print("   Setting mode to deterministic...")
        app.input_tab.set_mode('deterministic')
        print(f"   After set_mode - InputTab mode: {app.input_tab.current_mode}")
        print(f"   After set_mode - Mode indicator: '{app.mode_indicator.cget('text')}'")
        
        # Set main window mode (like CSV loading does)
        print("   Setting main window analysis mode...")
        app.set_analysis_mode('deterministic')
        print(f"   After set_analysis_mode - MainWindow mode: {app.analysis_mode}")
        print(f"   After set_analysis_mode - Mode indicator: '{app.mode_indicator.cget('text')}'")
        
        # Test if mode is actually visible/working
        if app.analysis_mode == 'deterministic' and "CPM" in app.mode_indicator.cget('text'):
            print("   ✅ RESULT: Manual mode setting works correctly")
        else:
            print("   ❌ RESULT: Manual mode setting FAILED!")
            
        # Test reset to None and then set again
        print(f"\n🔍 TEST RESET TO NONE THEN SET CPM:")
        app.set_analysis_mode(None)
        print(f"   After reset to None - Mode indicator: '{app.mode_indicator.cget('text')}'")
        
        app.set_analysis_mode('deterministic')
        print(f"   After set to deterministic - Mode indicator: '{app.mode_indicator.cget('text')}'")
        
        if app.analysis_mode == 'deterministic' and "CPM" in app.mode_indicator.cget('text'):
            print("   ✅ RESULT: Reset and set works correctly")
        else:
            print("   ❌ RESULT: Reset and set FAILED!")
        
        root.destroy()
        
        print("\n" + "=" * 70)
        print("CSV LOADING PATH TEST COMPLETED")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_csv_loading_path()
    if success:
        print("\n🔍 Check the results above to identify the CSV loading issue.")
    else:
        print("\n💥 Test failed with errors.")
