"""
PMhelper Edu — Factor Scoring Step Generator (V2 Phase 3B).

Generates worked-solution :class:`~pmhelper.core.step_generators_edu.Step`
trees for :class:`~pmhelper.core.factor_scoring.FactorScoringResult`.

Steps
-----
1. Criteria and weights (weighted model only)
2. Score each project per criterion
3. Compute totals and rank
4. Identify winner and interpret
"""

from __future__ import annotations

from typing import List

from pmhelper.core.step_generators_edu import Step
from pmhelper.core.factor_scoring import FactorScoringResult, FactorScoringEngine


def factor_scoring_steps(result: FactorScoringResult) -> List[Step]:
    """
    Generate step-by-step worked solution for *result*.

    Parameters
    ----------
    result : FactorScoringResult

    Returns
    -------
    list[Step]
    """
    steps: List[Step] = []

    # ── Build sorted project list (keep original ranking order) ─────────
    projects = sorted(result.projects, key=lambda ps: ps.rank)

    # ── Step 1: Model overview & criteria ────────────────────────────────
    if result.model == FactorScoringEngine.MODEL_WEIGHTED:
        steps.append(_weight_step(result))
    else:
        crit_list = ", ".join(c.name for c in result.criteria)
        model_desc = {
            FactorScoringEngine.MODEL_01:     "Binary 0-1 scoring: Yes(1) or No(0) per criterion.",
            FactorScoringEngine.MODEL_FACTOR: "Factor scoring: rate each criterion 1–5 (or custom).",
        }.get(result.model, "")
        steps.append(Step(
            title="Step 1 — Criteria",
            formula="—",
            interpretation=(
                f"Model: {result.model}.  {model_desc}\n"
                f"Criteria ({len(result.criteria)}): {crit_list}"
            ),
        ))

    # ── Step 2: per-project score breakdown ──────────────────────────────
    proj_children: List[Step] = []
    for ps in projects:
        if result.model == FactorScoringEngine.MODEL_WEIGHTED:
            crit_breakdown = "  |  ".join(
                f"{c.name}: {ps.scores[i]:.2f} × {result.criteria[i].weight:.3f} = {ps.weighted_scores[i]:.4f}"
                for i, c in enumerate(result.criteria)
            )
            formula = "score × weight per criterion"
        else:
            crit_breakdown = "  |  ".join(
                f"{c.name}: {ps.scores[i]:.2f}"
                for i, c in enumerate(result.criteria)
            )
            formula = "sum of scores"

        proj_children.append(Step(
            title=f"#{ps.rank}  {ps.project_name}",
            formula=formula,
            substitution=crit_breakdown,
            result=f"Total = {ps.total:.4f}",
            rag="green" if ps.rank == 1 else "",
        ))

    steps.append(Step(
        title="Step 2 — Score each project",
        formula=(
            "Total = Σ (scoreᵢ × weightᵢ)"
            if result.model == FactorScoringEngine.MODEL_WEIGHTED
            else "Total = Σ scoreᵢ"
        ),
        children=proj_children,
    ))

    # ── Step 3: Ranking table ─────────────────────────────────────────────
    rank_children = [
        Step(
            title=f"Rank {ps.rank}: {ps.project_name}",
            result=f"Total score = {ps.total:.4f}",
            rag="green" if ps.rank == 1 else "",
        )
        for ps in projects
    ]
    steps.append(Step(
        title="Step 3 — Rank projects (highest total = Rank 1)",
        formula="Sort descending by total score",
        children=rank_children,
    ))

    # ── Step 4: Conclusion ────────────────────────────────────────────────
    steps.append(Step(
        title="Step 4 — Recommended Project",
        result=f"Winner: {result.winner}",
        interpretation=(
            f"'{result.winner}' scores highest under the {result.model} model "
            f"and should be selected."
        ),
        rag="green",
    ))

    return steps


# ── Helper: weight step ──────────────────────────────────────────────

def _weight_step(result: FactorScoringResult) -> Step:
    raw_total = sum(c.weight for c in result.criteria)
    weight_children = [
        Step(
            title=c.name,
            formula="normalised weight = raw / Σ raw",
            substitution=f"= {c.weight:.4f} / {raw_total:.4f}",
            result=f"= {c.weight / raw_total:.4f}",
        )
        for c in result.criteria
    ]
    return Step(
        title="Step 1 — Criteria Weights (Normalised)",
        formula="Weights must sum to 1.0 for fair comparison",
        interpretation=(
            "Assign a relative importance weight to each criterion. "
            "Higher weight = greater influence on the total score."
        ),
        children=weight_children,
    )
