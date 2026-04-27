"""
PMhelper Edu — Three-Point Estimate Engine (V2 Phase 2).

Computes per-activity and project-level statistics from optimistic (O),
most-likely (M) and pessimistic (P) duration estimates using either the
PERT-Beta formula or the Triangular distribution formula.

Formulas
--------
PERT-Beta:
    tₑ = (O + 4M + P) / 6
    σ² = ((P − O) / 6)²

Triangular:
    tₑ = (O + M + P) / 3
    σ² = (O² + M² + P² − OM − OP − MP) / 18
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional


# ════════════════════════════════════════════════════════════════════
#  Data containers
# ════════════════════════════════════════════════════════════════════

@dataclass
class ActivityEstimate:
    """Three-point estimate result for one activity."""
    activity_id: str
    name: str
    optimistic: float
    most_likely: float
    pessimistic: float
    expected: float       # tₑ
    variance: float       # σ²
    std_dev: float        # σ
    is_critical: bool = False


@dataclass
class ThreePointResult:
    """Full result set for a three-point analysis run."""
    formula: str                               # "PERT" or "Triangular"
    activities: List[ActivityEstimate] = field(default_factory=list)
    project_expected: float = 0.0              # Σ tₑ along critical path
    project_variance: float = 0.0             # Σ σ² along critical path
    project_std_dev: float = 0.0              # √(project_variance)
    critical_path_ids: List[str] = field(default_factory=list)


# ════════════════════════════════════════════════════════════════════
#  Engine
# ════════════════════════════════════════════════════════════════════

class ThreePointEngine:
    """Stateless calculation engine for three-point estimates."""

    PERT = "PERT"
    TRIANGULAR = "Triangular"

    # ── Formula implementations ──────────────────────────────────

    @staticmethod
    def expected_pert(o: float, m: float, p: float) -> float:
        """PERT-Beta expected duration: (O + 4M + P) / 6."""
        return (o + 4.0 * m + p) / 6.0

    @staticmethod
    def expected_triangular(o: float, m: float, p: float) -> float:
        """Triangular expected duration: (O + M + P) / 3."""
        return (o + m + p) / 3.0

    @staticmethod
    def variance_pert(o: float, p: float) -> float:
        """PERT-Beta variance: ((P − O) / 6)²."""
        return ((p - o) / 6.0) ** 2

    @staticmethod
    def variance_triangular(o: float, m: float, p: float) -> float:
        """Triangular variance: (O² + M² + P² − OM − OP − MP) / 18."""
        return (o**2 + m**2 + p**2 - o * m - o * p - m * p) / 18.0

    # ── Main entry point ─────────────────────────────────────────

    @classmethod
    def calculate(
        cls,
        activities: List[dict],
        formula: str = PERT,
        critical_path_ids: Optional[List[str]] = None,
    ) -> ThreePointResult:
        """
        Calculate three-point estimates for a list of activities.

        Parameters
        ----------
        activities : list of dict
            Each dict must have keys:
              * ``id``            — activity identifier (str)
              * ``name`` or ``activity`` — display name (str, optional)
              * ``optimistic``   — optimistic duration (float)
              * ``most_likely``  — most-likely duration (float)
              * ``pessimistic``  — pessimistic duration (float)
            Rows where O/M/P cannot be converted to float are skipped.

        formula : str
            ``"PERT"`` for PERT-Beta or ``"Triangular"`` for Triangular.

        critical_path_ids : list of str, optional
            Activity IDs on the critical path.  Affects:
            * ``is_critical`` flag on each ``ActivityEstimate``,
            * project-level totals (summed over critical path only).
            If *None* or empty the project totals are summed over **all**
            activities (useful for standalone mode with no prior CPM run).

        Returns
        -------
        ThreePointResult
        """
        if formula not in (cls.PERT, cls.TRIANGULAR):
            raise ValueError(
                f"formula must be 'PERT' or 'Triangular', got {
                    formula!r}")

        cp_set = set(critical_path_ids or []) - {"START", "END"}
        estimates: List[ActivityEstimate] = []

        for act in activities:
            aid = str(act.get("id", "")).strip()
            if not aid:
                continue
            name = (act.get("name") or act.get("activity") or aid).strip()

            try:
                o = float(act["optimistic"])
                m = float(act["most_likely"])
                p = float(act["pessimistic"])
            except (KeyError, TypeError, ValueError):
                continue

            if o < 0 or m < 0 or p < 0:
                continue  # non-negative durations only
            if not (o <= m <= p):
                # Coerce: set m to median, warn silently
                vals = sorted([o, m, p])
                o, m, p = vals[0], vals[1], vals[2]

            if formula == cls.PERT:
                exp = cls.expected_pert(o, m, p)
                var = cls.variance_pert(o, p)
            else:
                exp = cls.expected_triangular(o, m, p)
                var = cls.variance_triangular(o, m, p)

            std = math.sqrt(max(var, 0.0))

            estimates.append(ActivityEstimate(
                activity_id=aid,
                name=name,
                optimistic=o,
                most_likely=m,
                pessimistic=p,
                expected=round(exp, 4),
                variance=round(var, 4),
                std_dev=round(std, 4),
                is_critical=(aid in cp_set) if cp_set else False,
            ))

        # Project totals: use critical path if specified, else all activities
        basis = [a for a in estimates if a.is_critical] if cp_set else estimates
        proj_var = sum(a.variance for a in basis)
        proj_std = math.sqrt(max(proj_var, 0.0))
        proj_exp = sum(a.expected for a in basis)

        return ThreePointResult(
            formula=formula,
            activities=estimates,
            project_expected=round(proj_exp, 4),
            project_variance=round(proj_var, 4),
            project_std_dev=round(proj_std, 4),
            critical_path_ids=sorted(cp_set),
        )
