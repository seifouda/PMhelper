#!/usr/bin/env python3
"""
Simple test to verify RCPS ES values fix
"""

import sys
sys.path.append('src')

from pmhelper.gui.main_window import MainWindow
import tkinter as tk

def test_rcps_es_values():
    print("[DEBUG] Testing RCPS ES Values Fix")
    print("=" * 50)
    
    # Create the main window
    root = tk.Tk()
    root.withdraw()  # Hide the window for testing
    app = MainWindow(root)
    
    # Load sample data
    app.input_tab.load_sample_data()
    print("✅ Sample data loaded")
    
    # Run CPM analysis first
    app.run_cpm_analysis()
    print("✅ CPM analysis completed")
    
    # Check original project duration
    if hasattr(app, 'current_data') and app.current_data is not None:
        ef_values = []
        for _, row in app.current_data.iterrows():
            if 'early_finish' in row:
                try:
                    ef_values.append(float(row['early_finish']))
                except:
                    pass
        cmp_duration = max(ef_values) if ef_values else 0
        print(f"📊 Original CPM Project Duration: {cmp_duration}")
    
    # Run RCPS analysis
    if not hasattr(app, 'rcps_tab') or app.rcps_tab is None:
        from pmhelper.gui.tabs.rcps_tab import RCPSTab
        app.rcps_tab = RCPSTab(app.notebook, app)
    
    app.rcps_tab.resource_limit_var.set(5)
    app.rcps_tab.run_rcps()
    print("✅ RCPS analysis completed")
    
    # Check RCPS network graph
    if hasattr(app.rcps_tab, 'rcps_network_graph') and app.rcps_tab.rcps_network_graph:
        print(f"\\n🔍 RCPS Network Graph Analysis:")
        
        # Calculate project duration from RCPS network graph
        ef_values = []
        fix_working = True
        
        for node_id, attrs in app.rcps_tab.rcps_network_graph.nodes(data=True):
            if node_id not in ['START', 'END', 'RA', 'RS']:
                ef = attrs.get('EF', 0)
                es = attrs.get('ES', 0)
                early_start = attrs.get('early_start', 0)
                actual_start = attrs.get('actual_start', 0)
                
                ef_values.append(ef)
                
                print(f"   {node_id}: ES={es}, early_start={early_start}, actual_start={actual_start}, EF={ef}")
                
                # Check if ES equals actual_start (the fix)
                if es != actual_start:
                    fix_working = False
                    print(f"   ❌ PROBLEM: {node_id} ES ({es}) != actual_start ({actual_start})")
                else:
                    print(f"   ✅ CORRECT: {node_id} ES ({es}) == actual_start ({actual_start})")
        
        rcps_duration = max(ef_values) if ef_values else 0
        print(f"\\n📊 RCPS Project Duration: {rcps_duration}")
        
        # Verify the fix
        if fix_working:
            print(f"✅ FIX SUCCESSFUL: All ES values use actual_start")
            if rcps_duration > cmp_duration:
                print(f"✅ DURATION CORRECT: RCPS duration ({rcps_duration}) > CPM duration ({cmp_duration})")
                print(f"   This confirms resource constraints are causing delays")
            else:
                print(f"⚠️  DURATION NOTE: RCPS duration ({rcps_duration}) <= CPM duration ({cmp_duration})")
        else:
            print(f"❌ FIX FAILED: Some ES values still use original early_start")
    
    root.destroy()
    print(f"\\n🎉 Test completed!")

if __name__ == "__main__":
    test_rcps_es_values()
