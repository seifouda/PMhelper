"""
PMhelper Edu — Resource Leveling Step Generator (V2 Phase 8).

Produces educational :class:`~pmhelper.core.step_generators_edu.Step` trees
that walk students through resource leveling and smoothing algorithms.

Entry points
------------
Each function returns ``List[Step]`` suitable for a :class:`WorkedSolutionWindow`.

* ``leveling_concepts_steps()``  — pure theory, no result needed
* ``float_analysis_steps(activities, schedule)`` — which activities can be shifted
* ``minimum_moment_algorithm_steps(result)`` — MM walk-through from recorded steps
* ``burgess_algorithm_steps(result)`` — Burgess walk-through from recorded steps
* ``before_after_comparison_steps(result)`` — before/after metric comparison
"""

from __future__ import annotations

from typing import Any, Dict, List

from pmhelper.core.step_generators_edu import Step


# ════════════════════════════════════════════════════════════════════
#  Theory (no calculation needed)
# ════════════════════════════════════════════════════════════════════

def leveling_concepts_steps() -> List[Step]:
    """Educational overview of resource leveling concepts."""
    steps: List[Step] = []

    steps.append(
        Step(
            title="Step 1 — What is Resource Leveling?",
            formula="Peak Usage ↓    Duration may ↑",
            interpretation=(
                "Resource leveling rearranges activity start times to reduce resource "
                "peaks and valleys. Activities are shifted within their float without "
                "extending the project unless necessary (constrained mode).\n\n"
                "Two modes:\n"
                "  • Smoothing — only shifts within float; never extends project\n"
                "  • Constrained — may extend duration to honour resource limits"),
        ))

    steps.append(Step(
        title="Step 2 — Float and Scheduling Flexibility",
        formula="Float = LS − ES = LF − EF",
        interpretation=(
            "Total Float is the amount of time an activity can be delayed without "
            "delaying the project end date. Activities with Float = 0 are on the "
            "critical path and cannot be moved without extending the project.\n\n"
            "Resource leveling only moves non-critical activities (Float > 0)."
        ),
        children=[
            Step(
                title="Free Float",
                formula="FF = min(ES of successors) − EF",
                interpretation=(
                    "Free Float is the slack before the earliest successor starts. "
                    "Shifting within free float doesn't affect any successor."
                ),
            ),
        ],
    ))

    steps.append(
        Step(
            title="Step 3 — Resource Profile",
            formula="r(t) = Σ resource_demand(i)  for all active activities i at period t",
            interpretation=(
                "The resource profile sums all demands at each time period. "
                "The goal of leveling is to flatten this profile — reducing spikes "
                "and filling troughs."),
        ))

    steps.append(
        Step(
            title="Step 4 — Smoothing vs Constrained Scheduling",
            formula="Smoothing: shift within float  |  Constrained: enforce resource_limit ≤ R_max",
            interpretation=(
                "Resource Smoothing (Mode: Smoothing):\n"
                "  – Shifts activities within their available float.\n"
                "  – Project duration is preserved.\n"
                "  – Metric minimised: Moment (Min-Moment) or Sum-of-Squares (Burgess).\n\n"
                "Resource-Constrained Scheduling (Mode: Constrained):\n"
                "  – Hard upper limit on resource usage per period.\n"
                "  – Activities that exceed the limit are delayed even beyond their float.\n"
                "  – Project duration may extend."),
        ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  Float Analysis
# ════════════════════════════════════════════════════════════════════

def float_analysis_steps(
        activities: List[Any], schedule: Dict[str, int]) -> List[Step]:
    """Show which activities have scheduling flexibility."""
    steps: List[Step] = []

    critical = [a for a in activities if getattr(a, "float", 0) == 0]
    non_critical = [a for a in activities if getattr(a, "float", 0) > 0]

    steps.append(Step(
        title="Step 1 — Identify the Critical Path",
        formula="Critical path = sequence of activities with Float = 0",
        interpretation=(
            f"Critical activities (Float = 0): "
            f"{', '.join(a.id for a in critical) or 'none'}\n\n"
            f"These activities cannot be moved without extending the project. "
            f"There are {len(critical)} critical and {len(non_critical)} non-critical "
            f"activities."
        ),
        rag="red" if not non_critical else "green",
    ))

    if not non_critical:
        steps.append(
            Step(
                title="Step 2 — No Leveling Possible",
                interpretation=(
                    "Every activity is on the critical path. Resource leveling "
                    "cannot improve the resource profile without extending the project."),
                rag="amber",
            ))
        return steps

    for act in sorted(non_critical, key=lambda a: -getattr(a, "float", 0)):
        current_start = schedule.get(act.id, act.es)
        steps.append(Step(
            title=f"Activity {act.id} — Float = {act.float} period(s)",
            formula=f"ES = {act.es},  LS = {act.ls},  Duration = {act.duration},  Res = {act.resource_demand}",
            substitution=(
                f"Current start = {current_start}  "
                f"(can shift to any time in [{act.es}, {act.ls}])"
            ),
            result=f"Available window: {act.ls - act.es} period(s) of flexibility",
            interpretation=(
                f"Activity {act.id} can start anywhere from period {act.es} to "
                f"period {act.ls}. Shifting it later reduces its resource overlap "
                f"with other activities scheduled early."
            ),
            rag="green" if act.float >= 2 else "amber",
        ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  Minimum Moment Algorithm Walk-Through
# ════════════════════════════════════════════════════════════════════

def minimum_moment_algorithm_steps(result: Dict[str, Any]) -> List[Step]:
    """Walk-through of the Minimum Moment leveling run."""
    steps: List[Step] = []
    leveling_steps = result.get("steps", [])
    orig_moment = result.get("original_moment", 0.0)
    final_moment = result.get("leveled_moment", 0.0)
    iterations = result.get("iterations", 0)
    improvement = result.get("improvement_pct", 0.0)

    # ── Theory recap ─────────────────────────────────────────────────
    steps.append(
        Step(
            title="Step 1 — Minimum Moment Method: The Formula",
            formula="M = Σₜ (r(t) − r̄)²   where r̄ = (Σ r(t)) / T",
            interpretation=(
                "The moment M measures the variance of the resource profile. "
                "A lower moment means a flatter profile.\n\n"
                "The algorithm iterates over all non-critical activities and tries "
                "each feasible start time, keeping the position that gives the "
                "smallest moment. It repeats until no improvement is found."),
        ))

    # ── Original state ────────────────────────────────────────────────
    orig_profile_obj = result.get("original_profile")
    if orig_profile_obj:
        peak = orig_profile_obj.get_peak_usage()
        mean = orig_profile_obj.get_mean_usage()
        steps.append(
            Step(
                title="Step 2 — Original Resource Profile",
                formula="M₀ = Σₜ (r(t) − r̄)²",
                substitution=f"r̄ = {
                    mean:.2f},  Peak = {
                    peak:.1f}",
                result=f"M₀ = {
                    orig_moment:.2f}",
                interpretation=(
                    f"Before leveling, the resource profile has a moment of {
                        orig_moment:.2f}. " f"The peak demand is {
                        peak:.1f} resources per period with a mean of {
                        mean:.2f}."),
                rag="amber" if orig_moment > 0 else "green",
            ))

    # ── Recorded moves ────────────────────────────────────────────────
    if leveling_steps:
        steps.append(Step(
            title=f"Step 3 — Leveling Moves ({len(leveling_steps)} total)",
            formula="For each move: new_M = Σₜ (r_new(t) − r̄)²",
            interpretation=(
                f"The algorithm made {len(leveling_steps)} improvement(s) across "
                f"{iterations} iteration(s)."
            ),
            children=[
                Step(
                    title=f"Move {ls.step_number}: Activity {ls.activity_id}",
                    formula=f"Shift day {ls.from_start} → day {ls.to_start}",
                    substitution=f"Moment before = {ls.metric_before:.2f}",
                    result=f"Moment after = {ls.metric_after:.2f}  (Δ = {ls.metric_after - ls.metric_before:+.2f})",
                    interpretation=ls.reason,
                    rag="green" if ls.metric_after < ls.metric_before else "amber",
                )
                for ls in leveling_steps
            ],
        ))
    else:
        steps.append(
            Step(
                title="Step 3 — No Moves Made",
                interpretation=(
                    "The algorithm found no improvement: the schedule is already at "
                    "minimum moment for the given float constraints."),
                rag="amber",
            ))

    # ── Final state ───────────────────────────────────────────────────
    final_profile_obj = result.get("leveled_profile")
    if final_profile_obj:
        leveled_peak = final_profile_obj.get_peak_usage()
        steps.append(Step(
            title="Step 4 — Leveled Resource Profile",
            formula="M_final = Σₜ (r_leveled(t) − r̄)²",
            result=f"M_final = {final_moment:.2f}  (improvement = {improvement:.1f}%)",
            interpretation=(
                f"After leveling, the moment dropped from {orig_moment:.2f} to "
                f"{final_moment:.2f} — a {improvement:.1f}% improvement. "
                f"Peak usage reduced to {leveled_peak:.1f}."
            ),
            rag="green" if improvement > 0 else "amber",
        ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  Burgess Algorithm Walk-Through
# ════════════════════════════════════════════════════════════════════

def burgess_algorithm_steps(result: Dict[str, Any]) -> List[Step]:
    """Walk-through of the Burgess leveling run."""
    steps: List[Step] = []
    leveling_steps = result.get("steps", [])
    orig_cost = result.get("original_cost", 0.0)
    final_cost = result.get("leveled_cost", 0.0)
    iterations = result.get("iterations", 0)
    improvement = result.get("improvement_pct", 0.0)

    # ── Theory recap ─────────────────────────────────────────────────
    steps.append(
        Step(
            title="Step 1 — Burgess Method: The Formula",
            formula="B = Σₜ r(t)²",
            interpretation=(
                "The Burgess cost B is the sum of squares of resource usage at each "
                "period. Unlike the moment method, it does not subtract the mean — "
                "this penalises high peaks more severely.\n\n"
                "The algorithm works identically to the Minimum Moment method but "
                "minimises B instead of M."),
        ))

    # ── Original state ────────────────────────────────────────────────
    orig_profile_obj = result.get("original_profile")
    if orig_profile_obj:
        peak = orig_profile_obj.get_peak_usage()
        steps.append(Step(
            title="Step 2 — Original Burgess Cost",
            formula="B₀ = Σₜ r(t)²",
            result=f"B₀ = {orig_cost:.2f}  (peak = {peak:.1f})",
            interpretation=(
                f"Before leveling, the sum of squared daily resource usage is "
                f"{orig_cost:.2f}. The peak is {peak:.1f} resources per period."
            ),
            rag="amber" if orig_cost > 0 else "green",
        ))

    # ── Recorded moves ────────────────────────────────────────────────
    if leveling_steps:
        steps.append(
            Step(
                title=f"Step 3 — Leveling Moves ({
                    len(leveling_steps)} total)",
                formula="For each move: B_new = Σₜ r_new(t)²",
                interpretation=(
                    f"The algorithm made {
                        len(leveling_steps)} improvement(s) across " f"{iterations} iteration(s)."),
                children=[
                    Step(
                        title=f"Move {
                            ls.step_number}: Activity {
                            ls.activity_id}",
                        formula=f"Shift day {
                            ls.from_start} → day {
                            ls.to_start}",
                        substitution=f"Burgess cost before = {
                            ls.metric_before:.2f}",
                        result=f"Burgess cost after = {
                            ls.metric_after:.2f}  (Δ = {
                            ls.metric_after -
                            ls.metric_before:+.2f})",
                        interpretation=ls.reason,
                        rag="green" if ls.metric_after < ls.metric_before else "amber",
                    ) for ls in leveling_steps],
            ))
    else:
        steps.append(
            Step(
                title="Step 3 — No Moves Made",
                interpretation=(
                    "The algorithm found no improvement: the schedule is already at "
                    "minimum Burgess cost for the given float constraints."),
                rag="amber",
            ))

    # ── Final state ───────────────────────────────────────────────────
    final_profile_obj = result.get("leveled_profile")
    if final_profile_obj:
        leveled_peak = final_profile_obj.get_peak_usage()
        steps.append(Step(
            title="Step 4 — Leveled Burgess Cost",
            formula="B_final = Σₜ r_leveled(t)²",
            result=f"B_final = {final_cost:.2f}  (improvement = {improvement:.1f}%)",
            interpretation=(
                f"After leveling, the Burgess cost dropped from {orig_cost:.2f} to "
                f"{final_cost:.2f} — a {improvement:.1f}% improvement. "
                f"Peak usage is now {leveled_peak:.1f}."
            ),
            rag="green" if improvement > 0 else "amber",
        ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  Before / After Comparison
# ════════════════════════════════════════════════════════════════════

def before_after_comparison_steps(result: Dict[str, Any]) -> List[Step]:
    """Compare before-and-after metrics for any leveling result."""
    steps: List[Step] = []

    peak_before = result.get("peak_usage_original", 0.0)
    peak_after = result.get("peak_usage_leveled", 0.0)
    moment_before = result.get(
        "original_moment", result.get(
            "original_cost", 0.0))
    moment_after = result.get(
        "leveled_moment", result.get(
            "leveled_cost", 0.0))
    improvement = result.get("improvement_pct", 0.0)
    feasible = result.get("feasible", True)

    peak_delta_pct = 0.0
    if peak_before > 0:
        peak_delta_pct = (peak_before - peak_after) / peak_before * 100

    steps.append(Step(
        title="Step 1 — Peak Resource Usage",
        formula="Peak reduction (%) = (Peak_before − Peak_after) / Peak_before × 100",
        substitution=f"({peak_before:.1f} − {peak_after:.1f}) / {peak_before:.1f} × 100",
        result=f"{peak_delta_pct:.1f}% reduction  ({peak_before:.1f} → {peak_after:.1f})",
        interpretation=(
            f"The peak daily resource demand dropped from {peak_before:.1f} to "
            f"{peak_after:.1f} resources per period — a {peak_delta_pct:.1f}% reduction. "
            "Lower peaks mean less risk of overloading the team."
        ),
        rag="green" if peak_delta_pct > 0 else ("amber" if peak_delta_pct == 0 else "red"),
    ))

    steps.append(Step(
        title="Step 2 — Resource Profile Smoothness",
        formula="Improvement (%) = (Metric_before − Metric_after) / Metric_before × 100",
        substitution=f"({moment_before:.2f} − {moment_after:.2f}) / {moment_before:.2f} × 100",
        result=f"{improvement:.1f}% improvement",
        interpretation=(
            f"The smoothness metric improved by {improvement:.1f}%. "
            "A larger improvement means the resource histogram is flatter, "
            "with fewer boom-and-bust periods."
        ),
        rag="green" if improvement >= 10 else ("amber" if improvement > 0 else "red"),
    ))

    steps.append(Step(
        title="Step 3 — Feasibility Check",
        formula="Feasible = all r(t) ≤ Resource_Limit",
        result="FEASIBLE" if feasible else "INFEASIBLE",
        interpretation=(
            "The leveled schedule respects the resource limit at every time period."
            if feasible else
            "Warning: the leveled schedule still exceeds the resource limit at one "
            "or more periods. Consider increasing the resource limit or switching "
            "to Constrained scheduling mode."
        ),
        rag="green" if feasible else "red",
    ))

    steps.append(
        Step(
            title="Step 4 — When to Use Each Method", interpretation=(
                "Minimum Moment Method:\n"
                "  – Balances the profile symmetrically around the mean.\n"
                "  – Best when you want an even distribution of workload.\n\n"
                "Burgess Method:\n"
                "  – More aggressively reduces high peaks (squares magnify large values).\n"
                "  – Better when high peaks carry disproportionate costs (e.g. overtime).\n\n"
                "Both methods produce heuristic solutions. Neither guarantees the "
                "global optimum, but both are fast and practical for real projects."), ))

    return steps
