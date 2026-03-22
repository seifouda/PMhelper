#!/usr/bin/env python3
"""
Interactive Network Viewer — vis.js HTML generation via pyvis.

Generates a self-contained HTML file with an interactive network diagram
that can be opened in any browser. Coexists with the Matplotlib in-app
diagrams (NetworkTab, PertDiagramTab).

Phase 17 — PMhelper Edu V1.
"""

import os
import platform
import tempfile
import webbrowser
from pathlib import Path

try:
    from pyvis.network import Network as PyvisNetwork
    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False


def generate_interactive_network(results_data, analysis_mode=None,
                                  mode='network'):
    """Build an interactive vis.js network and open it in the default browser.

    Parameters
    ----------
    results_data : dict
        The standard results dict with 'activities', 'critical_activities',
        'project_duration', etc.
    analysis_mode : str | None
        'deterministic' or 'probabilistic'.
    mode : str
        'network' for the simple Network Diagram view,
        'pert' for the PERT-style view (richer tooltips with ES/EF/LS/LF).

    Returns
    -------
    str | None
        Path to the generated HTML file, or *None* if pyvis is unavailable.
    """
    if not PYVIS_AVAILABLE:
        return None

    activities = results_data.get('activities', [])
    critical_activities = set(results_data.get('critical_activities', []))
    project_duration = results_data.get('project_duration', '?')

    if not activities:
        return None

    # --- build pyvis graph ------------------------------------------------
    net = _create_pyvis_network(project_duration, analysis_mode)
    _add_nodes(net, activities, critical_activities, analysis_mode, mode)
    _add_edges(net, activities, critical_activities)
    _apply_options(net)

    # --- write HTML -------------------------------------------------------
    html_path = _write_html(net)
    return html_path


def open_interactive_network(results_data, analysis_mode=None, mode='network'):
    """Generate the HTML and open it in the default browser.

    Convenience wrapper used by the GUI buttons.
    """
    html_path = generate_interactive_network(
        results_data, analysis_mode=analysis_mode, mode=mode)
    if html_path:
        _open_in_browser(html_path)
    return html_path


def _open_in_browser(path):
    """Open an HTML file in the default *browser*, not the default .html app.

    On Windows the default handler for .html may be VS Code or an editor,
    so we read the OS-registered browser from the registry and launch it
    directly.  Falls back to webbrowser.open() on other platforms.
    """
    url = Path(path).as_uri()          # file:///C:/Users/…
    if platform.system() == 'Windows':
        import subprocess
        import shlex
        # Read the system HTTP handler — this is always the browser
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
            ) as key:
                prog_id = winreg.QueryValueEx(key, "ProgId")[0]
            with winreg.OpenKey(
                winreg.HKEY_CLASSES_ROOT,
                rf"{prog_id}\shell\open\command"
            ) as key:
                cmd_template = winreg.QueryValueEx(key, "")[0]
            # cmd_template looks like: "C:\Program Files\...\chrome.exe" --flag "%1"
            # Replace %1 with our URL
            cmd = cmd_template.replace('%1', url)
            subprocess.Popen(cmd)
            return
        except Exception:
            pass
        # Fallback: webbrowser module
        webbrowser.open(url)
    else:
        webbrowser.open(url)


# ── internal helpers ─────────────────────────────────────────────────────


def _create_pyvis_network(project_duration, analysis_mode):
    """Create and configure the pyvis Network object."""
    title = "Project Network Diagram"
    if analysis_mode == 'probabilistic':
        title = "PERT Network Diagram"
    title += f"  -  Duration: {project_duration}"

    net = PyvisNetwork(
        height="100vh",
        width="100%",
        directed=True,
        heading=title,
        bgcolor="#ffffff",
        font_color="#333333",
        notebook=False,
        cdn_resources='in_line',
    )
    return net


def _add_nodes(net, activities, critical_activities, analysis_mode, mode):
    """Add activity nodes (+ synthetic START / END) to the pyvis graph."""
    node_ids = set()
    predecessors_map = {}

    for act in activities:
        aid = act.get('id', '')
        node_ids.add(aid)
        preds = act.get('predecessors', [])
        if isinstance(preds, str):
            preds = [p.strip() for p in preds.split(',') if p.strip()]
        predecessors_map[aid] = preds

    # Determine start / end nodes
    all_preds = {p for ps in predecessors_map.values() for p in ps}
    start_nodes = [n for n in node_ids if not predecessors_map.get(n)]
    end_nodes = [n for n in node_ids
                 if n not in all_preds or not any(
                     n in predecessors_map.get(other, [])
                     for other in node_ids if other != n)]
    # Simpler: end nodes = nodes that are never a predecessor
    _is_predecessor = set()
    for preds in predecessors_map.values():
        _is_predecessor.update(preds)
    end_nodes = [n for n in node_ids if n not in _is_predecessor]

    # Add START node
    net.add_node(
        '__START__',
        label='Start',
        color='#7BE141',
        shape='ellipse',
        size=30,
        font={'size': 14, 'face': 'Arial', 'bold': True},
        title='Project Start',
    )

    # Add activity nodes
    for act in activities:
        aid = act.get('id', '')
        duration = act.get('duration', 0)
        if analysis_mode == 'probabilistic':
            duration = act.get('expected', act.get('expected_duration', duration))

        is_critical = aid in critical_activities
        color = '#FF6B6B' if is_critical else '#97C2FC'
        border_width = 3 if is_critical else 1
        border_color = '#C0392B' if is_critical else '#2B7CE9'

        # Build tooltip
        tooltip = _build_tooltip(act, aid, duration, is_critical, mode)

        net.add_node(
            aid,
            label=str(aid),
            color={
                'background': color,
                'border': border_color,
                'highlight': {'background': '#FFF176', 'border': '#F57F17'},
            },
            shape='box',
            size=25,
            font={'size': 12, 'face': 'Arial'},
            title=tooltip,
            borderWidth=border_width,
        )

    # Add END node
    net.add_node(
        '__END__',
        label='End',
        color='#FFA807',
        shape='ellipse',
        size=30,
        font={'size': 14, 'face': 'Arial', 'bold': True},
        title='Project End',
    )

    # Edges from START to start-activities and from end-activities to END
    for sn in start_nodes:
        net.add_edge('__START__', sn, color='#888888', width=1)
    for en in end_nodes:
        net.add_edge(en, '__END__', color='#888888', width=1)


def _build_tooltip(act, aid, duration, is_critical, mode):
    """Build the HTML hover tooltip for a node."""
    es = act.get('ES', act.get('earliest_start', ''))
    ef = act.get('EF', act.get('earliest_finish', ''))
    ls = act.get('LS', act.get('latest_start', ''))
    lf = act.get('LF', act.get('latest_finish', ''))
    flt = act.get('float', act.get('total_float', act.get('Float', '')))
    name = act.get('name', act.get('activity', ''))

    lines = [f"<b>{aid}</b>"]
    if name:
        lines.append(f"Name: {name}")
    lines.append(f"Duration: {duration}")

    if mode == 'pert' or any(v != '' for v in (es, ef, ls, lf)):
        lines.append(f"ES: {es}  |  EF: {ef}")
        lines.append(f"LS: {ls}  |  LF: {lf}")
        lines.append(f"Float: {flt}")

    status = "CRITICAL" if is_critical else "Non-critical"
    lines.append(f"Status: {status}")
    return "<br>".join(lines)


def _add_edges(net, activities, critical_activities):
    """Add dependency edges between activity nodes."""
    for act in activities:
        aid = act.get('id', '')
        preds = act.get('predecessors', [])
        if isinstance(preds, str):
            preds = [p.strip() for p in preds.split(',') if p.strip()]

        for pred in preds:
            both_critical = (pred in critical_activities
                             and aid in critical_activities)
            edge_color = '#C0392B' if both_critical else '#848484'
            edge_width = 2.5 if both_critical else 1
            net.add_edge(
                pred, aid,
                color=edge_color,
                width=edge_width,
                arrows='to',
            )


def _apply_options(net):
    """Apply vis.js options for hierarchical layout, physics, interaction."""
    net.set_options("""
    {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "LR",
          "sortMethod": "directed",
          "levelSeparation": 200,
          "nodeSpacing": 120,
          "treeSpacing": 150,
          "blockShifting": true,
          "edgeMinimization": true,
          "parentCentralization": true
        }
      },
      "physics": {
        "enabled": false
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.8
          }
        },
        "smooth": {
          "type": "cubicBezier",
          "forceDirection": "horizontal",
          "roundness": 0.4
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 100,
        "navigationButtons": true,
        "keyboard": {
          "enabled": true,
          "bindToWindow": true
        },
        "zoomView": true,
        "dragView": true
      },
      "nodes": {
        "font": {
          "size": 12,
          "face": "Arial"
        },
        "margin": 10
      }
    }
    """)


def _write_html(net):
    """Write the pyvis network to a temp HTML file and return its path."""
    tmp = tempfile.NamedTemporaryFile(
        suffix='.html', prefix='pmhelper_network_', delete=False, mode='w',
        encoding='utf-8')
    tmp.close()
    # Generate the HTML string via pyvis, then write with explicit UTF-8
    # to avoid cp1252 encoding errors on Windows.
    net.generate_html(name=tmp.name)
    with open(tmp.name, 'w', encoding='utf-8') as f:
        f.write(net.html)
    return tmp.name
