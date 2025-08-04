#!/usr/bin/env python3
"""
CPM Timing Calculation Diagnostic

Test to identify why ES, EF, LS, LF, and float values are missing in PMHelper.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from pmhelper.core.cpm_analyzer import CPMAnalyzer
import networkx as nx


def diagnostic_test():
    """Run comprehensive diagnostic on CPM timing calculations"""
    print("=" * 80)
    print("CPM TIMING CALCULATION DIAGNOSTIC")
    print("=" * 80)
    
    # Simple test data
    test_activities = [
        {'id': 'A', 'duration': 3, 'predecessors': []},
        {'id': 'B', 'duration': 2, 'predecessors': ['A']},
        {'id': 'C', 'duration': 4, 'predecessors': ['A']},
        {'id': 'D', 'duration': 1, 'predecessors': ['B', 'C']},
    ]
    
    print("Test Data:")
    for act in test_activities:
        print(f"  {act['id']}: Duration={act['duration']}, Predecessors={act['predecessors']}")
    
    # Initialize CPM analyzer
    print("\nInitializing CPMAnalyzer...")
    analyzer = CPMAnalyzer()
    
    # Run analysis
    print("Running CPM analysis...")
    try:
        G, critical_paths, critical_activities = analyzer.analyze(test_activities)
        
        print(f"\nAnalysis Results:")
        print(f"Graph type: {type(G)}")
        print(f"Nodes: {len(G.nodes()) if G else 0}")
        print(f"Edges: {len(G.edges()) if G else 0}")
        print(f"Critical Paths: {critical_paths}")
        print(f"Critical Activities: {critical_activities}")
        
        # CRITICAL DIAGNOSTIC: Check node attributes
        print("\n" + "="*50)
        print("NODE ATTRIBUTE DIAGNOSTIC")
        print("="*50)
        
        if G and G.nodes():
            for node in G.nodes():
                node_data = G.nodes[node]
                print(f"\nNode {node}:")
                print(f"  All attributes: {node_data}")
                
                # Check specific timing attributes
                es = node_data.get('ES', 'MISSING')
                ef = node_data.get('EF', 'MISSING')
                ls = node_data.get('LS', 'MISSING')
                lf = node_data.get('LF', 'MISSING')
                float_val = node_data.get('float', 'MISSING')
                duration = node_data.get('duration', 'MISSING')
                
                print(f"  ES: {es}")
                print(f"  EF: {ef}")
                print(f"  LS: {ls}")
                print(f"  LF: {lf}")
                print(f"  Float: {float_val}")
                print(f"  Duration: {duration}")
                
                # Status check
                missing_values = [val for val in [es, ef, ls, lf, float_val] if val == 'MISSING']
                if missing_values:
                    print(f"  ❌ MISSING VALUES: {len(missing_values)} timing values missing")
                else:
                    print(f"  ✅ ALL TIMING VALUES PRESENT")
        else:
            print("❌ Graph is None or has no nodes!")
        
        # Test manual calculation to verify expected results
        print("\n" + "="*50)
        print("EXPECTED RESULTS VERIFICATION")
        print("="*50)
        print("Expected timing values:")
        print("  A: ES=0, EF=3, LS=0, LF=3, Float=0 (Critical)")
        print("  B: ES=3, EF=5, LS=5, LF=7, Float=2 (Non-critical)")
        print("  C: ES=3, EF=7, LS=3, LF=7, Float=0 (Critical)")
        print("  D: ES=7, EF=8, LS=7, LF=8, Float=0 (Critical)")
        print("  Critical Path: START→A→C→D→END")
        
    except Exception as e:
        print(f"❌ ERROR during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)


def test_networkbuilder_directly():
    """Test NetworkBuilder methods directly to isolate the issue"""
    print("=" * 80)
    print("DIRECT NETWORKBUILDER TEST")
    print("=" * 80)
    
    from pmhelper.core.network_builder import NetworkBuilder
    
    # Test data
    test_activities = [
        {'id': 'A', 'duration': 3, 'predecessors': []},
        {'id': 'B', 'duration': 2, 'predecessors': ['A']},
        {'id': 'C', 'duration': 4, 'predecessors': ['A']},
        {'id': 'D', 'duration': 1, 'predecessors': ['B', 'C']},
    ]
    
    builder = NetworkBuilder()
    
    print("Step 1: Building network...")
    G = builder.build_network(test_activities)
    print(f"Network built: {len(G.nodes())} nodes, {len(G.edges())} edges")
    
    print("\nInitial node attributes:")
    for node in G.nodes():
        print(f"  {node}: {G.nodes[node]}")
    
    print("\nStep 2: Forward pass...")
    G = builder.forward_pass(G)
    print("Forward pass completed")
    
    print("After forward pass:")
    for node in G.nodes():
        node_data = G.nodes[node]
        es = node_data.get('ES', 'MISSING')
        ef = node_data.get('EF', 'MISSING')
        print(f"  {node}: ES={es}, EF={ef}")
    
    print("\nStep 3: Backward pass...")
    G = builder.backward_pass(G)
    print("Backward pass completed")
    
    print("After backward pass:")
    for node in G.nodes():
        node_data = G.nodes[node]
        ls = node_data.get('LS', 'MISSING')
        lf = node_data.get('LF', 'MISSING')
        print(f"  {node}: LS={ls}, LF={lf}")
    
    print("\nStep 4: Float calculation...")
    G = builder.calculate_float(G)
    print("Float calculation completed")
    
    print("Final results:")
    for node in G.nodes():
        node_data = G.nodes[node]
        es = node_data.get('ES', 'MISSING')
        ef = node_data.get('EF', 'MISSING')
        ls = node_data.get('LS', 'MISSING')
        lf = node_data.get('LF', 'MISSING')
        float_val = node_data.get('float', 'MISSING')
        print(f"  {node}: ES={es}, EF={ef}, LS={ls}, LF={lf}, Float={float_val}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("Running CPM Timing Calculation Diagnostics...")
    
    # Test 1: Full CPMAnalyzer
    diagnostic_test()
    
    # Test 2: Direct NetworkBuilder
    test_networkbuilder_directly()
    
    print("\nDiagnostic complete. Check results above for missing timing values.")
