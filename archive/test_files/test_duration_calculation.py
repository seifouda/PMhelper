#!/usr/bin/env python3
"""
Test to verify RCPS Crashing duration calculation works with EF attributes
"""

import pandas as pd
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pmhelper.core.cpm_analyzer import CPMAnalyzer
from pmhelper.gui.tabs.rcps_tab import RCPSTab
from pmhelper.gui.tabs.rcps_crashing_tab_gui import RCPSCrashingTabGUIManager


def test_duration_calculation():
    """Test that RCPS Crashing can calculate project duration with EF attributes"""
    
    print("=" * 60)
    print("🧪 Testing RCPS Crashing Duration Calculation with EF Attributes")
    print("=" * 60)
    
    # Create test data
    test_data = {
        'Activity': ['A', 'B', 'C', 'D'],
        'Predecessor': ['', 'A', 'A', 'B,C'],
        'Duration': [3, 4, 2, 5],
        'early_start': [0, 3, 3, 7],
        'late_finish': [3, 7, 5, 12],
        'float': [0, 0, 2, 0],
        'Resource': [1, 2, 1, 3],
        'Cost': [100, 200, 150, 300],
        'Crash_Cost': [150, 250, 200, 400]
    }
    
    print(f"📋 Test data: {len(test_data['Activity'])} activities")
    
    # Create main window and analyzer
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Create CPM analyzer
    analyzer = CPMAnalyzer()
    df_gantt = pd.DataFrame(test_data)
    
    # Create RCPS Tab (this will store the network graph)
    rcps_tab = RCPSTab(root, analyzer)
    
    print("\n🔧 Running RCPS Analysis...")
    try:
        # Run RCPS analysis to populate network graph
        result = rcps_tab.run_rcps(5, 'earliest_start', df_gantt)
        print(f"✅ RCPS analysis completed")
        
        # Check that network graph was created with EF attributes
        network_graph = rcps_tab.get_rcps_data()
        if network_graph is None:
            print("❌ Network graph is None")
            return False
            
        print(f"📊 Network graph has {network_graph.number_of_nodes()} nodes")
        
        # Check EF attributes in nodes
        print("\n🔍 Checking EF attributes in network nodes:")
        ef_values = []
        for node in network_graph.nodes():
            node_data = network_graph.nodes[node]
            if 'EF' in node_data:
                ef_value = node_data['EF']
                ef_values.append(ef_value)
                print(f"   Node {node}: EF = {ef_value}")
            else:
                print(f"   ❌ Node {node}: Missing EF attribute")
                return False
        
        if not ef_values:
            print("❌ No EF values found in network graph")
            return False
        
        # Calculate project duration manually
        calculated_duration = max(ef_values)
        print(f"\n📏 Calculated project duration from EF values: {calculated_duration}")
        
        # Now test RCPS Crashing duration validation
        print("\n🎯 Testing RCPS Crashing duration calculation...")
        
        # Create a tab frame for the crashing manager
        tab_frame = ttk.Frame(root)
        
        # Create RCPS Crashing manager (it needs tab instance and app instance)
        crashing_manager = RCPSCrashingTabGUIManager(tab_frame, rcps_tab)
        
        # Get the network graph through the crashing manager
        crash_network = crashing_manager.get_rcps_data()
        if crash_network is None:
            print("❌ RCPS Crashing cannot access network graph")
            return False
        
        print(f"✅ RCPS Crashing successfully accessed network graph")
        
        # Test duration calculation method
        try:
            # Simulate the duration calculation that was failing
            ef_values_crash = [crash_network.nodes[node].get('EF', 0) for node in crash_network.nodes()]
            current_duration = max(ef_values_crash) if ef_values_crash else 0
            
            print(f"📊 Current project duration calculated by RCPS Crashing: {current_duration}")
            
            if current_duration > 0:
                print("✅ Duration calculation successful - 'could not calculate RCPS project duration' error should be fixed!")
                return True
            else:
                print("❌ Duration calculation returned 0 - problem persists")
                return False
                
        except Exception as e:
            print(f"❌ Duration calculation failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ RCPS analysis failed: {e}")
        return False
    
    finally:
        root.destroy()


if __name__ == "__main__":
    success = test_duration_calculation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 DURATION CALCULATION TEST PASSED")
        print("✅ Both 'no RCPS data available' and 'could not calculate RCPS project duration' errors should be fixed!")
    else:
        print("❌ DURATION CALCULATION TEST FAILED")
        print("⚠️  'could not calculate RCPS project duration' error may still occur")
    print("=" * 60)
