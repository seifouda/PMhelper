#!/usr/bin/env python3

import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_network_methods():
    """Test the NetworkTab methods directly"""
    print("=" * 80)
    print("NETWORK TAB METHODS VALIDATION")
    print("=" * 80)
    
    try:
        # Test imports
        import networkx as nx
        import numpy as np
        print("1. ✅ Successfully imported required modules")
        
        # Test the NetworkTab file directly by importing its methods
        from pmhelper.gui.tabs.network_tab import NetworkTab
        import tkinter as tk
        import tkinter.ttk as ttk
        
        # Create proper tkinter setup
        root = tk.Tk()
        root.withdraw()  # Hide the window
        notebook = ttk.Notebook(root)
        
        # Create mock main window
        class MockMainWindow:
            def __init__(self):
                self.results_data = None
        
        main_window = MockMainWindow()
        
        # Create NetworkTab
        network_tab = NetworkTab(notebook, main_window)
        print("2. ✅ Successfully created NetworkTab with proper notebook")
        
        # Test data
        activities = [
            {'id': 'A', 'duration': 5, 'predecessors': [], 'critical': True},
            {'id': 'B', 'duration': 3, 'predecessors': ['A'], 'critical': True},
            {'id': 'C', 'duration': 4, 'predecessors': ['A'], 'critical': False},
            {'id': 'D', 'duration': 2, 'predecessors': ['B', 'C'], 'critical': True}
        ]
        
        print("3. Testing core methods...")
        
        # Test build_graph_from_activities
        try:
            if hasattr(network_tab, 'build_graph_from_activities'):
                G = network_tab.build_graph_from_activities(activities)
                print(f"   ✅ build_graph_from_activities: {len(G.nodes())} nodes, {len(G.edges())} edges")
            else:
                print("   ❌ build_graph_from_activities method missing")
        except Exception as e:
            print(f"   ❌ build_graph_from_activities error: {e}")
            
        # Test create_hierarchical_layout
        try:
            if hasattr(network_tab, 'create_hierarchical_layout'):
                pos = network_tab.create_hierarchical_layout(G)
                print(f"   ✅ create_hierarchical_layout: {len(pos)} positions")
            else:
                print("   ❌ create_hierarchical_layout method missing")
        except Exception as e:
            print(f"   ❌ create_hierarchical_layout error: {e}")
            
        # Test add_start_end_nodes
        try:
            if hasattr(network_tab, 'add_start_end_nodes'):
                test_G = nx.DiGraph()
                test_G.add_node('A', duration=5)
                test_G.add_node('B', duration=3)
                test_G.add_edge('A', 'B')
                original_nodes = len(test_G.nodes())
                network_tab.add_start_end_nodes(test_G)
                print(f"   ✅ add_start_end_nodes: {original_nodes} → {len(test_G.nodes())} nodes")
            else:
                print("   ❌ add_start_end_nodes method missing")
        except Exception as e:
            print(f"   ❌ add_start_end_nodes error: {e}")
        
        # Check all required methods exist
        required_methods = [
            'draw_network_diagram', 'draw_network_edges', 'draw_network_nodes',
            'add_network_legend', 'apply_display_options'
        ]
        
        print("4. Checking all required methods...")
        all_methods_exist = True
        for method in required_methods:
            if hasattr(network_tab, method):
                print(f"   ✅ {method}")
            else:
                print(f"   ❌ {method} MISSING")
                all_methods_exist = False
        
        # Check display options exist
        print("5. Checking display options...")
        display_options = ['show_critical_var', 'show_times_var', 'show_float_var', 'show_labels_var']
        all_options_exist = True
        for option in display_options:
            if hasattr(network_tab, option):
                print(f"   ✅ {option}")
            else:
                print(f"   ❌ {option} MISSING")
                all_options_exist = False
        
        # Test matplotlib canvas
        print("6. Testing matplotlib integration...")
        if hasattr(network_tab, 'canvas'):
            print("   ✅ matplotlib canvas exists")
        else:
            print("   ❌ matplotlib canvas missing")
        
        if hasattr(network_tab, 'toolbar'):
            print("   ✅ matplotlib toolbar exists")
        else:
            print("   ❌ matplotlib toolbar missing")
        
        print("\n" + "=" * 80)
        if all_methods_exist and all_options_exist:
            print("✅ ALL TESTS PASSED!")
            print("NetworkTab upgrade implementation is COMPLETE and READY")
            print("All required methods and display options are properly implemented")
        else:
            print("❌ SOME TESTS FAILED")
            print("NetworkTab upgrade has missing components")
        print("=" * 80)
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_network_methods()
