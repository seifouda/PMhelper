"""
PMhelper Edu — Factor Scoring Engine (V2 Phase 3B).

Three project-selection scoring models, each ranking N projects against
M evaluation criteria.

Models
------
1. **Unweighted 0-1 Scoring** — each criterion is binary (Yes = 1 / No = 0);
   project with highest count wins.
2. **Unweighted Factor Scoring** — each criterion is scored on a scale
   (default 1–5); total score = sum of scores per project.
3. **Weighted Factor Scoring** — same as (2) but each criterion carries a
   weight; total = Σ (score × weight) per project.  Weights must sum to
   approximately 1.0 (or 100 %).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ════════════════════════════════════════════════════════════════════
#  Data containers
# ════════════════════════════════════════════════════════════════════

@dataclass
class ScoringCriterion:
    """One evaluation criterion."""
    name: str
    weight: float = 1.0   # used only in weighted model; ignored otherwise


@dataclass
class ProjectScore:
    """Result row for one project."""
    project_name: str
    scores: List[float]             # raw score per criterion (in order)
    weighted_scores: List[float]    # score × weight per criterion
    total: float
    rank: int = 0


@dataclass
class FactorScoringResult:
    """Output of one scoring run."""
    model: str                                  # "0-1", "Factor", "Weighted"
    criteria: List[ScoringCriterion]
    projects: List[ProjectScore]                # sorted by rank (1 = best)
    winner: str                                 # name of top-ranked project


# ════════════════════════════════════════════════════════════════════
#  Engine
# ════════════════════════════════════════════════════════════════════

class FactorScoringEngine:
    """Stateless factor scoring calculator."""

    MODEL_01       = "0-1"
    MODEL_FACTOR   = "Factor"
    MODEL_WEIGHTED = "Weighted"

    @classmethod
    def calculate(
        cls,
        criteria: List[ScoringCriterion],
        projects: List[str],
        score_matrix: List[List[float]],
        model: str = MODEL_WEIGHTED,
    ) -> FactorScoringResult:
        """
        Run a factor scoring analysis.

        Parameters
        ----------
        criteria : list of ScoringCriterion
            Ordered list of evaluation criteria.  For the weighted model,
            ``weight`` on each criterion is used.  Weights are normalised
            internally so they don't need to pre-sum to 1.0.
        projects : list of str
            Project names (rows).
        score_matrix : 2-D list  shape = (n_projects × n_criteria)
            Raw scores.  For the 0-1 model only 0 and 1 are valid; any
            value > 0.5 is treated as 1.
        model : str
            One of ``"0-1"``, ``"Factor"``, ``"Weighted"``.

        Returns
        -------
        FactorScoringResult
        """
        if model not in (cls.MODEL_01, cls.MODEL_FACTOR, cls.MODEL_WEIGHTED):
            raise ValueError(
                f"model must be one of '0-1', 'Factor', 'Weighted'; got {model!r}"
            )

        n_crit = len(criteria)
        n_proj = len(projects)

        if n_crit == 0:
            raise ValueError("At least one criterion is required.")
        if n_proj == 0:
            raise ValueError("At least one project is required.")
        if len(score_matrix) != n_proj:
            raise ValueError(
                f"score_matrix has {len(score_matrix)} rows but {n_proj} projects."
            )

        # Normalise weights (weighted model only)
        if model == cls.MODEL_WEIGHTED:
            raw_weights = [c.weight for c in criteria]
            weight_sum = sum(raw_weights)
            if weight_sum <= 0:
                raise ValueError("Criterion weights must sum to a positive value.")
            weights = [w / weight_sum for w in raw_weights]
        else:
            weights = [1.0] * n_crit

        results: List[ProjectScore] = []
        for i, proj_name in enumerate(projects):
            row = score_matrix[i]
            if len(row) != n_crit:
                raise ValueError(
                    f"Project '{proj_name}' has {len(row)} scores "
                    f"but {n_crit} criteria exist."
                )

            if model == cls.MODEL_01:
                raw = [1.0 if v > 0.5 else 0.0 for v in row]
            else:
                raw = [float(v) for v in row]

            if model == cls.MODEL_WEIGHTED:
                weighted = [r * w for r, w in zip(raw, weights)]
                total = sum(weighted)
            else:
                weighted = raw[:]
                total = sum(raw)

            results.append(ProjectScore(
                project_name=proj_name,
                scores=raw,
                weighted_scores=[round(w, 6) for w in weighted],
                total=round(total, 6),
            ))

        # Sort descending by total to assign ranks
        results.sort(key=lambda ps: ps.total, reverse=True)
        for rank, ps in enumerate(results, start=1):
            ps.rank = rank

        winner = results[0].project_name if results else ""

        return FactorScoringResult(
            model=model,
            criteria=criteria,
            projects=results,
            winner=winner,
        )
