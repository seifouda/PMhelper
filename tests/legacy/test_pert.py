#!/usr/bin/env python3

# Simple test to check if our modules can be imported
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from pert_analyzer import PERTAnalyzer
    print("✓ PERTAnalyzer import successful")
    
    # Test basic functionality
    analyzer = PERTAnalyzer()
    print("✓ PERTAnalyzer instantiation successful")
    
    # Test with sample data
    sample_data = [
        {'id': 'A', 'predecessors': '', 'optimistic': 3, 'most_likely': 4, 'pessimistic': 7},
        {'id': 'B', 'predecessors': 'A', 'optimistic': 2, 'most_likely': 3, 'pessimistic': 5}
    ]
    
    G, critical_paths, critical_activities = analyzer.analyze(sample_data)
    stats = analyzer.get_project_statistics()
    print("✓ PERT analysis successful")
    print(f"  Expected duration: {stats['expected_duration']}")
    print(f"  Variance: {stats['variance']}")
    print(f"  Standard deviation: {stats['std_deviation']}")
    
    # Test probability calculations
    prob = analyzer.calculate_completion_probability(10)
    print(f"✓ Probability calculation successful: P(T ≤ 10) = {prob}")
    
    duration = analyzer.calculate_duration_for_probability(0.8)
    print(f"✓ Duration calculation successful: Duration for P=0.8 = {duration}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
