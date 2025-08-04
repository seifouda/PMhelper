#!/usr/bin/env python3

print("Starting basic test...")

try:
    import sys
    from pathlib import Path
    print("Basic imports OK")
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    print("Path added")
    
    # Test matplotlib
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    print("Matplotlib OK")
    
    # Test basic imports
    import tkinter as tk
    print("Tkinter OK")
    
    import tkinter.ttk
    print("TTK OK")
    
    import networkx as nx
    print("NetworkX OK")
    
    # Test NetworkTab import
    from pmhelper.gui.tabs.network_tab import NetworkTab
    print("NetworkTab import OK")
    
    print("All basic tests passed!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
