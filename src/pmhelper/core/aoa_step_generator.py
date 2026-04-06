"""
PMhelper Edu — AOA Network Step Generators (V2 Phase 7).

Produces structured :class:`Step` trees for the five key concepts in
Activity-on-Arrow (AOA) network analysis:

  event_numbering_steps  — how/why events are numbered
  dummy_activity_steps   — when and why dummy activities are inserted
  forward_pass_steps     — computing Earliest Event Times (ET)
  backward_pass_steps    — computing Latest Event Times (LT)
  critical_path_steps    — identifying the critical path on the arrows

Each function returns ``List[Step]`` suitable for a
:class:`~pmhelper.gui.widgets.worked_solution_window.WorkedSolutionWindow`.
"""

from __future__ import annotations

from typing import List

from pmhelper.core.aoa_network_builder import AOAActivity, AOAEvent, AOANetwork
from pmhelper.core.step_generators_edu import Step


# ---------------------------------------------------------------------------
# 1. Event Numbering
# ---------------------------------------------------------------------------

def event_numbering_steps(network: AOANetwork) -> List[Step]:
    """Explain how events are numbered in the AOA network.

    Shows the total event count, start/end events, and lists each event
    with its label and role.
    """
    total = len(network.events)
    start_ev = network.events.get(network.start_event_id)
    end_ev = network.events.get(network.end_event_id)

    header = Step(
        title="Step 1 — Event Numbering",
        formula="Events = nodes in the AOA graph (each represents a point in time)",
        interpretation=(
            "In Activity-on-Arrow (AOA) networks, activities are the ARROWS "
            "and events are the CIRCLES (nodes). Each event represents an "
            "instant when its incoming activities are complete and outgoing "
            "activities may start."
        ),
    )

    event_children: List[Step] = []

    # Start event
    if start_ev:
        event_children.append(Step(
            title=f"Event {start_ev.id} — Start",
            result="No incoming arrows. The project begins here.",
            rag="green",
        ))

    # Intermediate events
    order = network._topo_event_order()
    for eid in order:
        if eid in (network.start_event_id, network.end_event_id):
            continue
        ev = network.events[eid]
        incoming = network._incoming(eid)
        outgoing = network._outgoing(eid)
        real_in  = [a for a in incoming if not a.is_dummy]
        dummy_in = [a for a in incoming if a.is_dummy]
        note = ""
        if dummy_in:
            note = f"  [Merge event — {len(dummy_in)} dummy arrow(s) arrive here]"
        event_children.append(Step(
            title=f"Event {eid}{(' — ' + ev.label) if ev.label else ''}",
            substitution=(
                f"Incoming: {', '.join(a.activity_id for a in incoming) or 'none'}  |  "
                f"Outgoing: {', '.join(a.activity_id for a in outgoing) or 'none'}"
                + note
            ),
        ))

    # End event
    if end_ev:
        event_children.append(Step(
            title=f"Event {end_ev.id} — End",
            result="No outgoing arrows. The project finishes here.",
            rag="green",
        ))

    header.children = event_children

    summary = Step(
        title="Summary",
        result=f"{total} events total: 1 Start, 1 End, {total - 2} intermediate.",
        interpretation=(
            f"The network has {len(network.real_activities())} real activities and "
            f"{len([a for a in network.activities if a.is_dummy])} dummy arrow(s)."
        ),
    )

    return [header, summary]


# ---------------------------------------------------------------------------
# 2. Dummy Activity Explanation
# ---------------------------------------------------------------------------

def dummy_activity_steps(network: AOANetwork) -> List[Step]:
    """Explain when and why dummy activities were inserted."""
    dummies = [a for a in network.activities if a.is_dummy]

    header = Step(
        title="Step 2 — Dummy Activities",
        formula="Dummy = zero-duration arrow inserted to preserve logical precedence",
        interpretation=(
            "Dummy activities (shown as dashed arrows) have ZERO duration. "
            "They carry no work — they exist purely to preserve the correct "
            "precedence relationships that cannot be shown with real arrows alone."
        ),
    )

    if not dummies:
        header.result = "No dummy activities are needed in this network."
        header.rag = "green"
        return [header]

    # Explanation of merge events
    merge_events = set(a.to_event for a in dummies)
    children: List[Step] = []

    for eid in sorted(merge_events):
        ev = network.events.get(eid)
        arriving_dummies = [a for a in dummies if a.to_event == eid]
        outgoing_real = [a for a in network.activities
                         if a.from_event == eid and not a.is_dummy]
        acts_waiting = ", ".join(a.activity_id for a in outgoing_real) or "(none)"
        from_events = ", ".join(str(a.from_event) for a in arriving_dummies)

        children.append(Step(
            title=f"Merge Event {eid}{(' — ' + ev.label) if ev and ev.label else ''}",
            substitution=(
                f"Dummy arrows arriving from events: {from_events}\n"
                f"Real activities that WAIT for this merge: {acts_waiting}"
            ),
            interpretation=(
                "This merge event collects results from multiple predecessor "
                "paths.  The dummies ensure every preceding activity must "
                "complete before the activities at this event can start."
            ),
            result=f"{len(arriving_dummies)} dummy arrow(s) → Event {eid}",
        ))

    header.children = children
    header.result = f"{len(dummies)} dummy arrow(s) in this network."

    return [header]


# ---------------------------------------------------------------------------
# 3. Forward Pass
# ---------------------------------------------------------------------------

def forward_pass_steps(network: AOANetwork) -> List[Step]:
    """Walk through the forward pass (Earliest Event Time, ET) computation."""
    order = network._topo_event_order()

    header = Step(
        title="Step 3 — Forward Pass (Earliest Event Times)",
        formula="ET(j) = max [ ET(i) + duration(i→j) ]  for all arrows i→j",
        interpretation=(
            "Starting at ET=0 for the first event, we work LEFT to RIGHT "
            "through the network.  For each event we take the MAXIMUM of "
            "(predecessor ET + arrow duration) over all incoming arrows."
        ),
    )

    children: List[Step] = []

    for eid in order:
        ev = network.events[eid]
        incoming = network._incoming(eid)

        if not incoming:
            children.append(Step(
                title=f"Event {eid} (Start)",
                formula="ET = 0  (by definition)",
                result=f"ET({eid}) = {ev.earliest_time:.0f}",
                rag="green",
            ))
            continue

        sub_parts = []
        contribs = []
        for a in incoming:
            fe = network.events[a.from_event]
            contrib = fe.earliest_time + a.duration
            contribs.append(contrib)
            label = a.activity_id if not a.is_dummy else f"dummy({a.from_event}->{a.to_event})"
            sub_parts.append(
                f"ET({a.from_event}) + dur({label}) = "
                f"{fe.earliest_time:.0f} + {a.duration:.0f} = {contrib:.0f}"
            )

        contrib_str = ", ".join(f"{c:.0f}" for c in contribs)
        is_crit = abs(ev.slack) < 1e-9
        children.append(Step(
            title=f"Event {eid}{(' — ' + ev.label) if ev.label else ''}",
            formula="ET(j) = max(ET(i) + duration)",
            substitution="  |  ".join(sub_parts),
            result=f"ET({eid}) = max({contrib_str}) = {ev.earliest_time:.0f}",
            rag="green" if is_crit else "",
        ))

    header.children = children

    end_ev = network.events.get(network.end_event_id)
    pd = network.project_duration
    summary = Step(
        title="Forward Pass Result",
        result=f"Project Duration = ET(Event {network.end_event_id}) = {pd:.0f}",
        interpretation=(
            "The project's earliest possible completion date is "
            f"{pd:.0f} time units."
        ),
        rag="green",
    )

    return [header, summary]


# ---------------------------------------------------------------------------
# 4. Backward Pass
# ---------------------------------------------------------------------------

def backward_pass_steps(network: AOANetwork) -> List[Step]:
    """Walk through the backward pass (Latest Event Time, LT) computation."""
    order = network._topo_event_order()

    header = Step(
        title="Step 4 — Backward Pass (Latest Event Times)",
        formula="LT(i) = min [ LT(j) − duration(i→j) ]  for all arrows i→j",
        interpretation=(
            "Starting at LT = project duration for the last event, we work "
            "RIGHT to LEFT.  For each event we take the MINIMUM of "
            "(successor LT − arrow duration) over all outgoing arrows."
        ),
    )

    children: List[Step] = []

    for eid in reversed(order):
        ev = network.events[eid]
        outgoing = network._outgoing(eid)

        if not outgoing:
            children.append(Step(
                title=f"Event {eid} (End)",
                formula="LT = project duration  (by definition)",
                result=f"LT({eid}) = {ev.latest_time:.0f}",
                rag="green",
            ))
            continue

        sub_parts = []
        for a in outgoing:
            te = network.events[a.to_event]
            contrib = te.latest_time - a.duration
            label = a.activity_id if not a.is_dummy else f"dummy({a.from_event}->{a.to_event})"
            sub_parts.append(
                f"LT({a.to_event}) − dur({label}) = "
                f"{te.latest_time:.0f} − {a.duration:.0f} = {contrib:.0f}"
            )

        is_crit = abs(ev.slack) < 1e-9
        children.append(Step(
            title=f"Event {eid}{(' — ' + ev.label) if ev.label else ''}",
            formula="LT(i) = min(LT(j) − duration)",
            substitution="  |  ".join(sub_parts),
            result=f"LT({eid}) = {ev.latest_time:.0f}   (slack = {ev.slack:.0f})",
            rag="green" if is_crit else "",
        ))

    header.children = children

    cp_events = [ev for ev in network.events.values() if abs(ev.slack) < 1e-9]
    summary = Step(
        title="Backward Pass Result",
        result=(
            f"Critical events (slack = 0): "
            + ", ".join(f"Event {e.id}" for e in sorted(cp_events, key=lambda x: x.id))
        ),
        interpretation="Events with slack = 0 lie on the critical path.",
        rag="green",
    )

    return [header, summary]


# ---------------------------------------------------------------------------
# 5. Critical Path
# ---------------------------------------------------------------------------

def critical_path_steps(network: AOANetwork) -> List[Step]:
    """Identify the critical path activities and explain total float."""
    cp_acts = network.critical_path_activities()
    all_real = network.real_activities()

    header = Step(
        title="Step 5 — Critical Path & Total Float",
        formula=(
            "Total Float (TF) = LT(to_event) − duration − ET(from_event)\n"
            "Critical activity: TF = 0  AND  both end-events on critical path"
        ),
        interpretation=(
            "Any activity with TF = 0 is on the critical path — it cannot be "
            "delayed without extending the project.  Activities with TF > 0 "
            "have scheduling flexibility (float)."
        ),
    )

    float_children: List[Step] = []

    for a in sorted(all_real, key=lambda x: x.activity_id):
        fe = network.events[a.from_event]
        te = network.events[a.to_event]
        tf = a.total_float
        ff = a.free_float
        is_crit = a.is_critical

        float_children.append(Step(
            title=f"Activity {a.activity_id} — '{a.name}'",
            formula="TF = LT(to) − dur − ET(from)",
            substitution=(
                f"= LT({a.to_event}) − {a.duration:.0f} − ET({a.from_event})\n"
                f"= {te.latest_time:.0f} − {a.duration:.0f} − {fe.earliest_time:.0f}"
            ),
            result=f"TF = {tf:.0f}   |   FF = {ff:.0f}   |   ES = {a.early_start:.0f}, EF = {a.early_finish:.0f}",
            interpretation=(
                "ON critical path — zero float, no schedule flexibility."
                if is_crit
                else f"Float = {tf:.0f} — can be delayed up to {tf:.0f} time unit(s) without delaying the project."
            ),
            rag="red" if is_crit else "green",
        ))

    header.children = float_children

    cp_ids = " → ".join(a.activity_id for a in cp_acts)
    summary = Step(
        title="Critical Path",
        result=f"Critical Path: {cp_ids or '(none identified)'}",
        interpretation=(
            f"Project Duration = {network.project_duration:.0f} time units.  "
            "Any delay on these activities will delay the whole project."
        ),
        rag="red" if cp_acts else "amber",
    )

    return [header, summary]
