#!/usr/bin/env python3

import sys
from pathlib import Path
import math
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.utils.file_handlers import FileHandler

def debug_variance_calculation():
    """Trace variance calculation step by step"""
    print("=" * 80)
    print("VARIANCE CALCULATION DEBUG")
    print("=" * 80)
    
    # Load test PERT data
    file_handler = FileHandler()
    activities_data = file_handler.load_csv('pert_test.csv')
    
    print("1. Individual Activity Variances (Manual vs Stored):")
    for activity in activities_data[:5]:  # First 5 activities
        o = float(activity.get('optimistic', 0))
        m = float(activity.get('most_likely', 0))
        p = float(activity.get('pessimistic', 0))
        variance_manual = ((p - o) / 6) ** 2
        
        print(f"  {activity['id']}: O={o}, M={m}, P={p}")
        print(f"    Manual Variance: ((P-O)/6)² = (({p}-{o})/6)² = {variance_manual:.3f}")
    
    # Test the PERT analyzer
    analyzer = PERTAnalyzer()
    print(f"\n2. Loading activities through PERT analyzer...")
    activities = analyzer.load_activities_from_pert_data(activities_data)
    
    print(f"\nStored variances in activities:")
    for activity in activities[:5]:
        print(f"  {activity['id']}: Stored variance = {activity['variance']:.3f}")
    
    # Run analysis
    print(f"\n3. Running PERT analysis...")
    G, critical_paths, critical_activities = analyzer.analyze(activities_data)
    
    print(f"\nCritical Path: {critical_paths[0] if critical_paths else 'None'}")
    print(f"Critical Activities: {critical_activities}")
    
    print(f"\n4. Critical Path Variances:")
    total_variance_manual = 0
    if critical_paths and critical_paths[0]:
        for activity in critical_paths[0]:
            if activity not in ['START', 'END']:
                if activity in G.nodes:
                    variance = G.nodes[activity]['variance']
                    print(f"  {activity}: Network variance = {variance:.3f}")
                    total_variance_manual += variance
                else:
                    print(f"  {activity}: NOT FOUND in network nodes!")
    
    print(f"\n5. Project Statistics Comparison:")
    print(f"  Manual Total Variance: {total_variance_manual:.3f}")
    print(f"  Manual Std Dev: {np.sqrt(total_variance_manual):.3f}")
    print(f"  Analyzer project_variance: {analyzer.project_variance}")
    print(f"  Analyzer project_std: {analyzer.project_std}")
    
    # Check get_project_statistics
    stats = analyzer.get_project_statistics()
    if stats:
        print(f"\n6. get_project_statistics() returns:")
        print(f"  variance = {stats.get('variance', 'MISSING')}")
        print(f"  std_deviation = {stats.get('std_deviation', 'MISSING')}")
        print(f"  expected_duration = {stats.get('expected_duration', 'MISSING')}")
    else:
        print(f"\n6. get_project_statistics() returns: None")
    
    print(f"\n7. Variance Calculation Issues Check:")
    if abs(total_variance_manual - analyzer.project_variance) > 0.001:
        print(f"  ❌ VARIANCE MISMATCH! Manual: {total_variance_manual:.3f}, Stored: {analyzer.project_variance}")
    else:
        print(f"  ✅ Variance calculation matches")
    
    if abs(np.sqrt(total_variance_manual) - analyzer.project_std) > 0.001:
        print(f"  ❌ STD DEV MISMATCH! Manual: {np.sqrt(total_variance_manual):.3f}, Stored: {analyzer.project_std}")
    else:
        print(f"  ✅ Standard deviation calculation matches")

if __name__ == "__main__":
    debug_variance_calculation()
