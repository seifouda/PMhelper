"""
PMhelper Edu — Crashing Step Generator (V2 Phase 11).

Produces :class:`~pmhelper.core.step_generators_edu.Step` trees that
walk through the project crashing (time-cost trade-off) algorithm.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pmhelper.core.step_generators_edu import Step


def crashing_theory_steps() -> List[Step]:
    """Generate theory / overview steps for project crashing.

    Returns
    -------
    list[Step]
    """
    return [
        Step(
            title="Step 1 — What is Project Crashing?",
            interpretation=(
                "Project crashing is a schedule compression technique "
                "that reduces the project duration by adding resources "
                "to critical-path activities, at an additional cost."
            ),
        ),
        Step(
            title="Step 2 — Crash Cost per Period",
            formula="Cost Slope = (Crash Cost − Normal Cost) / (Normal Duration − Crash Duration)",
            interpretation=(
                "The cost slope tells you how much extra it costs to "
                "reduce one period of duration for each activity. "
                "Lower slopes are crashed first (cheapest acceleration)."
            ),
        ),
        Step(
            title="Step 3 — Crashing Algorithm",
            interpretation=(
                "1. Identify the critical path.\n"
                "2. For each critical activity, compute the cost slope.\n"
                "3. Crash the activity with the lowest cost slope by one period.\n"
                "4. Update the schedule: re-run CPM forward/backward pass.\n"
                "5. Check if a new critical path has formed.\n"
                "6. Repeat until the target duration is reached or "
                "no further crashing is possible."
            ),
        ),
        Step(
            title="Step 4 — Stopping Criteria",
            interpretation=(
                "Crashing stops when:\n"
                "• The desired project duration is reached.\n"
                "• All critical activities are at their crash duration.\n"
                "• The marginal crashing cost exceeds the benefit."
            ),
        ),
    ]


def crashing_steps(
    activities: List[Dict[str, Any]],
    crash_log: Optional[List[Dict[str, Any]]] = None,
    target_duration: Optional[float] = None,
) -> List[Step]:
    """Generate worked-solution steps for a crashing analysis.

    Parameters
    ----------
    activities : list of dict
        Each dict has keys: ``id``, ``name``, ``normal_duration``,
        ``crash_duration``, ``normal_cost``, ``crash_cost``.
    crash_log : list of dict, optional
        Sequence of crash decisions. Each entry:
        ``{"step": int, "activity": str, "cost_slope": float,
           "days_crashed": int, "new_duration": float, "total_cost": float}``.
    target_duration : float, optional
        If given, shown as the crashing target.

    Returns
    -------
    list[Step]
    """
    steps: List[Step] = []

    # ── Step 1: Cost slopes ─────────────────────────────────────────
    slope_children: List[Step] = []
    for act in activities:
        aid = act.get("id", "?")
        nd = act.get("normal_duration", 0)
        cd = act.get("crash_duration", 0)
        nc = act.get("normal_cost", 0)
        cc = act.get("crash_cost", 0)
        max_crash = nd - cd
        if max_crash > 0:
            slope = (cc - nc) / max_crash
            slope_children.append(Step(
                title=f"Activity {aid}",
                formula="Cost Slope = (CC − NC) / (ND − CD)",
                substitution=f"= ({cc:,.0f} − {nc:,.0f}) / ({nd} − {cd})",
                result=f"= {slope:,.2f} per period",
                interpretation=f"Can crash by up to {max_crash} period(s).",
            ))
        else:
            slope_children.append(Step(
                title=f"Activity {aid}",
                result="Cannot be crashed (ND = CD)",
            ))

    if slope_children:
        steps.append(
            Step(
                title="Step 1 — Cost Slope per Activity",
                formula="Cost Slope = (Crash Cost − Normal Cost) / (Normal Duration − Crash Duration)",
                interpretation="Lower cost slope = cheaper to crash. Crash these first.",
                children=slope_children,
            ))

    # ── Step 2: Crash log (if provided) ─────────────────────────────
    if crash_log:
        log_children: List[Step] = []
        for entry in crash_log:
            step_num = entry.get("step", "?")
            act_id = entry.get("activity", "?")
            slope = entry.get("cost_slope", 0)
            days = entry.get("days_crashed", 1)
            new_dur = entry.get("new_duration", "?")
            total = entry.get("total_cost", 0)
            log_children.append(
                Step(
                    title=f"Iteration {step_num} — Crash Activity {act_id}",
                    formula=f"Cost Slope = {
                        slope:,.2f}",
                    substitution=f"Crash by {days} period(s)",
                    result=f"New project duration = {new_dur}, Total cost = {
                        total:,.0f}",
                    rag="amber" if days > 0 else "grey",
                ))
        steps.append(
            Step(
                title="Step 2 — Crashing Iterations",
                interpretation="Activities are crashed in order of ascending cost slope.",
                children=log_children,
            ))

    # ── Step 3: Summary ─────────────────────────────────────────────
    if crash_log:
        final = crash_log[-1] if crash_log else {}
        final_dur = final.get("new_duration", "?")
        final_cost = final.get("total_cost", 0)
        target_str = f" (target: {target_duration})" if target_duration else ""
        interp = (
            f"Final project duration: {final_dur}{target_str}. "
            f"Total project cost after crashing: {final_cost:,.0f}."
        )
        if target_duration and final_dur != "?" and float(
                final_dur) <= target_duration:
            rag = "green"
            interp += " Target duration achieved."
        elif target_duration:
            rag = "red"
            interp += " Target duration NOT achieved."
        else:
            rag = "grey"

        steps.append(Step(
            title="Step 3 — Crashing Summary",
            result=f"Duration = {final_dur}, Cost = {final_cost:,.0f}",
            interpretation=interp,
            rag=rag,
        ))

    return steps
