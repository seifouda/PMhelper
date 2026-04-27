"""
PMhelper Edu — WBS Layout Engine.
Walker's algorithm for tidy tree drawing.
Produces (x, y) positions for each node for Canvas or Matplotlib rendering.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

from pmhelper.core.wbs_models_edu import WBSTree


@dataclass
class NodeLayout:
    """Layout information for a single node."""
    node_id: str
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    # Internal Walker fields
    _prelim: float = 0.0
    _modifier: float = 0.0
    _change: float = 0.0
    _shift: float = 0.0
    _thread: str = ""           # node_id of thread
    _ancestor: str = ""         # node_id
    _number: int = 0            # position among siblings (1-based)


class WBSLayoutEngine:
    """Walker's algorithm for tidy tree layout.

    Produces a dict of node_id → (x, y) coordinates.
    Y-axis is depth (top-down), X-axis separates siblings.
    """

    def __init__(
        self,
        node_width: float = 140,
        node_height: float = 50,
        h_gap: float = 20,
        v_gap: float = 60,
    ):
        self.node_width = node_width
        self.node_height = node_height
        self.h_gap = h_gap
        self.v_gap = v_gap
        self._sibling_sep = node_width + h_gap
        self._subtree_sep = node_width + h_gap * 2

        self._layouts: Dict[str, NodeLayout] = {}
        self._tree: Optional[WBSTree] = None

    def compute(self, tree: WBSTree) -> Dict[str, NodeLayout]:
        """Compute layout positions for all nodes in the tree.

        Returns:
            Dict mapping node_id to NodeLayout with x, y coordinates.
        """
        self._tree = tree
        self._layouts = {}

        if tree.node_count() == 0:
            return {}

        # Initialise layouts
        for node in tree.nodes:
            layout = NodeLayout(
                node_id=node.id,
                width=self.node_width,
                height=self.node_height,
            )
            layout._ancestor = node.id
            self._layouts[node.id] = layout

        # Number siblings
        self._number_siblings(tree)

        # Process each root
        roots = tree.get_roots()
        for root in roots:
            self._first_walk(root.id)
            self._second_walk(root.id, -self._layouts[root.id]._prelim, 0)

        # Normalise: shift all positions so minimum x is 0
        if self._layouts:
            min_x = min(l.x for l in self._layouts.values())
            for l in self._layouts.values():
                l.x -= min_x

        return dict(self._layouts)

    def get_bounds(self) -> tuple[float, float, float, float]:
        """Return (min_x, min_y, max_x, max_y) of the layout."""
        if not self._layouts:
            return (0, 0, 0, 0)
        xs = [l.x for l in self._layouts.values()]
        ys = [l.y for l in self._layouts.values()]
        return (
            min(xs),
            min(ys),
            max(xs) + self.node_width,
            max(ys) + self.node_height,
        )

    # ------------------------------------------------------------------
    # Walker's Algorithm
    # ------------------------------------------------------------------

    def _number_siblings(self, tree: WBSTree):
        """Assign _number (1-based position among siblings) to each node."""
        # Number roots
        roots = tree.get_roots()
        for i, r in enumerate(roots):
            self._layouts[r.id]._number = i + 1

        # Number children of each node
        for node in tree.nodes:
            children = tree.get_children(node.id)
            for i, child in enumerate(children):
                self._layouts[child.id]._number = i + 1

    def _first_walk(self, node_id: str):
        """Bottom-up: compute preliminary x-positions."""
        tree = self._tree
        layout = self._layouts[node_id]
        children = tree.get_children(node_id)

        if not children:
            # Leaf node
            node = tree.get_node(node_id)
            siblings = tree.get_children(
                node.parent_id) if node.parent_id else tree.get_roots()
            left_sibling = self._get_left_sibling(node_id, siblings)
            if left_sibling:
                layout._prelim = self._layouts[left_sibling]._prelim + \
                    self._sibling_sep
            else:
                layout._prelim = 0
        else:
            # Internal node
            default_ancestor = children[0].id

            for child in children:
                self._first_walk(child.id)
                default_ancestor = self._apportion(child.id, default_ancestor)

            self._execute_shifts(node_id)

            first_child_layout = self._layouts[children[0].id]
            last_child_layout = self._layouts[children[-1].id]
            midpoint = (first_child_layout._prelim +
                        last_child_layout._prelim) / 2

            node = tree.get_node(node_id)
            siblings = tree.get_children(
                node.parent_id) if node.parent_id else tree.get_roots()
            left_sibling = self._get_left_sibling(node_id, siblings)

            if left_sibling:
                layout._prelim = self._layouts[left_sibling]._prelim + \
                    self._sibling_sep
                layout._modifier = layout._prelim - midpoint
            else:
                layout._prelim = midpoint

    def _second_walk(self, node_id: str, m: float, depth: int):
        """Top-down: compute final x,y positions."""
        layout = self._layouts[node_id]
        layout.x = layout._prelim + m
        layout.y = depth * (self.node_height + self.v_gap)

        children = self._tree.get_children(node_id)
        for child in children:
            self._second_walk(child.id, m + layout._modifier, depth + 1)

    def _apportion(self, node_id: str, default_ancestor: str) -> str:
        """Shift subtrees to avoid overlaps."""
        node = self._tree.get_node(node_id)
        siblings = (self._tree.get_children(node.parent_id)
                    if node.parent_id else self._tree.get_roots())
        left_sibling_id = self._get_left_sibling(node_id, siblings)

        if left_sibling_id is None:
            return default_ancestor

        # Walk contours
        v_inner_right = node_id
        v_outer_right = node_id
        v_inner_left = left_sibling_id
        v_outer_left = siblings[0].id  # leftmost sibling

        sir = self._layouts[v_inner_right]._modifier
        sor = self._layouts[v_outer_right]._modifier
        sil = self._layouts[v_inner_left]._modifier
        sol = self._layouts[v_outer_left]._modifier

        # Walk down the contours
        while (self._next_right(v_inner_left) is not None and
               self._next_left(v_inner_right) is not None):
            v_inner_left = self._next_right(v_inner_left)
            v_inner_right = self._next_left(v_inner_right)
            v_outer_left = self._next_left(v_outer_left)
            v_outer_right = self._next_right(v_outer_right)

            self._layouts[v_outer_right]._ancestor = node_id

            shift = ((self._layouts[v_inner_left]._prelim + sil) -
                     (self._layouts[v_inner_right]._prelim + sir) +
                     self._subtree_sep)

            if shift > 0:
                ancestor = self._find_ancestor(
                    v_inner_left, node_id, default_ancestor)
                self._move_subtree(ancestor, node_id, shift)
                sir += shift
                sor += shift

            sil += self._layouts[v_inner_left]._modifier
            sir += self._layouts[v_inner_right]._modifier
            sol += self._layouts[v_outer_left]._modifier
            sor += self._layouts[v_outer_right]._modifier

        # Set threads
        if (self._next_right(v_inner_left) is not None and
                self._next_right(v_outer_right) is None):
            self._layouts[v_outer_right]._thread = self._next_right(
                v_inner_left)
            self._layouts[v_outer_right]._modifier += sil - sor

        if (self._next_left(v_inner_right) is not None and
                self._next_left(v_outer_left) is None):
            self._layouts[v_outer_left]._thread = self._next_left(
                v_inner_right)
            self._layouts[v_outer_left]._modifier += sir - sol
            default_ancestor = node_id

        return default_ancestor

    def _execute_shifts(self, node_id: str):
        """Execute accumulated shifts for children."""
        children = self._tree.get_children(node_id)
        shift = 0.0
        change = 0.0
        for child in reversed(children):
            cl = self._layouts[child.id]
            cl._prelim += shift
            cl._modifier += shift
            change += cl._change
            shift += cl._shift + change

    def _move_subtree(self, ancestor_id: str, node_id: str, shift: float):
        """Move a subtree by shift amount."""
        anc_layout = self._layouts[ancestor_id]
        node_layout = self._layouts[node_id]
        subtrees = node_layout._number - anc_layout._number
        if subtrees > 0:
            node_layout._change -= shift / subtrees
            node_layout._shift += shift
            anc_layout._change += shift / subtrees
            node_layout._prelim += shift
            node_layout._modifier += shift

    def _find_ancestor(
            self,
            inner_left_id: str,
            node_id: str,
            default: str) -> str:
        """Find the greatest uncommon ancestor."""
        anc_id = self._layouts[inner_left_id]._ancestor
        node = self._tree.get_node(node_id)
        parent = self._tree.get_node(
            node.parent_id) if node.parent_id else None

        if parent:
            parent_children_ids = {
                c.id for c in self._tree.get_children(
                    parent.id)}
            if anc_id in parent_children_ids:
                return anc_id

        return default

    def _next_left(self, node_id: str) -> Optional[str]:
        """Next node on the left contour."""
        children = self._tree.get_children(node_id)
        if children:
            return children[0].id
        return self._layouts[node_id]._thread or None

    def _next_right(self, node_id: str) -> Optional[str]:
        """Next node on the right contour."""
        children = self._tree.get_children(node_id)
        if children:
            return children[-1].id
        return self._layouts[node_id]._thread or None

    def _get_left_sibling(self, node_id: str, siblings: list) -> Optional[str]:
        """Get the left sibling of a node."""
        prev = None
        for s in siblings:
            if s.id == node_id:
                return prev
            prev = s.id
        return None
