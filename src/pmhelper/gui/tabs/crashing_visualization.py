# CPM Crashing Visualization Functions
import networkx as nx
import matplotlib.pyplot as plt

def draw_network_diagram_on_ax(ax, G):
    pos = {}
    generations = list(nx.topological_generations(G))
    for i, gen in enumerate(generations):
        sorted_gen = sorted(gen)
        for j, node in enumerate(sorted_gen):
            y_pos = (j - len(sorted_gen) / 2 + 0.5) * 4
            pos[node] = (i * 3, y_pos)
    node_radius = 0.4
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
            ax.annotate("", xy=(end_x, end_y), xytext=(start_x, start_y),
                        arrowprops=dict(arrowstyle="->", color="black", lw=1.5))
    critical_activities = [node for node in G.nodes() if G.nodes[node].get('float', None) == 0 and node not in ['START', 'END']]
    for node in G.nodes():
        x, y = pos[node]
        if node == 'START':
            color = 'lightgreen'
        elif node == 'END':
            color = 'orange'
        elif node in critical_activities:
            color = 'red'
        else:
            color = 'lightblue'
        circle = plt.Circle((x, y), node_radius, fill=True, color=color, alpha=0.7,
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
            ax.text(x, y - node_radius / 2, str(G.nodes[node].get('duration', '')), ha='center', va='center', fontsize=9)
    ax.set_axis_off()
    ax.set_aspect('equal')

def draw_network_diagram_on_ax_small(ax, G):
    pos = {}
    generations = list(nx.topological_generations(G))
    for i, gen in enumerate(generations):
        sorted_gen = sorted(gen)
        for j, node in enumerate(sorted_gen):
            y_pos = (j - len(sorted_gen) / 2 + 0.5) * 2
            pos[node] = (i * 2, y_pos)
    node_radius = 0.3
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
            ax.annotate("", xy=(end_x, end_y), xytext=(start_x, start_y),
                        arrowprops=dict(arrowstyle="->", color="black", lw=1))
    critical_activities = [node for node in G.nodes() if G.nodes[node].get('float', None) == 0 and node not in ['START', 'END']]
    for node in G.nodes():
        x, y = pos[node]
        if node == 'START':
            color = 'lightgreen'
        elif node == 'END':
            color = 'orange'
        elif node in critical_activities:
            color = 'red'
        else:
            color = 'lightblue'
        circle = plt.Circle((x, y), node_radius, fill=True, color=color, alpha=0.7,
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
            ax.text(x, y - node_radius / 2, str(G.nodes[node].get('duration', '')), ha='center', va='center', fontsize=6)
    ax.set_axis_off()
    ax.set_aspect('equal')
