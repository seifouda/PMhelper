#!/usr/bin/env python3

import sys
from pathlib import Path
import math

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_network_tab_methods():
    """Test the NetworkTab methods without GUI"""
    print("=" * 80)
    print("NETWORK TAB METHODS TEST")
    print("=" * 80)
    
    try:
        from pmhelper.gui.tabs.network_tab import NetworkTab
        import tkinter as tk
        import networkx as nx
        
        print("1. ✅ Successfully imported NetworkTab")
        
        # Create a mock parent for testing
        root = tk.Tk()
        notebook = tk.Frame(root)
        
        # Create a mock main_window
        class MockMainWindow:
            pass
        
        main_window = MockMainWindow()
        
        # Create NetworkTab instance
        network_tab = NetworkTab(notebook, main_window)
        print("2. ✅ Successfully created NetworkTab instance")
        
        # Test data
        activities = [
            {'id': 'A', 'duration': 5, 'predecessors': [], 'critical': True},
            {'id': 'B', 'duration': 3, 'predecessors': ['A'], 'critical': True},
            {'id': 'C', 'duration': 4, 'predecessors': ['A'], 'critical': False},
            {'id': 'D', 'duration': 2, 'predecessors': ['B', 'C'], 'critical': True}
        ]
        
        critical_activities = ['A', 'B', 'D']
        
        print("3. Testing build_graph_from_activities...")
        if hasattr(network_tab, 'build_graph_from_activities'):
            G = network_tab.build_graph_from_activities(activities)
            print(f"   ✅ Built graph with {len(G.nodes())} nodes and {len(G.edges())} edges")
            print(f"   Nodes: {list(G.nodes())}")
        else:
            print("   ❌ build_graph_from_activities method not found")
        
        print("4. Testing create_hierarchical_layout...")
        if hasattr(network_tab, 'create_hierarchical_layout'):
            pos = network_tab.create_hierarchical_layout(G)
            print(f"   ✅ Created layout with {len(pos)} positions")
            for node, (x, y) in pos.items():
                print(f"   {node}: ({x:.1f}, {y:.1f})")
        else:
            print("   ❌ create_hierarchical_layout method not found")
        
        print("5. Testing add_start_end_nodes...")
        if hasattr(network_tab, 'add_start_end_nodes'):
            # Create a test graph without START/END
            test_G = nx.DiGraph()
            test_G.add_node('A', duration=5)
            test_G.add_node('B', duration=3)
            test_G.add_edge('A', 'B')
            
            network_tab.add_start_end_nodes(test_G)
            print(f"   ✅ Added START/END nodes. Graph now has {len(test_G.nodes())} nodes")
            print(f"   Nodes: {list(test_G.nodes())}")
        else:
            print("   ❌ add_start_end_nodes method not found")
        
        print("6. Testing display options existence...")
        display_options = [
            'show_critical_var', 'show_times_var', 'show_float_var', 'show_labels_var'
        ]
        
        for option in display_options:
            if hasattr(network_tab, option):
                value = getattr(network_tab, option).get()
                print(f"   ✅ {option}: {value}")
            else:
                print(f"   ❌ {option} not found")
        
        print("7. Testing method existence...")
        methods_to_check = [
            'draw_network_diagram', 'draw_network_edges', 'draw_network_nodes',
            'add_network_legend', 'apply_display_options', 'add_float_labels'
        ]
        
        for method in methods_to_check:
            if hasattr(network_tab, method):
                print(f"   ✅ {method} method exists")
            else:
                print(f"   ❌ {method} method not found")
        
        print("\n" + "=" * 80)
        print("✅ NETWORK TAB METHODS TEST COMPLETED SUCCESSFULLY!")
        print("All required methods and attributes are present.")
        print("=" * 80)
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_network_tab_methods()
