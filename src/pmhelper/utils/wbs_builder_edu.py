"""
PMhelper Edu — WBS Builder & Aggregator.
CSV import, manual creation helpers, and bottom-up aggregation.
"""

from __future__ import annotations
import csv
import io
from typing import List, Optional, TextIO

from pmhelper.core.wbs_models_edu import WBSTree, WBSNode, WBSStatus


class WBSBuilder:
    """Build / import WBS trees."""

    @staticmethod
    def create_default_tree(project_name: str = "New Project") -> WBSTree:
        """Create a minimal default WBS tree with a single root."""
        tree = WBSTree(project_name=project_name)
        root = WBSNode(
            name=project_name,
            wbs_code="1",
            parent_id="",
            sort_order=0,
        )
        tree.nodes.append(root)
        return tree

    @staticmethod
    def import_csv(
            source: str | TextIO,
            project_name: str = "Imported") -> WBSTree:
        """Import WBS from CSV.

        Expected columns (flexible ordering):
            WBS_Code, Name, Parent_WBS_Code, Duration, Cost, Status, Responsible, Description

        If Parent_WBS_Code is blank, the node is a root.
        If WBS_Code is missing, it will be auto-generated later.

        Returns:
            WBSTree with imported nodes.
        """
        tree = WBSTree(project_name=project_name)

        if isinstance(source, str):
            reader = csv.DictReader(io.StringIO(source))
        else:
            reader = csv.DictReader(source)

        # Normalise column names
        rows = []
        for row in reader:
            norm = {k.strip().lower().replace(" ", "_"): v.strip()
                    for k, v in row.items() if k}
            rows.append(norm)

        if not rows:
            return tree

        # Build map of wbs_code → node_id for parent linking
        code_to_id: dict[str, str] = {}
        nodes_by_code: dict[str, WBSNode] = {}

        for i, row in enumerate(rows):
            wbs_code = row.get("wbs_code", row.get("code", ""))
            name = row.get(
                "name", row.get(
                    "task_name", row.get(
                        "task", f"Task {
                            i + 1}")))
            parent_code = row.get(
                "parent_wbs_code", row.get(
                    "parent_code", row.get(
                        "parent", "")))

            # Parse optional fields
            try:
                duration = float(row.get("duration", 0))
            except (ValueError, TypeError):
                duration = 0.0

            try:
                cost = float(row.get("cost", row.get("budget", 0)))
            except (ValueError, TypeError):
                cost = 0.0

            status_str = row.get("status", "Not Started")
            try:
                status = WBSStatus(status_str)
            except ValueError:
                status = WBSStatus.NOT_STARTED

            responsible = row.get("responsible", row.get("owner", ""))
            description = row.get("description", row.get("desc", ""))

            node = WBSNode(
                wbs_code=wbs_code,
                name=name,
                duration=duration,
                cost=cost,
                status=status,
                responsible=responsible,
                description=description,
                sort_order=i,
            )

            tree.nodes.append(node)
            if wbs_code:
                code_to_id[wbs_code] = node.id
                nodes_by_code[wbs_code] = node

            # Stash parent code for linking pass
            node._temp_parent_code = parent_code  # type: ignore

        # Linking pass: resolve parent codes to IDs
        for node in tree.nodes:
            parent_code = getattr(node, '_temp_parent_code', '')
            if parent_code and parent_code in code_to_id:
                node.parent_id = code_to_id[parent_code]
            # else: remains root (parent_id = "")
            # Clean up temp attribute
            if hasattr(node, '_temp_parent_code'):
                del node._temp_parent_code

        # Regenerate codes if any were missing
        tree.regenerate_codes()

        return tree

    @staticmethod
    def add_child(tree: WBSTree, parent_id: str, name: str = "New Task",
                  **kwargs) -> WBSNode:
        """Add a child node under the given parent."""
        node = WBSNode(
            name=name,
            parent_id=parent_id,
            **kwargs,
        )
        tree.add_node(node)
        tree.regenerate_codes()
        return node

    @staticmethod
    def add_sibling(tree: WBSTree, sibling_id: str, name: str = "New Task",
                    **kwargs) -> Optional[WBSNode]:
        """Add a sibling node after the given node."""
        sibling = tree.get_node(sibling_id)
        if sibling is None:
            return None

        node = WBSNode(
            name=name,
            parent_id=sibling.parent_id,
            **kwargs,
        )
        tree.add_node(node)
        tree.regenerate_codes()
        return node


class WBSAggregator:
    """Bottom-up aggregation for summary (non-leaf) nodes."""

    @staticmethod
    def aggregate(tree: WBSTree) -> None:
        """Aggregate duration, cost, and progress bottom-up.

        Rules:
        - Duration: max(children durations)  — parallel work
        - Cost: sum(children costs)
        - Progress: weighted average by cost
        - Status: derived from children statuses
        """
        # Process in reverse-depth order (leaves first)
        # Build depth map
        depths: dict[str, int] = {}
        for node in tree.nodes:
            depths[node.id] = tree.get_depth(node.id)

        max_depth = max(depths.values()) if depths else 0

        for d in range(max_depth, -1, -1):
            nodes_at_depth = [
                n for n in tree.nodes if depths.get(
                    n.id, 0) == d]
            for node in nodes_at_depth:
                children = tree.get_children(node.id)
                if not children:
                    continue  # leaf — keep manual values

                # Duration → max
                child_durations = [c.duration for c in children]
                node.duration = max(child_durations) if child_durations else 0

                # Cost → sum
                node.cost = sum(c.cost for c in children)

                # Progress → cost-weighted average
                total_cost = sum(c.cost for c in children)
                if total_cost > 0:
                    node.progress = sum(
                        c.progress * c.cost for c in children) / total_cost
                else:
                    # Equal weight if no costs assigned
                    node.progress = sum(
                        c.progress for c in children) / len(children)

                # Status → derived
                node.status = WBSAggregator._derive_status(children)

    @staticmethod
    def _derive_status(children: List[WBSNode]) -> WBSStatus:
        """Derive parent status from children statuses."""
        statuses = {c.status for c in children}

        # All completed → completed
        if statuses == {WBSStatus.COMPLETED}:
            return WBSStatus.COMPLETED

        # All not started → not started
        if statuses == {WBSStatus.NOT_STARTED}:
            return WBSStatus.NOT_STARTED

        # Any delayed → delayed
        if WBSStatus.DELAYED in statuses:
            return WBSStatus.DELAYED

        # Any on hold and none in progress → on hold
        if WBSStatus.ON_HOLD in statuses and WBSStatus.IN_PROGRESS not in statuses:
            return WBSStatus.ON_HOLD

        # Otherwise → in progress
        return WBSStatus.IN_PROGRESS
