"""
PMhelper Edu — Three-Point Estimate Step Generator (V2 Phase 2).

Produces a structured list of :class:`~pmhelper.core.step_generators_edu.Step`
objects that walk through the worked solution for a
:class:`~pmhelper.core.three_point_engine.ThreePointResult`.

Steps produced
--------------
1. Expected Duration (tₑ) per activity  — one child per activity
2. Variance (σ²) per critical-path activity — one child per activity
3. Project Variance  — Σ σ²(critical)
4. Project Standard Deviation — √(σ²_project)
5. Project Expected Duration — Σ tₑ(critical)
"""

from __future__ import annotations

from typing import List

from pmhelper.core.step_generators_edu import Step
from pmhelper.core.three_point_engine import ThreePointResult


def three_point_steps(result: ThreePointResult) -> List[Step]:
    """
    Generate step-by-step worked solution for *result*.

    Parameters
    ----------
    result : ThreePointResult
        Output of :meth:`ThreePointEngine.calculate`.

    Returns
    -------
    list[Step]
    """
    steps: List[Step] = []

    # ── Formula strings ──────────────────────────────────────────
    if result.formula == "PERT":
        te_formula = "tₑ = (O + 4M + P) / 6"
        var_formula = "σ² = ((P − O) / 6)²"
        formula_desc = "PERT-Beta weighted average (double-weights the most-likely estimate)"
    else:
        te_formula = "tₑ = (O + M + P) / 3"
        var_formula = "σ² = (O² + M² + P² − OM − OP − MP) / 18"
        formula_desc = "Triangular distribution simple average"

    activities = result.activities
    cp_activities = [a for a in activities if a.is_critical] or activities

    # ── Step 1: Expected Duration per activity ───────────────────
    te_children: List[Step] = []
    for act in activities:
        label = f"{
            '★ ' if act.is_critical else ''}{
            act.activity_id}: {
            act.name}"
        if result.formula == "PERT":
            sub = (
                f"= ({act.optimistic} + 4×{act.most_likely} + {act.pessimistic}) / 6")
        else:
            sub = f"= ({act.optimistic} + {act.most_likely} + {act.pessimistic}) / 3"

        te_children.append(Step(
            title=label,
            formula=te_formula,
            substitution=sub,
            result=f"tₑ = {act.expected}",
            rag="amber" if act.is_critical else "",
        ))

    steps.append(Step(
        title="Step 1 — Expected Duration (tₑ) per Activity",
        formula=te_formula,
        interpretation=(
            f"{formula_desc}. "
            "★ marks critical-path activities whose tₑ flows directly into "
            "the project expected duration."
        ),
        children=te_children,
    ))

    # ── Step 2: Variance per critical-path activity ───────────────
    var_children: List[Step] = []
    for act in cp_activities:
        o, m, p = act.optimistic, act.most_likely, act.pessimistic
        if result.formula == "PERT":
            sub = f"= (({p} − {o}) / 6)²"
        else:
            sub = (
                f"= ({o}² + {m}² + {p}² − {o}×{m} − {o}×{p} − {m}×{p}) / 18"
            )
        var_children.append(Step(
            title=f"{act.activity_id}: {act.name}",
            formula=var_formula,
            substitution=sub,
            result=f"σ² = {act.variance}",
        ))

    steps.append(Step(
        title="Step 2 — Variance (σ²) per Critical-Path Activity",
        formula=var_formula,
        interpretation=(
            "Only critical-path activities contribute to project-level uncertainty. "
            "A large σ² signals a risky activity whose duration is hard to predict."
        ),
        children=var_children,
    ))

    # ── Step 3: Project Variance ──────────────────────────────────
    cp_var_vals = [str(a.variance) for a in cp_activities]
    sub_str = " + ".join(cp_var_vals) if cp_var_vals else "0"
    steps.append(Step(
        title="Step 3 — Project Variance (σ²_project)",
        formula="σ²_project = Σ σ²(critical-path activities)",
        substitution=f"= {sub_str}",
        result=f"= {result.project_variance}",
        interpretation=(
            "Project variance is the sum of variances along the critical path. "
            "Parallel non-critical activities do not add uncertainty to project duration."
        ),
    ))

    # ── Step 4: Project Standard Deviation ───────────────────────
    steps.append(Step(
        title="Step 4 — Project Standard Deviation (σ)",
        formula="σ = √(σ²_project)",
        substitution=f"= √({result.project_variance})",
        result=f"= {result.project_std_dev}",
        interpretation=(
            "Standard deviation in the same units as duration. "
            "Rule of thumb: the project will finish within ±1σ of the expected "
            "duration about 68% of the time, and within ±2σ about 95% of the time."
        ),
    ))

    # ── Step 5: Project Expected Duration ────────────────────────
    cp_te_vals = [str(a.expected) for a in cp_activities]
    te_sub = " + ".join(cp_te_vals) if cp_te_vals else "0"
    steps.append(
        Step(
            title="Step 5 — Project Expected Duration",
            formula="T_project = Σ tₑ(critical-path activities)",
            substitution=f"= {te_sub}",
            result=f"= {
                result.project_expected}",
            interpretation=(
                "The project's expected completion time, based on the sum of expected "
                "durations along the critical path."),
            rag="green" if result.project_std_dev < result.project_expected *
            0.1 else "amber",
        ))

    return steps
