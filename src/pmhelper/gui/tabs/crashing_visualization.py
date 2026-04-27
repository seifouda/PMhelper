# CPM Crashing Visualization Functions
import matplotlib.pyplot as plt
from pmhelper.utils.network_layout import sugiyama_layout, cleanup_virtual_nodes, draw_edges_polyline


def draw_network_diagram_on_ax(ax, G):
    result = sugiyama_layout(G, x_spacing=3.5, y_spacing=4.0)
    pos = result['pos']
    virtual_nodes = result['virtual_nodes']
    edge_paths = result['edge_paths']
    all_pos = result['all_pos']
    node_radius = 0.4

    critical_activities = [
        node for node in G.nodes() if G.nodes[node].get(
            'float', None) == 0 and node not in [
            'START', 'END'] and node not in virtual_nodes]

    def critical_check(u, v):
        return (u in critical_activities or u == 'START') and (
            v in critical_activities or v == 'END')

    draw_edges_polyline(ax, G, pos, all_pos, virtual_nodes, edge_paths,
                        node_radius=node_radius, critical_check=critical_check)

    for node in G.nodes():
        if node in virtual_nodes:
            continue
        if node not in pos:
            continue
        x, y = pos[node]
        if node == 'START':
            color = 'lightgreen'
        elif node == 'END':
            color = 'orange'
        elif node in critical_activities:
            color = 'red'
        else:
            color = 'lightblue'
        circle = plt.Circle(
            (x, y), node_radius, fill=True, color=color, alpha=1.0,
            edgecolor='black', linewidth=1.5)
        ax.add_patch(circle)
        if node in ['START', 'END']:
            display_text = 'Start' if node == 'START' else 'End'
            ax.text(x, y, display_text, ha='center', va='center',
                    fontsize=10, fontweight='bold')
        else:
            ax.plot([x - node_radius, x + node_radius], [y, y],
                    color='black', linewidth=1.2)
            ax.text(x, y + node_radius / 2, node, ha='center', va='center',
                    fontsize=10, fontweight='bold')
            ax.text(x, y - node_radius / 2,
                    str(G.nodes[node].get('duration', '')),
                    ha='center', va='center', fontsize=9)

    cleanup_virtual_nodes(G, virtual_nodes)
    ax.set_axis_off()
    ax.set_aspect('equal')


def draw_network_diagram_on_ax_small(ax, G):
    result = sugiyama_layout(G, x_spacing=2.5, y_spacing=2.0)
    pos = result['pos']
    virtual_nodes = result['virtual_nodes']
    edge_paths = result['edge_paths']
    all_pos = result['all_pos']
    node_radius = 0.3

    critical_activities = [
        node for node in G.nodes() if G.nodes[node].get(
            'float', None) == 0 and node not in [
            'START', 'END'] and node not in virtual_nodes]

    def critical_check(u, v):
        return (u in critical_activities or u == 'START') and (
            v in critical_activities or v == 'END')

    draw_edges_polyline(ax, G, pos, all_pos, virtual_nodes, edge_paths,
                        node_radius=node_radius, critical_check=critical_check)

    for node in G.nodes():
        if node in virtual_nodes:
            continue
        if node not in pos:
            continue
        x, y = pos[node]
        if node == 'START':
            color = 'lightgreen'
        elif node == 'END':
            color = 'orange'
        elif node in critical_activities:
            color = 'red'
        else:
            color = 'lightblue'
        circle = plt.Circle(
            (x, y), node_radius, fill=True, color=color, alpha=1.0,
            edgecolor='black', linewidth=1)
        ax.add_patch(circle)
        if node in ['START', 'END']:
            display_text = 'Start' if node == 'START' else 'End'
            ax.text(x, y, display_text, ha='center', va='center',
                    fontsize=7, fontweight='bold')
        else:
            ax.plot([x - node_radius, x + node_radius], [y, y],
                    color='black', linewidth=0.8)
            ax.text(x, y + node_radius / 2, node, ha='center', va='center',
                    fontsize=7, fontweight='bold')
            ax.text(x, y - node_radius / 2,
                    str(G.nodes[node].get('duration', '')),
                    ha='center', va='center', fontsize=6)

    cleanup_virtual_nodes(G, virtual_nodes)
    ax.set_axis_off()
    ax.set_aspect('equal')
