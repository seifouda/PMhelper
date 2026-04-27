"""
PMhelper Edu — WBS Validator.
DFS cycle detection, orphan check, depth limit, and structural validation.
"""

from __future__ import annotations
from typing import List, Set

from pmhelper.core.wbs_models_edu import WBSTree


class WBSValidationError:
    """A single validation finding."""

    def __init__(self, level: str, message: str, node_id: str = ""):
        self.level = level          # "ERROR" or "WARNING"
        self.message = message
        self.node_id = node_id

    def __repr__(self):
        return f"[{self.level}] {self.message}"


class WBSValidator:
    """Validate a WBSTree for structural integrity."""

    MAX_DEPTH = 10      # practical cap
    MAX_NODES = 3000    # performance cap

    @classmethod
    def validate(cls, tree: WBSTree) -> List[WBSValidationError]:
        """Run all validations and return list of errors/warnings."""
        errors: List[WBSValidationError] = []
        errors.extend(cls._check_cycles(tree))
        errors.extend(cls._check_orphans(tree))
        errors.extend(cls._check_depth(tree))
        errors.extend(cls._check_node_count(tree))
        errors.extend(cls._check_node_validity(tree))
        errors.extend(cls._check_duplicate_ids(tree))
        errors.extend(cls._check_roots(tree))
        return errors

    @classmethod
    def _check_cycles(cls, tree: WBSTree) -> List[WBSValidationError]:
        """DFS cycle detection."""
        errors = []
        visited: Set[str] = set()

        for node in tree.nodes:
            if node.id in visited:
                continue
            # Walk up from this node to root, checking for cycles
            path: Set[str] = set()
            current = node
            while current:
                if current.id in path:
                    errors.append(
                        WBSValidationError(
                            "ERROR",
                            f"Cycle detected involving node '{
                                current.name}' ({
                                current.id})",
                            current.id,
                        ))
                    break
                path.add(current.id)
                visited.add(current.id)
                if current.parent_id:
                    current = tree.get_node(current.parent_id)
                else:
                    break

        return errors

    @classmethod
    def _check_orphans(cls, tree: WBSTree) -> List[WBSValidationError]:
        """Check for nodes whose parent_id references a non-existent node."""
        errors = []
        node_ids = {n.id for n in tree.nodes}
        for node in tree.nodes:
            if node.parent_id and node.parent_id not in node_ids:
                errors.append(
                    WBSValidationError(
                        "ERROR",
                        f"Orphan node '{
                            node.name}' ({
                            node.id}) — parent '{
                            node.parent_id}' not found.",
                        node.id,
                    ))
        return errors

    @classmethod
    def _check_depth(cls, tree: WBSTree) -> List[WBSValidationError]:
        """Warn if any node exceeds maximum depth."""
        errors = []
        for node in tree.nodes:
            depth = tree.get_depth(node.id)
            if depth > cls.MAX_DEPTH:
                errors.append(
                    WBSValidationError(
                        "WARNING", f"Node '{
                            node.name}' at depth {depth} exceeds recommended max {
                            cls.MAX_DEPTH}.", node.id, ))
        return errors

    @classmethod
    def _check_node_count(cls, tree: WBSTree) -> List[WBSValidationError]:
        """Warn if node count exceeds performance limit."""
        errors = []
        n = tree.node_count()
        if n > cls.MAX_NODES:
            errors.append(
                WBSValidationError(
                    "WARNING",
                    f"WBS has {n} nodes, exceeding the recommended limit of {
                        cls.MAX_NODES}. " f"Performance may degrade.",
                ))
        return errors

    @classmethod
    def _check_node_validity(cls, tree: WBSTree) -> List[WBSValidationError]:
        """Run per-node validations (name, cost, duration, progress)."""
        errors = []
        for node in tree.nodes:
            for msg in node.validate():
                errors.append(WBSValidationError("ERROR", msg, node.id))
        return errors

    @classmethod
    def _check_duplicate_ids(cls, tree: WBSTree) -> List[WBSValidationError]:
        """Check for duplicate node IDs."""
        errors = []
        seen: Set[str] = set()
        for node in tree.nodes:
            if node.id in seen:
                errors.append(WBSValidationError(
                    "ERROR",
                    f"Duplicate node ID '{node.id}' (name '{node.name}').",
                    node.id,
                ))
            seen.add(node.id)
        return errors

    @classmethod
    def _check_roots(cls, tree: WBSTree) -> List[WBSValidationError]:
        """Warn if there are multiple root nodes (usually 1 expected)."""
        errors = []
        roots = tree.get_roots()
        if len(roots) == 0 and tree.node_count() > 0:
            errors.append(WBSValidationError(
                "ERROR",
                "No root nodes found but tree is not empty.",
            ))
        elif len(roots) > 1:
            names = ", ".join(r.name for r in roots[:5])
            errors.append(WBSValidationError(
                "WARNING",
                f"Multiple root nodes found ({len(roots)}): {names}. "
                f"WBS typically has a single root.",
            ))
        return errors
