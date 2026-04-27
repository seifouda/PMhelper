"""
Multi-Objective Optimization Visualizations

Implements visualization tools for Pareto frontier analysis, NPV sensitivity,
and trade-off analysis between multiple objectives.

Author: PMHelper Team
Version: 1.1.0
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")


def plot_pareto_frontier_2d(solutions_df: pd.DataFrame,
                            obj1: str,
                            obj2: str,
                            minimize_obj1: bool = True,
                            minimize_obj2: bool = True,
                            title: Optional[str] = None,
                            save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot 2D Pareto frontier between two objectives.

    Args:
        solutions_df: DataFrame with objective values and 'is_pareto' column
        obj1: Name of first objective (x-axis)
        obj2: Name of second objective (y-axis)
        minimize_obj1: Whether obj1 should be minimized
        minimize_obj2: Whether obj2 should be minimized
        title: Custom plot title
        save_path: Path to save figure (optional)

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Separate Pareto and dominated solutions
    pareto = solutions_df[solutions_df['is_pareto']]
    dominated = solutions_df[~solutions_df['is_pareto']]

    # Plot dominated solutions
    if not dominated.empty:
        ax.scatter(dominated[obj1], dominated[obj2],
                   alpha=0.3, s=30, color='lightgray',
                   label='Dominated Solutions', zorder=1)

    # Plot Pareto frontier
    if not pareto.empty:
        # Sort for line connection
        pareto_sorted = pareto.sort_values(obj1)

        ax.scatter(
            pareto_sorted[obj1],
            pareto_sorted[obj2],
            alpha=0.8,
            s=100,
            color='red',
            marker='*',
            label='Pareto Frontier',
            zorder=3,
            edgecolors='darkred',
            linewidths=1.5)

        # Connect Pareto points
        ax.plot(pareto_sorted[obj1], pareto_sorted[obj2],
                'r--', alpha=0.5, linewidth=2, zorder=2)

    # Labels and formatting
    obj1_label = obj1.replace('_', ' ').title()
    obj2_label = obj2.replace('_', ' ').title()

    direction1 = "minimize" if minimize_obj1 else "maximize"
    direction2 = "minimize" if minimize_obj2 else "maximize"

    ax.set_xlabel(f'{obj1_label} ({direction1})', fontsize=12)
    ax.set_ylabel(f'{obj2_label} ({direction2})', fontsize=12)

    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    else:
        ax.set_title(f'Pareto Frontier: {obj1_label} vs {obj2_label}',
                     fontsize=14, fontweight='bold')

    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Add ideal direction arrows
    if minimize_obj1 and minimize_obj2:
        ax.annotate('Ideal Direction',
                    xy=(0.05,
                        0.05),
                    xycoords='axes fraction',
                    fontsize=9,
                    color='green',
                    fontweight='bold',
                    bbox=dict(boxstyle='round',
                              facecolor='lightgreen',
                              alpha=0.3))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved Pareto frontier plot to {save_path}")

    return fig


def plot_pareto_frontier_3d(solutions_df: pd.DataFrame,
                            obj1: str,
                            obj2: str,
                            obj3: str,
                            title: Optional[str] = None,
                            save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot 3D Pareto frontier between three objectives.

    Args:
        solutions_df: DataFrame with objective values and 'is_pareto' column
        obj1, obj2, obj3: Names of objectives
        title: Custom plot title
        save_path: Path to save figure

    Returns:
        matplotlib Figure object
    """
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Separate solutions
    pareto = solutions_df[solutions_df['is_pareto']]
    dominated = solutions_df[~solutions_df['is_pareto']]

    # Plot dominated
    if not dominated.empty:
        ax.scatter(dominated[obj1], dominated[obj2], dominated[obj3],
                   alpha=0.2, s=20, color='lightgray', label='Dominated')

    # Plot Pareto
    if not pareto.empty:
        ax.scatter(
            pareto[obj1],
            pareto[obj2],
            pareto[obj3],
            alpha=0.8,
            s=100,
            color='red',
            marker='*',
            label='Pareto Frontier',
            edgecolors='darkred',
            linewidths=1.5)

    # Labels
    ax.set_xlabel(obj1.replace('_', ' ').title(), fontsize=11)
    ax.set_ylabel(obj2.replace('_', ' ').title(), fontsize=11)
    ax.set_zlabel(obj3.replace('_', ' ').title(), fontsize=11)

    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    else:
        ax.set_title(
            '3D Pareto Frontier',
            fontsize=14,
            fontweight='bold',
            pad=20)

    ax.legend(loc='best')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved 3D Pareto frontier plot to {save_path}")

    return fig


def plot_npv_sensitivity(sensitivity_df: pd.DataFrame,
                         title: Optional[str] = None,
                         save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot NPV sensitivity to discount rate changes.

    Args:
        sensitivity_df: DataFrame with columns: discount_rate, npv_original, npv_optimal, improvement
        title: Custom plot title
        save_path: Path to save figure

    Returns:
        matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Plot 1: NPV vs Discount Rate
    ax1.plot(
        sensitivity_df['discount_rate'],
        sensitivity_df['npv_original'],
        marker='o',
        linewidth=2,
        label='Original Schedule (Early Start)',
        color='blue')
    ax1.plot(
        sensitivity_df['discount_rate'],
        sensitivity_df['npv_optimal'],
        marker='s',
        linewidth=2,
        label='Optimized Schedule',
        color='green')

    ax1.set_xlabel('Discount Rate', fontsize=11)
    ax1.set_ylabel('Net Present Value ($)', fontsize=11)
    ax1.set_title(
        title or 'NPV Sensitivity to Discount Rate',
        fontsize=13,
        fontweight='bold')
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.axhline(0, color='red', linestyle='--', alpha=0.5, linewidth=1)

    # Format x-axis as percentage
    ax1.xaxis.set_major_formatter(
        plt.FuncFormatter(
            lambda x,
            p: f'{
                x * 100:.0f}%'))

    # Plot 2: Improvement vs Discount Rate
    ax2.plot(sensitivity_df['discount_rate'], sensitivity_df['improvement'],
             marker='D', linewidth=2, color='purple', label='NPV Improvement')
    ax2.fill_between(
        sensitivity_df['discount_rate'],
        0,
        sensitivity_df['improvement'],
        alpha=0.3,
        color='purple')

    ax2.set_xlabel('Discount Rate', fontsize=11)
    ax2.set_ylabel('NPV Improvement ($)', fontsize=11)
    ax2.set_title(
        'Optimization Benefit by Discount Rate',
        fontsize=13,
        fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(0, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax2.xaxis.set_major_formatter(
        plt.FuncFormatter(
            lambda x,
            p: f'{
                x * 100:.0f}%'))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved NPV sensitivity plot to {save_path}")

    return fig


def plot_tradeoff_analysis(tradeoffs_df: pd.DataFrame,
                           obj1: str,
                           obj2: str,
                           title: Optional[str] = None,
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot marginal rate of substitution between objectives.

    Args:
        tradeoffs_df: DataFrame from MultiObjectiveOptimizer.find_tradeoffs()
        obj1: First objective name
        obj2: Second objective name
        title: Custom plot title
        save_path: Path to save figure

    Returns:
        matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    obj1_label = obj1.replace('_', ' ').title()
    obj2_label = obj2.replace('_', ' ').title()

    # Plot 1: Objective values along frontier
    x = np.arange(len(tradeoffs_df))
    width = 0.35

    current_col = f'{obj1}_current'
    next_col = f'{obj1}_next'

    if current_col in tradeoffs_df.columns:
        ax1.bar(x - width / 2, tradeoffs_df[current_col], width,
                label=f'{obj1_label} (Current)', alpha=0.8, color='skyblue')
        ax1.bar(x + width / 2, tradeoffs_df[next_col], width,
                label=f'{obj1_label} (Next)', alpha=0.8, color='navy')

    ax1.set_xlabel('Transition', fontsize=11)
    ax1.set_ylabel(obj1_label, fontsize=11)
    ax1.set_title(
        f'{obj1_label} Along Pareto Frontier',
        fontsize=12,
        fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: Marginal rate of substitution
    if 'marginal_rate' in tradeoffs_df.columns:
        mrs_values = tradeoffs_df['marginal_rate'].replace(
            [np.inf, -np.inf], np.nan)
        ax2.plot(
            x,
            mrs_values,
            marker='o',
            linewidth=2,
            color='red',
            markersize=8)
        ax2.fill_between(x, 0, mrs_values, alpha=0.3, color='red')

        ax2.set_xlabel('Transition', fontsize=11)
        ax2.set_ylabel(f'Δ{obj2_label} / Δ{obj1_label}', fontsize=11)
        ax2.set_title(
            'Marginal Rate of Substitution',
            fontsize=12,
            fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(0, color='black', linestyle='-', alpha=0.3, linewidth=1)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved trade-off analysis plot to {save_path}")

    return fig


def plot_objective_comparison(solutions_df: pd.DataFrame,
                              objectives: List[str],
                              normalize: bool = True,
                              title: Optional[str] = None,
                              save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot parallel coordinates or radar chart comparing objectives across solutions.

    Args:
        solutions_df: DataFrame with objective values
        objectives: List of objective names to compare
        normalize: Whether to normalize values to [0, 1]
        title: Custom plot title
        save_path: Path to save figure

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Filter to Pareto solutions if available
    if 'is_pareto' in solutions_df.columns:
        plot_df = solutions_df[solutions_df['is_pareto']].copy()
    else:
        plot_df = solutions_df.copy()

    if plot_df.empty:
        plot_df = solutions_df.copy()

    # Normalize if requested
    if normalize:
        for obj in objectives:
            if obj in plot_df.columns:
                min_val = plot_df[obj].min()
                max_val = plot_df[obj].max()
                if max_val > min_val:
                    plot_df[f'{obj}_norm'] = (
                        plot_df[obj] - min_val) / (max_val - min_val)
                else:
                    plot_df[f'{obj}_norm'] = 0.5

        plot_cols = [f'{obj}_norm' for obj in objectives]
        ylabel = 'Normalized Value (0-1)'
    else:
        plot_cols = objectives
        ylabel = 'Objective Value'

    # Parallel coordinates plot
    x_positions = np.arange(len(objectives))

    for idx, row in plot_df.iterrows():
        values = [row.get(col, 0) for col in plot_cols]
        alpha = 0.7 if row.get('is_pareto', False) else 0.3
        color = 'red' if row.get('is_pareto', False) else 'gray'
        linewidth = 2 if row.get('is_pareto', False) else 1

        ax.plot(x_positions, values, marker='o', alpha=alpha,
                color=color, linewidth=linewidth)

    ax.set_xticks(x_positions)
    ax.set_xticklabels([obj.replace('_', ' ').title() for obj in objectives],
                       rotation=15, ha='right')
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title or 'Multi-Objective Comparison (Parallel Coordinates)',
                 fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D(
            [0],
            [0],
            color='red',
            linewidth=2,
            label='Pareto Solutions'),
        Line2D(
            [0],
            [0],
            color='gray',
            linewidth=1,
            alpha=0.3,
            label='Dominated Solutions')]
    ax.legend(handles=legend_elements, loc='best')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved objective comparison plot to {save_path}")

    return fig


def generate_multi_objective_report(optimizer,
                                    pareto_df: pd.DataFrame,
                                    objectives: List[str],
                                    save_path: Optional[str] = None) -> str:
    """
    Generate comprehensive text report for multi-objective optimization.

    Args:
        optimizer: MultiObjectiveOptimizer instance
        pareto_df: DataFrame of Pareto frontier solutions
        objectives: List of objective names
        save_path: Path to save report

    Returns:
        Report text as string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("MULTI-OBJECTIVE OPTIMIZATION REPORT")
    lines.append("=" * 80)
    lines.append("")

    # Summary statistics
    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Solutions Evaluated: {len(optimizer.solutions)}")
    lines.append(f"Pareto Frontier Size: {len(pareto_df)}")
    lines.append(f"Objectives: {', '.join(objectives)}")
    lines.append("")

    # Pareto solutions details
    lines.append("PARETO FRONTIER SOLUTIONS")
    lines.append("-" * 80)

    for idx, row in pareto_df.iterrows():
        lines.append(f"\nSolution #{idx + 1}:")
        for obj in objectives:
            if obj in row:
                lines.append(
                    f"  {
                        obj.replace(
                            '_',
                            ' ').title()}: {
                        row[obj]:.2f}")

    lines.append("")

    # Objective ranges on frontier
    lines.append("OBJECTIVE RANGES ON PARETO FRONTIER")
    lines.append("-" * 80)

    for obj in objectives:
        if obj in pareto_df.columns:
            min_val = pareto_df[obj].min()
            max_val = pareto_df[obj].max()
            range_val = max_val - min_val
            lines.append(f"{obj.replace('_', ' ').title()}:")
            lines.append(f"  Min: {min_val:.2f}")
            lines.append(f"  Max: {max_val:.2f}")
            lines.append(f"  Range: {range_val:.2f}")
            lines.append("")

    report_text = '\n'.join(lines)

    if save_path:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        logger.info(f"Saved multi-objective report to {save_path}")

    return report_text


def export_pareto_solutions(pareto_df: pd.DataFrame,
                            schedules: List[Dict[str, int]],
                            base_path: str,
                            formats: List[str] = ['csv', 'json', 'excel']):
    """
    Export Pareto frontier solutions in multiple formats.

    Args:
        pareto_df: DataFrame of Pareto solutions
        schedules: List of schedules corresponding to solutions
        base_path: Base file path (without extension)
        formats: List of formats to export ('csv', 'json', 'excel')
    """
    for fmt in formats:
        try:
            if fmt == 'csv':
                pareto_df.to_csv(f"{base_path}.csv", index=False)
                logger.info(f"Exported Pareto solutions to {base_path}.csv")

            elif fmt == 'json':
                export_data = {
                    'pareto_solutions': pareto_df.to_dict('records'),
                    'schedules': schedules
                }
                import json
                with open(f"{base_path}.json", 'w') as f:
                    json.dump(export_data, f, indent=2)
                logger.info(f"Exported Pareto solutions to {base_path}.json")

            elif fmt == 'excel':
                with pd.ExcelWriter(f"{base_path}.xlsx", engine='openpyxl') as writer:
                    pareto_df.to_excel(
                        writer, sheet_name='Pareto Frontier', index=False)
                logger.info(f"Exported Pareto solutions to {base_path}.xlsx")

        except Exception as e:
            logger.error(f"Failed to export in {fmt} format: {e}")
