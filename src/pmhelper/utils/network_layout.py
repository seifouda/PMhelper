"""
Sugiyama-style Layered Layout Engine for Network Diagrams.

Shared by: NetworkTab, PertDiagramTab, crashing_visualization (gui + core).

Algorithm:
1. Layer assignment via topological generations
2. Virtual (dummy) node insertion for edges spanning >1 layer
3. Barycenter Y-ordering with 4 iterative passes to minimise edge crossings
4. Final coordinate assignment with configurable spacing
"""

import networkx as nx


def sugiyama_layout(G, x_spacing=3.5, y_spacing=4.0, num_passes=4):
    """Compute a Sugiyama-style hierarchical layout for a DAG.

    Parameters
    ----------
    G : nx.DiGraph
        Directed acyclic graph.  **Modified in-place** — virtual nodes and
        edges are added to represent long-edge routing.  Callers should pass
        a copy if the original graph must stay pristine.
    x_spacing : float
        Horizontal gap between successive layers (columns).
    y_spacing : float
        Vertical gap between nodes inside a layer.
    num_passes : int
        Number of barycenter ordering iterations (default 4).

    Returns
    -------
    result : dict with keys:
        ``pos``           – ``{node: (x, y)}`` for **real** nodes only
        ``all_pos``       – ``{node: (x, y)}`` incl. virtual nodes
        ``virtual_nodes`` – ``set`` of virtual-node IDs
        ``edge_paths``    – ``{(u_orig, v_orig): [u, virt…, v]}``
    """

    # --- Step 1: layer assignment via topological generations ----
    generations = list(nx.topological_generations(G))
    node_layer = {}          # node → column index
    layers = []              # list[list[node]]  (mutable per-layer lists)
    for i, gen in enumerate(generations):
        layer = sorted(gen)  # initial alphabetical order
        layers.append(layer)
        for node in layer:
            node_layer[node] = i

    # --- Step 2: insert virtual (dummy) nodes for long edges ----
    virtual_nodes = set()
    edge_paths = {}          # (u, v) → [u, virt1, …, v]
    edges_to_process = list(G.edges())
    for u, v in edges_to_process:
        span = node_layer[v] - node_layer[u]
        if span <= 1:
            edge_paths[(u, v)] = [u, v]
            continue
        # Insert a virtual node at each intermediate layer
        path = [u]
        prev = u
        for k in range(1, span):
            virt_id = f'_virt_{u}_{v}_{k}'
            virtual_nodes.add(virt_id)
            target_layer = node_layer[u] + k
            layers[target_layer].append(virt_id)
            node_layer[virt_id] = target_layer
            G.add_node(virt_id, duration=0, virtual=True)
            G.add_edge(prev, virt_id)
            path.append(virt_id)
            prev = virt_id
        G.add_edge(prev, v)
        path.append(v)
        edge_paths[(u, v)] = path
        # Remove original long edge (replaced by chain)
        if G.has_edge(u, v):
            G.remove_edge(u, v)

    # --- Step 3: barycenter ordering (iterative passes) ----------
    pos = {}
    for i, layer in enumerate(layers):
        for j, node in enumerate(layer):
            pos[node] = (i * x_spacing, (j - len(layer) / 2 + 0.5) * y_spacing)

    for iteration in range(num_passes):
        if iteration % 2 == 0:
            layer_range = range(1, len(layers))        # forward
        else:
            layer_range = range(len(layers) - 2, -1, -1)  # backward

        for li in layer_range:
            layer = layers[li]
            bary_values = {}
            for node in layer:
                if iteration % 2 == 0:
                    neighbors = list(G.predecessors(node))
                else:
                    neighbors = list(G.successors(node))
                connected = [n for n in neighbors if n in pos]
                if connected:
                    bary_values[node] = sum(pos[n][1] for n in connected) / len(connected)
                else:
                    bary_values[node] = pos[node][1]
            layer.sort(key=lambda n: bary_values.get(n, 0))
            layers[li] = layer
            for j, node in enumerate(layer):
                x = node_layer[node] * x_spacing
                y = (j - len(layer) / 2 + 0.5) * y_spacing
                pos[node] = (x, y)

    # --- Step 4: build return maps -----------------------------------
    all_pos = dict(pos)
    real_pos = {n: p for n, p in pos.items() if n not in virtual_nodes}

    return {
        'pos': real_pos,
        'all_pos': all_pos,
        'virtual_nodes': virtual_nodes,
        'edge_paths': edge_paths,
    }


def cleanup_virtual_nodes(G, virtual_nodes):
    """Remove virtual nodes from *G* after drawing is complete."""
    for vn in list(virtual_nodes):
        if vn in G:
            G.remove_node(vn)


def draw_edges_polyline(ax, G, pos, all_pos, virtual_nodes, edge_paths,
                        node_radius=0.6, critical_check=None):
    """Draw edges as polylines routed through virtual-node waypoints.

    Parameters
    ----------
    ax : matplotlib Axes
    G  : the (augmented) graph
    pos : dict  – real-node positions
    all_pos : dict  – all positions incl. virtual
    virtual_nodes : set
    edge_paths : dict  – ``{(u,v): [u, virt…, v]}``
    node_radius : float
    critical_check : callable(u, v) → bool, or None
        If provided, returns True when the edge (u, v) should be drawn in red.
    """
    drawn_edges = set()

    # --- edges with explicit polyline paths --------------------------
    for (u_orig, v_orig), path in edge_paths.items():
        if len(path) < 2:
            continue
        is_critical = critical_check(u_orig, v_orig) if critical_check else False
        edge_color = 'red' if is_critical else 'black'
        edge_lw = 2.0 if is_critical else 1.5

        waypoints = [all_pos[n] for n in path if n in all_pos]
        if len(waypoints) < 2:
            continue

        for seg_idx in range(len(waypoints) - 1):
            x1, y1 = waypoints[seg_idx]
            x2, y2 = waypoints[seg_idx + 1]
            seg_start = path[seg_idx]
            seg_end = path[seg_idx + 1]

            # Offset start away from real node centre
            if seg_start not in virtual_nodes:
                dx, dy = x2 - x1, y2 - y1
                d = (dx ** 2 + dy ** 2) ** 0.5
                if d > 0:
                    x1 += node_radius * dx / d
                    y1 += node_radius * dy / d

            # Offset end away from real node centre
            if seg_end not in virtual_nodes:
                dx, dy = x2 - x1, y2 - y1
                d = (dx ** 2 + dy ** 2) ** 0.5
                if d > 0:
                    x2 -= node_radius * dx / d
                    y2 -= node_radius * dy / d

            if seg_idx == len(waypoints) - 2:
                ax.annotate(
                    "", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=edge_color, lw=edge_lw),
                    zorder=1,
                )
            else:
                ax.plot([x1, x2], [y1, y2],
                        color=edge_color, lw=edge_lw, zorder=1)

        for i in range(len(path) - 1):
            drawn_edges.add((path[i], path[i + 1]))

    # --- remaining direct edges not in edge_paths --------------------
    for u, v in G.edges():
        if (u, v) in drawn_edges:
            continue
        if u in virtual_nodes or v in virtual_nodes:
            continue
        if u not in pos or v not in pos:
            continue
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        dx, dy = x2 - x1, y2 - y1
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx_n, dy_n = dx / distance, dy / distance
            start_x = x1 + node_radius * dx_n
            start_y = y1 + node_radius * dy_n
            end_x = x2 - node_radius * dx_n
            end_y = y2 - node_radius * dy_n
            is_critical = critical_check(u, v) if critical_check else False
            edge_color = 'red' if is_critical else 'black'
            edge_lw = 2.0 if is_critical else 1.5
            ax.annotate(
                "", xy=(end_x, end_y), xytext=(start_x, start_y),
                arrowprops=dict(arrowstyle="->", color=edge_color, lw=edge_lw),
                zorder=1,
            )
