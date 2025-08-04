#!/usr/bin/env python3
"""
Simple test to check if launch_app.py works correctly with mode detection
"""

import sys
from pathlib import Path

# Add the code directory to the path
project_root = Path(__file__).parent
code_path = project_root / "code"
sys.path.insert(0, str(code_path))

def test_launch_app_behavior():
    """Test what happens when we import and use cpm_app like launch_app.py does"""
    print("=== Testing launch_app.py behavior ===")
    
    try:
        print("1. Importing cpm_app main function...")
        from cpm_app import main as cpm_main
        print("   ✅ Import successful")
        
        print("2. Testing direct CPMDesktopApp creation...")
        import tkinter as tk
        from cpm_app import CPMDesktopApp
        
        # Create a test instance
        root = tk.Tk()
        root.withdraw()  # Hide for testing
        app = CPMDesktopApp(root)
        
        print(f"   Initial mode: {app.analysis_mode}")
        print(f"   Initial label: {app.mode_label.cget('text')}")
        print(f"   Initial activities: {len(app.get_activities_data())}")
        
        if app.analysis_mode == 'deterministic' and 'Mode: CPM' in app.mode_label.cget('text'):
            print("   ✅ Mode detection working correctly")
        else:
            print("   ❌ Mode detection issue detected!")
            print(f"      Expected: mode='deterministic', label contains 'Mode: CPM'")
            print(f"      Actual: mode='{app.analysis_mode}', label='{app.mode_label.cget('text')}'")
        
        root.destroy()
        
        print("3. The issue might be that when launch_app.py runs, it calls:")
        print("   cpm_main() which creates a NEW instance of CPMDesktopApp")
        print("   Let's test if this new instance has the same issue...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_launch_app_behavior()
