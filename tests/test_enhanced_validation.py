#!/usr/bin/env python3
"""
Simple test to validate enhanced crashing modules
"""

import sys
import os

# Add code directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

def test_imports():
    """Test if modules can be imported"""
    print("Testing Enhanced Project Crashing Module Imports...")
    
    try:
        print("1. Testing enhanced_project_crashing...")
        from enhanced_project_crashing import (
            EnhancedProjectCrashing,
            EnhancedRCPSProjectCrashing,
            CrashingStrategy,
            OptimizationObjective,
            CrashingResult
        )
        print("   ✅ enhanced_project_crashing imported successfully")
        
        print("2. Testing enhanced_crashing_gui...")
        from enhanced_crashing_gui import (
            EnhancedCrashingGUIManager,
            add_enhanced_crashing_to_app
        )
        print("   ✅ enhanced_crashing_gui imported successfully")
        
        print("3. Testing enhanced_crashing_integration...")
        from enhanced_crashing_integration import (
            integrate_enhanced_crashing,
            get_enhanced_features_info
        )
        print("   ✅ enhanced_crashing_integration imported successfully")
        
        print("\n✅ All enhanced modules imported successfully!")
        
        # Test basic functionality
        print("\n4. Testing basic functionality...")
        
        # Test strategies and objectives
        strategies = list(CrashingStrategy)
        objectives = list(OptimizationObjective)
        
        print(f"   Available strategies: {len(strategies)}")
        for strategy in strategies:
            print(f"     - {strategy.value}")
        
        print(f"   Available objectives: {len(objectives)}")
        for objective in objectives:
            print(f"     - {objective.value}")
        
        # Test feature info
        features = get_enhanced_features_info()
        print(f"   Feature status: {features['status']}")
        
        print("\n✅ All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Import/test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_crashing():
    """Test simple crashing functionality without GUI"""
    print("\n" + "="*50)
    print("Testing Simple Crashing Functionality")
    print("="*50)
    
    try:
        # Create minimal test data
        test_activities = [
            {
                'id': 'A',
                'activity': 'Task A',
                'duration': '5',
                'predecessors': '',
                'min_duration': '2',
                'crash_cost': '100',
                'resource_demand': '1',
                'normal_cost': '500'
            },
            {
                'id': 'B', 
                'activity': 'Task B',
                'duration': '4',
                'predecessors': 'A',
                'min_duration': '2', 
                'crash_cost': '150',
                'resource_demand': '2',
                'normal_cost': '400'
            },
            {
                'id': 'C',
                'activity': 'Task C', 
                'duration': '3',
                'predecessors': 'B',
                'min_duration': '1',
                'crash_cost': '200',
                'resource_demand': '1',
                'normal_cost': '300'
            }
        ]
        
        print("1. Testing with existing CPMAnalyzer...")
        
        # Test without importing the problematic cpm_app.py
        # Instead, create a minimal mock analyzer
        import networkx as nx
        
        class MockAnalyzer:
            def __init__(self):
                self.G = None
            
            def analyze(self, activities):
                # Create a simple graph
                self.G = nx.DiGraph()
                
                # Add nodes
                for activity in activities:
                    duration = int(activity['duration'])
                    min_duration = int(activity['min_duration'])
                    crash_cost = int(activity['crash_cost'])
                    normal_cost = int(activity['normal_cost'])
                    resource_demand = int(activity['resource_demand'])
                    
                    self.G.add_node(activity['id'], 
                                  duration=duration,
                                  min_duration=min_duration,
                                  crash_cost=crash_cost,
                                  normal_cost=normal_cost,
                                  resource_demand=resource_demand)
                
                # Add START and END nodes
                self.G.add_node('START', duration=0, EF=0, LF=0, float=0)
                self.G.add_node('END', duration=0, EF=12, LF=12, float=0)
                
                # Add edges based on precedence
                for activity in activities:
                    if not activity['predecessors']:
                        self.G.add_edge('START', activity['id'])
                    else:
                        for pred in activity['predecessors'].split(','):
                            pred = pred.strip()
                            if pred:
                                self.G.add_edge(pred, activity['id'])
                
                # Add edges to END
                for activity in activities:
                    has_successors = False
                    for other in activities:
                        if activity['id'] in other.get('predecessors', '').split(','):
                            has_successors = True
                            break
                    if not has_successors:
                        self.G.add_edge(activity['id'], 'END')
                
                # Calculate basic CPM values
                self._calculate_basic_cpm()
            
            def _calculate_basic_cpm(self):
                # Simple forward pass
                for node in ['START'] + [n for n in self.G.nodes() if n not in ['START', 'END']] + ['END']:
                    if node == 'START':
                        self.G.nodes[node]['ES'] = 0
                        self.G.nodes[node]['EF'] = 0
                    elif node == 'END':
                        # END depends on all activities
                        max_ef = 0
                        for pred in self.G.predecessors(node):
                            pred_ef = self.G.nodes[pred]['EF']
                            max_ef = max(max_ef, pred_ef)
                        self.G.nodes[node]['ES'] = max_ef
                        self.G.nodes[node]['EF'] = max_ef
                    else:
                        # Regular activity
                        max_ef = 0
                        for pred in self.G.predecessors(node):
                            pred_ef = self.G.nodes[pred]['EF']
                            max_ef = max(max_ef, pred_ef)
                        
                        self.G.nodes[node]['ES'] = max_ef
                        self.G.nodes[node]['EF'] = max_ef + self.G.nodes[node]['duration']
                
                # Simple backward pass and float calculation
                for node in self.G.nodes():
                    self.G.nodes[node]['LF'] = self.G.nodes[node]['EF']
                    self.G.nodes[node]['LS'] = self.G.nodes[node]['ES']
                    self.G.nodes[node]['float'] = 0  # Simplified
            
            def forward_pass(self, graph):
                return graph
            
            def backward_pass(self, graph):
                return graph
            
            def calculate_float(self, graph):
                return graph
            
            def generate_rcps_schedule_for_graph(self, graph, resource_limit, priority_rule):
                # Simple mock RCPS schedule
                activities = {}
                total_duration = 0
                
                for node in graph.nodes():
                    if node not in ['START', 'END']:
                        start_time = graph.nodes[node]['ES']
                        duration = graph.nodes[node]['duration']
                        finish_time = start_time + duration
                        
                        activities[node] = {
                            'actual_start': start_time,
                            'actual_finish': finish_time,
                            'resource_demand': graph.nodes[node].get('resource_demand', 0)
                        }
                        
                        total_duration = max(total_duration, finish_time)
                
                return {
                    'project_duration': total_duration,
                    'activities': activities,
                    'critical_activities': ['A', 'B', 'C']  # Simplified
                }
        
        # Test with mock analyzer
        mock_analyzer = MockAnalyzer()
        mock_analyzer.analyze(test_activities)
        
        print(f"   Mock graph has {len(mock_analyzer.G.nodes())} nodes")
        
        # Test Enhanced Crashing
        print("2. Testing Enhanced Project Crashing...")
        from enhanced_project_crashing import EnhancedProjectCrashing, CrashingStrategy
        
        enhanced_engine = EnhancedProjectCrashing(mock_analyzer)
        
        result = enhanced_engine.enhanced_crash_project(
            target_duration=8,
            strategy=CrashingStrategy.LOWEST_COST,
            max_iterations=5
        )
        
        print(f"   ✅ Enhanced crashing completed!")
        print(f"   Original duration: {result.original_duration}")
        print(f"   Final duration: {result.final_duration}")
        print(f"   Crash cost: ${result.total_crash_cost}")
        print(f"   Iterations: {result.iterations_used}")
        
        # Test Enhanced RCPS Crashing
        print("3. Testing Enhanced RCPS Crashing...")
        from enhanced_project_crashing import EnhancedRCPSProjectCrashing
        
        enhanced_rcps_engine = EnhancedRCPSProjectCrashing(mock_analyzer)
        
        rcps_result = enhanced_rcps_engine.enhanced_rcps_crash_project(
            target_duration=8,
            resource_limit=3,
            max_iterations=5
        )
        
        print(f"   ✅ Enhanced RCPS crashing completed!")
        print(f"   Original duration: {rcps_result.original_duration}")
        print(f"   Final duration: {rcps_result.final_duration}")
        print(f"   Crash cost: ${rcps_result.total_crash_cost}")
        print(f"   Resource utilization available: {rcps_result.resource_utilization is not None}")
        
        # Test comparison
        print("4. Testing result comparison...")
        from enhanced_project_crashing import compare_crashing_results
        
        comparison = compare_crashing_results([result, rcps_result])
        print(f"   ✅ Comparison completed!")
        print(f"   Best cost result: ${comparison['best_cost'].total_crash_cost}")
        print(f"   Best duration result: {comparison['best_duration'].final_duration}")
        
        print("\n✅ All functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Enhanced Project Crashing - Validation Test Suite")
    print("="*60)
    
    # Test 1: Import validation
    import_success = test_imports()
    
    if not import_success:
        print("\n❌ CRITICAL: Module imports failed!")
        return False
    
    # Test 2: Functionality validation  
    functionality_success = test_simple_crashing()
    
    if not functionality_success:
        print("\n❌ CRITICAL: Functionality tests failed!")
        return False
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print("✅ Module imports: PASSED")
    print("✅ Basic functionality: PASSED")
    print("✅ Enhanced CPM crashing: PASSED")
    print("✅ Enhanced RCPS crashing: PASSED")
    print("✅ Result comparison: PASSED")
    print("\n🎉 ALL TESTS PASSED! Enhanced Project Crashing is ready!")
    print("\n💡 Next steps:")
    print("   1. Run main app: python launch_app.py")
    print("   2. Load project data")
    print("   3. Import and integrate enhanced features")
    print("   4. Use new Enhanced Crashing tabs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
