#!/usr/bin/env python3
"""
Debug script for PERT probability calculation
"""

from pert_analyzer import PERTAnalyzer
import math

def test_pert_probability():
    """Test PERT probability calculation with sample data"""
    
    # Create sample PERT data
    sample_data = [
        {'id': 'A', 'predecessors': '', 'optimistic': 3, 'most_likely': 4, 'pessimistic': 7},
        {'id': 'B', 'predecessors': '', 'optimistic': 7, 'most_likely': 9, 'pessimistic': 12},
        {'id': 'C', 'predecessors': 'A,B', 'optimistic': 4, 'most_likely': 5, 'pessimistic': 9},
        {'id': 'D', 'predecessors': 'A,B', 'optimistic': 10, 'most_likely': 11, 'pessimistic': 16},
        {'id': 'E', 'predecessors': 'C,D', 'optimistic': 18, 'most_likely': 20, 'pessimistic': 22},
    ]
    
    print("=== PERT Probability Debug Test ===")
    print("Sample data:")
    for activity in sample_data:
        optimistic = activity['optimistic']
        most_likely = activity['most_likely'] 
        pessimistic = activity['pessimistic']
        expected_time = (optimistic + 4 * most_likely + pessimistic) / 6
        variance = ((pessimistic - optimistic) / 6) ** 2
        print(f"Activity {activity['id']}: o={optimistic}, m={most_likely}, p={pessimistic}")
        print(f"  Expected time: {expected_time:.3f}, Variance: {variance:.3f}")
    
    # Initialize PERT analyzer
    analyzer = PERTAnalyzer()
    
    try:
        # Run analysis
        print("\n=== Running PERT Analysis ===")
        analyzer.analyze(sample_data)
        
        # Get project statistics
        stats = analyzer.get_project_statistics()
        print(f"\nProject Statistics: {stats}")
        
        # Test probability calculations
        print("\n=== Testing Probability Calculations ===")
        expected_duration = stats['expected_duration']
        
        test_durations = [
            expected_duration - 10,  # Below mean
            expected_duration,       # At mean (should be ~50%)
            expected_duration + 10   # Above mean
        ]
        
        for target in test_durations:
            print(f"\nTesting target duration: {target}")
            probability = analyzer.calculate_completion_probability(target)
            print(f"Result: {probability:.4f} ({probability*100:.2f}%)")
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pert_probability()
