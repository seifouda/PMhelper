#!/usr/bin/env python3
"""
Quick debug of why RCPS crashing isn't working - focusing on the algorithm logic
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from pmhelper.gui.tabs.project_crashing_core import RCPSProjectCrashing, CrashingStrategy, OptimizationObjective
from src.pmhelper.core.rcps_analyzer import RCPSAnalyzer
import pandas as pd

def quick_debug():
    print("🔧 QUICK RCPS CRASHING DEBUG")
    print("="*60)
    
    # Create sample data that should definitely be crashable
    sample_data = {
        'id': ['A', 'B', 'C'],
        'name': ['Design', 'Development', 'Testing'],
        'duration': [10, 15, 8],  # Large durations
        'early_start': [0, 10, 25],
        'actual_start': [0, 10, 25], 
        'predecessors': ['', 'A', 'B'],
        'resource': [1, 1, 1],
        'crash_cost': [50, 100, 75],  # Reasonable crash costs
        'min_duration': [5, 8, 4]  # Significant crash potential
    }
    
    df = pd.DataFrame(sample_data)
    print("📊 Sample data:")
    print(df[['id', 'duration', 'min_duration', 'crash_cost']])
    
    # Create RCPS analyzer
    analyzer = RCPSAnalyzer()
    analyzer.analyze(df, resource_limit=5, priority_rule='minimum_slack')
    
    print(f"\n📈 RCPS Analysis:")
    print(f"   Project duration: {analyzer.project_duration}")
    print(f"   Activities: {len(analyzer.activities)}")
    
    # Check critical path
    critical_activities = []
    for activity_id, activity in analyzer.activities.items():
        if activity.get('critical', False):
            critical_activities.append(activity_id)
    
    print(f"   Critical path: {critical_activities}")
    
    # Check crash potential
    print(f"\n💰 Crash potential:")
    for activity_id, activity in analyzer.activities.items():
        duration = activity.get('duration', 0)
        min_duration = activity.get('min_duration', duration)
        crash_cost = activity.get('crash_cost', 0)
        crashable = duration - min_duration
        print(f"   {activity_id}: duration={duration}, min={min_duration}, crashable={crashable}, cost={crash_cost}")
    
    # Test crashing
    print(f"\n🚀 Testing RCPS Crashing:")
    crashing_engine = RCPSProjectCrashing(analyzer, resource_limit=5)
    
    original_duration = analyzer.project_duration
    target_duration = original_duration - 5  # Try to reduce by 5
    
    print(f"   Target: {original_duration} -> {target_duration}")
    
    result = crashing_engine.run(
        target_duration=target_duration,
        strategy=CrashingStrategy.LOWEST_COST,
        objective=OptimizationObjective.MINIMIZE_COST,
        max_iterations=10  # Reduced for debugging
    )
    
    print(f"\n📋 Results:")
    print(f"   Original: {result.original_duration}")
    print(f"   Final: {result.final_duration}")
    print(f"   Target: {result.target_duration}")
    print(f"   Cost: {result.total_crash_cost}")
    print(f"   Reason: {result.termination_reason}")
    print(f"   Iterations: {result.iterations_used}")
    
    if result.crash_log:
        print(f"\n📝 Crash log ({len(result.crash_log)} entries):")
        for i, entry in enumerate(result.crash_log[:5]):  # Show first 5
            print(f"   {i+1}: {entry.get('activity', 'N/A')} crashed {entry.get('crash_amount', 0)} "
                  f"for cost {entry.get('cost', 0)}, duration now {entry.get('current_project_duration', 'N/A')}")
    else:
        print(f"   ❌ No crash log entries!")
        
    # Check if the issue is in the algorithm setup
    print(f"\n🔍 Debugging algorithm state:")
    
    # Check network graph
    if hasattr(analyzer, 'G'):
        G = analyzer.G
        print(f"   Graph nodes: {len(G.nodes)}")
        for node_id in ['A', 'B', 'C']:
            if node_id in G.nodes:
                node_data = G.nodes[node_id]
                print(f"   {node_id}: dur={node_data.get('duration', '?')}, "
                      f"float={node_data.get('float', '?')}, "
                      f"EF={node_data.get('EF', '?')}")
    else:
        print("   ❌ No graph found in analyzer!")

if __name__ == "__main__":
    quick_debug()
