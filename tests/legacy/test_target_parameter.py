#!/usr/bin/env python3
"""
Quick test to verify the target_duration parameter is passed correctly
"""

from pert_analyzer import PERTAnalyzer
import numpy as np
from scipy.stats import norm

def test_target_duration_parameter():
    """Test that target_duration parameter is handled correctly"""
    
    # Create sample PERT data with expected duration around 90
    sample_data = [
        {'id': 'A', 'predecessors': '', 'optimistic': 15, 'most_likely': 20, 'pessimistic': 30},
        {'id': 'B', 'predecessors': '', 'optimistic': 20, 'most_likely': 25, 'pessimistic': 35},
        {'id': 'C', 'predecessors': 'A', 'optimistic': 25, 'most_likely': 30, 'pessimistic': 40},
        {'id': 'D', 'predecessors': 'B', 'optimistic': 35, 'most_likely': 40, 'pessimistic': 50},
        {'id': 'E', 'predecessors': 'C,D', 'optimistic': 8, 'most_likely': 12, 'pessimistic': 18},
    ]
    
    print("=== Target Duration Parameter Test ===")
    
    # Initialize and run analysis
    analyzer = PERTAnalyzer()
    analyzer.analyze(sample_data)
    
    # Get project statistics
    stats = analyzer.get_project_statistics()
    expected_duration = stats['expected_duration']
    std_dev = stats['std_deviation']
    
    print(f"Project Expected Duration: {expected_duration}")
    print(f"Project Std Dev: {std_dev}")
    
    # Test specific target durations
    test_targets = [80, 90, 100]
    
    print(f"\n=== Testing Target Duration Parameters ===")
    for target in test_targets:
        probability = analyzer.calculate_completion_probability(target)
        
        # Manual calculation to verify
        z_score = (target - expected_duration) / std_dev
        manual_prob = norm.cdf(z_score)
        
        print(f"Target {target}:")
        print(f"  - Analyzer result: {probability:.4f} ({probability*100:.2f}%)")
        print(f"  - Manual calc: {manual_prob:.4f} ({manual_prob*100:.2f}%)")
        print(f"  - Z-score: {z_score:.3f}")
        
        # Test that the label would show the correct target
        label_text = f"P(T ≤ {target}) = {probability:.4f}"
        print(f"  - Expected label: {label_text}")
        print()

if __name__ == "__main__":
    test_target_duration_parameter()
