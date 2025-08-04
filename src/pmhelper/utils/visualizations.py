#!/usr/bin/env python3
"""
Visualization Module

Provides utilities for creating charts, diagrams, and visualizations for project analysis.
Includes network diagrams, Gantt charts, and other project management visualizations.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
import textwrap
from typing import Dict, List, Any, Optional, Tuple


class NetworkDiagramVisualizer:
    """Creates network diagrams for project networks"""
    
    @staticmethod
    def create_network_diagram(G, critical_activities=None, figsize=(12, 8)):
        """
        Create a network diagram visualization
        
        Args:
            G: NetworkX graph
            critical_activities: List of critical activity IDs
            figsize: Figure size tuple
            
        Returns:
            matplotlib.figure.Figure: The network diagram figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if critical_activities is None:
            critical_activities = []
        
        # Create layout
        pos = NetworkDiagramVisualizer._create_layout(G)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, 
                              arrowsize=20, arrowstyle='->', ax=ax)
        
        # Draw nodes
        node_colors = ['red' if node in critical_activities else 'lightblue' 
                      for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=2000, ax=ax)
        
        # Add node labels
        labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold', ax=ax)
        
        # Add timing information
        NetworkDiagramVisualizer._add_timing_labels(G, pos, ax)
        
        # Add legend
        NetworkDiagramVisualizer._add_legend(ax)
        
        ax.set_title("Project Network Diagram", fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def _create_layout(G):
        """Create a hierarchical layout for the network"""
        try:
            # Try to use hierarchical layout
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            # Fallback to spring layout
            pos = nx.spring_layout(G, k=3, iterations=50)
        
        return pos
    
    @staticmethod
    def _add_timing_labels(G, pos, ax):
        """Add timing information near nodes"""
        for node, (x, y) in pos.items():
            if node not in ['START', 'END']:
                # Add timing information below the node
                es = G.nodes[node].get('ES', 0)
                ef = G.nodes[node].get('EF', 0)
                ls = G.nodes[node].get('LS', 0)
                lf = G.nodes[node].get('LF', 0)
                duration = G.nodes[node].get('duration', 0)
                
                timing_text = f"ES:{es} EF:{ef}\\nLS:{ls} LF:{lf}\\nDur:{duration}"
                ax.text(x, y-0.15, timing_text, fontsize=8, ha='center', va='top',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))
    
    @staticmethod
    def _add_legend(ax):
        """Add legend to the diagram"""
        red_patch = mpatches.Patch(color='red', label='Critical Activity')
        blue_patch = mpatches.Patch(color='lightblue', label='Non-Critical Activity')
        ax.legend(handles=[red_patch, blue_patch], loc='upper right')


class GanttChartVisualizer:
    """Creates Gantt charts for project schedules"""
    
    @staticmethod
    def create_gantt_chart(G, critical_activities=None, figsize=(18, 12)):
        """
        Create a Gantt chart visualization
        
        Args:
            G: NetworkX graph with timing information
            critical_activities: List of critical activity IDs
            figsize: Figure size tuple
            
        Returns:
            matplotlib.figure.Figure: The Gantt chart figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if critical_activities is None:
            critical_activities = []
        
        # Prepare data
        activities_data = []
        for node in G.nodes():
            if node not in ['START', 'END']:
                activities_data.append({
                    'id': node,
                    'activity': G.nodes[node].get('activity', node),
                    'es': G.nodes[node].get('ES', 0),
                    'ef': G.nodes[node].get('EF', 0),
                    'ls': G.nodes[node].get('LS', 0),
                    'lf': G.nodes[node].get('LF', 0),
                    'duration': G.nodes[node].get('duration', 0),
                    'float': G.nodes[node].get('float', 0),
                    'critical': node in critical_activities
                })
        
        # Sort by early start time
        activities_data.sort(key=lambda x: x['es'])
        
        # Create Gantt chart
        y_pos = range(len(activities_data))
        
        for i, activity in enumerate(activities_data):
            # Early schedule bar
            color = 'red' if activity['critical'] else 'lightblue'
            ax.barh(i, activity['duration'], left=activity['es'], 
                   height=0.6, color=color, alpha=0.8, label='Early Schedule' if i == 0 else "")
            
            # Float (if any)
            if activity['float'] > 0:
                ax.barh(i, activity['float'], left=activity['ef'], 
                       height=0.3, color='yellow', alpha=0.6, label='Float' if i == 0 else "")
        
        # Customize chart
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{act['id']}: {act['activity']}" for act in activities_data])
        ax.invert_yaxis()
        ax.set_xlabel('Time')
        ax.set_title('Project Gantt Chart', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        return fig


class ScheduleTableVisualizer:
    """Creates visualizations for schedule tables"""
    
    @staticmethod
    def create_schedule_table_plot(cmp_table, rcps_table, time_cols, critical_ids, 
                                 actual_starts, figsize=(20, 12)):
        """
        Create a visualization of CPM and RCPS schedule tables
        
        Args:
            cmp_table: CPM schedule table DataFrame
            rcps_table: RCPS schedule table DataFrame
            time_cols: List of time column numbers
            critical_ids: Set of critical activity IDs
            actual_starts: Dictionary of actual start times
            figsize: Figure size tuple
            
        Returns:
            matplotlib.figure.Figure: The schedule table visualization
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
        
        # CPM Table
        ScheduleTableVisualizer._plot_single_table(
            ax1, cmp_table, time_cols, critical_ids, "CPM Schedule Table"
        )
        
        # RCPS Table
        ScheduleTableVisualizer._plot_single_table(
            ax2, rcps_table, time_cols, critical_ids, "RCPS Schedule Table", actual_starts
        )
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def _plot_single_table(ax, table, time_cols, critical_ids, title, actual_starts=None):
        """Plot a single schedule table"""
        # Create a color-coded table visualization
        table_data = table.copy()
        
        # Create color matrix
        colors = []
        for _, row in table_data.iterrows():
            row_colors = []
            for col in table_data.columns:
                if col in time_cols:
                    if isinstance(row[col], (int, float)) and row[col] > 0:
                        # Activity is scheduled
                        if row['id'] in critical_ids:
                            row_colors.append('red')  # Critical activity
                        else:
                            row_colors.append('lightblue')  # Non-critical activity
                    else:
                        row_colors.append('white')  # No activity
                else:
                    row_colors.append('lightgray')  # Header columns
            colors.append(row_colors)
        
        # Create table plot
        table_plot = ax.table(cellText=table_data.values,
                             colLabels=table_data.columns,
                             cellLoc='center',
                             loc='center',
                             cellColours=colors)
        
        table_plot.auto_set_font_size(False)
        table_plot.set_fontsize(8)
        table_plot.scale(1, 2)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.axis('off')


class PERTVisualizationHelper:
    """Helper class for PERT-specific visualizations"""
    
    @staticmethod
    def create_probability_chart(analyzer, target_durations=None, figsize=(10, 6)):
        """
        Create a probability distribution chart for PERT analysis
        
        Args:
            analyzer: PERTAnalyzer instance
            target_durations: List of target durations to highlight
            figsize: Figure size tuple
            
        Returns:
            matplotlib.figure.Figure: The probability chart
        """
        if not analyzer.G:
            raise ValueError("No analysis data available")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get project statistics
        stats = analyzer.get_project_statistics()
        if not stats:
            return fig
        
        expected_duration = stats['expected_duration']
        std_dev = stats['std_deviation']
        
        if std_dev == 0:
            ax.text(0.5, 0.5, 'No variance in project (deterministic)', 
                   ha='center', va='center', transform=ax.transAxes)
            return fig
        
        # Create duration range
        duration_range = np.linspace(expected_duration - 4*std_dev, 
                                   expected_duration + 4*std_dev, 1000)
        
        # Calculate probability density
        from scipy.stats import norm
        probabilities = norm.pdf(duration_range, expected_duration, std_dev)
        
        # Plot distribution
        ax.plot(duration_range, probabilities, 'b-', linewidth=2, label='Probability Distribution')
        ax.fill_between(duration_range, probabilities, alpha=0.3)
        
        # Mark expected duration
        ax.axvline(expected_duration, color='red', linestyle='--', 
                  label=f'Expected Duration: {expected_duration:.2f}')
        
        # Mark target durations if provided
        if target_durations:
            for target in target_durations:
                probability = analyzer.calculate_completion_probability(target)
                ax.axvline(target, color='green', linestyle=':',
                          label=f'Target {target}: {probability:.1%} probability')
        
        ax.set_xlabel('Project Duration')
        ax.set_ylabel('Probability Density')
        ax.set_title('PERT Project Duration Probability Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig


def create_comparison_chart(cmp_results, pert_results, figsize=(12, 8)):
    """
    Create a comparison chart between CPM and PERT results
    
    Args:
        cmp_results: CPM analysis results
        pert_results: PERT analysis results
        figsize: Figure size tuple
        
    Returns:
        matplotlib.figure.Figure: The comparison chart
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Duration comparison
    cmp_duration = max([cmp_results.nodes[node]['EF'] for node in cmp_results.nodes()])
    pert_duration = max([pert_results.nodes[node]['EF'] for node in pert_results.nodes()])
    
    ax1.bar(['CPM', 'PERT'], [cmp_duration, pert_duration], 
           color=['lightblue', 'lightcoral'])
    ax1.set_ylabel('Project Duration')
    ax1.set_title('Duration Comparison')
    
    # Critical path comparison
    cmp_critical = len([n for n in cmp_results.nodes() 
                       if cmp_results.nodes[n].get('float', 1) == 0])
    pert_critical = len([n for n in pert_results.nodes() 
                        if pert_results.nodes[n].get('float', 1) == 0])
    
    ax2.bar(['CPM', 'PERT'], [cmp_critical, pert_critical], 
           color=['lightblue', 'lightcoral'])
    ax2.set_ylabel('Number of Critical Activities')
    ax2.set_title('Critical Activities Comparison')
    
    plt.tight_layout()
    return fig
