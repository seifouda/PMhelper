"""
Crashing Visualization Module

This module contains all CPM crashing step visualization logic for use in the Crashing tab.

IMPORTANT:
    The initial network for crashing visualization should be built using the SAME network-building logic
    as the Network Diagram tab (e.g., via a shared build_network function/class).
    This ensures consistency in network structure, durations, and CPM attributes.

    Example (do this in your GUI/controller code, not here):
        # from pmhelper.core.network_builder import build_network
        # activities = ... # your activity data
        # G = build_network(activities)
        # draw_network_diagram_on_ax(ax, G, initial=True)

Visualization logic uses CPM values (float, critical path) as calculated by the network-building logic
for consistency. Initial state visualization must use the original, unmodified network before any crashing
steps are executed and logged.

Functions:
    - draw_network_diagram_on_ax: Draws a detailed CPM network diagram on a matplotlib axis.
    - draw_network_diagram_on_ax_small: Draws a compact CPM network diagram on a matplotlib axis.
"""

# Visualization dependencies
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Any
import copy

def draw_network_diagram_on_ax(ax, G: nx.DiGraph, initial=False):
    """
    Draws a CPM network diagram on the given matplotlib axis.

    Args:
        ax: Matplotlib axis to draw on.
        G: NetworkX DiGraph representing the CPM network.
        initial: If True, uses a deep copy of the original network (for initial state visualization).

    Node coloring:
        - Green: START node
        - Orange: END node
        - Red: Critical activities (float == 0, not START/END)
        - Blue: Non-critical activities

    Node labels:
        - START/END: Displayed as 'Start'/'End'
        - Other nodes: Activity name and duration

    Edges:
        - Drawn as arrows between nodes.
    """
    # Use a deep copy for initial visualization to avoid accidental modification
    if initial:
        G = copy.deepcopy(G)

    # Calculate node positions by generation (topological order)
    pos = {}
    generations = list(nx.topological_generations(G))
    for i, gen in enumerate(generations):
        sorted_gen = sorted(gen)
        for j, node in enumerate(sorted_gen):
            y_pos = (j - len(sorted_gen) / 2 + 0.5) * 4
            pos[node] = (i * 3, y_pos)

    node_radius = 0.4

    # Draw edges as arrows
    for u, v in G.edges():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        dx = x2 - x1
        dy = y2 - y1
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx_norm = dx / distance
            dy_norm = dy / distance
            start_x = x1 + node_radius * dx_norm
            start_y = y1 + node_radius * dy_norm
            end_x = x2 - node_radius * dx_norm
            end_y = y2 - node_radius * dy_norm
            ax.annotate(
                "",
                xy=(end_x, end_y),
                xytext=(start_x, start_y),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5)
            )

    # Identify critical activities (float == 0 and not START/END)
    critical_activities = [
        node for node in G.nodes()
        if G.nodes[node].get('float', None) == 0 and node not in ['START', 'END']
    ]

    # Draw nodes with appropriate coloring and labels
    for node in G.nodes():
        x, y = pos[node]
        # Determine node color
        if node == 'START':
            color = 'lightgreen'
        elif node == 'END':
            color = 'orange'
        elif node in critical_activities:
            color = 'red'
        else:
            color = 'lightblue'

        # Draw node circle
        circle = plt.Circle(
            (x, y), node_radius, fill=True, color=color, alpha=0.7,
            edgecolor='black', linewidth=1.5
        )
        ax.add_patch(circle)

        # Draw node label
        if node in ['START', 'END']:
            display_text = 'Start' if node == 'START' else 'End'
            ax.text(
                x, y, display_text, ha='center', va='center',
                fontsize=10, fontweight='bold'
            )
        else:
            # Draw horizontal line inside node
            ax.plot(
                [x - node_radius, x + node_radius], [y, y],
                color='black', linewidth=1.2
            )
            # Activity name above center
            ax.text(
                x, y + node_radius / 2, node, ha='center', va='center',
                fontsize=10, fontweight='bold'
            )
            # Duration below center
            ax.text(
                x, y - node_radius / 2, str(G.nodes[node].get('duration', '')),
                ha='center', va='center', fontsize=9
            )

    ax.set_axis_off()
    ax.set_aspect('equal')

def draw_network_diagram_on_ax_small(ax, G: nx.DiGraph):
    """
    Draws a compact CPM network diagram on the given matplotlib axis.

    Args:
        ax: Matplotlib axis to draw on.
        G: NetworkX DiGraph representing the CPM network.

    Node coloring and labeling is the same as draw_network_diagram_on_ax,
    but with smaller node sizes and fonts for compact display.
    """
    # Calculate node positions by generation (topological order)
    pos = {}
    generations = list(nx.topological_generations(G))
    for i, gen in enumerate(generations):
        sorted_gen = sorted(gen)
        for j, node in enumerate(sorted_gen):
            y_pos = (j - len(sorted_gen) / 2 + 0.5) * 2
            pos[node] = (i * 2, y_pos)

    node_radius = 0.3

    # Draw edges as arrows
    for u, v in G.edges():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        dx = x2 - x1
        dy = y2 - y1
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx_norm = dx / distance
            dy_norm = dy / distance
            start_x = x1 + node_radius * dx_norm
            start_y = y1 + node_radius * dy_norm
            end_x = x2 - node_radius * dx_norm
            end_y = y2 - node_radius * dy_norm
            ax.annotate(
                "",
                xy=(end_x, end_y),
                xytext=(start_x, start_y),
                arrowprops=dict(arrowstyle="->", color="black", lw=1)
            )

    # Identify critical activities (float == 0 and not START/END)
    critical_activities = [
        node for node in G.nodes()
        if G.nodes[node].get('float', None) == 0 and node not in ['START', 'END']
    ]

    # Draw nodes with appropriate coloring and labels
    for node in G.nodes():
        x, y = pos[node]
        # Determine node color
        if node == 'START':
            color = 'lightgreen'
        elif node == 'END':
            color = 'orange'
        elif node in critical_activities:
            color = 'red'
        else:
            color = 'lightblue'

        # Draw node circle
        circle = plt.Circle(
            (x, y), node_radius, fill=True, color=color, alpha=0.7,
            edgecolor='black', linewidth=1
        )
        ax.add_patch(circle)

        # Draw node label
        if node in ['START', 'END']:
            display_text = 'Start' if node == 'START' else 'End'
            ax.text(
                x, y, display_text, ha='center', va='center',
                fontsize=7, fontweight='bold'
            )
        else:
            # Draw horizontal line inside node
            ax.plot(
                [x - node_radius, x + node_radius], [y, y],
                color='black', linewidth=0.8
            )
            # Activity name above center
            ax.text(
                x, y + node_radius / 2, node, ha='center', va='center',
                fontsize=7, fontweight='bold'
            )
            # Duration below center
            ax.text(
                x, y - node_radius / 2, str(G.nodes[node].get('duration', '')),
                ha='center', va='center', fontsize=6
            )

    ax.set_axis_off()
    ax.set_aspect('equal')

