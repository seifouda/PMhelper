#!/usr/bin/env python3
"""
CPM CLI Module

Command-line interface for Critical Path Method analysis.
Provides command-line tools for CPM calculations, project scheduling, and reporting.
"""

from pmhelper.utils.calculations import CostCalculations, NetworkMetrics
from pmhelper.utils.file_handlers import FileHandler
from pmhelper.core.cpm_analyzer import CPMAnalyzer
import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def analyze_project(
        input_file,
        output_file=None,
        format_type='csv',
        verbose=False):
    """
    Analyze a project using CPM

    Args:
        input_file (str): Path to input file
        output_file (str): Path to output file (optional)
        format_type (str): File format ('csv' or 'excel')
        verbose (bool): Enable verbose output
    """
    try:
        # Load data
        if verbose:
            print(f"Loading data from {input_file}...")

        if format_type.lower() == 'excel':
            activities_data = FileHandler.load_excel(input_file)
        else:
            activities_data = FileHandler.load_csv(input_file)

        if verbose:
            print(f"Loaded {len(activities_data)} activities")

        # Validate required columns
        required_columns = ['id', 'duration']
        FileHandler.validate_required_columns(
            activities_data, required_columns)

        # Perform analysis
        analyzer = CPMAnalyzer()
        G, critical_paths, critical_activities = analyzer.analyze(
            activities_data)

        # Display results
        print("\\n=== CPM Analysis Results ===")
        print(
            f"Project Duration: {max([G.nodes[node]['EF'] for node in G.nodes()])} time units")
        print(
            f"Critical Path: {
                ' -> '.join(
                    critical_paths[0]) if critical_paths and critical_paths[0] else 'None found'}")
        print(f"Critical Activities: {', '.join(critical_activities)}")

        # Network metrics
        if verbose:
            metrics = NetworkMetrics.calculate_network_complexity(G)
            print("\\nNetwork Complexity:")
            print(f"  - Total Activities: {metrics['num_nodes']}")
            print(f"  - Dependencies: {metrics['num_edges']}")
            print(f"  - Network Density: {metrics['density']:.3f}")

        # Prepare results for export
        results_data = []
        for node in G.nodes():
            if node not in ['START', 'END']:
                results_data.append({
                    'activity_id': node,
                    'activity_name': G.nodes[node].get('activity', ''),
                    'duration': G.nodes[node]['duration'],
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
                FileHandler.save_excel(
                    results_data, output_file, 'CPM_Results')
            else:
                FileHandler.save_csv(results_data, output_file)
            print(f"\\nResults saved to {output_file}")

        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def crash_optimization(
        input_file,
        target_duration,
        max_budget=None,
        output_file=None,
        format_type='csv',
        verbose=False):
    """
    Perform crash optimization analysis

    Args:
        input_file (str): Path to input file
        target_duration (float): Target project duration
        max_budget (float): Maximum crash budget (optional)
        output_file (str): Path to output file (optional)
        format_type (str): File format ('csv' or 'excel')
        verbose (bool): Enable verbose output
    """
    try:
        # Load and analyze project
        if format_type.lower() == 'excel':
            activities_data = FileHandler.load_excel(input_file)
        else:
            activities_data = FileHandler.load_csv(input_file)

        analyzer = CPMAnalyzer()
        G, _, _ = analyzer.analyze(activities_data)

        initial_duration = max([G.nodes[node]['EF'] for node in G.nodes()])

        if verbose:
            print(f"Initial project duration: {initial_duration}")
            print(f"Target duration: {target_duration}")
            if max_budget:
                print(f"Maximum budget: {max_budget}")

        # Perform crash optimization
        crashed_G, total_crash_cost, crash_log = analyzer.crash_project(
            target_duration, max_budget=max_budget
        )

        final_duration = max([crashed_G.nodes[node]['EF']
                             for node in crashed_G.nodes()])

        # Display results
        print("\\n=== Crash Optimization Results ===")
        print(f"Initial Duration: {initial_duration} time units")
        print(f"Final Duration: {final_duration} time units")
        print(f"Time Saved: {initial_duration - final_duration} time units")
        print(f"Total Crash Cost: {total_crash_cost}")
        print(
            f"Target Achieved: {
                'Yes' if final_duration <= target_duration else 'No'}")

        if verbose and crash_log:
            print("\\nCrash Log:")
            for entry in crash_log:
                print(
                    f"  Step {
                        entry['iteration']}: Crashed activity {
                        entry['activity']} " f"(Cost: {
                        entry['crash_cost']}, New Duration: {
                        entry['new_duration']})")

        # Cost efficiency
        efficiency = CostCalculations.calculate_crash_efficiency(
            initial_duration, final_duration, total_crash_cost
        )
        print("\\nCost Efficiency:")
        print(
            f"  - Time Reduction: {efficiency['time_reduction_percent']:.1f}%")
        print(
            f"  - Cost per Time Unit: {efficiency['cost_per_time_unit']:.2f}")

        # Save results if requested
        if output_file and crash_log:
            if format_type.lower() == 'excel':
                FileHandler.save_excel(crash_log, output_file, 'Crash_Log')
            else:
                FileHandler.save_csv(crash_log, output_file)
            print(f"\\nCrash log saved to {output_file}")

        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='CPM Analysis Command Line Tool')

    subparsers = parser.add_subparsers(
        dest='command', help='Available commands')

    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze', help='Perform CPM analysis')
    analyze_parser.add_argument('input_file', help='Input file path')
    analyze_parser.add_argument('-o', '--output', help='Output file path')
    analyze_parser.add_argument(
        '-f',
        '--format',
        choices=[
            'csv',
            'excel'],
        default='csv',
        help='File format (default: csv)')
    analyze_parser.add_argument('-v', '--verbose', action='store_true',
                                help='Enable verbose output')

    # Crash command
    crash_parser = subparsers.add_parser(
        'crash', help='Perform crash optimization')
    crash_parser.add_argument('input_file', help='Input file path')
    crash_parser.add_argument(
        'target_duration',
        type=float,
        help='Target project duration')
    crash_parser.add_argument(
        '-b',
        '--budget',
        type=float,
        help='Maximum crash budget')
    crash_parser.add_argument(
        '-o',
        '--output',
        help='Output file path for crash log')
    crash_parser.add_argument(
        '-f',
        '--format',
        choices=[
            'csv',
            'excel'],
        default='csv',
        help='File format (default: csv)')
    crash_parser.add_argument('-v', '--verbose', action='store_true',
                              help='Enable verbose output')

    # Sample command
    sample_parser = subparsers.add_parser(
        'sample', help='Generate sample data file')
    sample_parser.add_argument('output_file', help='Output file path')
    sample_parser.add_argument(
        '-f',
        '--format',
        choices=[
            'csv',
            'excel'],
        default='csv',
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
    elif args.command == 'crash':
        success = crash_optimization(
            args.input_file,
            args.target_duration,
            args.budget,
            args.output,
            args.format,
            args.verbose
        )
    elif args.command == 'sample':
        try:
            sample_data = FileHandler.get_sample_cpm_data()
            if args.format.lower() == 'excel':
                FileHandler.save_excel(
                    sample_data, args.output_file, 'Sample_CPM_Data')
            else:
                FileHandler.save_csv(sample_data, args.output_file)
            print(f"Sample data saved to {args.output_file}")
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
