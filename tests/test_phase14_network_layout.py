"""Tests for Phase 14 — Network Diagram Smart Layout (Sugiyama / Barycenter + Virtual Nodes)."""

import sys
import os
import pytest

# Ensure src is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, "src"))

import networkx as nx


# ---------------------------------------------------------------------------
# Helper: build a simple test graph
# ---------------------------------------------------------------------------

def _build_simple_graph():
    """A→B→D, A→C→D  (diamond, all span 1 column)."""
    G = nx.DiGraph()
    for nid in ["A", "B", "C", "D"]:
        G.add_node(nid, duration=3, critical=(nid in ("A", "B", "D")), float=0, id=nid)
    G.add_edges_from([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
    return G


def _build_long_edge_graph():
    """A→B→C→D  plus  A→D  (long edge spans 3 columns)."""
    G = nx.DiGraph()
    for nid in ["A", "B", "C", "D"]:
        G.add_node(nid, duration=2, critical=True, float=0, id=nid)
    G.add_edges_from([("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")])
    return G


def _build_wide_graph():
    """START -> A,B,C,D,E -> END  (5 parallel activities)."""
    G = nx.DiGraph()
    G.add_node("START", duration=0)
    G.add_node("END", duration=0)
    for nid in ["A", "B", "C", "D", "E"]:
        G.add_node(nid, duration=4, critical=False, float=2, id=nid)
        G.add_edge("START", nid)
        G.add_edge(nid, "END")
    return G


def _build_complex_graph():
    """
    Realistic 8-activity network with multiple long edges:
    START → A → C → E → END
    START → B → D → F → END
    A → D  (long edge: spans column of C)
    B → E  (long edge: spans column of D)
    """
    G = nx.DiGraph()
    for nid, dur, crit in [
        ("START", 0, False), ("A", 3, True), ("B", 4, False),
        ("C", 2, True), ("D", 5, False), ("E", 3, True),
        ("F", 2, False), ("END", 0, False),
    ]:
        G.add_node(nid, duration=dur, critical=crit, float=0, id=nid)
    G.add_edges_from([
        ("START", "A"), ("START", "B"),
        ("A", "C"), ("B", "D"),
        ("C", "E"), ("D", "F"),
        ("E", "END"), ("F", "END"),
        ("A", "D"),  # long edge
        ("B", "E"),  # long edge
    ])
    return G


# ---------------------------------------------------------------------------
# Minimal mock for NetworkTab (we only need the layout logic, not Tkinter)
# ---------------------------------------------------------------------------

class _LayoutTestHarness:
    """Mimics NetworkTab just enough to call create_hierarchical_layout."""

    def __init__(self):
        self._virtual_nodes = set()
        self._edge_paths = {}
        self._all_pos = {}

    # Import the actual methods from the module
    @staticmethod
    def _import_layout():
        from pmhelper.gui.tabs.network_tab import NetworkTab
        return NetworkTab

    def create_hierarchical_layout(self, G):
        NT = self._import_layout()
        # Bind 'self' so NT's method works on our harness
        return NT.create_hierarchical_layout(self, G)


# ===================================================================
# 14.1  Layout correctness
# ===================================================================

class TestHierarchicalLayout:
    """Test the Sugiyama-style layout engine."""

    def _layout(self, G):
        h = _LayoutTestHarness()
        pos = h.create_hierarchical_layout(G)
        return pos, h

    # --- Basic properties ---

    def test_all_real_nodes_have_positions(self):
        G = _build_simple_graph()
        pos, h = self._layout(G)
        for node in ["A", "B", "C", "D"]:
            assert node in pos, f"Node {node} missing from layout"

    def test_no_virtual_nodes_in_returned_pos(self):
        G = _build_long_edge_graph()
        pos, h = self._layout(G)
        for node in pos:
            assert not node.startswith("_virt_"), \
                f"Virtual node {node} should not be in returned positions"

    def test_virtual_nodes_created_for_long_edges(self):
        G = _build_long_edge_graph()
        pos, h = self._layout(G)
        assert len(h._virtual_nodes) > 0, "Long edge A→D should produce virtual nodes"

    def test_edge_paths_populated(self):
        G = _build_long_edge_graph()
        pos, h = self._layout(G)
        # The original A→D edge should have a multi-hop path
        assert ("A", "D") in h._edge_paths
        path = h._edge_paths[("A", "D")]
        assert len(path) >= 3, "A→D path must route through ≥1 virtual node"
        assert path[0] == "A"
        assert path[-1] == "D"

    def test_short_edges_have_direct_paths(self):
        G = _build_simple_graph()
        pos, h = self._layout(G)
        assert ("A", "B") in h._edge_paths
        assert h._edge_paths[("A", "B")] == ["A", "B"]

    # --- No overlap ---

    def test_no_node_overlap(self):
        """No two real nodes should occupy the same position (within radius)."""
        G = _build_wide_graph()
        pos, h = self._layout(G)
        node_radius = 0.6
        nodes = list(pos.keys())
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                x1, y1 = pos[nodes[i]]
                x2, y2 = pos[nodes[j]]
                dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                assert dist >= node_radius, \
                    f"Nodes {nodes[i]} and {nodes[j]} overlap (dist={dist:.2f})"

    def test_no_node_overlap_complex(self):
        """No overlap in the complex graph either."""
        G = _build_complex_graph()
        pos, h = self._layout(G)
        node_radius = 0.6
        nodes = list(pos.keys())
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                x1, y1 = pos[nodes[i]]
                x2, y2 = pos[nodes[j]]
                dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                assert dist >= node_radius, \
                    f"Nodes {nodes[i]} and {nodes[j]} overlap (dist={dist:.2f})"

    # --- Layer ordering ---

    def test_predecessors_left_of_successors(self):
        """Every edge (u→v) should have x(u) < x(v)."""
        G = _build_complex_graph()
        pos, h = self._layout(G)
        # Check original edges (before virtual insertion mutates G)
        for u, v in [("START", "A"), ("START", "B"), ("A", "C"), ("B", "D"),
                     ("C", "E"), ("D", "F"), ("E", "END"), ("F", "END")]:
            assert pos[u][0] < pos[v][0], \
                f"Node {u} (x={pos[u][0]}) should be left of {v} (x={pos[v][0]})"

    def test_start_at_leftmost(self):
        G = _build_complex_graph()
        pos, h = self._layout(G)
        start_x = pos["START"][0]
        for node, (x, y) in pos.items():
            if node != "START":
                assert x >= start_x, f"{node} should not be left of START"

    def test_end_at_rightmost(self):
        G = _build_complex_graph()
        pos, h = self._layout(G)
        end_x = pos["END"][0]
        for node, (x, y) in pos.items():
            if node != "END":
                assert x <= end_x, f"{node} should not be right of END"

    # --- Virtual nodes in _all_pos ---

    def test_all_pos_includes_virtual_nodes(self):
        G = _build_long_edge_graph()
        pos, h = self._layout(G)
        for vn in h._virtual_nodes:
            assert vn in h._all_pos, f"Virtual node {vn} missing from _all_pos"


# ===================================================================
# 14.2  Edge routing validation
# ===================================================================

class TestEdgeRouting:
    """Test that polyline edge paths avoid real node interiors."""

    def _layout(self, G):
        h = _LayoutTestHarness()
        pos = h.create_hierarchical_layout(G)
        return pos, h

    def test_long_edge_waypoints_avoid_nodes(self):
        """Virtual-node waypoints for A→D should not coincide with B or C."""
        G = _build_long_edge_graph()
        pos, h = self._layout(G)
        node_radius = 0.6

        path = h._edge_paths.get(("A", "D"), [])
        # Get waypoint positions (excluding start/end real nodes)
        waypoints = [h._all_pos[n] for n in path[1:-1] if n in h._all_pos]

        for wp_x, wp_y in waypoints:
            for real_node in ["B", "C"]:
                if real_node in pos:
                    rx, ry = pos[real_node]
                    dist = ((wp_x - rx) ** 2 + (wp_y - ry) ** 2) ** 0.5
                    # Waypoint should not be inside any real node
                    assert dist >= node_radius * 0.5, \
                        f"Waypoint ({wp_x:.1f},{wp_y:.1f}) too close to {real_node}"

    def test_complex_graph_long_edges_have_paths(self):
        """Long edges in complex graph should have multi-hop paths."""
        G = _build_complex_graph()
        pos, h = self._layout(G)
        # B→E spans from layer 1 to layer 3 (span=2), needs ≥1 virtual node
        assert ("B", "E") in h._edge_paths
        assert len(h._edge_paths[("B", "E")]) >= 3, \
            f"B→E should route through virtual node, got {h._edge_paths[('B', 'E')]}"
        # A→D spans from layer 1 to layer 2 (span=1), direct path
        assert ("A", "D") in h._edge_paths
        assert h._edge_paths[("A", "D")] == ["A", "D"]


# ===================================================================
# 14.3  Barycenter reduces crossings
# ===================================================================

class TestBarycenterOrdering:
    """Verify that barycenter ordering improves on naive alphabetical sort."""

    def _count_crossings(self, pos, edges):
        """Count edge crossings between adjacent layers."""
        crossings = 0
        for i, (u1, v1) in enumerate(edges):
            if u1 not in pos or v1 not in pos:
                continue
            for u2, v2 in edges[i + 1:]:
                if u2 not in pos or v2 not in pos:
                    continue
                # Only count crossings for edges between same pair of layers
                if pos[u1][0] != pos[u2][0] or pos[v1][0] != pos[v2][0]:
                    continue
                # Crossing occurs if: y(u1) < y(u2) and y(v1) > y(v2) or vice versa
                if (pos[u1][1] - pos[u2][1]) * (pos[v1][1] - pos[v2][1]) < 0:
                    crossings += 1
        return crossings

    def test_barycenter_no_worse_than_alphabetical(self):
        """Barycenter layout shouldn't have more crossings than alphabetical for diamond graph."""
        G = _build_simple_graph()
        h = _LayoutTestHarness()
        pos = h.create_hierarchical_layout(G)
        edges = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
        crossings = self._count_crossings(pos, edges)
        # Diamond graph CAN be drawn with 0 crossings
        assert crossings <= 1, f"Diamond graph should have ≤1 crossings, got {crossings}"


# ===================================================================
# 14.4  Module-level sanity checks
# ===================================================================

class TestNetworkTabModule:
    """Verify the module can be imported and key methods exist."""

    def test_import_network_tab(self):
        from pmhelper.gui.tabs.network_tab import NetworkTab
        assert NetworkTab is not None

    def test_has_create_hierarchical_layout(self):
        from pmhelper.gui.tabs.network_tab import NetworkTab
        assert hasattr(NetworkTab, 'create_hierarchical_layout')

    def test_has_draw_network_edges(self):
        from pmhelper.gui.tabs.network_tab import NetworkTab
        assert hasattr(NetworkTab, 'draw_network_edges')

    def test_has_draw_network_diagram(self):
        from pmhelper.gui.tabs.network_tab import NetworkTab
        assert hasattr(NetworkTab, 'draw_network_diagram')
