#!/usr/bin/env python3
"""
Test Network tab toolbar after tab selection and proper timing
"""
import tkinter as tk
from tkinter import ttk
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_with_tab_selection():
    print("🔍 TESTING NETWORK TAB WITH TAB SELECTION")
    print("=" * 45)
    
    try:
        from pmhelper.gui.main_window import MainWindow
        
        # Create test window
        root = tk.Tk()
        root.withdraw()  # Hide for testing
        app = MainWindow(root)
        
        # Give time for initialization
        root.update()
        time.sleep(0.1)
        root.update_idletasks()
        
        # Force selection of Network tab
        try:
            for i in range(app.notebook.index("end")):
                tab_text = app.notebook.tab(i, "text")
                if "Network" in tab_text:
                    print(f"📍 Selecting Network tab (index {i})")
                    app.notebook.select(i)
                    break
        except:
            print("⚠️  Could not select Network tab")
        
        # Give more time after tab selection
        root.update()
        time.sleep(0.2)
        root.update_idletasks()
        
        # Check Network tab toolbar
        network_tab = app.network_tab
        
        if hasattr(network_tab, 'toolbar') and network_tab.toolbar:
            toolbar_frame = network_tab.toolbar.master
            
            # Force multiple updates
            toolbar_frame.update_idletasks()
            root.update()
            toolbar_frame.update_idletasks()
            
            toolbar_height = toolbar_frame.winfo_height()
            toolbar_geometry = toolbar_frame.winfo_geometry()
            
            print(f"📏 Toolbar frame height: {toolbar_height}")
            print(f"📐 Toolbar frame geometry: {toolbar_geometry}")
            
            # Check pack info
            pack_info = toolbar_frame.pack_info()
            print(f"📦 Pack info: {pack_info}")
            
            # Check parent frame
            parent_frame = toolbar_frame.master
            parent_height = parent_frame.winfo_height()
            parent_geometry = parent_frame.winfo_geometry()
            print(f"🏗️  Parent frame height: {parent_height}")
            print(f"🏗️  Parent frame geometry: {parent_geometry}")
            
            if toolbar_height > 20:
                print("✅ SUCCESS: Toolbar is visible!")
                result = "PASS"
            else:
                print("❌ FAIL: Toolbar height too small")
                result = "FAIL"
                
                # Debug: Try to see what's taking up the space
                siblings = parent_frame.winfo_children()
                print(f"🔍 Parent frame children: {len(siblings)}")
                for i, child in enumerate(siblings):
                    child_height = child.winfo_height()
                    child_geometry = child.winfo_geometry()
                    child_pack = child.pack_info() if hasattr(child, 'pack_info') else "Not packed"
                    print(f"  Child {i}: height={child_height}, geometry={child_geometry}, pack={child_pack}")
        else:
            print("❌ FAIL: Toolbar not found")
            result = "FAIL"
        
        root.destroy()
        print("=" * 45)
        print(f"🏆 RESULT: {result}")
        
        return result == "PASS"
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_tab_selection()
    print(f"\n{'✅ TOOLBAR WORKING!' if success else '❌ TOOLBAR STILL BROKEN'}")
    sys.exit(0 if success else 1)
