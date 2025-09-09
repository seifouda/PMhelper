#!/usr/bin/env python3
"""
Test RCPS Table Data Access

This script will test the new get_rcps_table_data method to see exactly
what data is in the RCPS table and if A and B are present.
"""

import tkinter as tk
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def test_rcps_table_data_access():
    """Test accessing RCPS table data"""
    
    print("🧪 TESTING RCPS TABLE DATA ACCESS")
    print("=" * 60)
    
    try:
        # Import and create application
        from pmhelper.gui.main_window import MainWindow
        
        root = tk.Tk()
        app = MainWindow(root)
        
        print("1. ✅ Application created")
        
        # Create RCPS tab
        app.show_rcps_tab()
        rcps_tab = app.rcps_tab
        
        print("2. ✅ RCPS tab created")
        
        # Test table data access before running RCPS
        print("\n3. 📊 Testing table data access BEFORE running RCPS:")
        table_data = rcps_tab.get_rcps_table_data()
        print(f"   Result: {table_data}")
        
        # Simulate running RCPS analysis
        print("\n4. 🚀 Simulating RCPS analysis...")
        
        # First, run CPM analysis (required for RCPS)
        print("   4a. Running CPM analysis first...")
        app.run_cpm_analysis()
        print("   ✅ CPM analysis completed")
        
        # Get input data
        df_gantt = app.get_activities_data()
        print(f"   Input activities: {len(df_gantt)} activities")
        
        # Handle both DataFrame and list formats
        if hasattr(df_gantt, 'to_dict'):
            # It's a pandas DataFrame
            activity_ids = list(df_gantt['id']) if 'id' in df_gantt.columns else [f"ACT_{i}" for i in range(len(df_gantt))]
        else:
            # It's a list of dictionaries
            activity_ids = [act.get('id', f'ACT_{i}') for i, act in enumerate(df_gantt)]
        
        print(f"   Activity IDs: {activity_ids}")
        
        # Now run RCPS analysis
        print("   4b. Running RCPS analysis...")
        try:
            rcps_tab.run_rcps()
            print("   ✅ RCPS analysis completed")
        except Exception as e:
            print(f"   ❌ RCPS analysis failed: {e}")
            import traceback
            traceback.print_exc()
            
        # Test table data access after running RCPS
        print("\n5. 📊 Testing table data access AFTER running RCPS:")
        table_data_after = rcps_tab.get_rcps_table_data()
        
        if table_data_after is not None:
            print(f"   ✅ Table data retrieved!")
            print(f"   📊 Shape: {table_data_after.shape}")
            print(f"   📊 Columns: {list(table_data_after.columns)}")
            
            # Check activity IDs
            if 'id' in table_data_after.columns:
                activity_ids = list(table_data_after['id'])
                print(f"   📋 Activity IDs in table: {activity_ids}")
                
                # Specifically check for A and B
                has_A = 'A' in activity_ids
                has_B = 'B' in activity_ids
                print(f"   🔍 Activity A present: {has_A}")
                print(f"   🔍 Activity B present: {has_B}")
                
                if has_A and has_B:
                    print("   ✅ BOTH A and B are present in RCPS table!")
                else:
                    print("   ❌ A and/or B missing from RCPS table")
                    
                    # Show which activities are missing
                    expected_ids = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
                    missing_ids = [id for id in expected_ids if id not in activity_ids]
                    extra_ids = [id for id in activity_ids if id not in expected_ids]
                    
                    if missing_ids:
                        print(f"   🚨 Missing activities: {missing_ids}")
                    if extra_ids:
                        print(f"   ➕ Extra activities: {extra_ids}")
        else:
            print("   ❌ No table data available")
        
        # Test RCPS crashing tab access
        print("\n6. 🎯 Testing RCPS Crashing tab access:")
        app.show_rcps_crashing_tab()
        rcps_crashing_tab = app.rcps_crashing_tab
        
        if rcps_crashing_tab and hasattr(rcps_crashing_tab, 'rcps_tab'):
            print("   ✅ RCPS Crashing tab has reference to RCPS tab")
            
            # Test getting analyzer through crashing tab
            analyzer = rcps_crashing_tab.get_rcps_analyzer()
            print(f"   📊 Analyzer through crashing tab: {type(analyzer)}")
            
            # Test getting resource limit
            resource_limit = rcps_crashing_tab.get_resource_limit()
            print(f"   📊 Resource limit: {resource_limit}")
            
        else:
            print("   ❌ RCPS Crashing tab not properly linked")
        
        root.destroy()
        
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY:")
        if table_data_after is not None:
            activity_ids = list(table_data_after['id']) if 'id' in table_data_after.columns else []
            has_A = 'A' in activity_ids
            has_B = 'B' in activity_ids
            
            if has_A and has_B:
                print("✅ SUCCESS: A and B are present in RCPS table")
                print("✅ RCPS Crashing should have access to complete data")
            else:
                print("❌ ISSUE: A and/or B missing from RCPS table")
                print("💡 This explains why your original debug log showed only C-I")
        else:
            print("❌ ISSUE: No RCPS table data generated")
        
    except Exception as e:
        print(f"❌ ERROR during test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_rcps_table_data_access()
