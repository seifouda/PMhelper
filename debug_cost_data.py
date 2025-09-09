#!/usr/bin/env python3
"""
Debug script to check cost data in base analyzer
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from pmhelper.core.cpm_analyzer import CPMAnalyzer

def debug_cost_data():
    # Load sample data like in the main app
    analyzer = CPMAnalyzer()
    
    # Load the default sample data
    from pmhelper.utils.sample_data import get_sample_activities
    activities_data = get_sample_activities()
    
    print("Raw sample data:")
    for activity in activities_data:
        print(f"  Activity {activity['id']}: {activity}")
    
    # Use the load_activities_from_data method
    analyzer.load_activities_from_data(activities_data)
    
    print("\nAfter loading into analyzer:")
    for activity in analyzer.activities:
        print(f"  Activity {activity['id']}: crash_cost={activity.get('crash_cost', 'MISSING')}, normal_cost={activity.get('normal_cost', 'MISSING')}")
        print(f"    Full activity: {activity}")

if __name__ == "__main__":
    debug_cost_data()
