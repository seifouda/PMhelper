#!/usr/bin/env python3
"""
Analyze why RCPS crashing isn't reducing duration despite working
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.pmhelper.gui.tabs.rcps_tab import RCPSTab
from pmhelper.gui.tabs.project_crashing_core import RCPSProjectCrashing, CrashingStrategy, OptimizationObjective
from src.pmhelper.core.rcps_analyzer import RCPSAnalyzer

def analyze_crashing_issue():
    print("🔍 ANALYZING RCPS CRASHING ISSUE")
    print("="*80)
    
    # Create mock GUI components
    class MockWidget:
        def config(self, **kwargs): pass
        def delete(self, *args): pass
        def insert(self, *args): pass
        def get(self, *args): return ""
        
    mock_widgets = {
        'summary_text': MockWidget(),
        'log_text': MockWidget(),
        'metrics_text': MockWidget()
    }
    
    # Create RCPS tab instance
    rcps_tab = RCPSTab(None, **mock_widgets)
    
    # Load sample data
    sample_data = {
        'A': {'name': 'Design Phase', 'duration': 5, 'predecessors': '', 'resource': 2, 'crash_cost': 100, 'min_duration': 3},
        'B': {'name': 'Requirements Analysis', 'duration': 3, 'predecessors': '', 'resource': 1, 'crash_cost': 150, 'min_duration': 2},
        'C': {'name': 'Architecture Design', 'duration': 7, 'predecessors': 'A,B', 'resource': 3, 'crash_cost': 200, 'min_duration': 4},
        'D': {'name': 'Database Design', 'duration': 5, 'predecessors': 'C', 'resource': 1, 'crash_cost': 120, 'min_duration': 3},
        'E': {'name': 'Frontend Development', 'duration': 6, 'predecessors': 'C', 'resource': 4, 'crash_cost': 180, 'min_duration': 4},
        'F': {'name': 'Backend Development', 'duration': 8, 'predecessors': 'C', 'resource': 5, 'crash_cost': 250, 'min_duration': 5},
        'G': {'name': 'Testing', 'duration': 3, 'predecessors': 'D', 'resource': 2, 'crash_cost': 90, 'min_duration': 2},
        'H': {'name': 'Deployment', 'duration': 4, 'predecessors': 'E,F', 'resource': 1, 'crash_cost': 160, 'min_duration': 2},
        'I': {'name': 'Documentation', 'duration': 3, 'predecessors': 'G,H', 'resource': 2, 'crash_cost': 110, 'min_duration': 2}
    }
    
    print("1. 📊 Loading data into RCPS...")
    rcps_tab.update_table_from_data(sample_data)
    
    print("2. 🔄 Running RCPS analysis...")
    rcps_tab.run_rcps(resource_limit=5, priority_rule='minimum_slack')
    
    # Get RCPS analyzer and data
    analyzer = rcps_tab.rcps_analyzer
    network_graph = rcps_tab.rcps_network_graph
    
    print(f"3. 📈 RCPS Analysis Results:")
    print(f"   Original duration: {analyzer.project_duration}")
    
    # Check critical path
    critical_activities = []
    for node_id, node_data in network_graph.nodes(data=True):
        if node_data.get('critical', False):
            critical_activities.append(node_id)
    
    print(f"   Critical path: {' -> '.join(critical_activities)}")
    
    # Analyze crash potential
    print("\n4. 💰 Crash Cost Analysis:")
    for activity_id in critical_activities:
        node_data = network_graph.nodes[activity_id]
        duration = node_data.get('duration', 0)
        crash_cost = node_data.get('crash_cost', 0)
        min_duration = node_data.get('min_duration', duration)
        crashable_time = duration - min_duration
        
        print(f"   {activity_id}: duration={duration}, min_duration={min_duration}, "
              f"crashable={crashable_time}, cost={crash_cost}")
    
    print("\n5. 🚀 Testing RCPS Crashing with different parameters...")
    
    # Test with different target durations
    crashing_engine = RCPSProjectCrashing(analyzer, resource_limit=5)
    
    for target_duration in [30, 25, 20, 15]:
        print(f"\n   Testing target duration: {target_duration}")
        try:
            result = crashing_engine.run(
                target_duration=target_duration,
                strategy=CrashingStrategy.LOWEST_COST,
                objective=OptimizationObjective.MINIMIZE_COST
            )
            print(f"   ✅ Result: {result.original_duration} -> {result.final_duration}")
            print(f"      Cost: {result.total_crash_cost}")
            print(f"      Reason: {result.termination_reason}")
            
            if result.crashed_activities:
                print(f"      Crashed: {list(result.crashed_activities.keys())}")
            else:
                print("      No activities crashed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n6. 🔍 Checking activity data structure...")
    activities = crashing_engine.analyzer.activities
    print(f"   Activities count: {len(activities)}")
    
    for act_id, act_data in activities.items():
        if act_id in ['A', 'B', 'C']:  # Sample a few
            print(f"   {act_id}: {act_data}")
    
    print("\n" + "="*80)
    print("🎯 ANALYSIS COMPLETE")

if __name__ == "__main__":
    analyze_crashing_issue()
