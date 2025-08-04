#!/usr/bin/env python3
"""
Test the actual PERT probability calculation with target duration 90
to verify the plot title shows correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code'))

from pert_analyzer import PERTAnalyzer

def test_pert_probability_plot():
    """Test PERT probability calculation and check what would appear in plot"""
    
    # Test data in proper format for PERTAnalyzer
    activities_data = [
        {"id": "A", "optimistic": 2, "most_likely": 4, "pessimistic": 6, "predecessors": ""},
        {"id": "B", "optimistic": 3, "most_likely": 5, "pessimistic": 7, "predecessors": "A"},
        {"id": "C", "optimistic": 1, "most_likely": 3, "pessimistic": 5, "predecessors": "A"},
        {"id": "D", "optimistic": 4, "most_likely": 6, "pessimistic": 8, "predecessors": "B,C"},
        {"id": "E", "optimistic": 2, "most_likely": 4, "pessimistic": 6, "predecessors": "D"},
        {"id": "F", "optimistic": 1, "most_likely": 2, "pessimistic": 3, "predecessors": "E"},
    ]
    
    analyzer = PERTAnalyzer()
    analyzer.load_activities_from_pert_data(activities_data)
    analyzer.analyze(activities_data)  # Need to run analysis first
    
    # Calculate probability for target duration 90
    target_duration = 90
    probability = analyzer.calculate_completion_probability(target_duration)
    
    # Get project statistics
    stats = analyzer.get_project_statistics()
    expected_duration = stats['expected_duration']
    std_dev = stats['std_deviation']
    
    print(f"Project Statistics:")
    print(f"Expected Duration: {expected_duration}")
    print(f"Standard Deviation: {std_dev}")
    print(f"Target Duration: {target_duration}")
    print(f"Probability: {probability:.4%}")
    
    # Simulate what the plot title would show
    plot_title = f"P(T<= {target_duration}.0)"
    print(f"\nPlot Title Should Show: '{plot_title}'")
    
    return probability, expected_duration, std_dev

if __name__ == "__main__":
    test_pert_probability_plot()
