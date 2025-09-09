#!/usr/bin/env python3
"""    # Run     # Run CPM analysis first (needed for comparison)
    app.run_cmp_analysis()
    print("✅ CPM analysis completed")
    
    # Check original CPM project duration from current_data
    if hasattr(app, 'current_data') and app.current_data is not None:
        # Calculate CPM duration from current_data
        ef_values = [row['early_finish'] for _, row in app.current_data.iterrows() if 'early_finish' in row]
        cmp_duration = max(ef_values) if ef_values else 'Unknown'
        print(f"📊 CPM Project Duration: {cmp_duration}")
    else:
        print(f"📊 CPM Project Duration: Not available")ysis first (needed for comparison)
    app.run_cpm_analysis()
    print("✅ CPM analysis completed")
    
    # Check original CPM project duration from current_data
    if hasattr(app, 'current_data') and app.current_data is not None:
        # Calculate CPM duration from current_data
        ef_values = [row['early_finish'] for _, row in app.current_data.iterrows() if 'early_finish' in row]
        cmp_duration = max(ef_values) if ef_values else 'Unknown'
        print(f"📊 CPM Project Duration: {cmp_duration}")
    else:
        print(f"📊 CPM Project Duration: Not available")o verify that RCPS crashing now uses the correct project duration (33) from RCPS analysis
instead of the original CPM duration (27)
"""

import sys
sys.path.append('src')

from pmhelper.gui.main_window import MainWindow
from pmhelper.utils.file_handlers import FileHandler
import tkinter as tk

def test_rcps_duration_fix():
    """Test that RCPS crashing starts with the correct resource-constrained project duration"""
    print("[DEBUG] Testing RCPS Duration Fix")
    print("=" * 60)
    
    # Create the main window
    root = tk.Tk()
    root.withdraw()  # Hide the window for testing
    app = MainWindow(root)
    
    # Load sample data
    app.input_tab.load_sample_data()
    print("✅ Sample data loaded")
    
    # Run CPM analysis first (needed for comparison)
    app.cpm_tab.run_cpm()
    print("✅ CPM analysis completed")
    
    # Check original CPM project duration
    if hasattr(app.cpm_tab, 'analysis_data') and app.cpm_tab.analysis_data:
        cmp_duration = app.cpm_tab.analysis_data.get('project_duration', 'Unknown')
        print(f"📊 CPM Project Duration: {cmp_duration}")
    
    # Run RCPS analysis with resource limit 5
    # First check if rcps_tab exists, if not create it
    if not hasattr(app, 'rcps_tab') or app.rcps_tab is None:
        from pmhelper.gui.tabs.rcps_tab import RCPSTab
        app.rcps_tab = RCPSTab(app.notebook, app)
    
    app.rcps_tab.resource_limit_var.set(5)
    app.rcps_tab.run_rcps()
    print("✅ RCPS analysis completed")
    
    # Check RCPS network graph ES values
    if hasattr(app.rcps_tab, 'rcps_network_graph') and app.rcps_tab.rcps_network_graph:
        print(f"\n🔍 RCPS Network Graph Analysis:")
        print(f"   Nodes: {len(app.rcps_tab.rcps_network_graph.nodes())}")
        
        # Calculate project duration from RCPS network graph
        ef_values = []
        es_actual_start_match = True
        
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
                    es_actual_start_match = False
                    print(f"   ❌ PROBLEM: {node_id} ES ({es}) != actual_start ({actual_start})")
                else:
                    print(f"   ✅ CORRECT: {node_id} ES ({es}) == actual_start ({actual_start})")
        
        rcps_duration = max(ef_values) if ef_values else 0
        print(f"\n📊 RCPS Project Duration (from network graph): {rcps_duration}")
        
        # Verify the fix
        if es_actual_start_match:
            print(f"✅ FIX SUCCESSFUL: All ES values use actual_start (resource-constrained schedule)")
        else:
            print(f"❌ FIX FAILED: Some ES values still use original early_start")
        
        # Expected result
        if rcps_duration == 33:
            print(f"✅ CORRECT DURATION: RCPS duration is 33 (resource-constrained)")
        elif rcps_duration == 27:
            print(f"❌ WRONG DURATION: RCPS duration is 27 (original CPM, bug not fixed)")
        else:
            print(f"⚠️  UNEXPECTED DURATION: RCPS duration is {rcps_duration}")
    
    else:
        print("❌ No RCPS network graph found")
    
    # Check RCPS table data to verify actual_start values
    if hasattr(app.rcps_tab, 'rcps_table_data') and app.rcps_tab.rcps_table_data is not None:
        print(f"\n📋 RCPS Table Data Analysis:")
        activities_with_actual_start = app.rcps_tab.rcps_table_data[
            (~app.rcps_tab.rcps_table_data['id'].isin(['RA', 'RS'])) & 
            (app.rcps_tab.rcps_table_data['actual_start'] != '')
        ]
        
        if len(activities_with_actual_start) > 0:
            max_ef_from_table = 0
            for _, row in activities_with_actual_start.iterrows():
                actual_start = int(row['actual_start'])
                duration = int(row['duration'])
                ef = actual_start + duration
                max_ef_from_table = max(max_ef_from_table, ef)
                print(f"   {row['id']}: actual_start={actual_start}, duration={duration}, EF={ef}")
            
            print(f"\n📊 RCPS Project Duration (from table data): {max_ef_from_table}")
        else:
            print("   No activities with actual_start found in table")
    
    # Now test RCPS Crashing to see if it uses the correct duration
    print(f"\n🔧 Testing RCPS Crashing with fixed network graph...")
    
    # Create crashing data
    crashing_df = app.rcps_tab.prepare_crashing_dataframe()
    if crashing_df is not None:
        print(f"✅ RCPS Crashing DataFrame prepared with {len(crashing_df)} activities")
        
        # Check if early_start values in crashing_df use actual_start
        early_start_values = []
        actual_start_values = []
        
        for _, row in crashing_df.iterrows():
            if 'early_start' in row and 'actual_start' in row:
                early_start_values.append(row['early_start'])
                actual_start_values.append(row['actual_start'])
                print(f"   {row['id']}: early_start={row['early_start']}, actual_start={row['actual_start']}")
        
        if early_start_values == actual_start_values:
            print(f"✅ CRASHING FIX SUCCESSFUL: early_start values match actual_start values")
        else:
            print(f"❌ CRASHING FIX FAILED: early_start and actual_start values don't match")
    
    root.destroy()
    print(f"\n🎉 Test completed!")

if __name__ == "__main__":
    test_rcps_duration_fix()
