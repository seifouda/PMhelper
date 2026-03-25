"""Tests for Phase 14A — Shared Sugiyama Layout Engine + PERT / Crashing integration."""

import sys
import os
import pytest
import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, "src"))

import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pmhelper.utils.network_layout import (
    sugiyama_layout,
    cleanup_virtual_nodes,
    draw_edges_polyline,
)


# ---------------------------------------------------------------------------
# Helpers: reusable test graphs
# ---------------------------------------------------------------------------

def _diamond():
    """A→B→D, A→C→D."""
    G = nx.DiGraph()
    for nid in ["A", "B", "C", "D"]:
        G.add_node(nid, duration=3, float=0, id=nid)
    G.add_edges_from([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
    return G


def _long_edge():
    """A→B→C→D  plus  A→D (spans 3 layers)."""
    G = nx.DiGraph()
    for nid in ["A", "B", "C", "D"]:
        G.add_node(nid, duration=2, float=0, id=nid)
    G.add_edges_from([("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")])
    return G


def _parallel():
    """START → {A,B,C,D,E} → END."""
    G = nx.DiGraph()
    G.add_node("START", duration=0)
    G.add_node("END", duration=0)
    for nid in "ABCDE":
        G.add_node(nid, duration=4, float=2, id=nid)
        G.add_edge("START", nid)
        G.add_edge(nid, "END")
    return G


def _complex():
    """
    START → A → C → E → END
    START → B → D → F → END
    A → D  (long)
    B → E  (long)
    """
    G = nx.DiGraph()
    for nid, dur in [("START", 0), ("A", 3), ("B", 4), ("C", 2),
                     ("D", 5), ("E", 3), ("F", 2), ("END", 0)]:
        G.add_node(nid, duration=dur, float=0, id=nid)
    G.add_edges_from([
        ("START", "A"), ("START", "B"),
        ("A", "C"), ("B", "D"),
        ("C", "E"), ("D", "F"),
        ("E", "END"), ("F", "END"),
        ("A", "D"), ("B", "E"),
    ])
    return G


def _crashing_network():
    """Network with START/END and critical path attributes for crashing viz."""
    G = nx.DiGraph()
    G.add_node("START", duration=0, float=0)
    G.add_node("END", duration=0, float=0)
    for nid, dur, flt in [("A", 5, 0), ("B", 3, 2), ("C", 4, 0), ("D", 2, 1)]:
        G.add_node(nid, duration=dur, float=flt, id=nid)
    G.add_edges_from([
        ("START", "A"), ("START", "B"),
        ("A", "C"), ("B", "D"),
        ("C", "END"), ("D", "END"),
    ])
    return G


# ===================================================================
# A1  sugiyama_layout() unit tests
# ===================================================================

class TestSugiyamaLayout:
    """Direct tests against the shared layout function."""

    def test_returns_expected_keys(self):
        result = sugiyama_layout(_diamond())
        for key in ("pos", "all_pos", "virtual_nodes", "edge_paths"):
            assert key in result

    def test_real_nodes_in_pos(self):
        result = sugiyama_layout(_diamond())
        for n in ["A", "B", "C", "D"]:
            assert n in result["pos"]

    def test_no_virtual_in_pos(self):
        result = sugiyama_layout(_long_edge())
        for n in result["pos"]:
            assert not n.startswith("_virt_")

    def test_virtual_nodes_created(self):
        result = sugiyama_layout(_long_edge())
        assert len(result["virtual_nodes"]) > 0

    def test_virtual_nodes_in_all_pos(self):
        result = sugiyama_layout(_long_edge())
        for vn in result["virtual_nodes"]:
            assert vn in result["all_pos"]

    def test_edge_paths_populated(self):
        result = sugiyama_layout(_long_edge())
        assert ("A", "D") in result["edge_paths"]
        path = result["edge_paths"][("A", "D")]
        assert path[0] == "A" and path[-1] == "D"
        assert len(path) >= 3

    def test_short_edges_direct(self):
        result = sugiyama_layout(_diamond())
        assert result["edge_paths"][("A", "B")] == ["A", "B"]

    def test_no_overlap(self):
        result = sugiyama_layout(_parallel())
        pos = result["pos"]
        nodes = list(pos)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                x1, y1 = pos[nodes[i]]
                x2, y2 = pos[nodes[j]]
                dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                assert dist >= 0.5, f"Overlap: {nodes[i]} and {nodes[j]} dist={dist:.2f}"

    def test_predecessors_left_of_successors(self):
        result = sugiyama_layout(_complex())
        pos = result["pos"]
        for u, v in [("START", "A"), ("A", "C"), ("C", "E"), ("E", "END")]:
            assert pos[u][0] < pos[v][0]

    def test_custom_spacing(self):
        r1 = sugiyama_layout(_diamond(), x_spacing=2.0, y_spacing=1.0)
        r2 = sugiyama_layout(_diamond(), x_spacing=10.0, y_spacing=8.0)
        # Wider spacing ⇒ larger x-extent
        xs1 = [p[0] for p in r1["pos"].values()]
        xs2 = [p[0] for p in r2["pos"].values()]
        assert max(xs2) - min(xs2) > max(xs1) - min(xs1)


# ===================================================================
# A2  cleanup_virtual_nodes()
# ===================================================================

class TestCleanupVirtualNodes:
    """Ensure virtual nodes are removed from the graph post-draw."""

    def test_virtual_nodes_removed(self):
        G = _long_edge()
        result = sugiyama_layout(G)
        vn = result["virtual_nodes"]
        assert len(vn) > 0
        cleanup_virtual_nodes(G, vn)
        for v in vn:
            assert v not in G

    def test_real_nodes_preserved(self):
        G = _long_edge()
        real = set(G.nodes())
        result = sugiyama_layout(G)
        cleanup_virtual_nodes(G, result["virtual_nodes"])
        for n in real:
            assert n in G

    def test_idempotent(self):
        G = _long_edge()
        result = sugiyama_layout(G)
        vn = result["virtual_nodes"]
        cleanup_virtual_nodes(G, vn)
        cleanup_virtual_nodes(G, vn)  # second call should not raise


# ===================================================================
# A3  draw_edges_polyline() smoke test
# ===================================================================

class TestDrawEdgesPolyline:
    """Smoke-test the edge drawing helper on a matplotlib Axes."""

    def test_smoke_no_crash(self):
        G = _long_edge()
        result = sugiyama_layout(G)
        fig, ax = plt.subplots()
        draw_edges_polyline(ax, G, result["pos"], result["all_pos"],
                            result["virtual_nodes"], result["edge_paths"])
        plt.close(fig)

    def test_with_critical_check(self):
        G = _long_edge()
        result = sugiyama_layout(G)
        fig, ax = plt.subplots()
        draw_edges_polyline(
            ax, G, result["pos"], result["all_pos"],
            result["virtual_nodes"], result["edge_paths"],
            critical_check=lambda u, v: True,
        )
        plt.close(fig)

    def test_complex_graph(self):
        G = _complex()
        result = sugiyama_layout(G)
        fig, ax = plt.subplots()
        draw_edges_polyline(ax, G, result["pos"], result["all_pos"],
                            result["virtual_nodes"], result["edge_paths"],
                            node_radius=0.4)
        cleanup_virtual_nodes(G, result["virtual_nodes"])
        plt.close(fig)


# ===================================================================
# A4  PERT diagram integration
# ===================================================================

class TestPertIntegration:
    """Verify PERT tab can be imported and its layout method works."""

    def test_import_pert_module(self):
        from pmhelper.gui.tabs.pert_diagram_tab import PertDiagramTab
        assert hasattr(PertDiagramTab, "create_hierarchical_layout")

    def test_pert_layout_delegates_to_shared(self):
        """PertDiagramTab.create_hierarchical_layout should use sugiyama_layout."""
        from pmhelper.gui.tabs.pert_diagram_tab import PertDiagramTab

        class _Harness:
            _virtual_nodes = set()
            _edge_paths = {}
            _all_pos = {}

        h = _Harness()
        G = _diamond()
        pos = PertDiagramTab.create_hierarchical_layout(h, G)
        assert "A" in pos
        assert len(h._virtual_nodes) == 0  # diamond has no long edges


# ===================================================================
# A5  Crashing visualization integration (gui/tabs)
# ===================================================================

class TestCrashingGuiIntegration:
    """Smoke-test the gui/tabs crashing visualization functions."""

    def test_draw_network_diagram(self):
        from pmhelper.gui.tabs.crashing_visualization import draw_network_diagram_on_ax
        G = _crashing_network()
        fig, ax = plt.subplots()
        draw_network_diagram_on_ax(ax, G)
        plt.close(fig)
        # Graph should be clean after draw (virtual nodes removed)
        for n in list(G.nodes()):
            assert not n.startswith("_virt_")

    def test_draw_network_diagram_small(self):
        from pmhelper.gui.tabs.crashing_visualization import draw_network_diagram_on_ax_small
        G = _crashing_network()
        fig, ax = plt.subplots()
        draw_network_diagram_on_ax_small(ax, G)
        plt.close(fig)
        for n in list(G.nodes()):
            assert not n.startswith("_virt_")


# ===================================================================
# A6  Crashing visualization integration (core)
# ===================================================================

class TestCrashingCoreIntegration:
    """Smoke-test the core crashing visualization functions."""

    def test_draw_network_diagram(self):
        from pmhelper.core.crashing_visualization import draw_network_diagram_on_ax
        G = _crashing_network()
        fig, ax = plt.subplots()
        draw_network_diagram_on_ax(ax, G)
        plt.close(fig)
        for n in list(G.nodes()):
            assert not n.startswith("_virt_")

    def test_draw_network_diagram_initial(self):
        """initial=True should use a deep copy, leaving G untouched."""
        from pmhelper.core.crashing_visualization import draw_network_diagram_on_ax
        G = _crashing_network()
        nodes_before = set(G.nodes())
        edges_before = set(G.edges())
        fig, ax = plt.subplots()
        draw_network_diagram_on_ax(ax, G, initial=True)
        plt.close(fig)
        assert set(G.nodes()) == nodes_before
        assert set(G.edges()) == edges_before

    def test_draw_network_diagram_small(self):
        from pmhelper.core.crashing_visualization import draw_network_diagram_on_ax_small
        G = _crashing_network()
        fig, ax = plt.subplots()
        draw_network_diagram_on_ax_small(ax, G)
        plt.close(fig)
        for n in list(G.nodes()):
            assert not n.startswith("_virt_")


# ===================================================================
# A7  NetworkTab still works via delegation
# ===================================================================

class TestNetworkTabDelegation:
    """Confirm NetworkTab's layout method still produces correct results."""

    def test_layout_via_network_tab(self):
        from pmhelper.gui.tabs.network_tab import NetworkTab

        class _Harness:
            _virtual_nodes = set()
            _edge_paths = {}
            _all_pos = {}

        h = _Harness()
        G = _complex()
        pos = NetworkTab.create_hierarchical_layout(h, G)
        assert "START" in pos
        assert "END" in pos
        # Long edge should produce virtual nodes
        assert len(h._virtual_nodes) > 0
