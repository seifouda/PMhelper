#!/usr/bin/env python3
"""
Risk Analysis CLI Module

Command-line interface for risk analysis features:
- pmhelper risk delay: Delay risk analysis
- pmhelper risk contingency: Contingency planning
- pmhelper risk strategies: Variance reduction strategies
- pmhelper risk prioritize: Activity risk prioritization
- pmhelper risk report: Comprehensive risk report
"""

from pmhelper.utils.file_handlers import FileHandler
from pmhelper.core.pert_analyzer import PERTAnalyzer
import argparse
import sys
import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class RiskCLI:
    """Command-line interface for risk analysis"""

    def __init__(self):
        self.pert_analyzer = None
        self.file_handler = FileHandler()

    def load_pert_data(self, filepath: str) -> bool:
        """Load PERT data from file"""
        try:
            # Read CSV file
            df = pd.read_csv(filepath)

            # Normalize column names to lowercase with underscores (PERT
            # analyzer format)
            df.columns = df.columns.str.strip().str.lower(
            ).str.replace(' ', '_').str.replace('-', '_')

            # Ensure 'id' column exists (from 'activity', 'task', etc.)
            if 'id' not in df.columns:
                if 'activity' in df.columns:
                    df['id'] = df['activity']
                elif 'task' in df.columns:
                    df['id'] = df['task']
                else:
                    print(
                        "Error: CSV must have 'activity', 'task', or 'id' column",
                        file=sys.stderr)
                    return False

            # Ensure 'predecessors' column exists
            if 'predecessors' not in df.columns:
                if 'predecessor' in df.columns:
                    df['predecessors'] = df['predecessor']
                else:
                    df['predecessors'] = ''  # Empty if not specified

            # Validate required columns
            required_cols = ['id', 'optimistic', 'most_likely', 'pessimistic']
            missing_cols = [
                col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(
                    f"Error: CSV is missing required columns: {missing_cols}",
                    file=sys.stderr)
                print(f"Found columns: {list(df.columns)}", file=sys.stderr)
                return False

            # Initialize PERT analyzer
            self.pert_analyzer = PERTAnalyzer()
            # Convert DataFrame to list of dicts for PERT analyzer
            activities_list = df.to_dict('records')
            self.pert_analyzer.analyze(activities_list)

            return True

        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error loading data: {str(e)}", file=sys.stderr)
            return False

    def format_output(self, data: Dict[str, Any], format: str) -> str:
        """Format output based on specified format"""
        if format == 'json':
            return json.dumps(data, indent=2)
        elif format == 'csv':
            # Convert to DataFrame if possible
            if isinstance(
                data, dict) and all(
                isinstance(
                    v, (list, dict)) for v in data.values()):
                df = pd.DataFrame(data)
                return df.to_csv(index=False)
            else:
                # Simple key-value CSV
                output = "Key,Value\n"
                for k, v in data.items():
                    if isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            output += f"{k}.{sub_k},{sub_v}\n"
                    else:
                        output += f"{k},{v}\n"
                return output
        else:  # text format
            return self.format_text(data)

    def format_text(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Format data as human-readable text"""
        output = []
        prefix = "  " * indent

        for key, value in data.items():
            if isinstance(value, dict):
                output.append(f"{prefix}{key}:")
                output.append(self.format_text(value, indent + 1))
            elif isinstance(value, (list, tuple)):
                output.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        output.append(self.format_text(item, indent + 1))
                    else:
                        output.append(f"{prefix}  - {item}")
            elif isinstance(value, float):
                # Format floats nicely
                if abs(value) < 0.01 or abs(value) > 10000:
                    output.append(f"{prefix}{key}: {value:.4e}")
                elif value > 1:
                    output.append(f"{prefix}{key}: {value:.2f}")
                else:
                    output.append(f"{prefix}{key}: {value:.4f}")
            else:
                output.append(f"{prefix}{key}: {value}")

        return "\n".join(output)

    # ========================================================================
    # COMMAND: delay
    # ========================================================================

    def cmd_delay(self, args):
        """Execute delay risk analysis command"""
        if not self.load_pert_data(args.input):
            return 1

        try:
            # Parse max penalty
            max_penalty = None if args.max_penalty is None else float(
                args.max_penalty) / 100.0

            # Calculate delay risk
            result = self.pert_analyzer.analyze_delay_risk(
                contract_time=float(args.contract_time),
                penalty_rate=float(args.penalty_rate),
                max_penalty_percent=max_penalty
            )

            # Format and output
            if args.format == 'text':
                print("=" * 70)
                print("DELAY RISK ANALYSIS")
                print("=" * 70)
                print("\nInput Parameters:")
                print(f"  Contract Time: {args.contract_time} weeks")
                print(f"  Penalty Rate: ${args.penalty_rate}/week")
                if max_penalty:
                    print(f"  Max Penalty: {args.max_penalty}%")
                print("\nResults:")
                print(self.format_text(result))

                # Risk level indicator
                prob = result['delay_probability']
                if prob < 0.1:
                    print(f"\n[OK] RISK LEVEL: LOW ({prob:.1%})")
                elif prob < 0.3:
                    print(f"\n[!] RISK LEVEL: MODERATE ({prob:.1%})")
                else:
                    print(f"\n[!!] RISK LEVEL: HIGH ({prob:.1%})")
            else:
                print(self.format_output(result, args.format))

            return 0

        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1

    # ========================================================================
    # COMMAND: contingency
    # ========================================================================

    def cmd_contingency(self, args):
        """Execute contingency planning command"""
        if not self.load_pert_data(args.input):
            return 1

        try:
            # Parse daily cost
            daily_cost = None if args.daily_cost is None else float(
                args.daily_cost)

            # Calculate contingency
            result = self.pert_analyzer.estimate_contingency(
                confidence_level=float(args.confidence),
                daily_cost_rate=daily_cost
            )

            # Format and output
            if args.format == 'text':
                print("=" * 70)
                print("CONTINGENCY PLANNING")
                print("=" * 70)
                print("\nInput Parameters:")
                print(f"  Confidence Level: {args.confidence * 100:.0f}%")
                if daily_cost:
                    print(f"  Daily Cost Rate: ${daily_cost}/day")
                print("\nResults:")
                print(self.format_text(result))
                print(f"\n{result['recommendation']}")
            else:
                print(self.format_output(result, args.format))

            return 0

        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1

    # ========================================================================
    # COMMAND: strategies
    # ========================================================================

    def cmd_strategies(self, args):
        """Execute variance reduction strategies command"""
        if not self.load_pert_data(args.input):
            return 1

        try:
            # Calculate strategies
            result = self.pert_analyzer.analyze_variance_reduction_strategies(
                contract_time=float(args.contract_time),
                penalty_rate=float(args.penalty_rate),
                time_reduction_cost=float(args.time_cost),
                variance_reduction_cost=float(args.variance_cost),
                max_budget=float(args.budget)
            )

            # Format and output
            if args.format == 'text':
                print("=" * 70)
                print("VARIANCE REDUCTION STRATEGY COMPARISON")
                print("=" * 70)
                print("\nInput Parameters:")
                print(f"  Contract Time: {args.contract_time} weeks")
                print(f"  Penalty Rate: ${args.penalty_rate}/week")
                print(f"  Time Reduction Cost: ${args.time_cost}/week")
                print(f"  Variance Reduction Cost: ${args.variance_cost}/unit")
                print(f"  Max Budget: ${args.budget}")

                print("\nBaseline:")
                print(f"  Risk Cost: ${result['baseline']['risk_cost']:,.2f}")

                print("\nStrategy A (Reduce Time):")
                sa = result['strategy_a']
                print(f"  Time Reduction: {sa['time_reduction']:.2f} weeks")
                print(f"  Investment: ${sa['investment']:,.2f}")
                print(f"  Benefit: ${sa['benefit']:,.2f}")
                print(f"  Net Benefit: ${sa['net_benefit']:,.2f}")
                print(f"  ROI: {sa['roi']:.1f}%")

                print("\nStrategy B (Reduce Variance):")
                sb = result['strategy_b']
                print(f"  Variance Reduction: {sb['variance_reduction']:.2f}")
                print(f"  Investment: ${sb['investment']:,.2f}")
                print(f"  Benefit: ${sb['benefit']:,.2f}")
                print(f"  Net Benefit: ${sb['net_benefit']:,.2f}")
                print(f"  ROI: {sb['roi']:.1f}%")

                print("\nMixed Strategy:")
                sm = result['mixed_strategy']
                print(f"  Time Reduction: {sm['time_reduction']:.2f} weeks")
                print(f"  Variance Reduction: {sm['variance_reduction']:.2f}")
                print(f"  Investment: ${sm['investment']:,.2f}")
                print(f"  Benefit: ${sm['benefit']:,.2f}")
                print(f"  Net Benefit: ${sm['net_benefit']:,.2f}")
                print(f"  ROI: {sm['roi']:.1f}%")

                best = result['best_strategy']
                print(f"\n[BEST] RECOMMENDED STRATEGY: {best['name']}")
                print(f"  Best Net Benefit: ${best['net_benefit']:,.2f}")
            else:
                print(self.format_output(result, args.format))

            return 0

        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1

    # ========================================================================
    # COMMAND: prioritize
    # ========================================================================

    def cmd_prioritize(self, args):
        """Execute activity risk prioritization command"""
        if not self.load_pert_data(args.input):
            return 1

        try:
            # Calculate risk scores
            df = self.pert_analyzer.prioritize_activity_risks()

            # Format and output
            if args.format == 'csv':
                print(df.to_csv(index=False))
            elif args.format == 'json':
                print(df.to_json(orient='records', indent=2))
            else:  # text
                print("=" * 70)
                print("ACTIVITY RISK PRIORITIZATION")
                print("=" * 70)
                print(f"\nTotal Activities: {len(df)}")

                # Count by risk level
                high_risk = len(df[df['risk_score'] >= 0.6])
                medium_risk = len(
                    df[(df['risk_score'] >= 0.3) & (df['risk_score'] < 0.6)])
                low_risk = len(df[df['risk_score'] < 0.3])

                print(f"High Risk (≥0.6): {high_risk}")
                print(f"Medium Risk (0.3-0.6): {medium_risk}")
                print(f"Low Risk (<0.3): {low_risk}")

                print("\nActivity Details:")
                print(
                    f"{
                        'Activity':<12} {
                        'Risk Score':<12} {
                        'Exp.Time':<12} {
                        'Variance':<12} {
                        'Float':<12}")
                print("-" * 70)

                for idx, row in df.iterrows():
                    print(
                        f"{
                            row['activity_id']:<12} {
                            row['risk_score']:<12.3f} " f"{
                            row['expected_time']:<12.2f} {
                            row['variance']:<12.3f} " f"{
                            row['total_float']:<12.2f}")

                if args.show_recommendations:
                    print("\nRecommendations:")
                    print("-" * 70)
                    for idx, row in df.iterrows():
                        print(f"{row['activity_id']}: {row['recommendation']}")

            return 0

        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1

    # ========================================================================
    # COMMAND: report
    # ========================================================================

    def cmd_report(self, args):
        """Execute comprehensive risk report command"""
        if not self.load_pert_data(args.input):
            return 1

        try:
            print("=" * 70)
            print("COMPREHENSIVE RISK ANALYSIS REPORT")
            print("=" * 70)
            print(f"\nProject: {Path(args.input).stem}")
            print(
                f"Analysis Date: {
                    pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Parse max penalty
            max_penalty = None if args.max_penalty is None else float(
                args.max_penalty) / 100.0
            daily_cost = None if args.daily_cost is None else float(
                args.daily_cost)

            # 1. Delay Risk Analysis
            print("\n" + "=" * 70)
            print("1. DELAY RISK ANALYSIS")
            print("=" * 70)
            delay_result = self.pert_analyzer.analyze_delay_risk(
                contract_time=float(args.contract_time),
                penalty_rate=float(args.penalty_rate),
                max_penalty_percent=max_penalty
            )
            print(self.format_text(delay_result))

            # 2. Contingency Planning
            print("\n" + "=" * 70)
            print("2. CONTINGENCY PLANNING")
            print("=" * 70)
            contingency_result = self.pert_analyzer.estimate_contingency(
                confidence_level=float(args.confidence),
                daily_cost_rate=daily_cost
            )
            print(self.format_text(contingency_result))

            # 3. Variance Reduction Strategies
            print("\n" + "=" * 70)
            print("3. VARIANCE REDUCTION STRATEGIES")
            print("=" * 70)
            if args.time_cost and args.variance_cost and args.budget:
                strategies_result = self.pert_analyzer.analyze_variance_reduction_strategies(
                    contract_time=float(
                        args.contract_time), penalty_rate=float(
                        args.penalty_rate), time_reduction_cost=float(
                        args.time_cost), variance_reduction_cost=float(
                        args.variance_cost), max_budget=float(
                        args.budget))
                print(self.format_text(strategies_result))
            else:
                print(
                    "  [Skipped: Requires --time-cost, --variance-cost, and --budget]")

            # 4. Activity Risk Prioritization
            print("\n" + "=" * 70)
            print("4. ACTIVITY RISK PRIORITIZATION")
            print("=" * 70)
            df = self.pert_analyzer.prioritize_activity_risks()

            high_risk = df[df['risk_score'] >= 0.6]
            print(f"\nHigh Priority Activities ({len(high_risk)}):")
            if len(high_risk) > 0:
                for idx, row in high_risk.iterrows():
                    print(
                        f"  {
                            row['activity_id']}: Risk={
                            row['risk_score']:.3f}, {
                            row['recommendation']}")
            else:
                print("  None")

            medium_risk = df[(df['risk_score'] >= 0.3) &
                             (df['risk_score'] < 0.6)]
            print(f"\nMedium Priority Activities ({len(medium_risk)}):")
            if len(medium_risk) > 0:
                for idx, row in medium_risk.head(5).iterrows():
                    print(
                        f"  {
                            row['activity_id']}: Risk={
                            row['risk_score']:.3f}, {
                            row['recommendation']}")
                if len(medium_risk) > 5:
                    print(f"  ... and {len(medium_risk) - 5} more")
            else:
                print("  None")

            # 5. Overall Recommendations
            print("\n" + "=" * 70)
            print("5. OVERALL RECOMMENDATIONS")
            print("=" * 70)

            delay_prob = delay_result['delay_probability']
            if delay_prob > 0.3:
                print("  [!] HIGH RISK PROJECT")
                print("  - Add contingency buffer immediately")
                print("  - Focus on high-risk activities")
                print("  - Consider variance reduction strategies")
            elif delay_prob > 0.1:
                print("  [!] MODERATE RISK PROJECT")
                print("  - Add recommended contingency buffer")
                print("  - Monitor high-risk activities closely")
            else:
                print("  [OK] LOW RISK PROJECT")
                print("  - Minimal contingency needed")
                print("  - Standard monitoring sufficient")

            print("\n" + "=" * 70)
            print("END OF REPORT")
            print("=" * 70)

            return 0

        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1


def create_parser():
    """Create argument parser for CLI"""
    parser = argparse.ArgumentParser(
        prog='pmhelper risk',
        description='Risk analysis tools for PERT projects'
    )

    subparsers = parser.add_subparsers(
        dest='command', help='Risk analysis commands')

    # ========================================================================
    # COMMAND: delay
    # ========================================================================
    delay_parser = subparsers.add_parser(
        'delay',
        help='Analyze delay risk and calculate expected delay'
    )
    delay_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input PERT data CSV file'
    )
    delay_parser.add_argument(
        '-c', '--contract-time',
        required=True,
        type=float,
        help='Contract completion time (weeks)'
    )
    delay_parser.add_argument(
        '-p', '--penalty-rate',
        required=True,
        type=float,
        help='Penalty rate per time unit ($/week)'
    )
    delay_parser.add_argument(
        '-m', '--max-penalty',
        type=float,
        default=None,
        help='Maximum penalty as percentage of project value (default: no cap)'
    )
    delay_parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format (default: text)'
    )

    # ========================================================================
    # COMMAND: contingency
    # ========================================================================
    contingency_parser = subparsers.add_parser(
        'contingency',
        help='Estimate contingency buffer for target confidence level'
    )
    contingency_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input PERT data CSV file'
    )
    contingency_parser.add_argument(
        '-c', '--confidence',
        type=float,
        default=0.95,
        help='Confidence level (0.80-0.999, default: 0.95)'
    )
    contingency_parser.add_argument(
        '-d', '--daily-cost',
        type=float,
        default=None,
        help='Daily cost rate for budget estimation ($/day)'
    )
    contingency_parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format (default: text)'
    )

    # ========================================================================
    # COMMAND: strategies
    # ========================================================================
    strategies_parser = subparsers.add_parser(
        'strategies',
        help='Compare variance reduction strategies'
    )
    strategies_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input PERT data CSV file'
    )
    strategies_parser.add_argument(
        '-c', '--contract-time',
        required=True,
        type=float,
        help='Contract completion time (weeks)'
    )
    strategies_parser.add_argument(
        '-p', '--penalty-rate',
        required=True,
        type=float,
        help='Penalty rate per time unit ($/week)'
    )
    strategies_parser.add_argument(
        '-t', '--time-cost',
        required=True,
        type=float,
        help='Cost per unit time reduction ($/week)'
    )
    strategies_parser.add_argument(
        '-v', '--variance-cost',
        required=True,
        type=float,
        help='Cost per unit variance reduction ($/unit)'
    )
    strategies_parser.add_argument(
        '-b', '--budget',
        required=True,
        type=float,
        help='Maximum budget for variance reduction ($)'
    )
    strategies_parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format (default: text)'
    )

    # ========================================================================
    # COMMAND: prioritize
    # ========================================================================
    prioritize_parser = subparsers.add_parser(
        'prioritize',
        help='Prioritize activities by risk score'
    )
    prioritize_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input PERT data CSV file'
    )
    prioritize_parser.add_argument(
        '-r', '--show-recommendations',
        action='store_true',
        help='Show detailed recommendations for each activity'
    )
    prioritize_parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format (default: text)'
    )

    # ========================================================================
    # COMMAND: report
    # ========================================================================
    report_parser = subparsers.add_parser(
        'report',
        help='Generate comprehensive risk analysis report'
    )
    report_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input PERT data CSV file'
    )
    report_parser.add_argument(
        '-c', '--contract-time',
        required=True,
        type=float,
        help='Contract completion time (weeks)'
    )
    report_parser.add_argument(
        '-p', '--penalty-rate',
        required=True,
        type=float,
        help='Penalty rate per time unit ($/week)'
    )
    report_parser.add_argument(
        '--confidence',
        type=float,
        default=0.95,
        help='Confidence level for contingency (default: 0.95)'
    )
    report_parser.add_argument(
        '-m', '--max-penalty',
        type=float,
        default=None,
        help='Maximum penalty percentage (default: no cap)'
    )
    report_parser.add_argument(
        '-d', '--daily-cost',
        type=float,
        default=None,
        help='Daily cost rate ($/day)'
    )
    report_parser.add_argument(
        '-t', '--time-cost',
        type=float,
        help='Cost per unit time reduction ($/week) - optional for strategies'
    )
    report_parser.add_argument(
        '-v',
        '--variance-cost',
        type=float,
        help='Cost per unit variance reduction ($/unit) - optional for strategies')
    report_parser.add_argument(
        '-b', '--budget',
        type=float,
        help='Maximum budget for variance reduction ($) - optional for strategies'
    )

    return parser


def main(args=None):
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args(args)

    if not args.command:
        parser.print_help()
        return 1

    # Create CLI instance
    cli = RiskCLI()

    # Execute command
    if args.command == 'delay':
        return cli.cmd_delay(args)
    elif args.command == 'contingency':
        return cli.cmd_contingency(args)
    elif args.command == 'strategies':
        return cli.cmd_strategies(args)
    elif args.command == 'prioritize':
        return cli.cmd_prioritize(args)
    elif args.command == 'report':
        return cli.cmd_report(args)
    else:
        print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
