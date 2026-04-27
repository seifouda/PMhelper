"""
PMhelper Edu — RACI Matrix Data Model (V2 Phase 4).

Two matrix types are supported:

1. **Task × Role** — Project activities (rows) vs team roles/people (cols).
2. **Deliverables × Department** — WBS deliverables (rows) vs org depts (cols).

Cell values: ``"R"``, ``"A"``, ``"C"``, ``"I"``, or ``""`` (unassigned).

PM Rules enforced by :meth:`RACIMatrix.validate`
-------------------------------------------------
* Each row must have **exactly one A** (Accountable).
* Each row must have **at least one R** (Responsible).
* Each column should have at least one assignment (warn if fully empty).

Persistence
-----------
:meth:`RACIMatrix.to_dict` / :meth:`RACIMatrix.from_dict` produce plain JSON-
serialisable dicts for storage in ``.pmproj`` project files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ════════════════════════════════════════════════════════════════════
#  Constants
# ════════════════════════════════════════════════════════════════════

VALID_VALUES = frozenset({"R", "A", "C", "I", ""})

#: Colours suitable for Tkinter ``bg=`` / ``background`` config
CELL_COLORS: Dict[str, str] = {
    "R": "#bfdbfe",   # light blue
    "A": "#fecaca",   # light red
    "C": "#fef08a",   # light yellow
    "I": "#bbf7d0",   # light green
    "": "#f3f4f6",   # light grey (unassigned)
}

#: Human-readable descriptions for tooltip / educational text
ROLE_DESCRIPTIONS: Dict[str, str] = {
    "R": "Responsible — does the work",
    "A": "Accountable — owns the outcome (one per activity)",
    "C": "Consulted — provides input (two-way communication)",
    "I": "Informed — kept in the loop (one-way communication)",
    "": "Not assigned",
}


# ════════════════════════════════════════════════════════════════════
#  Validation result
# ════════════════════════════════════════════════════════════════════

@dataclass
class ValidationIssue:
    """One validation warning or error."""
    level: str          # "error" or "warning"
    row: Optional[int]  # None = cross-row issue
    col: Optional[int]
    message: str


# ════════════════════════════════════════════════════════════════════
#  RACI Matrix
# ════════════════════════════════════════════════════════════════════

@dataclass
class RACIMatrix:
    """
    Rectangular matrix of RACI cell values.

    Parameters
    ----------
    rows : list of str
        Row labels (activity names / deliverable names).
    cols : list of str
        Column labels (role names / department names).
    cells : dict, optional
        Mapping ``"<row_idx>,<col_idx>"`` → value.
        Missing keys default to ``""``.
    """

    rows: List[str] = field(default_factory=list)
    cols: List[str] = field(default_factory=list)
    #: Serialisable cell storage: string key "row,col" → value
    cells: Dict[str, str] = field(default_factory=dict)

    # ── Cell access ─────────────────────────────────────────────

    @staticmethod
    def _key(row_idx: int, col_idx: int) -> str:
        return f"{row_idx},{col_idx}"

    def get_cell(self, row_idx: int, col_idx: int) -> str:
        """Return cell value or ``""`` if unset."""
        return self.cells.get(self._key(row_idx, col_idx), "")

    def set_cell(self, row_idx: int, col_idx: int, value: str) -> None:
        """
        Set a cell.  Empty string clears the cell.

        Raises
        ------
        ValueError
            If *value* is not in ``VALID_VALUES``.
        """
        if value not in VALID_VALUES:
            raise ValueError(
                f"Invalid RACI value {value!r}. "
                f"Must be one of {sorted(VALID_VALUES)!r}."
            )
        key = self._key(row_idx, col_idx)
        if value == "":
            self.cells.pop(key, None)
        else:
            self.cells[key] = value

    def get_row(self, row_idx: int) -> List[str]:
        """Return a list of all cell values for *row_idx*."""
        return [self.get_cell(row_idx, c) for c in range(len(self.cols))]

    def get_col(self, col_idx: int) -> List[str]:
        """Return a list of all cell values for *col_idx*."""
        return [self.get_cell(r, col_idx) for r in range(len(self.rows))]

    # ── Statistics ───────────────────────────────────────────────

    def count_by_type(self) -> Dict[str, int]:
        """Return total count of each RACI assignment type."""
        counts: Dict[str, int] = {"R": 0, "A": 0, "C": 0, "I": 0, "": 0}
        for r in range(len(self.rows)):
            for c in range(len(self.cols)):
                v = self.get_cell(r, c)
                counts[v] = counts.get(v, 0) + 1
        return counts

    # ── Validation ───────────────────────────────────────────────

    def validate(self) -> List[ValidationIssue]:
        """
        Check PM rules and return a list of :class:`ValidationIssue` items.

        Rules
        -----
        * E1 — Each row must have exactly one **A**.
        * E2 — Each row must have at least one **R**.
        * W1 — Each column should have at least one assignment.
        """
        issues: List[ValidationIssue] = []

        for r_idx, row_name in enumerate(self.rows):
            row = self.get_row(r_idx)
            a_count = row.count("A")
            r_count = row.count("R")

            if a_count == 0:
                issues.append(ValidationIssue(
                    level="error", row=r_idx, col=None,
                    message=f"'{row_name}' has no Accountable (A). "
                    f"Every activity must have exactly one A.",
                ))
            elif a_count > 1:
                issues.append(ValidationIssue(
                    level="error", row=r_idx, col=None,
                    message=f"'{row_name}' has {a_count} Accountable (A) "
                    f"assignments. Only one A is allowed per activity.",
                ))

            if r_count == 0:
                issues.append(ValidationIssue(
                    level="error", row=r_idx, col=None,
                    message=f"'{row_name}' has no Responsible (R). "
                    f"At least one person must be responsible.",
                ))

        for c_idx, col_name in enumerate(self.cols):
            col = self.get_col(c_idx)
            if all(v == "" for v in col):
                issues.append(ValidationIssue(
                    level="warning", row=None, col=c_idx,
                    message=f"Role/column '{col_name}' has no assignments. "
                    f"Consider whether this role is needed.",
                ))

        return issues

    @property
    def is_valid(self) -> bool:
        """True if there are no error-level issues."""
        return not any(i.level == "error" for i in self.validate())

    # ── Persistence ──────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialise to a plain dict (JSON-safe)."""
        return {
            "rows": list(self.rows),
            "cols": list(self.cols),
            "cells": dict(self.cells),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RACIMatrix":
        """Reconstruct from a dict produced by :meth:`to_dict`."""
        return cls(
            rows=data.get("rows", []),
            cols=data.get("cols", []),
            cells=data.get("cells", {}),
        )

    # ── Convenience constructors ─────────────────────────────────

    @classmethod
    def empty(cls,
              rows: Optional[List[str]] = None,
              cols: Optional[List[str]] = None) -> "RACIMatrix":
        """Return a blank matrix with given row/col labels."""
        return cls(rows=rows or [], cols=cols or [])

    # ── Utility ─────────────────────────────────────────────────

    def summary_text(self) -> str:
        """One-line text summary: total assignments per type."""
        c = self.count_by_type()
        parts = [f"{k}={c[k]}" for k in ("R", "A", "C", "I") if c[k] > 0]
        return "  ".join(parts) if parts else "No assignments"
