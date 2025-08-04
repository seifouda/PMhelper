#!/usr/bin/env python3
"""
Debug CSV loading in the auto-detect method
"""

import tkinter as tk
import csv
import sys
import os
sys.path.append('code')
from cpm_app import CPMDesktopApp

# Create a simple test CSV
test_csv_content = """id,activity,duration,predecessors,min_duration,crash_cost,resource_demand,normal_cost
A,Design Phase,5,,1,300,2,100
B,Requirements Analysis,3,,2,500,1,150
"""

test_csv_path = "debug_csv.csv"

def debug_csv_loading():
    """Debug the CSV loading process step by step"""
    # Create test CSV
    with open(test_csv_path, 'w', newline='') as f:
        f.write(test_csv_content)
    
    # Test the auto-detection logic
    root = tk.Tk()
    root.withdraw()
    app = CPMDesktopApp(root)
    
    print("Testing auto-detection and CSV loading...")
    
    try:
        # Test auto-detection
        with open(test_csv_path, 'r', newline='') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            print(f"CSV headers: {headers}")
            
            detected_mode = app.auto_detect_mode(headers)
            print(f"Detected mode: {detected_mode}")
            
            # Clear data but preserve mode
            print(f"Before clear: mode={app.analysis_mode}, activities={len(app.get_activities_data())}")
            app.clear_all(reset_mode=False)
            print(f"After clear: mode={app.analysis_mode}, activities={len(app.get_activities_data())}")
            
            # Set mode like auto-detect does
            app.analysis_mode = 'deterministic'
            app.current_analyzer = app.cpm_analyzer
            app.setup_deterministic_tree()
            app.mode_label.config(text="Mode: CPM (Auto-detected)", foreground="blue")
            print(f"After mode setup: mode={app.analysis_mode}")
            
            # Now try to load the CSV data
            file.seek(0)  # Reset file pointer
            reader = csv.DictReader(file)
            
            row_count = 0
            for row in reader:
                print(f"Processing row: {dict(row)}")
                
                activity_name = row.get('activity', '').strip()
                predecessors = row.get('predecessors', '').strip()
                min_duration = row.get('min_duration', '').strip()
                crash_cost = row.get('crash_cost', '0').strip()
                resource_demand = row.get('resource_demand', '0').strip()
                normal_cost = row.get('normal_cost', '0').strip()
                
                # Insert into tree
                item = app.tree.insert("", tk.END, values=(
                    row['id'],
                    activity_name,
                    row['duration'],
                    predecessors,
                    min_duration,
                    crash_cost,
                    resource_demand,
                    normal_cost
                ))
                print(f"Inserted tree item: {item}")
                row_count += 1
            
            print(f"Total rows processed: {row_count}")
            print(f"Final activities count: {len(app.get_activities_data())}")
            
    except Exception as e:
        print(f"Error during debug: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        root.destroy()
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)

if __name__ == "__main__":
    debug_csv_loading()
