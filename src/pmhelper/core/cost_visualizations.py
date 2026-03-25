"""
Cost Optimization Visualizations

Provides plotting and reporting functions for time-cost optimization,
resource leveling, and multi-objective analysis.

Author: PMHelper Team
Version: 1.1.0
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


def plot_time_cost_curve(curve_data: pd.DataFrame, optimal_point: dict) -> plt.Figure:
    """
    Generate time-cost optimization curve plot.

    Shows:
    - Direct cost line (increasing as project crashes)
    - Indirect cost line (decreasing with shorter duration)
    - Total cost line (U-shaped)
    - Marker at optimal point

    Args:
        curve_data: DataFrame with duration, direct_cost, indirect_cost, total_cost columns
        optimal_point: Dictionary with optimal duration and costs from find_optimal_duration()

    Returns:
        matplotlib Figure object

    Example:
        >>> fig = plot_time_cost_curve(curve_df, optimal_result)
        >>> fig.savefig('time_cost_curve.png')
        >>> plt.show()
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot cost lines
    ax.plot(curve_data['duration'], curve_data['direct_cost'],
            label='Direct Cost', marker='o', color='#2E86AB', linewidth=2, markersize=6)
    ax.plot(curve_data['duration'], curve_data['indirect_cost'],
            label='Indirect Cost', marker='s', color='#06A77D', linewidth=2, markersize=6)
    ax.plot(curve_data['duration'], curve_data['total_cost'],
            label='Total Cost', marker='^', color='#D62828', linewidth=3, markersize=7)

    # Mark optimal point
    ax.scatter([optimal_point['optimal_duration']],
               [optimal_point['optimal_total_cost']],
               color='gold', s=300, marker='*', edgecolors='black', linewidths=2,
               label='Optimal Point', zorder=10)

    # Add annotation for optimal point
    ax.annotate(
        f"Optimal: {optimal_point['optimal_duration']} days\n${optimal_point['optimal_total_cost']:,.0f}",
        xy=(optimal_point['optimal_duration'], optimal_point['optimal_total_cost']),
        xytext=(20, 20), textcoords='offset points',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', color='black', lw=2),
        fontsize=10, fontweight='bold'
    )

    # Formatting
    ax.set_xlabel('Project Duration (days)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cost ($)', fontsize=12, fontweight='bold')
    ax.set_title('Time-Cost Trade-off Curve', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='best', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    plt.tight_layout()
    logger.info("Generated time-cost curve plot")
    return fig


def generate_cost_report(cpm_result, optimization_result: dict) -> str:
    """
    Generate text report of cost optimization.

    Args:
        cpm_result: CPMAnalyzer instance with analysis results
        optimization_result: Dictionary from find_optimal_duration()

    Returns:
        Formatted text report

    Example:
        >>> report = generate_cost_report(cpm, optimal_result)
        >>> print(report)
    """
    # Format activities crashed list - use .get() for safety
    activities_crashed = optimization_result.get('activities_crashed', [])
    activities_crashed_str = '\n'.join(
        f"  - {act}" for act in activities_crashed
    ) if activities_crashed else "  None"

    # Extract values with safe defaults
    normal_duration = optimization_result.get('normal_duration', 0)
    normal_direct = optimization_result.get('normal_direct', 0)
    normal_indirect = optimization_result.get('normal_indirect', 0)
    normal_total = optimization_result.get('normal_total', 0)
    
    optimal_duration = optimization_result.get('optimal_duration', 0)
    direct_cost = optimization_result.get('direct_cost', 0)
    indirect_cost = optimization_result.get('indirect_cost', 0)
    optimal_total_cost = optimization_result.get('optimal_total_cost', 0)
    
    savings_vs_normal = optimization_result.get('savings_vs_normal', 0)
    savings_pct = optimization_result.get('savings_pct', 0)
    time_reduction = normal_duration - optimal_duration

    report = f"""
{'='*70}
                    COST OPTIMIZATION REPORT
{'='*70}

PROJECT OVERVIEW
----------------
Project Name: {getattr(cpm_result, 'project_name', 'Unnamed Project')}
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

NORMAL SCHEDULE (No Crashing)
------------------------------
  Duration:      {normal_duration} days
  Direct Cost:   ${normal_direct:,.2f}
  Indirect Cost: ${normal_indirect:,.2f}
  Total Cost:    ${normal_total:,.2f}

OPTIMIZED SCHEDULE (Cost Minimized)
------------------------------------
  Duration:      {optimal_duration} days
  Direct Cost:   ${direct_cost:,.2f}
  Indirect Cost: ${indirect_cost:,.2f}
  Total Cost:    ${optimal_total_cost:,.2f}

SAVINGS ANALYSIS
----------------
  Absolute Savings: ${savings_vs_normal:,.2f}
  Percentage Save:  {savings_pct:.1f}%
  Time Reduction:   {time_reduction} days

ACTIVITIES CRASHED
------------------
{activities_crashed_str}

RECOMMENDATION
--------------
"""
    
    if savings_vs_normal > 0:
        report += f"✓ RECOMMENDED: Crash project to {optimal_duration} days\n"
        report += f"  Expected cost savings: ${savings_vs_normal:,.2f}\n"
    else:
        report += "✓ RECOMMENDED: Maintain normal schedule (no cost benefit from crashing)\n"
    
    report += f"\n{'='*70}\n"
    
    logger.info("Generated cost optimization report")
    return report


def plot_cost_breakdown(optimization_result: dict) -> plt.Figure:
    """
    Plot cost breakdown comparison between normal and optimized schedules.

    Args:
        optimization_result: Dictionary from find_optimal_duration()

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Data
    schedules = ['Normal\nSchedule', 'Optimized\nSchedule']
    direct_costs = [
        optimization_result['normal_direct'],
        optimization_result['direct_cost']
    ]
    indirect_costs = [
        optimization_result['normal_indirect'],
        optimization_result['indirect_cost']
    ]

    # Positions
    x = np.arange(len(schedules))
    width = 0.35

    # Stacked bars
    bars1 = ax.bar(x, direct_costs, width, label='Direct Cost', color='#2E86AB')
    bars2 = ax.bar(x, indirect_costs, width, bottom=direct_costs,
                   label='Indirect Cost', color='#06A77D')

    # Add total cost labels on top
    totals = [
        optimization_result['normal_total'],
        optimization_result['optimal_total_cost']
    ]
    for i, (bar1, bar2, total) in enumerate(zip(bars1, bars2, totals)):
        height = bar1.get_height() + bar2.get_height()
        ax.text(bar1.get_x() + bar1.get_width() / 2., height,
                f'${total:,.0f}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)

    # Formatting
    ax.set_ylabel('Cost ($)', fontsize=12, fontweight='bold')
    ax.set_title('Cost Breakdown: Normal vs Optimized', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(schedules, fontsize=11)
    ax.legend(fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')

    plt.tight_layout()
    logger.info("Generated cost breakdown plot")
    return fig


def plot_savings_analysis(curve_data: pd.DataFrame, optimal_point: dict) -> plt.Figure:
    """
    Plot savings analysis showing cost reduction potential.

    Args:
        curve_data: DataFrame with time-cost curve data
        optimal_point: Dictionary with optimal duration and costs

    Returns:
        matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left plot: Total cost curve with savings area
    normal_cost = curve_data.iloc[0]['total_cost']
    optimal_cost = optimal_point['optimal_total_cost']
    
    ax1.plot(curve_data['duration'], curve_data['total_cost'],
             color='#D62828', linewidth=3, marker='o')
    ax1.axhline(normal_cost, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='Normal Cost')
    ax1.axhline(optimal_cost, color='green', linestyle='--', linewidth=1, alpha=0.7, label='Optimal Cost')
    
    # Fill savings area
    ax1.fill_between([optimal_point['optimal_duration']], [optimal_cost], [normal_cost],
                     color='green', alpha=0.3, label='Savings')
    
    ax1.scatter([optimal_point['optimal_duration']], [optimal_cost],
                color='gold', s=200, marker='*', edgecolors='black', linewidths=2, zorder=10)
    
    ax1.set_xlabel('Project Duration (days)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Total Cost ($)', fontsize=11, fontweight='bold')
    ax1.set_title('Total Cost Curve', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    # Right plot: Savings metrics
    metrics = {
        'Time\nSaved': optimal_point['normal_duration'] - optimal_point['optimal_duration'],
        'Cost\nSavings': optimal_point['savings_vs_normal'],
        'Savings\n%': optimal_point['savings_pct']
    }
    
    colors = ['#2E86AB', '#06A77D', '#F77F00']
    bars = ax2.bar(metrics.keys(), metrics.values(), color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bar, (key, value) in zip(bars, metrics.items()):
        height = bar.get_height()
        if 'Savings\n%' in key:
            label = f'{value:.1f}%'
        elif 'Time' in key:
            label = f'{value:.0f} days'
        else:
            label = f'${value:,.0f}'
        
        ax2.text(bar.get_x() + bar.get_width() / 2., height,
                label, ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    ax2.set_ylabel('Value', fontsize=11, fontweight='bold')
    ax2.set_title('Optimization Benefits', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    logger.info("Generated savings analysis plot")
    return fig


def export_optimization_results(curve_data: pd.DataFrame, optimal_point: dict, 
                                filepath: str, format: str = 'csv') -> None:
    """
    Export optimization results to file.

    Args:
        curve_data: DataFrame with time-cost curve data
        optimal_point: Dictionary with optimal results
        filepath: Output file path
        format: Export format ('csv', 'excel', or 'json')

    Example:
        >>> export_optimization_results(curve_df, optimal, 'results.csv', 'csv')
    """
    if format == 'csv':
        curve_data.to_csv(filepath, index=False)
        logger.info(f"Exported optimization results to {filepath}")
    elif format == 'excel':
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            curve_data.to_excel(writer, sheet_name='Time-Cost Curve', index=False)
            
            # Add summary sheet
            summary_data = pd.DataFrame([optimal_point])
            summary_data.to_excel(writer, sheet_name='Optimization Summary', index=False)
        logger.info(f"Exported optimization results to {filepath}")
    elif format == 'json':
        export_data = {
            'curve_data': curve_data.to_dict(orient='records'),
            'optimal_point': optimal_point
        }
        import json
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        logger.info(f"Exported optimization results to {filepath}")
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'csv', 'excel', or 'json'")
