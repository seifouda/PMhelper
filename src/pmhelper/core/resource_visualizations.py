"""
Resource Leveling Visualizations

Provides plotting and reporting functions for resource leveling analysis.
Shows before/after resource profiles, utilization metrics, and improvements.

Author: PMHelper Team
Version: 1.1.0
"""

import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


def plot_resource_profile(
        original_profile: pd.DataFrame,
        leveled_profile: pd.DataFrame,
        resource_limit: Optional[float] = None,
        method_name: str = "Resource Leveling") -> plt.Figure:
    """
    Plot before/after resource profiles.

    Shows:
    - Original resource usage histogram
    - Leveled resource usage histogram
    - Resource limit line (if specified)
    - Metrics comparison

    Args:
        original_profile: DataFrame from ResourceProfile.to_dataframe() (original)
        leveled_profile: DataFrame from ResourceProfile.to_dataframe() (leveled)
        resource_limit: Optional maximum resource capacity
        method_name: Name of leveling method for title

    Returns:
        matplotlib Figure object

    Example:
        >>> fig = plot_resource_profile(original_df, leveled_df, resource_limit=10)
        >>> fig.savefig('resource_leveling.png')
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Original profile
    ax1.bar(
        original_profile['time'],
        original_profile['resource_usage'],
        color='lightcoral',
        edgecolor='darkred',
        alpha=0.7,
        label='Resource Usage')

    if resource_limit:
        ax1.axhline(resource_limit, color='red', linestyle='--', linewidth=2,
                    label=f'Resource Limit ({resource_limit})')

    # Add peak marker
    peak_idx = original_profile['resource_usage'].idxmax()
    peak_time = original_profile.loc[peak_idx, 'time']
    peak_usage = original_profile.loc[peak_idx, 'resource_usage']
    ax1.scatter([peak_time], [peak_usage], color='darkred', s=200,
                marker='v', zorder=10, label=f'Peak: {peak_usage:.1f}')

    ax1.set_ylabel('Resource Usage', fontsize=12, fontweight='bold')
    ax1.set_title(f'Original Schedule (Before {method_name})',
                  fontsize=13, fontweight='bold', pad=15)
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')

    # Leveled profile
    ax2.bar(
        leveled_profile['time'],
        leveled_profile['resource_usage'],
        color='lightgreen',
        edgecolor='darkgreen',
        alpha=0.7,
        label='Resource Usage')

    if resource_limit:
        ax2.axhline(resource_limit, color='red', linestyle='--', linewidth=2,
                    label=f'Resource Limit ({resource_limit})')

    # Add peak marker
    peak_idx = leveled_profile['resource_usage'].idxmax()
    peak_time = leveled_profile.loc[peak_idx, 'time']
    peak_usage = leveled_profile.loc[peak_idx, 'resource_usage']
    ax2.scatter([peak_time], [peak_usage], color='darkgreen', s=200,
                marker='v', zorder=10, label=f'Peak: {peak_usage:.1f}')

    ax2.set_xlabel('Time (periods)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Resource Usage', fontsize=12, fontweight='bold')
    ax2.set_title(f'Leveled Schedule (After {method_name})',
                  fontsize=13, fontweight='bold', pad=15)
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    logger.info("Generated resource profile comparison plot")
    return fig


def plot_resource_histogram(original_profile: pd.DataFrame,
                            leveled_profile: pd.DataFrame) -> plt.Figure:
    """
    Plot resource usage histogram comparison.

    Args:
        original_profile: DataFrame with original resource usage
        leveled_profile: DataFrame with leveled resource usage

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Combine data for overlapping histograms
    ax.hist(original_profile['resource_usage'], bins=20, alpha=0.6,
            color='coral', label='Original', edgecolor='black')
    ax.hist(leveled_profile['resource_usage'], bins=20, alpha=0.6,
            color='green', label='Leveled', edgecolor='black')

    ax.set_xlabel('Resource Usage', fontsize=12, fontweight='bold')
    ax.set_ylabel(
        'Frequency (# of time periods)',
        fontsize=12,
        fontweight='bold')
    ax.set_title('Resource Usage Distribution', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    logger.info("Generated resource usage histogram")
    return fig


def plot_leveling_metrics(result: dict) -> plt.Figure:
    """
    Plot leveling improvement metrics.

    Args:
        result: Dictionary from leveling algorithm with metrics

    Returns:
        matplotlib Figure object
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    # Metric 1: Moment/Cost comparison
    metric_name = 'Moment' if 'original_moment' in result else 'Cost'
    original_value = result.get(
        'original_moment', result.get(
            'original_cost', 0))
    leveled_value = result.get('leveled_moment', result.get('leveled_cost', 0))

    categories = ['Original', 'Leveled']
    values = [original_value, leveled_value]
    colors = ['coral', 'lightgreen']

    bars = ax1.bar(
        categories,
        values,
        color=colors,
        edgecolor='black',
        linewidth=1.5)
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.,
                 height,
                 f'{val:.1f}',
                 ha='center',
                 va='bottom',
                 fontweight='bold',
                 fontsize=11)

    ax1.set_ylabel(metric_name, fontsize=11, fontweight='bold')
    ax1.set_title(f'{metric_name} Reduction', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')

    # Metric 2: Peak usage comparison
    peak_original = result.get('peak_usage_original', 0)
    peak_leveled = result.get('peak_usage_leveled', 0)

    categories = ['Original', 'Leveled']
    values = [peak_original, peak_leveled]

    bars = ax2.bar(
        categories,
        values,
        color=colors,
        edgecolor='black',
        linewidth=1.5)
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.,
                 height,
                 f'{val:.1f}',
                 ha='center',
                 va='bottom',
                 fontweight='bold',
                 fontsize=11)

    ax2.set_ylabel('Peak Resource Usage', fontsize=11, fontweight='bold')
    ax2.set_title('Peak Usage Reduction', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    # Metric 3: Improvement percentage
    improvement = result.get('improvement_pct', 0)
    iterations = result.get('iterations', 0)

    metrics = {'Improvement\n%': improvement, 'Iterations': iterations}
    colors_metric = ['#2E86AB', '#F77F00']

    bars = ax3.bar(metrics.keys(), metrics.values(), color=colors_metric,
                   edgecolor='black', linewidth=1.5)
    for bar, (key, val) in zip(bars, metrics.items()):
        height = bar.get_height()
        label = f'{val:.1f}%' if 'Improvement' in key else f'{int(val)}'
        ax3.text(
            bar.get_x() +
            bar.get_width() /
            2.,
            height,
            label,
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=11)

    ax3.set_ylabel('Value', fontsize=11, fontweight='bold')
    ax3.set_title('Leveling Performance', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

    # Metric 4: Feasibility status
    feasible = result.get('feasible', True)
    status_text = "✓ FEASIBLE" if feasible else "✗ INFEASIBLE"
    status_color = 'green' if feasible else 'red'

    ax4.text(0.5, 0.6, status_text, ha='center', va='center',
             fontsize=24, fontweight='bold', color=status_color)

    if feasible:
        ax4.text(0.5, 0.35, "Schedule meets resource constraints",
                 ha='center', va='center', fontsize=12, style='italic')
    else:
        ax4.text(
            0.5,
            0.35,
            "Resource limit exceeded",
            ha='center',
            va='center',
            fontsize=12,
            style='italic',
            color='red')

    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    ax4.set_title('Feasibility Check', fontsize=12, fontweight='bold')

    plt.tight_layout()
    logger.info("Generated leveling metrics plot")
    return fig


def generate_leveling_report(result: dict,
                             method_name: str = "Resource Leveling") -> str:
    """
    Generate text report of resource leveling results.

    Args:
        result: Dictionary from leveling algorithm
        method_name: Name of the leveling method used

    Returns:
        Formatted text report

    Example:
        >>> report = generate_leveling_report(result, "Minimum Moment")
        >>> print(report)
    """
    metric_name = 'Moment' if 'original_moment' in result else 'Cost'
    original_value = result.get(
        'original_moment', result.get(
            'original_cost', 0))
    leveled_value = result.get('leveled_moment', result.get('leveled_cost', 0))

    # Get schedule changes
    original_schedule = result.get('original_schedule', {})
    leveled_schedule = result.get('leveled_schedule', {})

    moved_activities = []
    for act_id in sorted(leveled_schedule.keys()):
        if leveled_schedule[act_id] != original_schedule.get(act_id, -1):
            moved_activities.append({
                'id': act_id,
                'original': original_schedule.get(act_id, 0),
                'leveled': leveled_schedule[act_id],
                'shift': leveled_schedule[act_id] - original_schedule.get(act_id, 0)
            })

    report = f"""
{'=' * 70}
            RESOURCE LEVELING REPORT - {method_name.upper()}
{'=' * 70}

SUMMARY
-------
Method: {method_name}
Iterations: {result.get('iterations', 0)}
Feasibility: {'FEASIBLE' if result.get('feasible', True) else 'INFEASIBLE'}

ORIGINAL SCHEDULE (Early Start)
--------------------------------
  Peak Resource Usage: {result.get('peak_usage_original', 0):.2f}
  {metric_name}: {original_value:.2f}

LEVELED SCHEDULE (Optimized)
-----------------------------
  Peak Resource Usage: {result.get('peak_usage_leveled', 0):.2f}
  {metric_name}: {leveled_value:.2f}

IMPROVEMENT
-----------
  {metric_name} Reduction: {original_value - leveled_value:.2f}
  Percentage Improvement: {result.get('improvement_pct', 0):.1f}%
  Peak Reduction: {result.get('peak_usage_original', 0) - result.get('peak_usage_leveled', 0):.2f}

ACTIVITY SCHEDULE CHANGES
--------------------------
"""

    if moved_activities:
        report += "  Activity | Original Start | Leveled Start | Shift\n"
        report += "  " + "-" * 54 + "\n"
        for act in moved_activities:
            report += f"  {
                act['id']:8} | {
                act['original']:14} | {
                act['leveled']:13} | {
                act['shift']:+5}\n"
        report += f"\n  Total activities moved: {len(moved_activities)}\n"
    else:
        report += "  No activities moved (already optimal)\n"

    report += f"\n{'=' * 70}\n"

    logger.info("Generated resource leveling report")
    return report


def plot_gantt_comparison(original_schedule: Dict[str, int],
                          leveled_schedule: Dict[str, int],
                          activities: List,
                          resource_limit: Optional[float] = None) -> plt.Figure:
    """
    Plot Gantt chart comparison of original vs leveled schedules.

    Args:
        original_schedule: Dict mapping activity ID to start time (original)
        leveled_schedule: Dict mapping activity ID to start time (leveled)
        activities: List of Activity objects
        resource_limit: Optional resource limit for annotation

    Returns:
        matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    activities_dict = {act.id: act for act in activities}
    activity_ids = sorted(original_schedule.keys())

    # Original Gantt
    for i, act_id in enumerate(activity_ids):
        if act_id not in activities_dict:
            continue

        activity = activities_dict[act_id]
        start = original_schedule[act_id]
        duration = activity.duration

        color = 'coral' if activity.float == 0 else 'lightblue'
        ax1.barh(i, duration, left=start, height=0.6,
                 color=color, edgecolor='black', alpha=0.8)
        ax1.text(start + duration / 2, i, act_id,
                 ha='center', va='center', fontweight='bold', fontsize=9)

    ax1.set_yticks(range(len(activity_ids)))
    ax1.set_yticklabels(activity_ids)
    ax1.set_ylabel('Activities', fontsize=11, fontweight='bold')
    ax1.set_title(
        'Original Schedule (Early Start)',
        fontsize=12,
        fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')

    # Leveled Gantt
    for i, act_id in enumerate(activity_ids):
        if act_id not in activities_dict:
            continue

        activity = activities_dict[act_id]
        start = leveled_schedule[act_id]
        duration = activity.duration

        color = 'darkgreen' if activity.float == 0 else 'lightgreen'
        ax2.barh(i, duration, left=start, height=0.6,
                 color=color, edgecolor='black', alpha=0.8)
        ax2.text(start + duration / 2, i, act_id,
                 ha='center', va='center', fontweight='bold', fontsize=9)

    ax2.set_yticks(range(len(activity_ids)))
    ax2.set_yticklabels(activity_ids)
    ax2.set_xlabel('Time', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Activities', fontsize=11, fontweight='bold')
    ax2.set_title('Leveled Schedule', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(
            facecolor='coral',
            edgecolor='black',
            label='Critical (Original)',
            alpha=0.8),
        Patch(
            facecolor='lightblue',
            edgecolor='black',
            label='Non-Critical (Original)',
            alpha=0.8),
        Patch(
            facecolor='darkgreen',
            edgecolor='black',
            label='Critical (Leveled)',
            alpha=0.8),
        Patch(
            facecolor='lightgreen',
            edgecolor='black',
            label='Non-Critical (Leveled)',
            alpha=0.8)]
    fig.legend(
        handles=legend_elements,
        loc='upper right',
        bbox_to_anchor=(
            0.98,
            0.98))

    plt.tight_layout()
    logger.info("Generated Gantt chart comparison")
    return fig


def export_leveling_results(
        result: dict,
        filepath: str,
        format: str = 'csv') -> None:
    """
    Export resource leveling results to file.

    Args:
        result: Dictionary from leveling algorithm
        filepath: Output file path
        format: Export format ('csv', 'excel', or 'json')

    Example:
        >>> export_leveling_results(result, 'leveling_results.csv', 'csv')
    """
    if format == 'csv':
        # Export schedule comparison
        data = []
        original_schedule = result.get('original_schedule', {})
        leveled_schedule = result.get('leveled_schedule', {})

        for act_id in sorted(leveled_schedule.keys()):
            data.append({
                'activity_id': act_id,
                'original_start': original_schedule.get(act_id, 0),
                'leveled_start': leveled_schedule[act_id],
                'shift': leveled_schedule[act_id] - original_schedule.get(act_id, 0)
            })

        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        logger.info(f"Exported leveling results to {filepath}")

    elif format == 'json':
        import json
        # Prepare data for JSON export
        export_data = {
            'leveled_schedule': result.get('leveled_schedule', {}),
            'original_schedule': result.get('original_schedule', {}),
            'metrics': {
                'improvement_pct': result.get('improvement_pct', 0),
                'iterations': result.get('iterations', 0),
                'peak_usage_original': result.get('peak_usage_original', 0),
                'peak_usage_leveled': result.get('peak_usage_leveled', 0),
                'feasible': result.get('feasible', True)
            }
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        logger.info(f"Exported leveling results to {filepath}")

    else:
        raise ValueError(f"Unsupported format: {format}. Use 'csv' or 'json'")
