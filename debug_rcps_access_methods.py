#!/usr/bin/env python3
"""
Debug RCPS Access in Live App
Create a simple script to test RCPS table access patterns
"""

def debug_rcps_access_methods():
    """Test different ways to access RCPS data"""
    print("🔍 DEBUGGING RCPS ACCESS METHODS")
    print("=" * 50)
    
    print("\n📋 CURRENT ACCESS PATTERN IN RCPS CRASHING:")
    print("1. self.app.rcps_tab.rcps_table_data")
    print("2. self.tab.rcps_tab.rcps_table_data") 
    
    print("\n🎯 ALTERNATIVE ACCESS PATTERNS:")
    print("1. Use app's tab registry/dictionary")
    print("2. Access through main window tab references")
    print("3. Use direct method calls")
    
    print("\n🛠️ IMPROVED ACCESS METHOD:")
    print("""
def get_rcps_table_data_improved(self):
    \"\"\"Improved RCPS table data access with multiple fallbacks\"\"\"
    try:
        # Method 1: Through app's rcps_tab
        if hasattr(self.app, 'rcps_tab') and self.app.rcps_tab:
            if hasattr(self.app.rcps_tab, 'get_rcps_table_data'):
                data = self.app.rcps_tab.get_rcps_table_data()
                if data is not None:
                    print("[DEBUG] Got RCPS data via app.rcps_tab.get_rcps_table_data()")
                    return data
            
        # Method 2: Through tab manager references  
        if hasattr(self.app, 'tab_managers'):
            for tab_name, tab_manager in self.app.tab_managers.items():
                if 'rcps' in tab_name.lower() and 'crashing' not in tab_name.lower():
                    if hasattr(tab_manager, 'get_rcps_table_data'):
                        data = tab_manager.get_rcps_table_data()
                        if data is not None:
                            print(f"[DEBUG] Got RCPS data via tab_managers[{tab_name}]")
                            return data
                            
        # Method 3: Search for RCPS tab in app's children/attributes
        for attr_name in dir(self.app):
            if 'rcps' in attr_name.lower() and not attr_name.startswith('_'):
                tab_obj = getattr(self.app, attr_name)
                if hasattr(tab_obj, 'get_rcps_table_data'):
                    data = tab_obj.get_rcps_table_data()
                    if data is not None:
                        print(f"[DEBUG] Got RCPS data via app.{attr_name}")
                        return data
                        
        print("[ERROR] No RCPS table data found through any access method")
        return None
        
    except Exception as e:
        print(f"[ERROR] Exception in get_rcps_table_data_improved: {e}")
        return None
    """)
    
    print("\n✅ TESTING STEPS:")
    print("1. Launch PMHelper: python launch_app.py")
    print("2. Load sample data")
    print("3. Run CPM analysis")
    print("4. Go to RCPS Schedule tab")
    print("5. Run RCPS analysis (watch for success messages)")
    print("6. Go to RCPS Crashing tab")
    print("7. Try running crashing")
    print("8. Check console for '[DEBUG]' and '[ERROR]' messages")

if __name__ == "__main__":
    debug_rcps_access_methods()
