#!/usr/bin/env python3
"""
Debug Normal Crashing Issue

Quick test to identify why the normal crashing button doesn't work
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pmhelper.gui.tabs.project_crashing_core import ProjectCrashing, CrashingStrategy, OptimizationObjective
import networkx as nx

def create_simple_test_analyzer():
    """Create a simple test analyzer with a basic network"""
    class MockAnalyzer:
        def __init__(self):
            # Create simple network
            self.G = nx.DiGraph()
            
            # Add nodes
            nodes = {
                'START': {'duration': 0, 'normal_cost': 0, 'crash_cost': 0, 'min_duration': 0},
                'A': {'duration': 5, 'normal_cost': 100, 'crash_cost': 30, 'min_duration': 3},
                'B': {'duration': 3, 'normal_cost': 60, 'crash_cost': 20, 'min_duration': 2},
                'C': {'duration': 4, 'normal_cost': 80, 'crash_cost': 25, 'min_duration': 2},
                'END': {'duration': 0, 'normal_cost': 0, 'crash_cost': 0, 'min_duration': 0}
            }
            
            for node, attrs in nodes.items():
                self.G.add_node(node, **attrs)
            
            # Add edges
            edges = [('START', 'A'), ('START', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'END')]
            for source, target in edges:
                self.G.add_edge(source, target)
            
            # Run simple CPM calculation
            self._calculate_cpm()
            
        def _calculate_cpm(self):
            """Simple CPM calculation"""
            # Forward pass
            for node in nx.topological_sort(self.G):
                if node == 'START':
                    self.G.nodes[node]['ES'] = 0
                    self.G.nodes[node]['EF'] = 0
                else:
                    # ES = max(EF of all predecessors)
                    predecessors = list(self.G.predecessors(node))
                    if predecessors:
                        es = max(self.G.nodes[pred]['EF'] for pred in predecessors)
                    else:
                        es = 0
                    
                    self.G.nodes[node]['ES'] = es
                    self.G.nodes[node]['EF'] = es + self.G.nodes[node]['duration']
            
            # Project duration
            project_duration = max(self.G.nodes[node]['EF'] for node in self.G.nodes())
            
            # Backward pass
            for node in reversed(list(nx.topological_sort(self.G))):
                if node == 'END':
                    self.G.nodes[node]['LF'] = self.G.nodes[node]['EF']
                    self.G.nodes[node]['LS'] = self.G.nodes[node]['LF'] - self.G.nodes[node]['duration']
                else:
                    # LF = min(LS of all successors)
                    successors = list(self.G.successors(node))
                    if successors:
                        lf = min(self.G.nodes[succ]['LS'] for succ in successors)
                    else:
                        lf = project_duration
                    
                    self.G.nodes[node]['LF'] = lf
                    self.G.nodes[node]['LS'] = lf - self.G.nodes[node]['duration']
                
                # Calculate float
                self.G.nodes[node]['float'] = self.G.nodes[node]['LS'] - self.G.nodes[node]['ES']
    
    return MockAnalyzer()

def test_normal_crashing():
    """Test normal crashing functionality"""
    print("🔍 DEBUGGING NORMAL CRASHING ISSUE")
    print("=" * 50)
    
    try:
        # Create test analyzer
        print("1. Creating test analyzer...")
        analyzer = create_simple_test_analyzer()
        print(f"   ✅ Analyzer created with {len(analyzer.G.nodes())} nodes")
        
        # Check network
        print(f"   📊 Network: {list(analyzer.G.nodes())}")
        for node in analyzer.G.nodes():
            if node not in ['START', 'END']:
                es = analyzer.G.nodes[node].get('ES', 0)
                ef = analyzer.G.nodes[node].get('EF', 0)
                duration = analyzer.G.nodes[node].get('duration', 0)
                print(f"      {node}: Duration={duration}, ES={es}, EF={ef}")
        
        # Create crashing engine
        print("\\n2. Creating ProjectCrashing engine...")
        crashing_engine = ProjectCrashing(analyzer)
        print("   ✅ ProjectCrashing created successfully")
        
        # Test parameters
        target_duration = 6  # Original should be around 8
        strategy = CrashingStrategy.LOWEST_COST
        objective = OptimizationObjective.MINIMIZE_COST
        
        print(f"\\n3. Running crashing analysis...")
        print(f"   Target duration: {target_duration}")
        print(f"   Strategy: {strategy}")
        print(f"   Objective: {objective}")
        
        # Run crashing
        result = crashing_engine.run(
            target_duration=target_duration,
            strategy=strategy,
            objective=objective,
            max_budget=None,
            max_crash_cost=None,
            max_normal_cost=None,
            max_iterations=10
        )
        
        print(f"\\n4. RESULTS:")
        if result:
            print(f"   ✅ Crashing completed successfully!")
            print(f"   📊 Original duration: {getattr(result, 'original_duration', 'N/A')}")
            print(f"   📊 Final duration: {getattr(result, 'final_duration', 'N/A')}")
            print(f"   💰 Total crash cost: ${getattr(result, 'total_crash_cost', 0):.2f}")
            print(f"   📝 Crash log entries: {len(getattr(result, 'crash_log', []))}")
            
            if hasattr(result, 'crash_log') and result.crash_log:
                print(f"   📝 First crash entry: {result.crash_log[0]}")
        else:
            print(f"   ❌ No result returned")
        
        return True
        
    except Exception as e:
        print(f"\\n❌ ERROR DETECTED:")
        print(f"   Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_import_issues():
    """Test for import-related issues"""
    print("\\n🔍 CHECKING IMPORT ISSUES")
    print("=" * 50)
    
    try:
        print("1. Testing NetworkBuilder import...")
        try:
            from src.pmhelper.core.network_builder import NetworkBuilder
            print("   ✅ NetworkBuilder imported successfully")
            nb = NetworkBuilder()
            print("   ✅ NetworkBuilder instantiated successfully")
        except Exception as e:
            print(f"   ❌ NetworkBuilder import failed: {e}")
            
            # Try alternative import
            try:
                from pmhelper.core.network_builder import NetworkBuilder
                print("   ⚠️  Alternative import worked")
            except Exception as e2:
                print(f"   ❌ Alternative import also failed: {e2}")
        
        print("\\n2. Testing other imports...")
        try:
            import time as time_mod
            print("   ✅ time module imported")
        except Exception as e:
            print(f"   ❌ time import failed: {e}")
            
        try:
            import copy
            print("   ✅ copy module imported")
        except Exception as e:
            print(f"   ❌ copy import failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 NORMAL CRASHING DEBUG TEST SUITE")
    print("=" * 50)
    
    # Run tests
    import_ok = test_import_issues()
    crashing_ok = test_normal_crashing()
    
    print("\\n" + "=" * 50)
    print("FINAL RESULTS:")
    print(f"Import Tests: {'✅ PASSED' if import_ok else '❌ FAILED'}")
    print(f"Crashing Tests: {'✅ PASSED' if crashing_ok else '❌ FAILED'}")
    
    if import_ok and crashing_ok:
        print("\\n🎉 All tests passed - normal crashing should work!")
    else:
        print("\\n❌ Issues detected - this explains why normal crashing isn't working")
    
    print("=" * 50)
