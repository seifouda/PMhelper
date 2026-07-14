#!/usr/bin/env python3
"""
Project Selection CLI Module

Command-line interface for project selection and decision analysis.
Provides CLI tools for AHP, Linear Scoring, B/C Analysis, and Portfolio Optimization.

Author: PMHelper Team
Version: 1.0.0
"""

from pmhelper.utils.selection_io import (
    SelectionFileHandler, SelectionExportHandler
)
from pmhelper.core.selection import (
    AHPAnalyzer, LinearScoringAnalyzer, BenefitCostAnalyzer,
    PortfolioOptimizer, CriterionDirection
)
import click
import json
import sys
from pathlib import Path
import pandas as pd

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@click.group()
@click.version_option(version='1.0.0')
def selection():
    """
    Project Selection and Decision Analysis Tools

    Provides multiple methods for project selection:
    - AHP: Analytic Hierarchy Process
    - Linear Scoring: Multi-criteria scoring with normalization
    - B/C Analysis: Benefit-to-Cost analysis
    - Portfolio: Project portfolio optimization

    Examples:
        pmhelper selection ahp --help
        pmhelper selection portfolio --budget 5000000 --projects projects.csv
    """


@selection.command()
@click.option('--criteria', '-c', type=click.Path(exists=True), required=True,
              help='JSON file with criteria definitions')
@click.option('--matrix', '-m', type=click.Path(exists=True), required=True,
              help='CSV file with pairwise comparison matrix')
@click.option('--alternatives', '-a', type=click.Path(exists=True),
              help='CSV file with alternatives and scores')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file path for results (JSON)')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
def ahp(criteria, matrix, alternatives, output, verbose):
    """
    Perform Analytic Hierarchy Process (AHP) analysis.

    Calculate criterion weights from pairwise comparisons and rank alternatives.

    Examples:
        pmhelper selection ahp -c criteria.json -m matrix.csv -o results.json
        pmhelper selection ahp -c criteria.json -m matrix.csv -a alternatives.csv -o results.json -v
    """
    try:
        if verbose:
            click.echo("Loading criteria...")

        # Load criteria from JSON
        with open(criteria, 'r') as f:
            criteria_data = json.load(f)

        criterion_names = [c['name'] for c in criteria_data]

        # Create AHP analyzer
        ahp = AHPAnalyzer(criterion_names)

        if verbose:
            click.echo(
                f"Loaded {
                    len(criterion_names)} criteria: {
                    ', '.join(criterion_names)}")
            click.echo("Loading comparison matrix...")

        # Load pairwise comparison matrix from CSV
        matrix_df = pd.read_csv(matrix, index_col=0)

        # Set comparisons
        for i, criterion_i in enumerate(criterion_names):
            for j, criterion_j in enumerate(criterion_names):
                if i < j:  # Only upper triangle
                    value = float(matrix_df.iloc[i, j])
                    ahp.set_comparison(criterion_i, criterion_j, value)

        if verbose:
            click.echo("Calculating weights...")

        # Calculate weights
        weights = ahp.calculate_weights()
        cr = ahp.calculate_consistency_ratio()

        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("AHP Analysis Results")
        click.echo("=" * 60)
        click.echo(f"\nConsistency Ratio: {cr:.4f}")

        if cr < 0.1:
            click.secho("✓ Acceptable consistency", fg='green')
        elif cr < 0.15:
            click.secho("⚠ Acceptable with caution", fg='yellow')
        else:
            click.secho("✗ Inconsistent - revise comparisons", fg='red')

        click.echo("\nCriterion Weights:")
        for criterion, weight in zip(criterion_names, weights):
            bar_length = int(weight * 40)
            bar = "█" * bar_length
            click.echo(f"  {criterion:20s} {bar} {weight:.4f}")

        results = {
            'method': 'AHP',
            'consistency_ratio': float(cr),
            'weights': {
                name: float(weight) for name,
                weight in zip(
                    criterion_names,
                    weights)},
            'ranked_alternatives': []}

        # Rank alternatives if provided
        if alternatives:
            if verbose:
                click.echo("\nLoading alternatives...")

            alt_df = pd.read_csv(alternatives)

            # Prepare alternative scores
            alternative_scores = {}
            for _, row in alt_df.iterrows():
                alt_name = row['name']
                scores = {criterion: row[criterion]
                          for criterion in criterion_names}
                alternative_scores[alt_name] = scores

            if verbose:
                click.echo(f"Loaded {len(alternative_scores)} alternatives")
                click.echo("Ranking alternatives...")

            # Rank alternatives
            ranked_df = ahp.rank_alternatives(alternative_scores)

            click.echo("\n" + "-" * 60)
            click.echo("Ranked Alternatives:")
            click.echo("-" * 60)
            click.echo(ranked_df.to_string(index=False))

            # Add to results
            results['ranked_alternatives'] = ranked_df.to_dict('records')

        # Save results
        output_path = Path(output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        click.secho(f"\n✓ Results saved to {output}", fg='green')

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


@selection.command()
@click.option('--data', '-d', type=click.Path(exists=True), required=True,
              help='CSV file with alternatives and criterion values')
@click.option('--weights', '-w', type=click.Path(exists=True), required=True,
              help='JSON file with criterion weights and directions')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file path for results (CSV)')
@click.option('--sensitivity', '-s', is_flag=True,
              help='Perform sensitivity analysis')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
def score(data, weights, output, sensitivity, verbose):
    """
    Perform Linear Scoring analysis.

    Normalize criterion values and calculate weighted scores.

    Examples:
        pmhelper selection score -d alternatives.csv -w weights.json -o ranked.csv
        pmhelper selection score -d alternatives.csv -w weights.json -o ranked.csv -s -v
    """
    try:
        if verbose:
            click.echo("Loading data...")

        # Load data
        data_df = pd.read_csv(data)

        with open(weights, 'r') as f:
            weights_data = json.load(f)

        # Extract criteria and directions
        criteria = list(weights_data['criteria'].keys())
        directions = {
            name: CriterionDirection.MAXIMIZE if info['direction'] == 'maximize'
            else CriterionDirection.MINIMIZE
            for name, info in weights_data['criteria'].items()
        }

        criterion_weights = {
            name: info['weight']
            for name, info in weights_data['criteria'].items()
        }

        if verbose:
            click.echo(
                f"Loaded {
                    len(data_df)} alternatives with {
                    len(criteria)} criteria")

        # Create analyzer
        analyzer = LinearScoringAnalyzer(criteria, directions)

        if verbose:
            click.echo("Calculating scores...")

        # Calculate scores
        results_df = analyzer.calculate_scores(data_df, criterion_weights)

        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("Linear Scoring Results")
        click.echo("=" * 60)
        click.echo("\nRanked Alternatives:")
        click.echo(results_df.to_string(index=False))

        # Save results
        results_df.to_csv(output, index=False)
        click.secho(f"\n✓ Results saved to {output}", fg='green')

        # Sensitivity analysis
        if sensitivity:
            if verbose:
                click.echo("\nPerforming sensitivity analysis...")

            weight_ranges = {
                name: (max(0.0, weight - 0.2), min(1.0, weight + 0.2))
                for name, weight in criterion_weights.items()
            }

            sens_results = analyzer.sensitivity_analysis(
                data_df, criterion_weights, weight_ranges)

            click.echo("\n" + "-" * 60)
            click.echo("Sensitivity Analysis:")
            click.echo("-" * 60)

            for criterion, variations in sens_results['variations'].items():
                rank_changes = sum(1 for v in variations if v['rank_changed'])
                click.echo(f"\n{criterion}:")
                click.echo(
                    f"  Weight variations causing rank changes: {rank_changes}/{len(variations)}")

            # Save sensitivity results
            sens_output = Path(output).stem + '_sensitivity.json'
            with open(sens_output, 'w') as f:
                json.dump(sens_results, f, indent=2, default=str)

            click.secho(
                f"✓ Sensitivity results saved to {sens_output}",
                fg='green')

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


@selection.command()
@click.option('--projects', '-p', type=click.Path(exists=True), required=True,
              help='CSV file with project data (cost, benefits, life, etc.)')
@click.option('--marr', '-m', type=float, required=True,
              help='Minimum Attractive Rate of Return (as decimal, e.g., 0.12)')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file path for results (JSON)')
@click.option('--analysis-type',
              '-t',
              type=click.Choice(['independent',
                                 'mutually_exclusive']),
              default='mutually_exclusive',
              help='Analysis type')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
def bc(projects, marr, output, analysis_type, verbose):
    """
    Perform Benefit-to-Cost (B/C) analysis.

    Calculate B/C ratios and perform incremental analysis for mutually exclusive projects.

    Examples:
        pmhelper selection bc -p projects.csv -m 0.12 -o analysis.json
        pmhelper selection bc -p projects.csv -m 0.12 -t independent -o analysis.json -v
    """
    try:
        if verbose:
            click.echo("Loading project data...")

        # Load projects
        projects_df = pd.read_csv(projects)

        required_cols = ['name', 'initial_cost', 'life', 'annual_benefits']
        if not all(col in projects_df.columns for col in required_cols):
            raise ValueError(
                f"CSV must contain columns: {
                    ', '.join(required_cols)}")

        # Add optional columns if missing
        if 'annual_om' not in projects_df.columns:
            projects_df['annual_om'] = 0.0
        if 'salvage' not in projects_df.columns:
            projects_df['salvage'] = 0.0

        if verbose:
            click.echo(f"Loaded {len(projects_df)} projects")
            click.echo(f"MARR: {marr * 100:.1f}%")
            click.echo(f"Analysis type: {analysis_type}")

        # Create analyzer
        analyzer = BenefitCostAnalyzer()

        if verbose:
            click.echo("\nPerforming B/C analysis...")

        # Perform analysis
        if analysis_type == 'mutually_exclusive':
            results = analyzer.incremental_analysis(projects_df, marr)
        else:
            # For independent projects, just calculate B/C ratios
            projects_df['CR'] = projects_df.apply(
                lambda row: analyzer.calculate_capital_recovery(
                    row['initial_cost'],
                    row.get('salvage', 0.0),
                    marr,
                    row['life']
                ),
                axis=1
            )

            projects_df['BC_Ratio'] = projects_df.apply(
                lambda row: analyzer.calculate_bc_ratio(
                    row['annual_benefits'],
                    row['CR'],
                    row.get('annual_om', 0.0)
                ),
                axis=1
            )

            results = {
                'analysis_type': 'independent',
                'all_projects': projects_df.to_dict('records'),
                'viable_projects': projects_df[projects_df['BC_Ratio'] >= 1.0].to_dict('records')
            }

        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("B/C Analysis Results")
        click.echo("=" * 60)

        if analysis_type == 'mutually_exclusive':
            if results['optimal_project']:
                click.echo("\nOptimal Project:")
                opt = results['optimal_project']
                click.secho(f"  {opt['name']}", fg='green', bold=True)
                click.echo(f"  B/C Ratio: {opt['BC_Ratio']:.3f}")
                click.echo(f"  Initial Cost: ${opt['initial_cost']:,.2f}")
                click.echo(
                    f"  Annual Benefits: ${
                        opt['annual_benefits']:,.2f}")

                if results['comparisons']:
                    click.echo("\nIncremental Analysis:")
                    for comp in results['comparisons']:
                        decision_color = 'green' if comp['incremental_bc'] >= 1.0 else 'red'
                        click.echo(
                            f"  {
                                comp['current']} vs {
                                comp['challenger']}:")
                        click.echo(
                            f"    Incremental B/C: {comp['incremental_bc']:.3f}")
                        click.secho(
                            f"    Decision: {
                                comp['decision']}",
                            fg=decision_color)
            else:
                click.secho(
                    "\n✗ No viable projects found (all B/C ratios < 1.0)",
                    fg='red')
        else:
            viable = results['viable_projects']
            click.echo(
                f"\nViable Projects (B/C ≥ 1.0): {len(viable)}/{len(results['all_projects'])}")

            if viable:
                click.echo("\nProject Rankings:")
                sorted_projects = sorted(
                    viable, key=lambda x: x['BC_Ratio'], reverse=True)
                for i, proj in enumerate(sorted_projects, 1):
                    click.echo(
                        f"  {i}. {proj['name']}: B/C = {proj['BC_Ratio']:.3f}")

        # Save results
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        click.secho(f"\n✓ Results saved to {output}", fg='green')

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


@selection.command()
@click.option('--projects', '-p', type=click.Path(exists=True), required=True,
              help='CSV file with project data (name, cost, benefit)')
@click.option('--budget', '-b', type=float, required=True,
              help='Total budget available')
@click.option('--constraints', '-c', type=click.Path(exists=True),
              help='JSON file with constraints (optional)')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file path for results (JSON)')
@click.option('--time-limit', '-t', type=int, default=60,
              help='Solver time limit in seconds')
@click.option('--sensitivity', '-s', is_flag=True,
              help='Perform budget sensitivity analysis')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
def portfolio(
        projects,
        budget,
        constraints,
        output,
        time_limit,
        sensitivity,
        verbose):
    """
    Optimize project portfolio using Integer Linear Programming.

    Select optimal subset of projects to maximize benefits within budget.

    Examples:
        pmhelper selection portfolio -p projects.csv -b 5000000 -o portfolio.json
        pmhelper selection portfolio -p projects.csv -b 5000000 -c constraints.json -o portfolio.json -v
    """
    try:
        if verbose:
            click.echo("Loading project data...")

        # Load projects
        projects_df = pd.read_csv(projects)

        required_cols = ['name', 'cost', 'benefit']
        if not all(col in projects_df.columns for col in required_cols):
            raise ValueError(
                f"CSV must contain columns: {
                    ', '.join(required_cols)}")

        if verbose:
            click.echo(f"Loaded {len(projects_df)} projects")
            click.echo(f"Budget: ${budget:,.2f}")

        # Load constraints if provided
        constraint_list = None
        if constraints:
            with open(constraints, 'r') as f:
                constraint_list = json.load(f)
            if verbose:
                click.echo(f"Loaded {len(constraint_list)} constraints")

        # Create optimizer
        optimizer = PortfolioOptimizer()

        if verbose:
            click.echo("\nOptimizing portfolio...")

        # Optimize
        results = optimizer.optimize(
            projects_df,
            budget,
            constraint_list,
            time_limit
        )

        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("Portfolio Optimization Results")
        click.echo("=" * 60)

        click.echo(f"\nSolver Status: {results['status']}")

        if results['status'] in ['Optimal', 'Not Solved']:
            selected_projects = results['selected_projects']

            if selected_projects:
                click.secho(
                    f"\nSelected Projects: {
                        len(selected_projects)}",
                    fg='green',
                    bold=True)
                for proj_name in selected_projects:
                    proj_data = projects_df[projects_df['name']
                                            == proj_name].iloc[0]
                    click.echo(f"  • {proj_name}")
                    click.echo(f"    Cost: ${proj_data['cost']:,.2f}")
                    click.echo(f"    Benefit: ${proj_data['benefit']:,.2f}")

                click.echo(f"\nTotal Cost: ${results['total_cost']:,.2f}")
                click.echo(
                    f"Total Annual Benefit: ${
                        results['total_benefit']:,.2f}")
                click.echo(
                    f"Budget Utilization: {
                        results['budget_utilization']:.1f}%")
                click.echo(
                    f"Objective Value: ${
                        results['objective_value']:,.2f}")

                if results.get('shadow_price_budget'):
                    click.echo(
                        f"\nMarginal Value of $1 additional budget: ${
                            results['shadow_price_budget']:.2f}")
            else:
                click.secho(
                    "\n⚠ No projects selected (budget too low?)",
                    fg='yellow')
        else:
            click.secho(
                f"\n✗ Optimization failed: {
                    results.get(
                        'message',
                        'Unknown error')}",
                fg='red')

        # Save results
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        click.secho(f"\n✓ Results saved to {output}", fg='green')

        # Sensitivity analysis
        if sensitivity and results['status'] in ['Optimal', 'Not Solved']:
            if verbose:
                click.echo("\nPerforming budget sensitivity analysis...")

            budget_range = (budget * 0.5, budget * 1.5)
            sens_df = optimizer.sensitivity_budget(
                projects_df,
                budget,
                budget_range,
                steps=10,
                constraints=constraint_list
            )

            click.echo("\n" + "-" * 60)
            click.echo("Budget Sensitivity Analysis:")
            click.echo("-" * 60)
            click.echo(sens_df.to_string(index=False))

            # Save sensitivity results
            sens_output = Path(output).stem + '_sensitivity.csv'
            sens_df.to_csv(sens_output, index=False)
            click.secho(
                f"✓ Sensitivity results saved to {sens_output}",
                fg='green')

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


@selection.command()
@click.option('--file', '-f', type=click.Path(exists=True), required=True,
              help='.pmsel file to load')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
def info(file, verbose):
    """
    Display information about a .pmsel file.

    Examples:
        pmhelper selection info -f problem.pmsel
        pmhelper selection info -f problem.pmsel -v
    """
    try:
        # Validate file
        validation = SelectionFileHandler.validate_file(file)

        click.echo("\n" + "=" * 60)
        click.echo("Selection Problem Information")
        click.echo("=" * 60)

        if validation['valid']:
            click.secho("\n✓ File is valid", fg='green')

            # Load and display info
            problem = SelectionFileHandler.load(file)

            click.echo(f"\nID: {problem.id}")
            click.echo(f"Name: {problem.name}")
            click.echo(f"Method: {problem.method}")
            click.echo(f"Version: {problem.version}")

            if problem.description:
                click.echo(f"\nDescription:\n  {problem.description}")

            if problem.criteria:
                click.echo(f"\nCriteria: {len(problem.criteria)}")
                if verbose:
                    for criterion in problem.criteria:
                        click.echo(
                            f"  • {
                                criterion.name} ({
                                criterion.direction.value})")

            if problem.alternatives:
                click.echo(f"Alternatives: {len(problem.alternatives)}")
                if verbose:
                    for alt in problem.alternatives:
                        click.echo(f"  • {alt.name}")

            if problem.projects:
                click.echo(f"Projects: {len(problem.projects)}")
                if verbose:
                    for proj in problem.projects:
                        click.echo(f"  • {proj.name}: ${proj.cost:,.2f}")

            if problem.budget:
                click.echo(f"\nBudget: ${problem.budget:,.2f}")

            if problem.marr:
                click.echo(f"MARR: {problem.marr * 100:.1f}%")

            if problem.constraints:
                click.echo(f"\nConstraints: {len(problem.constraints)}")
                if verbose:
                    for const in problem.constraints:
                        click.echo(f"  • {const.type}")

            click.echo(f"\nCreated: {problem.created_at}")
            click.echo(f"Updated: {problem.updated_at}")

        else:
            click.secho("\n✗ File is invalid", fg='red')
            click.echo("\nErrors:")
            for error in validation['errors']:
                click.echo(f"  • {error}")

    except Exception as e:
        click.secho(f"\n✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


@selection.command()
@click.option('--input', '-i', type=click.Path(exists=True), required=True,
              help='Input CSV file')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output .pmsel file')
@click.option('--method',
              '-m',
              type=click.Choice(['ahp',
                                 'linear_scoring',
                                 'benefit_cost',
                                 'portfolio']),
              required=True,
              help='Selection method')
@click.option('--name', '-n', type=str, required=True,
              help='Problem name')
@click.option('--description', '-d', type=str,
              help='Problem description')
def convert(input, output, method, name, description):
    """
    Convert CSV data to .pmsel format.

    Examples:
        pmhelper selection convert -i data.csv -o problem.pmsel -m ahp -n "Software Selection"
        pmhelper selection convert -i projects.csv -o portfolio.pmsel -m portfolio -n "R&D Portfolio" -d "2024 R&D projects"
    """
    try:
        click.echo(f"Converting {input} to .pmsel format...")

        # Import from CSV
        problem = SelectionExportHandler.from_csv(input, method)

        # Update metadata
        problem.name = name
        if description:
            problem.description = description

        # Save to .pmsel
        SelectionFileHandler.save(problem, output)

        click.secho("\n✓ Converted successfully!", fg='green')
        click.echo(f"Output: {output}")
        click.echo(f"Method: {method}")
        click.echo(
            f"Items: {len(problem.alternatives or problem.projects or [])}")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


if __name__ == '__main__':
    selection()
