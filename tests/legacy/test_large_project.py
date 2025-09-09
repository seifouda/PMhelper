#!/usr/bin/env python3
"""
Test with larger project similar to user's scenario (mean = 89)
"""

from pert_analyzer import PERTAnalyzer

def test_large_project():
    """Test with a project that has expected duration around 89"""
    
    # Create sample data that results in expected duration around 89
    sample_data = [
        {'id': 'A', 'predecessors': '', 'optimistic': 8, 'most_likely': 10, 'pessimistic': 15},
        {'id': 'B', 'predecessors': '', 'optimistic': 12, 'most_likely': 15, 'pessimistic': 20},
        {'id': 'C', 'predecessors': 'A', 'optimistic': 18, 'most_likely': 22, 'pessimistic': 30},
        {'id': 'D', 'predecessors': 'B', 'optimistic': 25, 'most_likely': 30, 'pessimistic': 38},
        {'id': 'E', 'predecessors': 'C,D', 'optimistic': 15, 'most_likely': 20, 'pessimistic': 28},
        {'id': 'F', 'predecessors': 'E', 'optimistic': 8, 'most_likely': 12, 'pessimistic': 18},
    ]
    
    print("=== Large Project Test (Target: Mean ~89) ===")
    
    # Calculate expected times
    for activity in sample_data:
        optimistic = activity['optimistic']
        most_likely = activity['most_likely'] 
        pessimistic = activity['pessimistic']
        expected_time = (optimistic + 4 * most_likely + pessimistic) / 6
        variance = ((pessimistic - optimistic) / 6) ** 2
        print(f"Activity {activity['id']}: Expected={expected_time:.2f}, Variance={variance:.3f}")
    
    # Initialize and run analysis
    analyzer = PERTAnalyzer()
    analyzer.analyze(sample_data)
    
    # Get project statistics
    stats = analyzer.get_project_statistics()
    expected_duration = stats['expected_duration']
    print(f"\nProject Expected Duration: {expected_duration}")
    print(f"Project Variance: {stats['variance']}")
    print(f"Project Std Dev: {stats['std_deviation']}")
    
    # Test the specific scenarios from user's problem
    test_cases = [
        (80, "Below mean"),
        (expected_duration, "At mean (should be ~50%)"),
        (100, "Above mean")
    ]
    
    print(f"\n=== Testing Probability Calculations ===")
    for target, description in test_cases:
        probability = analyzer.calculate_completion_probability(target)
        print(f"Target {target}: {probability:.4f} ({probability*100:.2f}%) - {description}")

if __name__ == "__main__":
    test_large_project()
