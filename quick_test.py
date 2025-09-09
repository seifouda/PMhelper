#!/usr/bin/env python3
"""
Quick test to verify Network tab toolbar is now visible with correct packing order
"""
import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def quick_toolbar_test():
    print("🔍 TESTING NETWORK TAB TOOLBAR VISIBILITY")
    print("=" * 45)
    
    try:
        from pmhelper.gui.main_window import MainWindow
        
        # Create test window
        root = tk.Tk()
        root.withdraw()  # Hide for testing
        app = MainWindow(root)
        
        # Give time for initialization
        root.update()
        root.after(100)
        root.update_idletasks()
        
        # Check Network tab toolbar
        network_tab = app.network_tab
        
        if hasattr(network_tab, 'toolbar') and network_tab.toolbar:
            toolbar_frame = network_tab.toolbar.master
            toolbar_height = toolbar_frame.winfo_height()
            toolbar_geometry = toolbar_frame.winfo_geometry()
            
            print(f"📏 Toolbar frame height: {toolbar_height}")
            print(f"📐 Toolbar frame geometry: {toolbar_geometry}")
            
            # Check if toolbar has proper pack info
            pack_info = toolbar_frame.pack_info()
            print(f"📦 Pack info: {pack_info}")
            
            if toolbar_height > 20:  # Reasonable toolbar height
                print("✅ SUCCESS: Toolbar is visible!")
                result = "PASS"
            else:
                print("❌ FAIL: Toolbar height too small")
                result = "FAIL"
        else:
            print("❌ FAIL: Toolbar not found")
            result = "FAIL"
        
        root.destroy()
        print("=" * 45)
        print(f"🏆 RESULT: {result}")
        
        return result == "PASS"
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = quick_toolbar_test()
    print(f"\n{'✅ TOOLBAR FIX SUCCESSFUL!' if success else '❌ TOOLBAR STILL NOT WORKING'}")
    sys.exit(0 if success else 1)
