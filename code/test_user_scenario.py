#!/usr/bin/env python3
"""
Test with project having expected duration closer to 89
"""

from pert_analyzer import PERTAnalyzer

def test_user_scenario():
    """Test with a project that has expected duration around 89"""
    
    # Create sample data that results in expected duration around 89
    sample_data = [
        {'id': 'A', 'predecessors': '', 'optimistic': 10, 'most_likely': 12, 'pessimistic': 18},
        {'id': 'B', 'predecessors': '', 'optimistic': 15, 'most_likely': 18, 'pessimistic': 25},
        {'id': 'C', 'predecessors': 'A', 'optimistic': 20, 'most_likely': 25, 'pessimistic': 35},
        {'id': 'D', 'predecessors': 'B', 'optimistic': 30, 'most_likely': 35, 'pessimistic': 45},
        {'id': 'E', 'predecessors': 'C,D', 'optimistic': 18, 'most_likely': 22, 'pessimistic': 30},
        {'id': 'F', 'predecessors': 'E', 'optimistic': 10, 'most_likely': 15, 'pessimistic': 22},
    ]
    
    print("=== User Scenario Test (Target: Mean ~89) ===")
    
    # Initialize and run analysis
    analyzer = PERTAnalyzer()
    analyzer.analyze(sample_data)
    
    # Get project statistics
    stats = analyzer.get_project_statistics()
    expected_duration = stats['expected_duration']
    print(f"Project Expected Duration: {expected_duration}")
    print(f"Project Variance: {stats['variance']}")
    print(f"Project Std Dev: {stats['std_deviation']}")
    print(f"Critical Path: {stats['critical_path']}")
    
    # Test the exact scenarios from user's problem
    test_cases = [
        (80, "User's test case 1"),
        (89, "User's test case 2 (should be close to mean)"),
        (expected_duration, "Actual mean (should be exactly 50%)"),
        (100, "User's test case 3")
    ]
    
    print(f"\n=== Testing User's Exact Scenarios ===")
    for target, description in test_cases:
        probability = analyzer.calculate_completion_probability(target)
        print(f"Target {target}: {probability:.4f} ({probability*100:.2f}%) - {description}")

if __name__ == "__main__":
    test_user_scenario()
