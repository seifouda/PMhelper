#!/usr/bin/env python3
"""
Test script to verify the CPM/PERT application fixes.
This script tests the missing method fix and basic functionality.
"""

import sys
import os
import traceback

# Add the code directory to the path
sys.path.insert(0, r'd:\PMhelper\code')

def test_cpm_analyzer():
    """Test CPM analyzer with deterministic data"""
    print("Testing CPM Analyzer...")
    
    try:
        # Import the CPM analyzer (this should work now)
        from cpm_app import CPMAnalyzer
        
        # Create analyzer instance
        analyzer = CPMAnalyzer()
        
        # Test sample deterministic data
        sample_data = [
            {
                'id': 'A',
                'activity': 'Design Phase',
                'duration': '5',
                'predecessors': '',
                'min_duration': '1',
                'crash_cost': '300',
                'resource_demand': '2'
            },
            {
                'id': 'B',
                'activity': 'Requirements Analysis',
                'duration': '3',
                'predecessors': '',
                'min_duration': '2',
                'crash_cost': '500',
                'resource_demand': '1'
            },
            {
                'id': 'C',
                'activity': 'Architecture Design',
                'duration': '7',
                'predecessors': 'A,B',
                'min_duration': '5',
                'crash_cost': '600',
                'resource_demand': '3'
            },
            {
                'id': 'D',
                'activity': 'Testing',
                'duration': '3',
                'predecessors': 'C',
                'min_duration': '3',
                'crash_cost': '800',
                'resource_demand': '2'
            }
        ]
        
        print("✓ CPM Analyzer imported successfully")
        
        # Test load_activities_from_data method
        activities = analyzer.load_activities_from_data(sample_data)
        print("✓ load_activities_from_data method works")
        print(f"  Processed {len(activities)} activities")
        
        # Test complete analysis
        G, critical_paths, critical_activities = analyzer.analyze(sample_data)
        print("✓ Complete CPM analysis works")
        print(f"  Critical paths found: {len(critical_paths)}")
        print(f"  Critical activities: {critical_activities}")
        
        # Test project duration calculation
        project_duration = max([G.nodes[node]['EF'] for node in G.nodes()])
        print(f"  Project duration: {project_duration}")
        
        return True
        
    except Exception as e:
        print(f"✗ CPM Analyzer test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_pert_analyzer():
    """Test PERT analyzer with probabilistic data"""
    print("\nTesting PERT Analyzer...")
    
    try:
        # Import the PERT analyzer
        from pert_analyzer import PERTAnalyzer
        
        # Create analyzer instance
        analyzer = PERTAnalyzer()
        
        # Test sample probabilistic data
        sample_data = [
            {
                'id': 'A',
                'predecessors': '',
                'optimistic': 3,
                'most_likely': 4,
                'pessimistic': 7,
                'min_duration': 1,
                'crash_cost': 300,
                'resource_demand': 2,
                'normal_cost': 300
            },
            {
                'id': 'B',
                'predecessors': '',
                'optimistic': 7,
                'most_likely': 9,
                'pessimistic': 12,
                'min_duration': 2,
                'crash_cost': 600,
                'resource_demand': 4,
                'normal_cost': 300
            },
            {
                'id': 'C',
                'predecessors': 'A,B',
                'optimistic': 4,
                'most_likely': 5,
                'pessimistic': 9,
                'min_duration': 1,
                'crash_cost': 500,
                'resource_demand': 2,
                'normal_cost': 300
            }
        ]
        
        print("✓ PERT Analyzer imported successfully")
        
        # Test load_activities_from_pert_data method
        activities = analyzer.load_activities_from_pert_data(sample_data)
        print("✓ load_activities_from_pert_data method works")
        print(f"  Processed {len(activities)} activities")
        
        # Test complete analysis
        G, critical_paths, critical_activities = analyzer.analyze(sample_data)
        print("✓ Complete PERT analysis works")
        print(f"  Critical paths found: {len(critical_paths)}")
        print(f"  Critical activities: {critical_activities}")
        
        # Test project duration and variance
        project_duration = max([G.nodes[node]['EF'] for node in G.nodes()])
        print(f"  Project duration: {project_duration}")
        print(f"  Project variance: {analyzer.project_variance}")
        print(f"  Project standard deviation: {analyzer.project_std}")
        
        return True
        
    except Exception as e:
        print(f"✗ PERT Analyzer test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_gui_imports():
    """Test GUI application imports"""
    print("\nTesting GUI Application Imports...")
    
    try:
        # Test importing the main desktop application
        from cpm_app import CPMDesktopApp
        print("✓ CPMDesktopApp imported successfully")
        
        # Test that both analyzers are available
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window for testing
        
        app = CPMDesktopApp(root)
        print("✓ CPMDesktopApp instantiated successfully")
        
        # Verify analyzers exist
        assert hasattr(app, 'cpm_analyzer'), "CPM analyzer missing"
        assert hasattr(app, 'pert_analyzer'), "PERT analyzer missing"
        assert hasattr(app.cpm_analyzer, 'load_activities_from_data'), "load_activities_from_data method missing"
        assert hasattr(app.pert_analyzer, 'load_activities_from_pert_data'), "load_activities_from_pert_data method missing"
        
        print("✓ Both analyzers available with correct methods")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ GUI application test failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("CPM/PERT Application Fix Verification")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(test_cpm_analyzer())
    results.append(test_pert_analyzer())
    results.append(test_gui_imports())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All {total} tests PASSED!")
        print("\nThe CPM/PERT application should now work correctly:")
        print("- CPM analysis with deterministic data")
        print("- PERT analysis with probabilistic data")
        print("- All GUI components should be functional")
        return 0
    else:
        print(f"✗ {total - passed} of {total} tests FAILED!")
        print("\nSome issues remain that need to be addressed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
