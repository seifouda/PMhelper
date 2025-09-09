#!/usr/bin/env python3
"""
RCPS Table Data Structure Analyzer

Checks what data is available in RCPS table and how to best integrate it.
"""

import tkinter as tk
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def check_rcps_table_data():
    """Check what RCPS table data is available"""
    
    print("=" * 80)
    print("RCPS TABLE DATA STRUCTURE ANALYSIS")
    print("=" * 80)
    
    try:
        from pmhelper.gui.main_window import MainWindow
        
        # Create application
        root = tk.Tk()
        app = MainWindow(root)
        
        print("1. 🚀 Loading sample data and running analyses...")
        app.load_sample_data()
        app.run_cpm_analysis() 
        app.show_rcps_tab()
        
        # Run RCPS analysis to generate table data
        rcps_tab = app.rcps_tab
        # Use the correct method signature for run_rcps
        rcps_tab.run_rcps()
        
        print("2. 📊 Checking RCPS table structure...")
        
        # Check RCPS table structure
        if hasattr(rcps_tab, 'rcps_table_data') and rcps_tab.rcps_table_data is not None:
            table = rcps_tab.rcps_table_data
            
            print(f"\n✅ RCPS TABLE DATA FOUND:")
            print(f"   Shape: {table.shape}")
            print(f"   Columns: {list(table.columns)}")
            
            print(f"\n📋 SAMPLE RCPS DATA:")
            activity_count = 0
            for idx, row in table.iterrows():
                if row.get('id') not in ['RA', 'RS']:  # Skip resource rows
                    activity_count += 1
                    print(f"   Activity {row.get('id')}:")
                    print(f"      Duration: {row.get('duration')}")
                    print(f"      Early Start: {row.get('early_start')}")
                    print(f"      Early Finish: {row.get('early_finish', 'N/A')}")
                    print(f"      Late Start: {row.get('late_start', 'N/A')}")
                    print(f"      Late Finish: {row.get('late_finish')}")
                    print(f"      Actual Start: {row.get('actual_start')}")
                    print(f"      Float: {row.get('float')}")
                    print(f"      Critical: {row.get('critical', 'N/A')}")
                    print(f"      Crash Cost: {row.get('crash_cost', 'N/A')}")
                    print(f"      Min Duration: {row.get('min_duration', 'N/A')}")
                    print()
            
            print(f"🔢 SUMMARY:")
            print(f"   Total activities found: {activity_count}")
            
            # Check if RCPS table has all required data for crashing
            required_fields = ['id', 'duration', 'early_start', 'late_finish', 'actual_start', 'float', 'crash_cost', 'min_duration']
            available_fields = [field for field in required_fields if field in table.columns]
            missing_fields = [field for field in required_fields if field not in table.columns]
            
            print(f"\n🎯 CRASHING COMPATIBILITY CHECK:")
            print(f"   Required fields: {required_fields}")
            print(f"   Available fields: {available_fields}")
            if missing_fields:
                print(f"   Missing fields: {missing_fields}")
            
            # Calculate RCPS project duration
            if 'late_finish' in table.columns:
                max_late_finish = table[table['id'].isin(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'])]['late_finish'].max()
                print(f"   RCPS Project Duration: {max_late_finish}")
            
            if 'actual_start' in table.columns:
                # Check for resource delays
                has_delays = any(table[table['id'].isin(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'])]['actual_start'] > 
                               table[table['id'].isin(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'])]['early_start'])
                print(f"   Resource Delays Detected: {has_delays}")
            
            # Determine best approach based on available data
            if len(missing_fields) == 0:
                print(f"\n✅ RECOMMENDATION: OPTION 1 (Direct Table Data Conversion)")
                print(f"   All required fields available for direct conversion")
                print(f"   Can create analyzer directly from RCPS table data")
            elif len(missing_fields) <= 2:
                print(f"\n⚠️  RECOMMENDATION: OPTION 4 (Data Injection Approach)")
                print(f"   Most fields available, can inject RCPS data into existing analyzer")
            else:
                print(f"\n❌ RECOMMENDATION: OPTION 2 (Hybrid Analyzer Approach)")
                print(f"   Too many missing fields, need complex hybrid approach")
                
        else:
            print(f"\n❌ NO RCPS TABLE DATA FOUND")
            print(f"   Need to ensure RCPS analysis runs successfully first")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_rcps_table_data()
