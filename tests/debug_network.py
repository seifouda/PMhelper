#!/usr/bin/env python3
"""
Debug Network Building

Test network building with detailed output to understand the dependency issues.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from pmhelper.core.network_builder import NetworkBuilder
import networkx as nx


def debug_network_building():
    """Debug network building step by step"""
    print("=" * 80)
    print("NETWORK BUILDING DEBUG")
    print("=" * 80)
    
    # Test activities with known dependencies
    test_activities = [
        {'id': 'A', 'duration': 3, 'predecessors': []},           
        {'id': 'B', 'duration': 2, 'predecessors': ['A']},       
        {'id': 'C', 'duration': 4, 'predecessors': ['A']},         
        {'id': 'D', 'duration': 1, 'predecessors': ['B', 'C']}, # D depends on both B and C
    ]
    
    print("Input Activities:")
    for act in test_activities:
        print(f"  {act['id']}: Duration={act['duration']}, Predecessors={act['predecessors']}")
    
    # Step 1: Build network
    builder = NetworkBuilder()
    G = builder.build_network(test_activities)
    
    print("\nStep 1: Network Structure")
    print(f"Nodes: {list(G.nodes())}")
    print(f"Edges: {list(G.edges())}")
    
    print("\nNode Details:")
    for node in G.nodes():
        node_data = G.nodes[node]
        predecessors = list(G.predecessors(node))
        successors = list(G.successors(node))
        print(f"  {node}: Duration={node_data.get('duration', 0)}, Pred={predecessors}, Succ={successors}")
    
    # Step 2: Forward pass
    print("\nStep 2: Forward Pass")
    G = builder.forward_pass(G)
    
    print("After Forward Pass:")
    for node in nx.topological_sort(G):
        node_data = G.nodes[node]
        es = node_data.get('ES', 0)
        ef = node_data.get('EF', 0)
        duration = node_data.get('duration', 0)
        predecessors = list(G.predecessors(node))
        
        # Calculate expected ES manually
        if predecessors:
            pred_efs = [G.nodes[pred].get('EF', 0) for pred in predecessors]
            expected_es = max(pred_efs) if pred_efs else 0
        else:
            expected_es = 0
            
        print(f"  {node}: ES={es} (expected {expected_es}), EF={ef}, Duration={duration}, Pred={predecessors}")
    
    # Step 3: Backward pass
    print("\nStep 3: Backward Pass")
    G = builder.backward_pass(G)
    
    project_duration = max(G.nodes[node].get('EF', 0) for node in G.nodes())
    print(f"Project Duration: {project_duration}")
    
    print("After Backward Pass:")
    for node in reversed(list(nx.topological_sort(G))):
        node_data = G.nodes[node]
        ls = node_data.get('LS', 0)
        lf = node_data.get('LF', 0)
        duration = node_data.get('duration', 0)
        successors = list(G.successors(node))
        
        print(f"  {node}: LS={ls}, LF={lf}, Duration={duration}, Succ={successors}")
    
    # Step 4: Calculate float
    print("\nStep 4: Float Calculation")
    G = builder.calculate_float(G)
    
    print("Final Results:")
    for node in G.nodes():
        if node not in ['START', 'END']:
            node_data = G.nodes[node]
            es = node_data.get('ES', 0)
            ef = node_data.get('EF', 0)
            ls = node_data.get('LS', 0)
            lf = node_data.get('LF', 0)
            float_val = node_data.get('float', 0)
            
            print(f"  {node}: ES={es}, EF={ef}, LS={ls}, LF={lf}, Float={float_val}")
    
    # Step 5: Identify critical path
    print("\nStep 5: Critical Path Analysis")
    critical_paths, critical_activities = builder.identify_critical_path(G)
    
    print(f"Critical Paths: {critical_paths}")
    print(f"Critical Activities: {critical_activities}")
    
    # Manual verification
    print("\nManual Verification:")
    print("Expected:")
    print("  A: ES=0, EF=3, LS=0, LF=3, Float=0 (Critical)")
    print("  B: ES=3, EF=5, LS=5, LF=7, Float=2 (Non-critical)")
    print("  C: ES=3, EF=7, LS=3, LF=7, Float=0 (Critical)")
    print("  D: ES=7, EF=8, LS=7, LF=8, Float=0 (Critical)")
    print("  Critical Path: START→A→C→D→END")
    
    return G


if __name__ == "__main__":
    debug_network_building()
