#!/usr/bin/env python3
"""
Compare Network tab vs PERT tab toolbar implementations
"""
import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def compare_tabs():
    print("🔍 COMPARING NETWORK TAB vs PERT TAB")
    print("=" * 50)
    
    try:
        from pmhelper.gui.main_window import MainWindow
        
        # Create test window
        root = tk.Tk()
        root.withdraw()
        app = MainWindow(root)
        
        # Give time for initialization
        root.update()
        root.after(200)
        root.update_idletasks()
        
        # Check PERT tab
        print("📊 PERT TAB:")
        pert_tab = app.pert_diagram_tab
        if hasattr(pert_tab, 'toolbar') and pert_tab.toolbar:
            pert_frame = pert_tab.toolbar.master
            pert_height = pert_frame.winfo_height()
            pert_geometry = pert_frame.winfo_geometry()
            print(f"  ✅ PERT toolbar height: {pert_height}")
            print(f"  ✅ PERT toolbar geometry: {pert_geometry}")
            print(f"  ✅ PERT pack info: {pert_frame.pack_info()}")
        else:
            print("  ❌ PERT toolbar not found")
        
        print()
        
        # Check Network tab
        print("🌐 NETWORK TAB:")
        network_tab = app.network_tab
        if hasattr(network_tab, 'toolbar') and network_tab.toolbar:
            network_frame = network_tab.toolbar.master
            network_height = network_frame.winfo_height()
            network_geometry = network_frame.winfo_geometry()
            print(f"  📏 Network toolbar height: {network_height}")
            print(f"  📐 Network toolbar geometry: {network_geometry}")
            print(f"  📦 Network pack info: {network_frame.pack_info()}")
        else:
            print("  ❌ Network toolbar not found")
        
        # Check parent frames
        print("\n🏗️  PARENT FRAME COMPARISON:")
        if hasattr(pert_tab, 'main_frame'):
            print(f"  PERT main_frame geometry: {pert_tab.main_frame.winfo_geometry()}")
        
        if hasattr(network_tab, 'network_frame'):
            print(f"  Network network_frame geometry: {network_tab.network_frame.winfo_geometry()}")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_tabs()
