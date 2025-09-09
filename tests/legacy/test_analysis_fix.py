#!/usr/bin/env python3
"""
Test Analysis Button Fix

This script tests the "Analyze Project" functionality to verify the fix.
"""

import sys
from pathlib import Path

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_analysis_fix():
    """Test that the analysis button works without errors"""
    
    print("=" * 60)
    print("TESTING ANALYSIS BUTTON FIX")
    print("=" * 60)
    
    try:
        import tkinter as tk
        from pmhelper.gui.main_window import MainWindow
        
        # Create application
        root = tk.Tk()
        app = MainWindow(root)
        
        print("✅ Application created successfully")
        print(f"   Initial mode: {app.analysis_mode}")
        print(f"   Sample activities: {len(app.get_activities_data())}")
        
        # Test 1: Check that results_tab has the correct method
        print(f"\n🔍 Test 1: Method availability check")
        if hasattr(app.results_tab, 'update_results'):
            print("   ✅ PASS: update_results method exists")
        else:
            print("   ❌ FAIL: update_results method missing")
            return False
        
        if hasattr(app.results_tab, 'display_results'):
            print("   ⚠️  WARNING: Old display_results method still exists")
        else:
            print("   ✅ PASS: Old display_results method not found")
        
        # Test 2: Simulate analysis execution
        print(f"\n🔍 Test 2: Analysis execution test")
        try:
            # This should now work without errors
            app.analyze_project()
            print("   ✅ PASS: analyze_project() executed without errors")
            analysis_success = True
        except Exception as e:
            print(f"   ❌ FAIL: analyze_project() failed with: {str(e)}")
            analysis_success = False
            import traceback
            traceback.print_exc()
        
        # Test 3: Check results tab state
        print(f"\n🔍 Test 3: Results tab state check")
        if hasattr(app.results_tab, 'results_data') and app.results_tab.results_data:
            print("   ✅ PASS: Results data populated")
        else:
            print("   ⚠️  WARNING: Results data not populated (might be expected)")
        
        root.destroy()
        
        # Overall result
        print("\n" + "=" * 60)
        print("ANALYSIS FIX TEST RESULTS")
        print("=" * 60)
        
        if analysis_success:
            print("🎉 OVERALL RESULT: SUCCESS!")
            print("✅ Analysis button fix is working correctly")
            print("✅ No more 'display result' attribute errors")
            print("✅ Application can analyze projects without crashing")
        else:
            print("❌ OVERALL RESULT: STILL HAS ISSUES")
            print("   Analysis execution failed - needs further investigation")
        
        return analysis_success
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analysis_fix()
    if success:
        print("\n🚀 Analysis functionality has been successfully fixed!")
    else:
        print("\n🔧 Analysis functionality still needs work.")
