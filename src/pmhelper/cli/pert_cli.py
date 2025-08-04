#!/usr/bin/env python3
"""
PERT CLI Module

Command-line interface for PERT (Program Evaluation and Review Technique) analysis.
Provides command-line tools for probabilistic project analysis and reporting.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.utils.file_handlers import FileHandler
from pmhelper.utils.calculations import ProbabilityCalculations, NetworkMetrics


def analyze_project(input_file, output_file=None, format_type='csv', verbose=False):
    """
    Analyze a project using PERT
    
    Args:
        input_file (str): Path to input file
        output_file (str): Path to output file (optional)
        format_type (str): File format ('csv' or 'excel')
        verbose (bool): Enable verbose output
    """
    try:
        # Load data
        if verbose:
            print(f"Loading PERT data from {input_file}...")
        
        if format_type.lower() == 'excel':
            activities_data = FileHandler.load_excel(input_file)
        else:
            activities_data = FileHandler.load_csv(input_file)
        
        if verbose:
            print(f"Loaded {len(activities_data)} activities")
        
        # Validate required columns for PERT
        required_columns = ['id', 'optimistic', 'most_likely', 'pessimistic']
        FileHandler.validate_required_columns(activities_data, required_columns)
        
        # Perform PERT analysis
        analyzer = PERTAnalyzer()
        G, critical_paths, critical_activities = analyzer.analyze(activities_data)
        
        # Get project statistics
        stats = analyzer.get_project_statistics()
        
        # Display results
        print("\\n=== PERT Analysis Results ===")
        print(f"Expected Project Duration: {stats['expected_duration']:.2f} time units")
        print(f"Project Standard Deviation: {stats['std_deviation']:.3f}")
        print(f"Project Variance: {stats['variance']:.3f}")
        print(f"Critical Path: {' -> '.join(critical_paths[0]) if critical_paths and critical_paths[0] else 'None found'}")
        print(f"Critical Activities: {', '.join(critical_activities)}")
        
        # Probability analysis
        expected_duration = stats['expected_duration']
        print("\\n=== Probability Analysis ===")
        
        # Common probability scenarios
        scenarios = [
            (expected_duration, "Expected Duration"),
            (expected_duration + stats['std_deviation'], "Expected + 1 Std Dev"),
            (expected_duration + 2 * stats['std_deviation'], "Expected + 2 Std Dev"),
        ]
        
        for duration, description in scenarios:
            prob = analyzer.calculate_completion_probability(duration)
            print(f"Probability of completing by {duration:.1f} ({description}): {prob:.1%}")
        
        # Duration for specific probabilities
        print("\\n=== Duration for Target Probabilities ===")
        for prob in [0.5, 0.8, 0.9, 0.95]:
            duration = analyzer.calculate_duration_for_probability(prob)
            print(f"{prob:.0%} probability of completion by: {duration:.2f} time units")
        
        # Network metrics
        if verbose:
            metrics = NetworkMetrics.calculate_network_complexity(G)
            print(f"\\nNetwork Complexity:")
            print(f"  - Total Activities: {metrics['num_nodes']}")
            print(f"  - Dependencies: {metrics['num_edges']}")
            print(f"  - Network Density: {metrics['density']:.3f}")
            
            # Critical activities variance breakdown
            if stats['critical_activities_variance']:
                print("\\nCritical Activities Variance:")
                for activity_info in stats['critical_activities_variance']:
                    print(f"  - {activity_info['id']}: Variance = {activity_info['variance']:.3f}")
        
        # Prepare results for export
        results_data = []
        for node in G.nodes():
            if node not in ['START', 'END']:
                results_data.append({
                    'activity_id': node,
                    'activity_name': G.nodes[node].get('activity', ''),
                    'optimistic': G.nodes[node].get('optimistic', 0),
                    'most_likely': G.nodes[node].get('most_likely', 0),
                    'pessimistic': G.nodes[node].get('pessimistic', 0),
                    'expected_time': G.nodes[node].get('expected_time', 0),
                    'variance': G.nodes[node].get('variance', 0),
                    'duration_ceil': G.nodes[node]['duration'],
                    'early_start': G.nodes[node]['ES'],
                    'early_finish': G.nodes[node]['EF'],
                    'late_start': G.nodes[node]['LS'],
                    'late_finish': G.nodes[node]['LF'],
                    'float': G.nodes[node]['float'],
                    'critical': 'Yes' if G.nodes[node]['float'] == 0 else 'No'
                })
        
        # Save results if output file specified
        if output_file:
            if format_type.lower() == 'excel':
                FileHandler.save_excel(results_data, output_file, 'PERT_Results')
            else:
                FileHandler.save_csv(results_data, output_file)
            print(f"\\nResults saved to {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def probability_analysis(input_file, target_durations=None, target_probabilities=None, 
                        format_type='csv', verbose=False):
    """
    Perform detailed probability analysis
    
    Args:
        input_file (str): Path to input file
        target_durations (list): List of target durations to analyze
        target_probabilities (list): List of target probabilities to analyze
        format_type (str): File format ('csv' or 'excel')
        verbose (bool): Enable verbose output
    """
    try:
        # Load and analyze project
        if format_type.lower() == 'excel':
            activities_data = FileHandler.load_excel(input_file)
        else:
            activities_data = FileHandler.load_csv(input_file)
        
        analyzer = PERTAnalyzer()
        G, _, _ = analyzer.analyze(activities_data)
        stats = analyzer.get_project_statistics()
        
        print("\\n=== PERT Probability Analysis ===")
        print(f"Expected Duration: {stats['expected_duration']:.2f}")
        print(f"Standard Deviation: {stats['std_deviation']:.3f}")
        
        # Analyze target durations
        if target_durations:
            print("\\n=== Completion Probabilities ===")
            for duration in target_durations:
                prob = analyzer.calculate_completion_probability(duration)
                print(f"Probability of completing by {duration}: {prob:.1%}")
        
        # Analyze target probabilities
        if target_probabilities:
            print("\\n=== Required Durations ===")
            for prob in target_probabilities:
                duration = analyzer.calculate_duration_for_probability(prob)
                print(f"Duration for {prob:.0%} probability: {duration:.2f} time units")
        
        # Risk analysis
        if verbose:
            risk_metrics = ProbabilityCalculations.calculate_risk_metrics(
                stats['expected_duration'], stats['std_deviation']
            )
            print("\\n=== Risk Analysis ===")
            print(f"Coefficient of Variation: {risk_metrics['coefficient_of_variation']:.3f}")
            print(f"Probability of finishing on expected time: {risk_metrics['probability_on_time']:.1%}")
            print(f"Probability of being >10% late: {risk_metrics['probability_10_percent_late']:.1%}")
            print(f"Probability of being >20% late: {risk_metrics['probability_20_percent_late']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='PERT Analysis Command Line Tool')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Perform PERT analysis')
    analyze_parser.add_argument('input_file', help='Input file path')
    analyze_parser.add_argument('-o', '--output', help='Output file path')
    analyze_parser.add_argument('-f', '--format', choices=['csv', 'excel'], default='csv',
                               help='File format (default: csv)')
    analyze_parser.add_argument('-v', '--verbose', action='store_true',
                               help='Enable verbose output')
    
    # Probability command
    prob_parser = subparsers.add_parser('probability', help='Perform probability analysis')
    prob_parser.add_argument('input_file', help='Input file path')
    prob_parser.add_argument('-d', '--durations', nargs='+', type=float,
                            help='Target durations to analyze')
    prob_parser.add_argument('-p', '--probabilities', nargs='+', type=float,
                            help='Target probabilities to analyze (0-1)')
    prob_parser.add_argument('-f', '--format', choices=['csv', 'excel'], default='csv',
                            help='File format (default: csv)')
    prob_parser.add_argument('-v', '--verbose', action='store_true',
                            help='Enable verbose output')
    
    # Sample command
    sample_parser = subparsers.add_parser('sample', help='Generate sample PERT data file')
    sample_parser.add_argument('output_file', help='Output file path')
    sample_parser.add_argument('-f', '--format', choices=['csv', 'excel'], default='csv',
                              help='File format (default: csv)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'analyze':
        success = analyze_project(
            args.input_file, 
            args.output, 
            args.format, 
            args.verbose
        )
    elif args.command == 'probability':
        success = probability_analysis(
            args.input_file,
            args.durations,
            args.probabilities,
            args.format,
            args.verbose
        )
    elif args.command == 'sample':
        try:
            sample_data = FileHandler.get_sample_pert_data()
            if args.format.lower() == 'excel':
                FileHandler.save_excel(sample_data, args.output_file, 'Sample_PERT_Data')
            else:
                FileHandler.save_csv(sample_data, args.output_file)
            print(f"Sample PERT data saved to {args.output_file}")
            success = True
        except Exception as e:
            print(f"Error: {str(e)}")
            success = False
    else:
        parser.print_help()
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
