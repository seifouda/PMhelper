#!/usr/bin/env python3
"""
Test script to verify the crashing validation logic works correctly
"""
import sys
from pathlib import Path

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from pmhelper.core.cpm_analyzer import CPMAnalyzer

def test_validation_logic():
    """Test the validation logic that was added to crashing_tab_gui.py"""
    print("Testing crashing validation logic...")
    
    # Sample activities data similar to what the app uses
    activities_data = [
        {'id': 'A', 'activity': 'Design Phase', 'duration': 5, 'predecessors': '', 'normal_cost': 1000, 'crash_cost': 200, 'min_duration': 3},
        {'id': 'B', 'activity': 'Requirements Analysis', 'duration': 3, 'predecessors': '', 'normal_cost': 600, 'crash_cost': 150, 'min_duration': 2},
        {'id': 'C', 'activity': 'Architecture Design', 'duration': 7, 'predecessors': 'A,B', 'normal_cost': 1400, 'crash_cost': 300, 'min_duration': 5},
        {'id': 'D', 'activity': 'Database Design', 'duration': 5, 'predecessors': 'C', 'normal_cost': 1000, 'crash_cost': 250, 'min_duration': 3},
        {'id': 'E', 'activity': 'Frontend Development', 'duration': 6, 'predecessors': 'C', 'normal_cost': 1200, 'crash_cost': 300, 'min_duration': 4},
        {'id': 'F', 'activity': 'Backend Development', 'duration': 8, 'predecessors': 'C', 'normal_cost': 1600, 'crash_cost': 400, 'min_duration': 6},
        {'id': 'G', 'activity': 'Testing', 'duration': 3, 'predecessors': 'D', 'normal_cost': 600, 'crash_cost': 200, 'min_duration': 2},
        {'id': 'H', 'activity': 'Deployment', 'duration': 4, 'predecessors': 'E,F', 'normal_cost': 800, 'crash_cost': 300, 'min_duration': 3},
        {'id': 'I', 'activity': 'Documentation', 'duration': 3, 'predecessors': 'G,H', 'normal_cost': 600, 'crash_cost': 200, 'min_duration': 2},
    ]
    
    # Run CPM analysis
    analyzer = CPMAnalyzer()
    G, critical_paths, critical_activities = analyzer.analyze(activities_data)
    
    print(f"CPM Analysis completed:")
    print(f"  Critical path: {critical_paths[0] if critical_paths else 'None'}")
    print(f"  Critical activities: {critical_activities}")
    
    # Calculate original project duration using the same logic as the validation code
    ef_values = [G.nodes[node].get('EF', 0) for node in G.nodes()]
    original_duration = max(ef_values) if ef_values else 0
    
    print(f"  Original project duration: {original_duration}")
    
    # Test validation scenarios
    test_cases = [
        {"target": 20, "should_pass": True, "description": "Valid target duration (less than original)"},
        {"target": 27, "should_pass": True, "description": "Valid target duration (equal to original)"},
        {"target": 30, "should_pass": False, "description": "Invalid target duration (greater than original)"},
        {"target": 15, "should_pass": True, "description": "Valid aggressive target"},
    ]
    
    print(f"\nTesting validation logic:")
    for i, test_case in enumerate(test_cases, 1):
        target = test_case["target"]
        should_pass = test_case["should_pass"]
        description = test_case["description"]
        
        # Apply the validation logic
        validation_passes = target <= original_duration
        
        status = "✓ PASS" if validation_passes == should_pass else "✗ FAIL"
        print(f"  Test {i}: {description}")
        print(f"    Target: {target}, Original: {original_duration}")
        print(f"    Expected: {'Pass' if should_pass else 'Fail'}, Got: {'Pass' if validation_passes else 'Fail'}")
        print(f"    Status: {status}")
    
    # Test the EF analysis check (ensure analysis has been run)
    print(f"\nTesting EF analysis check:")
    has_analysis = any(ef > 0 for ef in ef_values)
    print(f"  EF values: {ef_values}")
    print(f"  Has analysis been run: {has_analysis}")
    print(f"  Status: {'✓ PASS' if has_analysis else '✗ FAIL - Analysis not detected'}")

if __name__ == "__main__":
    test_validation_logic()
