#!/usr/bin/env python3
"""
Network Building Debug

Test to check if the network dependencies are being built correctly.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from pmhelper.core.cpm_analyzer import CPMAnalyzer
from pmhelper.core.network_builder import NetworkBuilder


def debug_network_dependencies():
    """Debug network dependency building step by step"""
    print("=" * 80)
    print("NETWORK DEPENDENCY DEBUG")
    print("=" * 80)
    
    # Test data with clear dependencies
    test_activities = [
        {'id': 'A', 'duration': 3, 'predecessors': []},
        {'id': 'B', 'duration': 2, 'predecessors': ['A']},      # B depends on A
        {'id': 'C', 'duration': 4, 'predecessors': ['A']},      # C depends on A  
        {'id': 'D', 'duration': 1, 'predecessors': ['B', 'C']}, # D depends on B and C
    ]
    
    print("Input activities:")
    for act in test_activities:
        print(f"  {act['id']}: Duration={act['duration']}, Predecessors={act['predecessors']}")
    
    # Step 1: Check CPMAnalyzer's load_activities_from_data
    print("\nStep 1: CPMAnalyzer.load_activities_from_data")
    analyzer = CPMAnalyzer()
    processed_activities = analyzer.load_activities_from_data(test_activities)
    
    print("Processed activities:")
    for act in processed_activities:
        print(f"  {act['id']}: Duration={act['duration']}, Predecessors={act['predecessors']}")
    
    # Step 2: Check NetworkBuilder.build_network
    print("\nStep 2: NetworkBuilder.build_network")
    builder = NetworkBuilder()
    G = builder.build_network(processed_activities)
    
    print(f"Network built: {len(G.nodes())} nodes, {len(G.edges())} edges")
    print("Nodes:", list(G.nodes()))
    print("Edges:", list(G.edges()))
    
    print("\nDependency verification:")
    for node in G.nodes():
        predecessors = list(G.predecessors(node))
        successors = list(G.successors(node))
        print(f"  {node}: Predecessors={predecessors}, Successors={successors}")
    
    # Step 3: Check if dependencies match expected
    expected_deps = {
        'A': [],
        'B': ['A'],
        'C': ['A'],
        'D': ['B', 'C']
    }
    
    print("\nDependency validation:")
    for node, expected_preds in expected_deps.items():
        if G.has_node(node):
            actual_preds = [p for p in G.predecessors(node) if p not in ['START']]
            if set(actual_preds) == set(expected_preds):
                print(f"  ✅ {node}: Expected {expected_preds}, Got {actual_preds}")
            else:
                print(f"  ❌ {node}: Expected {expected_preds}, Got {actual_preds}")
        else:
            print(f"  ❌ {node}: Not found in graph")
    
    return G


def debug_timing_with_correct_dependencies():
    """Test timing calculations with verified dependencies"""
    print("\n" + "=" * 80)
    print("TIMING CALCULATION WITH VERIFIED DEPENDENCIES")
    print("=" * 80)
    
    G = debug_network_dependencies()
    
    if G:
        builder = NetworkBuilder()
        
        print("\nInitial node attributes:")
        for node in G.nodes():
            print(f"  {node}: {G.nodes[node]}")
        
        print("\nExecuting forward pass...")
        G = builder.forward_pass(G)
        
        print("After forward pass (ES, EF):")
        for node in G.nodes():
            if node not in ['START', 'END']:
                es = G.nodes[node].get('ES', 'MISSING')
                ef = G.nodes[node].get('EF', 'MISSING')
                print(f"  {node}: ES={es}, EF={ef}")
        
        print("\nExecuting backward pass...")
        G = builder.backward_pass(G)
        
        print("After backward pass (LS, LF):")
        for node in G.nodes():
            if node not in ['START', 'END']:
                ls = G.nodes[node].get('LS', 'MISSING')
                lf = G.nodes[node].get('LF', 'MISSING')
                print(f"  {node}: LS={ls}, LF={lf}")
        
        print("\nExecuting float calculation...")
        G = builder.calculate_float(G)
        
        print("Final results:")
        for node in G.nodes():
            if node not in ['START', 'END']:
                es = G.nodes[node].get('ES')
                ef = G.nodes[node].get('EF')
                ls = G.nodes[node].get('LS')
                lf = G.nodes[node].get('LF')
                float_val = G.nodes[node].get('float')
                print(f"  {node}: ES={es}, EF={ef}, LS={ls}, LF={lf}, Float={float_val}")
        
        print("\nExpected vs Actual:")
        expected = {
            'A': {'ES': 0, 'EF': 3, 'LS': 0, 'LF': 3, 'Float': 0},
            'B': {'ES': 3, 'EF': 5, 'LS': 5, 'LF': 7, 'Float': 2},
            'C': {'ES': 3, 'EF': 7, 'LS': 3, 'LF': 7, 'Float': 0},
            'D': {'ES': 7, 'EF': 8, 'LS': 7, 'LF': 8, 'Float': 0},
        }
        
        for node, exp_vals in expected.items():
            if G.has_node(node):
                actual_vals = {
                    'ES': G.nodes[node].get('ES'),
                    'EF': G.nodes[node].get('EF'),
                    'LS': G.nodes[node].get('LS'),
                    'LF': G.nodes[node].get('LF'),
                    'Float': G.nodes[node].get('float')
                }
                
                if actual_vals == exp_vals:
                    print(f"  ✅ {node}: All values match expected")
                else:
                    print(f"  ❌ {node}: Expected {exp_vals}, Got {actual_vals}")


if __name__ == "__main__":
    print("Running Network Dependency Debug...")
    debug_timing_with_correct_dependencies()
    print("\nDebug complete.")
