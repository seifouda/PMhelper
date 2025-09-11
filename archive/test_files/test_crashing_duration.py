#!/usr/bin/env python3
"""
Test RCPS crashin    # Calculate project durations
    cmp_duration = max([attrs['early_start'] + attrs['duration'] for _, attrs in G.nodes(data=True)])
    rcps_duration = max([attrs['EF'] for _, attrs in G.nodes(data=True)])
    
    print(f"📊 CPM Project Duration (theoretical): {cmp_duration}")
    print(f"📊 RCPS Project Duration (resource-constrained): {rcps_duration}") mock data to isolate the duration issue
"""

import sys
sys.path.append('src')
import pandas as pd
import networkx as nx
from pmhelper.gui.tabs.project_crashing_core import RCPSProjectCrashing
from pmhelper.core.rcps_analyzer import RCPSAnalyzer

def test_rcps_crashing_duration():
    print("[DEBUG] Testing RCPS Crashing Duration Issue")
    print("=" * 60)
    
    # Create mock RCPS network graph with actual_start times (duration = 33)
    G = nx.DiGraph()
    
    # Add mock activities with RCPS times (resource-constrained)
    activities = [
        {'id': 'A', 'duration': 5, 'early_start': 0, 'actual_start': 0, 'EF': 5, 'ES': 0},    # CPM: 0-5, RCPS: 0-5
        {'id': 'B', 'duration': 3, 'early_start': 0, 'actual_start': 0, 'EF': 3, 'ES': 0},    # CPM: 0-3, RCPS: 0-3  
        {'id': 'C', 'duration': 7, 'early_start': 5, 'actual_start': 5, 'EF': 12, 'ES': 5},   # CPM: 5-12, RCPS: 5-12
        {'id': 'D', 'duration': 5, 'early_start': 12, 'actual_start': 17, 'EF': 22, 'ES': 17}, # CPM: 12-17, RCPS: 17-22 (delayed)
        {'id': 'E', 'duration': 6, 'early_start': 12, 'actual_start': 12, 'EF': 18, 'ES': 12}, # CPM: 12-18, RCPS: 12-18
        {'id': 'F', 'duration': 8, 'early_start': 12, 'actual_start': 18, 'EF': 26, 'ES': 18}, # CPM: 12-20, RCPS: 18-26 (delayed)
        {'id': 'G', 'duration': 3, 'early_start': 17, 'actual_start': 22, 'EF': 25, 'ES': 22}, # CPM: 17-20, RCPS: 22-25 (delayed)
        {'id': 'H', 'duration': 4, 'early_start': 20, 'actual_start': 26, 'EF': 30, 'ES': 26}, # CPM: 20-24, RCPS: 26-30 (delayed)
        {'id': 'I', 'duration': 3, 'early_start': 24, 'actual_start': 30, 'EF': 33, 'ES': 30}, # CPM: 24-27, RCPS: 30-33 (delayed)
    ]
    
    # Add nodes to graph
    for activity in activities:
        G.add_node(activity['id'], **activity, 
                  min_duration=max(1, activity['duration'] - 2),  # Can crash by up to 2 units
                  crash_cost=100,  # Crash cost per unit
                  normal_cost=50,  # Normal cost per unit
                  float=0)  # All critical for simplicity
    
    # Add edges (dependencies)
    edges = [('A', 'C'), ('B', 'C'), ('C', 'D'), ('C', 'E'), ('C', 'F'), 
             ('D', 'G'), ('E', 'H'), ('F', 'H'), ('G', 'I'), ('H', 'I')]
    G.add_edges_from(edges)
    
    print(f"Created mock RCPS network graph with {len(G.nodes())} nodes")
    
    # Calculate project durations
    cpm_duration = max([attrs['early_start'] + attrs['duration'] for _, attrs in G.nodes(data=True)])
    rcps_duration = max([attrs['EF'] for _, attrs in G.nodes(data=True)])
    
    print(f"📊 CPM Project Duration (theoretical): {cpm_duration}")
    print(f"📊 RCPS Project Duration (resource-constrained): {rcps_duration}")
    
    # Test 1: Create RCPS crashing with CPM-style network (ES = early_start)
    print(f"\n🔧 TEST 1: RCPS Crashing with CPM-style ES values")
    G_cpm = G.copy()
    for node in G_cpm.nodes():
        G_cpm.nodes[node]['ES'] = G_cpm.nodes[node]['early_start']  # Use original CPM early_start
        G_cpm.nodes[node]['EF'] = G_cpm.nodes[node]['early_start'] + G_cpm.nodes[node]['duration']
    
    analyzer1 = RCPSAnalyzer(G_cpm, resource_limit=10)
    crashing1 = RCPSProjectCrashing(analyzer1, resource_limit=10)
    result1 = crashing1._lowest_cost_strategy(target_duration=25, max_iterations=5)
    print(f"Result 1 - Original duration: {result1.original_duration}")
    
    # Test 2: Create RCPS crashing with RCPS-style network (ES = actual_start) 
    print(f"\n🔧 TEST 2: RCPS Crashing with RCPS-style ES values")
    G_rcps = G.copy()
    for node in G_rcps.nodes():
        G_rcps.nodes[node]['ES'] = G_rcps.nodes[node]['actual_start']  # Use RCPS actual_start
        G_rcps.nodes[node]['early_start'] = G_rcps.nodes[node]['actual_start']  # Update early_start too
        # EF should already be correct from mock data
    
    analyzer2 = RCPSAnalyzer(G_rcps, resource_limit=10)  
    crashing2 = RCPSProjectCrashing(analyzer2, resource_limit=10)
    result2 = crashing2._lowest_cost_strategy(target_duration=30, max_iterations=5)
    print(f"Result 2 - Original duration: {result2.original_duration}")
    
    print(f"\n📋 Summary:")
    print(f"   Test 1 (CPM ES): Started from {result1.original_duration}")
    print(f"   Test 2 (RCPS ES): Started from {result2.original_duration}")
    print(f"   Expected difference: {rcps_duration - cpm_duration} time units due to resource constraints")

if __name__ == "__main__":
    test_rcps_crashing_duration()
