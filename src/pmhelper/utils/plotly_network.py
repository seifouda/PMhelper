"""
Plotly Network Diagram — generates an interactive network diagram as a Plotly Figure.

Used by the embedded PlotlyChartFrame inside NetworkTab.
"""

import networkx as nx

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from pmhelper.utils.network_layout import sugiyama_layout, cleanup_virtual_nodes


def generate_plotly_network(results_data, analysis_mode=None):
    """Build an interactive Plotly network diagram (AON).

    Parameters
    ----------
    results_data : dict
        Standard results dict with 'activities', 'critical_activities', etc.
    analysis_mode : str | None
        'deterministic' or 'probabilistic'.

    Returns
    -------
    plotly.graph_objects.Figure | None
    """
    if not PLOTLY_AVAILABLE:
        return None

    activities = results_data.get("activities", [])
    critical_set = set(results_data.get("critical_activities", []))
    if not activities:
        return None

    # ── Build NetworkX graph ─────────────────────────────────────────
    G = nx.DiGraph()
    act_map = {}  # id → activity dict
    for act in activities:
        aid = act.get("id", "")
        act_map[aid] = act
        dur = act.get("duration", 0)
        if analysis_mode == "probabilistic":
            dur = act.get("expected", act.get("expected_duration", dur))
        G.add_node(aid, duration=dur, critical=(aid in critical_set))

    for act in activities:
        aid = act.get("id", "")
        preds = act.get("predecessors", [])
        if isinstance(preds, str):
            preds = [p.strip() for p in preds.split(",") if p.strip()]
        for p in preds:
            if p in G.nodes:
                G.add_edge(p, aid)

    # Add START / END pseudo-nodes only if they don't already exist
    if "START" not in G.nodes:
        starts = [n for n in G.nodes() if G.in_degree(n) == 0]
        if starts:
            G.add_node("START", duration=0, critical=False)
            for n in starts:
                G.add_edge("START", n)
    if "END" not in G.nodes:
        ends = [n for n in G.nodes() if G.out_degree(n) == 0 and n != "START"]
        if ends:
            G.add_node("END", duration=0, critical=False)
            for n in ends:
                G.add_edge(n, "END")

    # ── Layout ───────────────────────────────────────────────────────
    n = len([nd for nd in G.nodes() if nd not in ("START", "END")])
    if n <= 50:
        x_sp, y_sp = 3.5, 2.5
    elif n <= 200:
        x_sp, y_sp = 2.0, 2.5
    else:
        x_sp, y_sp = 1.0, 1.5

    result = sugiyama_layout(G, x_spacing=x_sp, y_spacing=y_sp)
    pos = result["pos"]
    all_pos = result["all_pos"]
    virtual_nodes = result["virtual_nodes"]
    edge_paths = result["edge_paths"]

    # ── Edge traces ──────────────────────────────────────────────────
    # Collect polyline segments for normal and critical edges separately.
    norm_x, norm_y = [], []
    crit_x, crit_y = [], []

    for (u, v), path in edge_paths.items():
        waypoints = [all_pos[n] for n in path if n in all_pos]
        if len(waypoints) < 2:
            continue
        is_crit = (G.nodes.get(u, {}).get("critical", False)
                   and G.nodes.get(v, {}).get("critical", False))
        buf_x = crit_x if is_crit else norm_x
        buf_y = crit_y if is_crit else norm_y
        for wx, wy in waypoints:
            buf_x.append(wx)
            buf_y.append(wy)
        buf_x.append(None)  # line break
        buf_y.append(None)

    fig = go.Figure()

    if norm_x:
        fig.add_trace(go.Scatter(
            x=norm_x, y=norm_y, mode="lines",
            line=dict(color="#999", width=1),
            hoverinfo="skip", showlegend=False,
        ))
    if crit_x:
        fig.add_trace(go.Scatter(
            x=crit_x, y=crit_y, mode="lines",
            line=dict(color="#cc2222", width=2.5),
            hoverinfo="skip", showlegend=False,
        ))

    # ── Node traces ──────────────────────────────────────────────────
    # Split into critical / normal / start-end for distinct colours.
    groups = {
        "Critical": {"ids": [], "x": [], "y": [], "text": [], "hover": [],
                     "color": "#E74C3C", "size": 18},
        "Normal": {"ids": [], "x": [], "y": [], "text": [], "hover": [],
                   "color": "#3498DB", "size": 18},
        "Milestone": {"ids": [], "x": [], "y": [], "text": [], "hover": [],
                      "color": "#F39C12", "size": 22},
    }

    for node in G.nodes():
        if node in virtual_nodes:
            continue
        if node not in pos:
            continue
        x, y = pos[node]
        a = act_map.get(node, {})
        dur = G.nodes[node].get("duration", 0)
        is_crit = node in critical_set

        if node in ("START", "END"):
            grp = "Milestone"
            label = "Start" if node == "START" else "End"
            hover_text = label
        else:
            grp = "Critical" if is_crit else "Normal"
            name = a.get("name", a.get("activity", ""))
            label = node
            es = a.get("ES", "")
            ef = a.get("EF", "")
            ls = a.get("LS", "")
            lf = a.get("LF", "")
            flt = a.get("float", a.get("total_float", ""))
            hover_text = (
                f"<b>{node}</b>"
                f"{'<br>' + str(name) if name else ''}"
                f"<br>Duration: {dur}"
                f"<br>ES: {es}  EF: {ef}"
                f"<br>LS: {ls}  LF: {lf}"
                f"<br>Float: {flt}"
                f"<br>{'CRITICAL' if is_crit else 'Non-critical'}"
            )

        g = groups[grp]
        g["ids"].append(node)
        g["x"].append(x)
        g["y"].append(y)
        g["text"].append(label)
        g["hover"].append(hover_text)

    # Adaptive label size
    if n > 200:
        text_size = 7
        marker_size = 10
    elif n > 50:
        text_size = 8
        marker_size = 14
    else:
        text_size = 10
        marker_size = 18

    for name, g in groups.items():
        if not g["x"]:
            continue
        fig.add_trace(go.Scatter(
            x=g["x"], y=g["y"],
            mode="markers+text",
            marker=dict(color=g["color"], size=marker_size,
                        line=dict(width=1, color="#333")),
            text=g["text"],
            textposition="middle center",
            textfont=dict(size=text_size, color="white"),
            hovertext=g["hover"],
            hoverinfo="text",
            name=name,
        ))

    # ── Layout ───────────────────────────────────────────────────────
    project_dur = results_data.get("project_duration", "?")
    title = f"Interactive Network Diagram — {
        len(activities)} activities, Duration: {project_dur}"

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(
                size=14)),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""),
        plot_bgcolor="white",
        hovermode="closest",
        margin=dict(
            l=10,
            r=10,
            t=60,
            b=10),
        dragmode="pan",
    )

    # Cleanup virtual nodes from the graph copy
    cleanup_virtual_nodes(G, virtual_nodes)

    return fig
