"""
PMhelper Edu — WBS (Work Breakdown Structure) data model.
PG-only. Pure data classes, no Tkinter dependency.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict
import uuid


class WBSStatus(Enum):
    """Five-state status for WBS tasks."""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED   = "Completed"
    DELAYED     = "Delayed"
    ON_HOLD     = "On Hold"


# Colours for rendering each status
WBS_STATUS_COLOURS: Dict[WBSStatus, str] = {
    WBSStatus.NOT_STARTED: "#e0e0e0",   # grey
    WBSStatus.IN_PROGRESS: "#cce5ff",   # blue
    WBSStatus.COMPLETED:   "#d4edda",   # green
    WBSStatus.DELAYED:     "#f8d7da",   # red
    WBSStatus.ON_HOLD:     "#fff3cd",   # amber
}


@dataclass
class WBSNode:
    """A single node in the WBS tree."""
    id: str = ""
    wbs_code: str = ""              # e.g. "1.2.3"
    name: str = ""
    parent_id: str = ""             # empty string = root
    duration: float = 0.0           # days (leaf: manual, summary: max of children)
    cost: float = 0.0               # $ (leaf: manual, summary: sum of children)
    progress: float = 0.0           # 0-100% (leaf: manual, summary: weighted avg by cost)
    status: WBSStatus = WBSStatus.NOT_STARTED
    responsible: str = ""
    description: str = ""
    linked_task_id: str = ""        # optional link to CPM/EVM task
    sort_order: int = 0             # for ordering siblings

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]

    @property
    def is_root(self) -> bool:
        return self.parent_id == ""

    def validate(self) -> List[str]:
        errors = []
        if not self.name.strip():
            errors.append(f"WBS node '{self.wbs_code}': Name is required.")
        if self.duration < 0:
            errors.append(f"WBS node '{self.wbs_code}': Duration cannot be negative.")
        if self.cost < 0:
            errors.append(f"WBS node '{self.wbs_code}': Cost cannot be negative.")
        if not 0 <= self.progress <= 100:
            errors.append(f"WBS node '{self.wbs_code}': Progress must be 0-100%.")
        return errors

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "wbs_code": self.wbs_code,
            "name": self.name,
            "parent_id": self.parent_id,
            "duration": self.duration,
            "cost": self.cost,
            "progress": self.progress,
            "status": self.status.value,
            "responsible": self.responsible,
            "description": self.description,
            "linked_task_id": self.linked_task_id,
            "sort_order": self.sort_order,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WBSNode":
        return cls(
            id=d.get("id", ""),
            wbs_code=d.get("wbs_code", ""),
            name=d.get("name", ""),
            parent_id=d.get("parent_id", ""),
            duration=float(d.get("duration", 0)),
            cost=float(d.get("cost", 0)),
            progress=float(d.get("progress", 0)),
            status=WBSStatus(d.get("status", "Not Started")),
            responsible=d.get("responsible", ""),
            description=d.get("description", ""),
            linked_task_id=d.get("linked_task_id", ""),
            sort_order=int(d.get("sort_order", 0)),
        )


@dataclass
class WBSTree:
    """
    WBS Tree — flat list of nodes with parent_id links.
    Children are computed from parent_id, never stored explicitly.
    """
    nodes: List[WBSNode] = field(default_factory=list)
    project_name: str = "Untitled Project"
    _undo_stack: List[List[dict]] = field(default_factory=list, repr=False)
    _redo_stack: List[List[dict]] = field(default_factory=list, repr=False)
    _max_undo: int = field(default=20, repr=False)

    # ------------------------------------------------------------------
    # Node lookup
    # ------------------------------------------------------------------

    def get_node(self, node_id: str) -> Optional[WBSNode]:
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def get_children(self, parent_id: str) -> List[WBSNode]:
        """Get direct children of a node, sorted by sort_order."""
        children = [n for n in self.nodes if n.parent_id == parent_id]
        return sorted(children, key=lambda n: n.sort_order)

    def get_roots(self) -> List[WBSNode]:
        """Get top-level nodes (no parent)."""
        return self.get_children("")

    def is_leaf(self, node_id: str) -> bool:
        return len(self.get_children(node_id)) == 0

    def get_depth(self, node_id: str) -> int:
        """Return depth of a node (0 = root)."""
        depth = 0
        current = self.get_node(node_id)
        while current and current.parent_id:
            depth += 1
            current = self.get_node(current.parent_id)
            if depth > 100:  # safety
                break
        return depth

    def get_ancestors(self, node_id: str) -> List[WBSNode]:
        """Get all ancestors from parent up to root."""
        ancestors = []
        current = self.get_node(node_id)
        visited = set()
        while current and current.parent_id and current.parent_id not in visited:
            visited.add(current.parent_id)
            parent = self.get_node(current.parent_id)
            if parent:
                ancestors.append(parent)
                current = parent
            else:
                break
        return ancestors

    def get_descendants(self, node_id: str) -> List[WBSNode]:
        """Get all descendants (DFS)."""
        result = []
        stack = list(self.get_children(node_id))
        visited = set()
        while stack:
            node = stack.pop()
            if node.id in visited:
                continue
            visited.add(node.id)
            result.append(node)
            stack.extend(self.get_children(node.id))
        return result

    def node_count(self) -> int:
        return len(self.nodes)

    # ------------------------------------------------------------------
    # CRUD with undo
    # ------------------------------------------------------------------

    def _save_undo(self):
        """Save current state to undo stack."""
        snapshot = [n.to_dict() for n in self.nodes]
        self._undo_stack.append(snapshot)
        if len(self._undo_stack) > self._max_undo:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        # Save current to redo
        self._redo_stack.append([n.to_dict() for n in self.nodes])
        snapshot = self._undo_stack.pop()
        self.nodes = [WBSNode.from_dict(d) for d in snapshot]
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        self._undo_stack.append([n.to_dict() for n in self.nodes])
        snapshot = self._redo_stack.pop()
        self.nodes = [WBSNode.from_dict(d) for d in snapshot]
        return True

    def add_node(self, node: WBSNode) -> None:
        """Add a node to the tree."""
        self._save_undo()
        # auto-assign sort_order
        siblings = self.get_children(node.parent_id)
        if siblings:
            node.sort_order = max(s.sort_order for s in siblings) + 1
        self.nodes.append(node)

    def delete_node(self, node_id: str, cascade: bool = True) -> List[WBSNode]:
        """Delete a node.

        Args:
            cascade: if True, delete all descendants.
                     if False, promote children to deleted node's parent.

        Returns:
            List of deleted nodes.
        """
        node = self.get_node(node_id)
        if node is None:
            return []

        self._save_undo()
        deleted = [node]

        if cascade:
            descendants = self.get_descendants(node_id)
            deleted.extend(descendants)
            delete_ids = {n.id for n in deleted}
            self.nodes = [n for n in self.nodes if n.id not in delete_ids]
        else:
            # Promote children to parent
            children = self.get_children(node_id)
            for child in children:
                child.parent_id = node.parent_id
            self.nodes = [n for n in self.nodes if n.id != node_id]

        return deleted

    def reparent_node(self, node_id: str, new_parent_id: str) -> bool:
        """Move a node under a new parent.

        Returns False if the move would create a cycle.
        """
        node = self.get_node(node_id)
        if node is None:
            return False

        # Prevent cycle: new_parent cannot be a descendant of node
        if new_parent_id:
            desc_ids = {d.id for d in self.get_descendants(node_id)}
            if new_parent_id in desc_ids or new_parent_id == node_id:
                return False

        self._save_undo()
        node.parent_id = new_parent_id
        # Re-assign sort order in new parent
        siblings = self.get_children(new_parent_id)
        node.sort_order = max((s.sort_order for s in siblings if s.id != node.id), default=-1) + 1
        return True

    # ------------------------------------------------------------------
    # WBS Code generation
    # ------------------------------------------------------------------

    def regenerate_codes(self):
        """Regenerate WBS codes for all nodes based on tree structure."""
        def _assign(parent_id: str, prefix: str):
            children = self.get_children(parent_id)
            for i, child in enumerate(children, 1):
                child.wbs_code = f"{prefix}{i}" if prefix else str(i)
                _assign(child.id, child.wbs_code + ".")

        _assign("", "")

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "nodes": [n.to_dict() for n in self.nodes],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WBSTree":
        nodes = [WBSNode.from_dict(nd) for nd in d.get("nodes", [])]
        return cls(
            nodes=nodes,
            project_name=d.get("project_name", "Untitled Project"),
        )
