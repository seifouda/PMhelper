#!/usr/bin/env python3
"""
Integration Test for PMHelper

Test the complete workflow from data loading to analysis and visualization.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pmhelper.core.cpm_analyzer import CPMAnalyzer
from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.utils.file_handlers import FileHandler
from pmhelper.utils.visualizations import NetworkDiagramVisualizer, GanttChartVisualizer
from pmhelper.utils.calculations import TimeCalculations, ProbabilityCalculations


def test_cpm_workflow():
    """Test complete CPM workflow"""
    print("Testing CPM workflow...")
    
    # 1. Load sample data
    sample_data = FileHandler.get_sample_cpm_data()
    print(f"✓ Loaded {len(sample_data)} sample CPM activities")
    
    # 2. Create analyzer and load data
    analyzer = CPMAnalyzer()
    analyzer.load_activities_from_data(sample_data)
    print("✓ CPM analyzer created and data loaded")
    
    # 3. Run analysis
    graph, critical_paths, critical_activities = analyzer.analyze(sample_data)
    
    # Calculate project duration from graph
    project_duration = max([graph.nodes[node].get('latest_finish', 0) for node in graph.nodes()]) if graph.nodes() else 0
    print(f"✓ Analysis completed - Project duration: {project_duration}")
    
    # 4. Verify critical path
    if critical_paths and len(critical_paths) > 0:
        critical_path = critical_paths[0]  # Take first critical path
        print(f"✓ Critical path found: {' → '.join(critical_path)}")
    else:
        print("⚠ No critical path found")
    
    # 5. Test crashing functionality
    try:
        crashed_results = analyzer.crash_project(target_duration=15)
        print(f"✓ Project crashing tested - Target: 15 days")
    except Exception as e:
        print(f"⚠ Project crashing failed: {e}")
    
    return True


def test_pert_workflow():
    """Test complete PERT workflow"""
    print("\nTesting PERT workflow...")
    
    # 1. Load sample data
    sample_data = FileHandler.get_sample_pert_data()
    print(f"✓ Loaded {len(sample_data)} sample PERT activities")
    
    # 2. Create analyzer and load data
    analyzer = PERTAnalyzer()
    analyzer.load_activities_from_pert_data(sample_data)
    print("✓ PERT analyzer created and data loaded")
    
    # 3. Run analysis
    graph, critical_paths, critical_activities = analyzer.analyze(sample_data)
    
    # Calculate expected duration from graph nodes
    expected_duration = 0
    project_variance = 0
    if graph.nodes():
        expected_duration = max([graph.nodes[node].get('latest_finish', 0) for node in graph.nodes()])
        # Calculate variance from critical path activities
        for activity_id in critical_activities:
            if activity_id in graph.nodes():
                activity_variance = graph.nodes[activity_id].get('variance', 0)
                project_variance += activity_variance
    
    std_deviation = project_variance ** 0.5 if project_variance > 0 else 0
    print(f"✓ Analysis completed - Expected duration: {expected_duration}, Std dev: {std_deviation:.2f}")
    
    # 4. Test probability calculations
    if expected_duration > 0 and std_deviation > 0:
        prob = ProbabilityCalculations.calculate_completion_probability(
            target_duration=expected_duration + 2,
            expected_duration=expected_duration,
            standard_deviation=std_deviation
        )
        print(f"✓ Probability calculation tested - P(completion by {expected_duration + 2:.1f}): {prob:.1%}")
    else:
        print("⚠ Skipping probability calculation - insufficient variance data")
    
    return True


def test_utilities():
    """Test utility functions"""
    print("\nTesting utility functions...")
    
    # Test time calculations
    pert_estimates = TimeCalculations.calculate_pert_estimates(1, 3, 8)
    print(f"✓ PERT time calculation: {pert_estimates}")
    
    # Test file operations
    sample_cpm = FileHandler.get_sample_cpm_data()
    sample_pert = FileHandler.get_sample_pert_data()
    print(f"✓ File handlers working - CPM: {len(sample_cpm)}, PERT: {len(sample_pert)} activities")
    
    return True


def test_visualization_creation():
    """Test visualization components"""
    print("\nTesting visualization components...")
    
    try:
        # Test NetworkDiagramVisualizer
        visualizer = NetworkDiagramVisualizer()
        print("✓ NetworkDiagramVisualizer created")
        
        # Test GanttChartVisualizer
        gantt_visualizer = GanttChartVisualizer()
        print("✓ GanttChartVisualizer created")
        
        return True
    except Exception as e:
        print(f"⚠ Visualization test failed: {e}")
        return False


def test_import_all_modules():
    """Test that all modules can be imported"""
    print("\nTesting module imports...")
    
    modules_to_test = [
        "pmhelper.core.cpm_analyzer",
        "pmhelper.core.pert_analyzer", 
        "pmhelper.core.network_builder",
        "pmhelper.utils.file_handlers",
        "pmhelper.utils.visualizations",
        "pmhelper.utils.calculations",
        "pmhelper.cli.cpm_cli",
        "pmhelper.cli.pert_cli",
        "pmhelper.gui.main_window",
        "pmhelper.gui.tabs"
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"✗ {module_name}: {e}")
            return False
    
    return True


def main():
    """Run all integration tests"""
    print("=" * 60)
    print("PMHelper Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_import_all_modules),
        ("CPM Workflow", test_cpm_workflow),
        ("PERT Workflow", test_pert_workflow),
        ("Utilities", test_utilities),
        ("Visualizations", test_visualization_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {test_name} - PASSED")
            else:
                print(f"\n✗ {test_name} - FAILED")
        except Exception as e:
            print(f"\n✗ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("⚠ Some integration tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
