#!/usr/bin/env python3
"""
RCPS Crashing Data Flow Debugger

This script adds comprehensive debugging to understand the data structure
being passed from RCPS tab to RCPS crashing tab and identify why activities
A and B are missing.
"""

import tkinter as tk
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def debug_rcps_data_flow():
    """Debug the RCPS data flow and network graph building"""
    
    print("=" * 60)
    print("RCPS CRASHING DATA FLOW DEBUGGER")
    print("=" * 60)
    
    try:
        # Import necessary modules
        from pmhelper.gui.main_window import MainWindow
        
        # Create application instance
        root = tk.Tk()
        app = MainWindow(root)
        
        print("\n1. APPLICATION INITIALIZED")
        print(f"   Mode: {app.analysis_mode}")
        
        # Trigger RCPS tab creation by calling show_rcps_tab
        print("\n2. CREATING RCPS TAB")
        app.show_rcps_tab()
        
        # Access the RCPS tab
        rcps_tab = None
        rcps_crashing_tab = None
        
        # Check if RCPS tab was created
        if hasattr(app, 'rcps_tab') and app.rcps_tab:
            rcps_tab = app.rcps_tab
            print(f"   ✅ Found RCPS tab via direct attribute")
        
        if hasattr(app, 'rcps_crashing_tab') and app.rcps_crashing_tab:
            rcps_crashing_tab = app.rcps_crashing_tab
            print(f"   ✅ Found RCPS Crashing tab via direct attribute")
        
        if not rcps_tab:
            print("❌ ERROR: RCPS tab not found or not created")
            return
            
        if not rcps_crashing_tab:
            print("⚠️  WARNING: RCPS Crashing tab not found - this is normal if not accessed yet")
        
        print("\n3. CHECKING RCPS TAB DATA AVAILABILITY")
        
        # Check if RCPS tab has data
        print(f"   RCPS network graph: {hasattr(rcps_tab, 'rcps_network_graph')}")
        print(f"   RCPS analyzer: {hasattr(rcps_tab, 'rcps_analyzer')}")
        print(f"   CMP table data: {hasattr(rcps_tab, 'cmp_table_data')}")
        print(f"   RCPS table data: {hasattr(rcps_tab, 'rcps_table_data')}")
        print(f"   Gantt data: {hasattr(rcps_tab, 'gantt_data')}")
        
        if hasattr(rcps_tab, 'rcps_network_graph') and rcps_tab.rcps_network_graph is not None:
            graph = rcps_tab.rcps_network_graph
            print(f"\n3. RCPS NETWORK GRAPH ANALYSIS")
            print(f"   Graph type: {type(graph)}")
            print(f"   Number of nodes: {len(graph.nodes()) if hasattr(graph, 'nodes') else 'N/A'}")
            print(f"   Number of edges: {len(graph.edges()) if hasattr(graph, 'edges') else 'N/A'}")
            
            if hasattr(graph, 'nodes'):
                print(f"   Nodes: {list(graph.nodes())}")
                
                print(f"\n4. NODE ATTRIBUTES ANALYSIS")
                for node in graph.nodes():
                    attrs = graph.nodes[node]
                    print(f"   Node {node}:")
                    for key, value in attrs.items():
                        print(f"      {key}: {value}")
                    print()
            
            if hasattr(graph, 'edges'):
                print(f"5. EDGE ANALYSIS")
                print(f"   Edges: {list(graph.edges())}")
        else:
            print("\n3. ❌ NO RCPS NETWORK GRAPH AVAILABLE")
            print("   This explains why RCPS crashing has no data!")
            
        if hasattr(rcps_tab, 'rcps_analyzer') and rcps_tab.rcps_analyzer is not None:
            analyzer = rcps_tab.rcps_analyzer
            print(f"\n6. RCPS ANALYZER ANALYSIS")
            print(f"   Analyzer type: {type(analyzer)}")
            print(f"   Has activities: {hasattr(analyzer, 'activities')}")
            print(f"   Has graph: {hasattr(analyzer, 'G')}")
            
            if hasattr(analyzer, 'activities'):
                activities = analyzer.activities
                print(f"   Number of activities: {len(activities)}")
                print(f"   Activity IDs: {[act.get('id', 'NO_ID') for act in activities]}")
                
                print(f"\n7. ACTIVITIES DETAILED ANALYSIS")
                for i, activity in enumerate(activities):
                    print(f"   Activity {i}:")
                    for key, value in activity.items():
                        print(f"      {key}: {value}")
                    print()
            
            if hasattr(analyzer, 'G') and analyzer.G is not None:
                orig_graph = analyzer.G
                print(f"\n8. ORIGINAL ANALYZER GRAPH")
                print(f"   Original graph nodes: {list(orig_graph.nodes())}")
                print(f"   Original graph edges: {list(orig_graph.edges())}")
        else:
            print("\n6. ❌ NO RCPS ANALYZER AVAILABLE")
        
        # Check table data if available
        if hasattr(rcps_tab, 'rcps_table_data') and rcps_tab.rcps_table_data is not None:
            table = rcps_tab.rcps_table_data
            print(f"\n9. RCPS TABLE DATA ANALYSIS")
            print(f"   Table type: {type(table)}")
            print(f"   Table shape: {table.shape if hasattr(table, 'shape') else 'N/A'}")
            print(f"   Table columns: {list(table.columns) if hasattr(table, 'columns') else 'N/A'}")
            
            if hasattr(table, 'iterrows'):
                print(f"\n10. TABLE ROWS ANALYSIS")
                for idx, row in table.iterrows():
                    if row.get('id') not in ['RA', 'RS']:  # Skip resource rows
                        print(f"    Row {idx} - ID: {row.get('id')}")
                        print(f"      Duration: {row.get('duration')}")
                        print(f"      Early Start: {row.get('early_start')}")
                        print(f"      Actual Start: {row.get('actual_start', 'NOT_AVAILABLE')}")
                        print()
        else:
            print("\n9. ❌ NO RCPS TABLE DATA AVAILABLE")
        
        print("\n" + "=" * 60)
        print("DEBUGGING SUMMARY")
        print("=" * 60)
        
        # Provide diagnosis
        has_graph = hasattr(rcps_tab, 'rcps_network_graph') and rcps_tab.rcps_network_graph is not None
        has_analyzer = hasattr(rcps_tab, 'rcps_analyzer') and rcps_tab.rcps_analyzer is not None
        has_table = hasattr(rcps_tab, 'rcps_table_data') and rcps_tab.rcps_table_data is not None
        
        print(f"✅ RCPS Network Graph Available: {has_graph}")
        print(f"✅ RCPS Analyzer Available: {has_analyzer}")
        print(f"✅ RCPS Table Data Available: {has_table}")
        
        if not (has_graph and has_analyzer):
            print(f"\n❌ PROBLEM IDENTIFIED:")
            print(f"   RCPS Crashing tab requires both network graph and analyzer")
            print(f"   to function properly. Missing data explains the issue.")
            print(f"\n💡 SOLUTION:")
            print(f"   Run RCPS analysis first in the RCPS Schedule tab")
            print(f"   This will populate the required data structures")
        else:
            print(f"\n✅ ALL DATA AVAILABLE")
            print(f"   The RCPS crashing should work correctly")
            
        root.destroy()
        
    except Exception as e:
        print(f"❌ ERROR during debugging: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_rcps_data_flow()
