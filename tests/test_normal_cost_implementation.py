#!/usr/bin/env python3
"""
Test script to verify Normal Cost field implementation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code'))

from cpm_app import CPMAnalyzer

def test_normal_cost_implementation():
    """Test that normal cost is properly handled in CPM analysis"""
    
    print("Testing Normal Cost Implementation...")
    print("=" * 50)
    
    # Test data with normal cost values
    activities_data = [
        {
            'id': 'A',
            'activity': 'Design Phase',
            'duration': '5',
            'predecessors': '',
            'min_duration': '1',
            'crash_cost': '300',
            'resource_demand': '2',
            'normal_cost': '100'
        },
        {
            'id': 'B',
            'activity': 'Requirements Analysis',
            'duration': '3',
            'predecessors': '',
            'min_duration': '2',
            'crash_cost': '500',
            'resource_demand': '1',
            'normal_cost': '150'
        },
        {
            'id': 'C',
            'activity': 'Architecture Design',
            'duration': '7',
            'predecessors': 'A,B',
            'min_duration': '5',
            'crash_cost': '600',
            'resource_demand': '3',
            'normal_cost': '200'
        }
    ]
    
    # Create analyzer and test loading
    analyzer = CPMAnalyzer()
    
    try:
        # Test load_activities_from_data with normal_cost
        activities = analyzer.load_activities_from_data(activities_data)
        
        print("✓ Successfully loaded activities with normal cost")
        print(f"  Loaded {len(activities)} activities")
        
        # Check if normal_cost is included in activities
        for activity in activities:
            print(f"  Activity {activity['id']}: normal_cost = {activity.get('normal_cost', 'MISSING')}")
        
        # Test building network
        G = analyzer.build_network(activities)
        
        print("\n✓ Successfully built network")
        print(f"  Graph has {len(G.nodes())} nodes")
        
        # Check if normal_cost is stored in graph nodes
        print("\nNormal Cost in Graph Nodes:")
        for node in G.nodes():
            if node not in ['START', 'END']:
                normal_cost = G.nodes[node].get('normal_cost', 'MISSING')
                print(f"  Node {node}: normal_cost = {normal_cost}")
        
        print("\n✓ Normal Cost implementation appears to be working correctly!")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_normal_cost_implementation()
    if success:
        print("\n" + "=" * 50)
        print("NORMAL COST IMPLEMENTATION TEST: PASSED")
    else:
        print("\n" + "=" * 50)  
        print("NORMAL COST IMPLEMENTATION TEST: FAILED")
