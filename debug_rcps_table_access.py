#!/usr/bin/env python3
"""
Debug RCPS Table Access
Check if RCPS table data is available and properly structured
"""

def check_rcps_tab_access():
    """Check if we can access RCPS tab and its data"""
    print("🔍 DEBUGGING RCPS TABLE ACCESS")
    print("=" * 50)
    
    # Try to import and access the RCPS tab
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Try to access the app structure
        print("📱 Attempting to access PMHelper app structure...")
        
        # Check if we can import the main components
        try:
            from pmhelper.gui.main_window import PMHelperGUI
            print("✅ Successfully imported PMHelperGUI")
        except ImportError as e:
            print(f"❌ Failed to import PMHelperGUI: {e}")
            
        try:
            from pmhelper.gui.tabs.rcps_tab_gui import RCPSTabGUIManager
            print("✅ Successfully imported RCPSTabGUIManager")
        except ImportError as e:
            print(f"❌ Failed to import RCPSTabGUIManager: {e}")
            
        try:
            from pmhelper.gui.tabs.rcps_crashing_tab_gui import RCPSCrashingTabGUIManager
            print("✅ Successfully imported RCPSCrashingTabGUIManager")
        except ImportError as e:
            print(f"❌ Failed to import RCPSCrashingTabGUIManager: {e}")
            
    except Exception as e:
        print(f"❌ Error during import check: {e}")
        
    print("\n🔧 DEBUGGING TIPS:")
    print("1. Launch PMHelper GUI: python launch_app.py")
    print("2. Load sample data")
    print("3. Run CPM analysis first") 
    print("4. Go to RCPS Schedule tab and run RCPS analysis")
    print("5. Check console for RCPS table data messages")
    print("6. Then try RCPS crashing")
    
    print("\n🎯 EXPECTED RCPS DATA STRUCTURE:")
    print("- rcps_table_data should be a DataFrame")
    print("- Should contain columns: id, name, duration, early_start, early_finish, etc.")
    print("- Should NOT be None or empty")
    print("- Should contain activity rows (not just RA/RS)")
    
    print("\n💡 If RCPS analysis fails:")
    print("- Check if sample data has resource assignments")
    print("- Verify resource capacity is set properly")
    print("- Look for error messages during RCPS analysis")

if __name__ == "__main__":
    check_rcps_tab_access()
