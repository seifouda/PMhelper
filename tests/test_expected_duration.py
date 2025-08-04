#!/usr/bin/env python3

import sys
from pathlib import Path
import math

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.utils.file_handlers import FileHandler

def test_expected_duration_calculation():
    print("Testing Expected Duration Calculation")
    print("=" * 50)
    
    # Load test PERT data
    file_handler = FileHandler()
    activities_data = file_handler.load_csv('pert_test.csv')
    
    # Test the new two-phase analysis
    analyzer = PERTAnalyzer()
    G, critical_paths, critical_activities = analyzer.analyze(activities_data)
    
    critical_path = critical_paths[0] if critical_paths else []
    print(f"Critical Path: {critical_path}")
    
    # Calculate statistical expected duration (precise)
    statistical_expected_duration = 0
    print(f"\nStatistical Expected Duration Calculation:")
    for activity_id in critical_path:
        if activity_id not in ['START', 'END']:
            # Find the original activity data
            for activity_data in activities_data:
                if activity_data.get('id') == activity_id:
                    opt = float(activity_data.get('optimistic', 0))
                    most = float(activity_data.get('most_likely', 0))
                    pess = float(activity_data.get('pessimistic', 0))
                    expected_time = (opt + 4 * most + pess) / 6
                    statistical_expected_duration += expected_time
                    print(f"  {activity_id}: ({opt} + 4*{most} + {pess})/6 = {expected_time:.2f}")
                    break
    
    print(f"\nStatistical Expected Duration: {statistical_expected_duration:.1f}")
    
    # Calculate scheduling duration (integer-based)
    scheduling_duration = 0
    print(f"\nScheduling Duration Calculation (Integer-based):")
    for activity_id in critical_path:
        if activity_id not in ['START', 'END']:
            # Find the original activity data
            for activity_data in activities_data:
                if activity_data.get('id') == activity_id:
                    opt = float(activity_data.get('optimistic', 0))
                    most = float(activity_data.get('most_likely', 0))
                    pess = float(activity_data.get('pessimistic', 0))
                    expected_time = (opt + 4 * most + pess) / 6
                    ceiling_time = math.ceil(expected_time)
                    scheduling_duration += ceiling_time
                    print(f"  {activity_id}: ceil({expected_time:.2f}) = {ceiling_time}")
                    break
    
    print(f"\nScheduling Duration: {scheduling_duration}")
    
    # Verify with network EF
    max_ef = 0
    for node in G.nodes():
        ef = G.nodes[node].get('EF', 0)
        if ef > max_ef:
            max_ef = ef
    
    print(f"Network Max EF: {max_ef}")
    
    print(f"\nSummary:")
    print(f"  Statistical Expected Duration: {statistical_expected_duration:.1f} (should be ~42.8)")
    print(f"  Scheduling Duration: {scheduling_duration} (integer sum)")
    print(f"  Network EF: {max_ef} (should match scheduling)")
    
    return statistical_expected_duration, scheduling_duration, max_ef

if __name__ == "__main__":
    test_expected_duration_calculation()
