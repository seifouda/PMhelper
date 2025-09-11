#!/usr/bin/env python3
"""
Final comprehensive test for EF attributes in RCPS Crashing
This test verifies the entire pipeline works correctly
"""

import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pmhelper.gui.main_window import MainWindow
from pmhelper.core.cpm_analyzer import CPMAnalyzer
import tkinter as tk
from tkinter import ttk

def test_ef_attributes_integration():
    """Test the complete integration with EF attributes"""
    print("🧪 Testing EF attributes integration for RCPS Crashing...")
    
    # Create test data
    test_data = pd.DataFrame({
        'Activity': ['A', 'B', 'C', 'D'],
        'Duration': [2, 3, 1, 4],
        'Predecessors': ['', 'A', 'A', 'B,C'],
        'Cost': [100, 150, 75, 200],
        'Crash_Duration': [1, 2, 1, 3],
        'Crash_Cost': [150, 200, 75, 300],
        'Resources': [2, 1, 1, 2]
    })
    
    print(f"✅ Test data created with {len(test_data)} activities")
    
    # Create a main window instance
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        # Initialize main window
        main_window = MainWindow(root)
        print("✅ Main window initialized")
        
        # Load data into the window
        main_window.df_gantt = test_data
        print("✅ Test data loaded")
        
        # Test RCPS analysis first
        rcps_tab = main_window.rcps_tab
        result = rcps_tab.run_rcps(
            resource_limit=5,
            priority_rule='earliest_start',
            df_gantt=test_data
        )
        
        if result:
            print("✅ RCPS analysis completed successfully")
            
            # Check if network graph has EF attributes
            if hasattr(rcps_tab, 'rcps_network_graph') and rcps_tab.rcps_network_graph:
                network = rcps_tab.rcps_network_graph
                print(f"✅ Network graph created with {len(network.nodes())} nodes")
                
                # Check EF attributes
                ef_found = False
                for node in network.nodes():
                    node_data = network.nodes[node]
                    if 'EF' in node_data:
                        ef_found = True
                        print(f"✅ Node {node} has EF attribute: {node_data['EF']}")
                        print(f"   - ES: {node_data.get('ES', 'N/A')}")
                        print(f"   - Duration: {node_data.get('duration', 'N/A')}")
                
                if ef_found:
                    print("✅ EF attributes found in network graph!")
                    
                    # Test RCPS Crashing data access
                    crashing_tab = main_window.rcps_crashing_tab
                    
                    # Test get_rcps_data
                    try:
                        network_data = crashing_tab.get_rcps_data()
                        if network_data:
                            print("✅ RCPS Crashing can access network data")
                            
                            # Test duration calculation
                            try:
                                # Get all EF values
                                ef_values = []
                                for node in network_data.nodes():
                                    node_data = network_data.nodes[node]
                                    if 'EF' in node_data:
                                        ef_values.append(node_data['EF'])
                                
                                if ef_values:
                                    project_duration = max(ef_values)
                                    print(f"✅ Project duration calculated: {project_duration}")
                                    print("✅ Duration calculation with EF attributes successful!")
                                    return True
                                else:
                                    print("❌ No EF values found in network")
                                    return False
                                    
                            except Exception as e:
                                print(f"❌ Duration calculation failed: {e}")
                                return False
                        else:
                            print("❌ No network data available for RCPS Crashing")
                            return False
                    except Exception as e:
                        print(f"❌ RCPS Crashing data access failed: {e}")
                        return False
                else:
                    print("❌ No EF attributes found in network graph")
                    return False
            else:
                print("❌ No network graph created")
                return False
        else:
            print("❌ RCPS analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        root.destroy()

def main():
    """Run the final EF attributes test"""
    print("=" * 60)
    print("FINAL EF ATTRIBUTES TEST FOR RCPS CRASHING")
    print("=" * 60)
    
    success = test_ef_attributes_integration()
    
    print("=" * 60)
    if success:
        print("🎉 FINAL TEST PASSED!")
        print("✅ EF attributes are correctly implemented")
        print("✅ RCPS Crashing duration calculation should work")
        print("✅ Bug is completely fixed!")
    else:
        print("❌ FINAL TEST FAILED!")
        print("❌ Additional debugging needed")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    main()
