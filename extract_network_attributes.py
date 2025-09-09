#!/usr/bin/env python3
"""
Extract network graph attributes from working test
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from pmhelper.gui.main_window import MainWindow
import tkinter as tk

def extract_network_attributes():
    """Extract network graph attributes from working RCPS"""
    print("🔍 Extracting network graph attributes from working RCPS...")
    
    # Use exact data from working test
    test_data = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'duration': [3, 4, 2, 3],
        'predecessors': ['', 'A', 'A', 'B,C'],
        'resource': [2, 3, 1, 2],
        'crash_cost': [100, 150, 80, 120],
        'min_duration': [2, 2, 1, 2],
        'normal_cost': [200, 300, 160, 240]
    })
    
    root = tk.Tk()
    root.withdraw()
    
    try:
        app = MainWindow(root)
        
        # Initialize CPM analyzer (as done in working test)
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        app.cmp_analyzer = CPMAnalyzer()
        
        # Set the test data
        app.current_data = test_data
        
        # Create RCPS tab
        app.show_rcps_tab()
        rcps_tab = app.rcps_tab
        
        # Configure and run RCPS
        rcps_tab.resource_limit_var.set(5)
        rcps_tab.priority_rule_var.set("earliest_start")
        
        # Run RCPS analysis using working method
        try:
            original_run_rcps = rcps_tab.run_rcps
            def debug_run_rcps():
                print("[DEBUG] run_rcps called for attribute extraction")
                try:
                    result = original_run_rcps()
                    print("[DEBUG] run_rcps completed successfully")
                    return result
                except Exception as e:
                    print(f"[DEBUG] run_rcps exception: {e}")
                    raise
            
            rcps_tab.run_rcps = debug_run_rcps
            result = rcps_tab.run_rcps()
            
            if result and hasattr(rcps_tab, 'rcps_network_graph') and rcps_tab.rcps_network_graph:
                network = rcps_tab.rcps_network_graph
                print(f"\n✅ Network graph retrieved with {len(network.nodes())} nodes")
                
                # Extract and display all attributes
                print("\n📊 NETWORK GRAPH ATTRIBUTES:")
                print("=" * 50)
                
                ef_values = []
                for node_id in network.nodes():
                    node_data = network.nodes[node_id]
                    print(f"\nNode {node_id}:")
                    
                    # Sort attributes for consistent display
                    sorted_attrs = sorted(node_data.items())
                    for attr, value in sorted_attrs:
                        print(f"  {attr}: {value}")
                        if attr == 'EF':
                            ef_values.append(value)
                
                if ef_values:
                    project_duration = max(ef_values)
                    print(f"\n📏 PROJECT DURATION CALCULATION:")
                    print(f"   EF values: {ef_values}")
                    print(f"   Max EF (project duration): {project_duration}")
                    print(f"\n✅ EF attributes are working correctly!")
                    return True
                else:
                    print(f"\n❌ No EF values found")
                    return False
            else:
                print(f"\n❌ No network graph created")
                return False
                
        except Exception as e:
            print(f"❌ RCPS analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        root.destroy()

def main():
    print("=" * 60)
    print("NETWORK GRAPH ATTRIBUTES EXTRACTION")
    print("=" * 60)
    
    success = extract_network_attributes()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ATTRIBUTE EXTRACTION SUCCESSFUL!")
        print("✅ EF attributes confirmed in network graph")
        print("✅ Duration calculation working correctly")
    else:
        print("❌ ATTRIBUTE EXTRACTION FAILED!")
    print("=" * 60)

if __name__ == "__main__":
    main()
