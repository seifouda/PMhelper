#!/usr/bin/env python3

# Test PERT analyzer with the actual test data
import sys
import os
import csv

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from pert_analyzer import PERTAnalyzer
    
    # Load data from the actual test CSV
    activities_data = []
    with open('../pert_test.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            pert_data = {
                'id': row['id'],
                'predecessors': row.get('predecessors', '').strip(),
                'optimistic': float(row['optimistic']),
                'most_likely': float(row['most_likely']),
                'pessimistic': float(row['pessimistic'])
            }
            activities_data.append(pert_data)
    
    print(f"Loaded {len(activities_data)} activities")
    
    # Analyze with PERT
    analyzer = PERTAnalyzer()
    G, critical_paths, critical_activities = analyzer.analyze(activities_data)
    stats = analyzer.get_project_statistics()
    
    print("\n=== PERT Analysis Results ===")
    print(f"Expected duration: {stats['expected_duration']}")
    print(f"Variance: {stats['variance']}")
    print(f"Standard deviation: {stats['std_deviation']}")
    print(f"Critical path: {' -> '.join(stats['critical_path'])}")
    
    print("\n=== Critical Activities Variance ===")
    for activity_info in stats['critical_activities_variance']:
        print(f"{activity_info['id']}: Variance = {activity_info['variance']:.3f}, Expected Time = {activity_info['expected_time']}")
    
    print("\n=== Probability Calculations ===")
    
    # Test various target durations
    test_durations = [50, 55, 60, 65, 70]
    for target_duration in test_durations:
        prob = analyzer.calculate_completion_probability(target_duration)
        print(f"P(T ≤ {target_duration}) = {prob:.4f} ({prob*100:.2f}%)")
    
    print("\n=== Duration for Probability ===")
    
    # Test various probabilities
    test_probs = [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    for target_prob in test_probs:
        duration = analyzer.calculate_duration_for_probability(target_prob)
        print(f"Duration for P = {target_prob:.2f}: {duration:.2f} time units")
    
    # Check if any of the calculations are zero
    print("\n=== Debugging Zero Probability Issue ===")
    project_duration = max([G.nodes[node]['EF'] for node in G.nodes()])
    print(f"Project duration from graph: {project_duration}")
    print(f"Project variance: {analyzer.project_variance}")
    print(f"Project std dev: {analyzer.project_std}")
    
    # Test calculation details for specific case
    target_duration = 50
    z_score = (target_duration - project_duration) / analyzer.project_std if analyzer.project_std > 0 else 0
    print(f"For target duration {target_duration}:")
    print(f"  Z-score: {z_score:.4f}")
    print(f"  Raw probability: {analyzer.calculate_completion_probability(target_duration)}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
