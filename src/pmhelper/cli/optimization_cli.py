#!/usr/bin/env python3
"""
Cost Optimization CLI Module

Command-line interface for advanced cost optimization features:
- Time-Cost Optimization
- Resource Leveling
- NPV Maximization
- Multi-Objective Pareto Analysis

Author: PMHelper Team
Version: 1.1.0
"""

from pmhelper.core.multi_objective_visualizations import (
    plot_pareto_frontier_2d,
    generate_multi_objective_report,
    export_pareto_solutions)
from pmhelper.core.multi_objective import MultiObjectiveOptimizer, ScheduleGenerator
from pmhelper.core.npv_optimization import NPVOptimizer, activities_from_cpm_with_cashflows
from pmhelper.core.resource_visualizations import (
    plot_resource_profile, generate_leveling_report
)
from pmhelper.core.resource_leveling import ResourceLevelingFactory, activities_from_cpm
from pmhelper.core.cost_visualizations import (
    plot_time_cost_curve, generate_cost_report, export_optimization_results
)
from pmhelper.core.cost_optimization import IndirectCostModel, TimeCostOptimizer
from pmhelper.core.cpm_analyzer import CPMAnalyzer
from pmhelper.utils.file_handlers import FileHandler
import argparse
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def optimize_time_cost(args):
    """
    Perform time-cost optimization

    Args:
        args: Command line arguments with input_file, indirect_costs, output
    """
    print("=== Time-Cost Optimization ===\n")

    # Load project data
    print(f"Loading project from {args.input_file}...")
    if args.input_file.endswith('.xlsx'):
        activities_data = FileHandler.load_excel(args.input_file)
    else:
        activities_data = FileHandler.load_csv(args.input_file)
    print(f"Loaded {len(activities_data)} activities\n")

    # Analyze with CPM
    print("Performing CPM analysis...")
    analyzer = CPMAnalyzer()
    analyzer.analyze(activities_data)
    print("CPM analysis complete\n")

    # Load indirect costs
    print(f"Loading indirect costs from {args.indirect_costs}...")
    with open(args.indirect_costs, 'r') as f:
        daily_costs = json.load(f)
    print(f"Loaded costs: {daily_costs}\n")

    # Create indirect cost model
    indirect_model = IndirectCostModel(daily_costs)

    # Create optimizer
    optimizer = TimeCostOptimizer(analyzer, indirect_model)

    # Find optimal duration
    print("Optimizing project duration...")
    result = optimizer.find_optimal_duration()

    # Generate curve
    curve_data = optimizer.generate_curve()

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Optimal Duration: {result['optimal_duration']} days")
    print(f"Optimal Total Cost: ${result['optimal_total_cost']:,.2f}")
    print(f"Direct Cost: ${result['direct_cost']:,.2f}")
    print(f"Indirect Cost: ${result['indirect_cost']:,.2f}")
    print(
        f"Savings: ${
            result.get(
                'savings',
                0):,.2f} ({
            result.get(
                'savings_pct',
                0):.2f}%)")
    print("=" * 60 + "\n")

    # Generate report
    report = generate_cost_report(result, daily_costs)

    # Save outputs
    if args.output:
        base_path = args.output

        # Save visualization
        print("Generating visualization...")
        fig = plot_time_cost_curve(
            curve_data, result, save_path=f"{base_path}_curve.png")
        print(f"✓ Saved: {base_path}_curve.png")

        # Save report
        with open(f"{base_path}_report.txt", 'w') as f:
            f.write(report)
        print(f"✓ Saved: {base_path}_report.txt")

        # Export data
        export_optimization_results(result, curve_data, base_path,
                                    formats=['csv', 'json'])
        print(f"✓ Saved: {base_path}.csv, {base_path}.json")

    print("\nOptimization complete!")


def optimize_resources(args):
    """
    Perform resource leveling

    Args:
        args: Command line arguments with input_file, method, limit, output
    """
    print("=== Resource Leveling ===\n")

    # Load project data
    print(f"Loading project from {args.input_file}...")
    if args.input_file.endswith('.xlsx'):
        activities_data = FileHandler.load_excel(args.input_file)
    else:
        activities_data = FileHandler.load_csv(args.input_file)
    print(f"Loaded {len(activities_data)} activities\n")

    # Analyze with CPM
    print("Performing CPM analysis...")
    analyzer = CPMAnalyzer()
    analyzer.analyze(activities_data)
    print("CPM analysis complete\n")

    # Convert to activities
    activities = activities_from_cpm(analyzer)

    # Create leveler
    print(f"Creating {args.method} leveler...")
    resource_limit = args.limit if args.limit else None
    leveler = ResourceLevelingFactory.create(
        args.method, activities, resource_limit)

    # Run leveling
    print("Leveling resources...")
    result = leveler.level()

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Method: {result['method']}")
    print("\nOriginal Schedule:")
    print(f"  Peak Usage: {result['original_peak']:.1f}")
    print(f"  Total Moment: {result['original_moment']:.1f}")
    print(f"  Average Usage: {result['original_avg']:.1f}")
    print("\nLeveled Schedule:")
    print(f"  Peak Usage: {result['leveled_peak']:.1f}")
    print(f"  Total Moment: {result['leveled_moment']:.1f}")
    print(f"  Average Usage: {result['leveled_avg']:.1f}")
    print(f"\nImprovement: {result['improvement']:.2f}%")
    print(f"Moves Made: {result['moves_made']}")
    print("=" * 60 + "\n")

    # Save outputs
    if args.output:
        base_path = args.output

        # Generate visualization
        print("Generating visualization...")
        fig = plot_resource_profile(
            result, save_path=f"{base_path}_profile.png")
        print(f"✓ Saved: {base_path}_profile.png")

        # Generate report
        report = generate_leveling_report(result)
        with open(f"{base_path}_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ Saved: {base_path}_report.txt")

        # Export schedule
        if 'leveled_schedule' in result:
            schedule_data = [{
                'activity': act,
                'start_time': time
            } for act, time in result['leveled_schedule'].items()]
            FileHandler.save_csv(schedule_data, f"{base_path}_schedule.csv")
            print(f"✓ Saved: {base_path}_schedule.csv")

    print("\nLeveling complete!")


def optimize_npv(args):
    """
    Perform NPV optimization

    Args:
        args: Command line arguments with input_file, cash_flows, discount_rate, output
    """
    print("=== NPV Optimization ===\n")

    # Load project data
    print(f"Loading project from {args.input_file}...")
    if args.input_file.endswith('.xlsx'):
        activities_data = FileHandler.load_excel(args.input_file)
    else:
        activities_data = FileHandler.load_csv(args.input_file)
    print(f"Loaded {len(activities_data)} activities\n")

    # Analyze with CPM
    print("Performing CPM analysis...")
    analyzer = CPMAnalyzer()
    analyzer.analyze(activities_data)
    print("CPM analysis complete\n")

    # Load cash flows
    print(f"Loading cash flows from {args.cash_flows}...")
    with open(args.cash_flows, 'r') as f:
        cash_flows = json.load(f)
    print(f"Loaded cash flows for {len(cash_flows)} activities\n")

    # Convert to cash flow activities
    activities = activities_from_cpm_with_cashflows(analyzer, cash_flows)

    # Create optimizer
    optimizer = NPVOptimizer(activities, discount_rate=args.discount_rate)

    # Optimize
    print("Optimizing schedule for maximum NPV...")
    result = optimizer.maximize_npv()

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Discount Rate: {args.discount_rate * 100:.1f}%")
    print(f"\nOriginal NPV: ${result['original_npv']:,.2f}")
    print(f"Optimized NPV: ${result['optimal_npv']:,.2f}")
    print(
        f"Improvement: ${
            result['improvement']:,.2f} ({
            result['improvement_pct']:.2f}%)")
    print(f"Iterations: {result['iterations']}")

    if result['moved_activities']:
        print(f"\nActivities Repositioned: {len(result['moved_activities'])}")
        for move in result['moved_activities']:
            print(
                f"  • {
                    move['id']}: {
                    move['original_start']} → {
                    move['optimal_start']}")

    print("=" * 60 + "\n")

    # Sensitivity analysis if requested
    if args.sensitivity:
        print("Running sensitivity analysis...")
        rates = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20]
        sensitivity_df = optimizer.sensitivity_analysis(rates)

        print("\nSensitivity Analysis:")
        print(sensitivity_df.to_string(index=False))
        print()

        if args.output:
            from pmhelper.core.multi_objective_visualizations import plot_npv_sensitivity
            fig = plot_npv_sensitivity(
                sensitivity_df, save_path=f"{
                    args.output}_sensitivity.png")
            print(f"✓ Saved: {args.output}_sensitivity.png")

            sensitivity_df.to_csv(
                f"{args.output}_sensitivity.csv", index=False)
            print(f"✓ Saved: {args.output}_sensitivity.csv")

    # Save outputs
    if args.output:
        # Save schedule
        schedule_data = [{
            'activity': act,
            'start_time': time
        } for act, time in result['optimal_schedule'].items()]
        FileHandler.save_csv(schedule_data, f"{args.output}_schedule.csv")
        print(f"✓ Saved: {args.output}_schedule.csv")

        # Save cash flow schedule
        cf_schedule = optimizer.get_cash_flow_schedule(
            result['optimal_schedule'])
        cf_schedule.to_csv(f"{args.output}_cashflows.csv", index=False)
        print(f"✓ Saved: {args.output}_cashflows.csv")

    print("\nNPV optimization complete!")


def optimize_pareto(args):
    """
    Perform multi-objective Pareto optimization

    Args:
        args: Command line arguments with input_file, objectives, samples, output
    """
    print("=== Multi-Objective Pareto Optimization ===\n")

    # Load project data
    print(f"Loading project from {args.input_file}...")
    if args.input_file.endswith('.xlsx'):
        activities_data = FileHandler.load_excel(args.input_file)
    else:
        activities_data = FileHandler.load_csv(args.input_file)
    print(f"Loaded {len(activities_data)} activities\n")

    # Analyze with CPM
    print("Performing CPM analysis...")
    analyzer = CPMAnalyzer()
    analyzer.analyze(activities_data)
    print("CPM analysis complete\n")

    # Convert to activities
    activities = activities_from_cpm(analyzer)

    # Parse objectives
    objectives_list = args.objectives.split(',')
    print(f"Objectives: {', '.join(objectives_list)}\n")

    # Define objective functions
    def calc_duration(schedule):
        return max(schedule.get(act.id, act.es) +
                   act.duration for act in activities)

    def calc_cost(schedule):
        # Simplified: use duration as proxy
        return sum(act.duration * 100 for act in activities)

    objectives = {}
    if 'duration' in objectives_list:
        objectives['duration'] = calc_duration
    if 'cost' in objectives_list:
        objectives['cost'] = calc_cost

    # Create optimizer
    optimizer = MultiObjectiveOptimizer(objectives)

    # Generate schedules
    print(f"Generating {args.samples} candidate schedules...")
    schedules = ScheduleGenerator.generate_sampled(activities, args.samples)

    # Compute Pareto frontier
    print("Computing Pareto frontier...")
    frontier = optimizer.generate_solutions_grid(
        schedules, list(objectives.keys()))

    # Get summary
    solutions_df = optimizer.get_solution_summary()
    pareto_df = optimizer.get_pareto_summary()

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total Solutions Evaluated: {len(optimizer.solutions)}")
    print(f"Pareto Frontier Size: {len(frontier)}")
    print(
        f"Pareto Efficiency: {len(frontier) / len(optimizer.solutions) * 100:.1f}%")
    print("\nPareto Solutions:")
    print(pareto_df.to_string(index=False))
    print("=" * 60 + "\n")

    # Save outputs
    if args.output:
        base_path = args.output

        # Generate visualization
        if len(objectives_list) >= 2:
            print("Generating Pareto frontier visualization...")
            obj1, obj2 = objectives_list[0], objectives_list[1]
            fig = plot_pareto_frontier_2d(
                solutions_df, obj1, obj2,
                minimize_obj1=True, minimize_obj2=True,
                save_path=f"{base_path}_pareto.png"
            )
            print(f"✓ Saved: {base_path}_pareto.png")

        # Generate report
        report = generate_multi_objective_report(
            optimizer, pareto_df, objectives_list,
            save_path=f"{base_path}_report.txt"
        )
        print(f"✓ Saved: {base_path}_report.txt")

        # Export Pareto solutions
        pareto_schedules = [sol.schedule for sol in optimizer.pareto_frontier]
        export_pareto_solutions(pareto_df, pareto_schedules, base_path,
                                formats=['csv', 'json'])
        print(f"✓ Saved: {base_path}.csv, {base_path}.json")

    print("\nPareto optimization complete!")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='PMHelper Cost Optimization Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Time-Cost Optimization
  pmhelper optimize time-cost --input project.csv --indirect costs.json --output results/tc

  # Resource Leveling
  pmhelper optimize resources --input project.csv --method minimum_moment --limit 10 --output results/rl

  # NPV Optimization
  pmhelper optimize npv --input project.csv --cash-flows flows.json --discount-rate 0.12 --output results/npv

  # Pareto Frontier
  pmhelper optimize pareto --input project.csv --objectives duration,cost --samples 100 --output results/pareto
        """
    )

    subparsers = parser.add_subparsers(
        dest='command', help='Optimization type')

    # Time-Cost Optimization
    tc_parser = subparsers.add_parser(
        'time-cost', help='Time-cost trade-off optimization')
    tc_parser.add_argument(
        '--input',
        required=True,
        help='Input project file (CSV/Excel)')
    tc_parser.add_argument('--indirect', dest='indirect_costs', required=True,
                           help='Indirect costs JSON file')
    tc_parser.add_argument('--output', help='Output base path')
    tc_parser.set_defaults(func=optimize_time_cost)

    # Resource Leveling
    rl_parser = subparsers.add_parser(
        'resources', help='Resource leveling optimization')
    rl_parser.add_argument('--input', dest='input_file', required=True,
                           help='Input project file (CSV/Excel)')
    rl_parser.add_argument('--method', choices=['minimum_moment', 'burgess'],
                           default='minimum_moment', help='Leveling method')
    rl_parser.add_argument(
        '--limit',
        type=float,
        help='Resource limit (optional)')
    rl_parser.add_argument('--output', help='Output base path')
    rl_parser.set_defaults(func=optimize_resources)

    # NPV Optimization
    npv_parser = subparsers.add_parser('npv', help='NPV maximization')
    npv_parser.add_argument('--input', dest='input_file', required=True,
                            help='Input project file (CSV/Excel)')
    npv_parser.add_argument(
        '--cash-flows',
        dest='cash_flows',
        required=True,
        help='Cash flows JSON file (activity_id: cash_flow)')
    npv_parser.add_argument(
        '--discount-rate',
        dest='discount_rate',
        type=float,
        default=0.10,
        help='Discount rate (default: 0.10)')
    npv_parser.add_argument('--sensitivity', action='store_true',
                            help='Run sensitivity analysis')
    npv_parser.add_argument('--output', help='Output base path')
    npv_parser.set_defaults(func=optimize_npv)

    # Pareto Frontier
    pareto_parser = subparsers.add_parser(
        'pareto', help='Multi-objective Pareto optimization')
    pareto_parser.add_argument('--input', dest='input_file', required=True,
                               help='Input project file (CSV/Excel)')
    pareto_parser.add_argument(
        '--objectives',
        required=True,
        help='Comma-separated objectives (e.g., duration,cost)')
    pareto_parser.add_argument(
        '--samples',
        type=int,
        default=100,
        help='Number of candidate schedules (default: 100)')
    pareto_parser.add_argument('--output', help='Output base path')
    pareto_parser.set_defaults(func=optimize_pareto)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Run selected command
    try:
        args.func(args)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
