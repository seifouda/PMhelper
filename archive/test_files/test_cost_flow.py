#!/usr/bin/env python3
"""
Simple test to trace cost data in RCPS crashing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_cost_flow():
    # Simulate the sample data with costs
    from pmhelper.utils.file_handlers import FileHandler
    from pmhelper.core.cpm_analyzer import CPMAnalyzer
    
    print("=== STEP 1: Get Sample Data ===")
    sample_data = FileHandler.get_sample_cpm_data()
    
    for activity in sample_data:
        print(f"Activity {activity['id']}: crash_cost={activity.get('crash_cost', 'MISSING')}, normal_cost={activity.get('normal_cost', 'MISSING')}")
    
    print("\n=== STEP 2: Load into CPM Analyzer ===")
    analyzer = CPMAnalyzer()
    activities = analyzer.load_activities_from_data(sample_data)
    
    for activity in activities:
        print(f"Activity {activity['id']}: crash_cost={activity.get('crash_cost', 'MISSING')}, normal_cost={activity.get('normal_cost', 'MISSING')}")
        print(f"  Full activity data: {activity}")

if __name__ == "__main__":
    test_cost_flow()
