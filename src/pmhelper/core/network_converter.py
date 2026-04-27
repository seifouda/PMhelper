"""
PMhelper Edu — AOA / AON Network Converter (V2 Phase 7).

Two public functions:

  aon_to_aoa(activity_list) -> AOANetwork
      Converts an AON activity list (dicts with id, duration, predecessors)
      to an Activity-on-Arrow network.  Inserts dummy activities wherever
      needed to preserve logical precedence.

  aoa_to_aon(network) -> List[Dict]
      Strips dummy arrows and reconstructs an AON activity list (with
      interpreted predecessor relationships).
"""

from __future__ import annotations

from typing import Dict, List, Set

import networkx as nx

from pmhelper.core.aoa_network_builder import AOAActivity, AOAEvent, AOANetwork


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def aon_to_aoa(activity_list: List[Dict]) -> AOANetwork:
    """Convert an AON activity list to an AOA (Activity-on-Arrow) network.

    Parameters
    ----------
    activity_list : list of dict
        Each dict must contain at minimum:
          - ``'id'``          : activity identifier (str)
          - ``'duration'``    : activity duration (numeric)
          - ``'predecessors'``: list of predecessor ids (list[str] or comma str)

        Optional keys: ``'name'``, ``'expected_duration'``, ``'activity_id'``

    Returns
    -------
    AOANetwork
        Fully constructed network (CPM *not* yet run — call ``.run_cpm()``).

    Algorithm
    ---------
    1. Build AON DiGraph; topological sort.
    2. Create one start event (id=1).
    3. Allocate a unique *exit_event* for every real activity.
    4. Compute each activity's *from_event*:
       - No predecessors → start event.
       - Single predecessor → that predecessor's exit event (simple chain).
       - Multiple predecessors with distinct exit events → new *merge event*
         plus a dummy arrow from each predecessor exit event to the merge event.
    5. Activities with no successors are "end activities".
       If exactly one → label its exit event "End".
       If several → create an explicit end event and add dummies to it.
    """
    if not activity_list:
        start = AOAEvent(id=1, label="Start")
        end = AOAEvent(id=2, label="End")
        return AOANetwork(
            events={1: start, 2: end},
            activities=[],
            start_event_id=1,
            end_event_id=2,
        )

    # ── Build AON graph ──────────────────────────────────────────────
    G: nx.DiGraph = nx.DiGraph()
    act_map: Dict[str, Dict] = {}

    for a in activity_list:
        aid = a.get("id") or a.get("activity_id", "")
        if not aid or aid in ("START", "END"):
            continue
        act_map[aid] = a
        G.add_node(aid)

    for a in activity_list:
        aid = a.get("id") or a.get("activity_id", "")
        if not aid or aid not in act_map:
            continue
        preds = a.get("predecessors", [])
        if isinstance(preds, str):
            preds = [p.strip() for p in preds.split(",") if p.strip()]
        for p in preds:
            if p and p in act_map:
                G.add_edge(p, aid)

    try:
        topo: List[str] = [
            aid for aid in nx.topological_sort(G) if aid in act_map]
    except nx.NetworkXUnfeasible:
        raise ValueError(
            "Activity network contains a cycle — cannot convert to AOA."
        )

    # ── Event counter (closure) ──────────────────────────────────────
    _next_id = [1]

    def _new_event(label: str = "") -> AOAEvent:
        ev = AOAEvent(id=_next_id[0], label=label)
        _next_id[0] += 1
        return ev

    events: Dict[int, AOAEvent] = {}
    activities: List[AOAActivity] = []

    # ── Start event ──────────────────────────────────────────────────
    start_event = _new_event("Start")
    events[start_event.id] = start_event

    # ── Pre-allocate a unique exit event for each activity ───────────
    exit_event: Dict[str, AOAEvent] = {}
    for aid in topo:
        ev = _new_event()
        exit_event[aid] = ev
        events[ev.id] = ev

    # ── Compute from_event for each activity ─────────────────────────
    from_event: Dict[str, AOAEvent] = {}

    for aid in topo:
        preds = list(G.predecessors(aid))

        if not preds:
            # Start activity — anchored to the start event
            from_event[aid] = start_event

        elif len(preds) == 1:
            # Simple chain — reuse the predecessor's exit event directly
            from_event[aid] = exit_event[preds[0]]

        else:
            # Multiple predecessors — collect their unique exit events
            seen: Dict[int, AOAEvent] = {}
            for p in preds:
                pe = exit_event[p]
                seen[pe.id] = pe
            unique_exits = list(seen.values())

            if len(unique_exits) == 1:
                # All predecessors already share one exit event — no dummy
                # needed
                from_event[aid] = unique_exits[0]
            else:
                # Need a merge event + one dummy per distinct predecessor exit
                merge_ev = _new_event()
                events[merge_ev.id] = merge_ev
                for pe in unique_exits:
                    dummy = AOAActivity(
                        from_event=pe.id,
                        to_event=merge_ev.id,
                        activity_id=f"D_{pe.id}_{merge_ev.id}",
                        name="dummy",
                        duration=0.0,
                        is_dummy=True,
                    )
                    activities.append(dummy)
                from_event[aid] = merge_ev

    # ── Add real activity arrows ─────────────────────────────────────
    for aid in topo:
        a = act_map[aid]
        dur = float(
            a.get("duration")
            or a.get("expected_duration")
            or 0
        )
        activities.append(
            AOAActivity(
                from_event=from_event[aid].id,
                to_event=exit_event[aid].id,
                activity_id=aid,
                name=a.get("name", aid),
                duration=dur,
                is_dummy=False,
            )
        )

    # ── End event ────────────────────────────────────────────────────
    end_acts = [aid for aid in topo if G.out_degree(aid) == 0]

    if len(end_acts) == 1:
        end_ev = exit_event[end_acts[0]]
        end_ev.label = "End"
    else:
        end_ev = _new_event("End")
        events[end_ev.id] = end_ev
        for aid in end_acts:
            dummy = AOAActivity(
                from_event=exit_event[aid].id,
                to_event=end_ev.id,
                activity_id=f"D_{exit_event[aid].id}_{end_ev.id}",
                name="dummy",
                duration=0.0,
                is_dummy=True,
            )
            activities.append(dummy)

    return AOANetwork(
        events=events,
        activities=activities,
        start_event_id=start_event.id,
        end_event_id=end_ev.id,
    )


def aoa_to_aon(network: AOANetwork) -> List[Dict]:
    """Convert an AOA network back to an AON activity list.

    Dummy arrows are stripped.  For each real activity, its AON predecessors
    are determined by tracing *backwards* through dummy chains to find which
    real activities deliver into the activity's from_event.

    Parameters
    ----------
    network : AOANetwork

    Returns
    -------
    list of dict
        Each dict contains ``'id'``, ``'name'``, ``'duration'``,
        ``'predecessors'`` (sorted list).
    """
    # Build a backward-reachability graph through dummy arrows only
    # dummy_preds[event_id] = list of event_ids reachable backwards via dummies
    dummy_preds: Dict[int, List[int]] = {eid: [] for eid in network.events}
    for a in network.activities:
        if a.is_dummy:
            dummy_preds[a.to_event].append(a.from_event)

    def _dummy_ancestors(event_id: int) -> Set[int]:
        """BFS backward through dummy arrows — returns all ancestor event ids."""
        visited: Set[int] = set()
        queue = list(dummy_preds.get(event_id, []))
        while queue:
            eid = queue.pop()
            if eid not in visited:
                visited.add(eid)
                queue.extend(dummy_preds.get(eid, []))
        return visited

    # Map: event_id → list of real activity_ids that arrive at that event
    event_arrivals: Dict[int, List[str]] = {eid: [] for eid in network.events}
    for a in network.real_activities():
        event_arrivals[a.to_event].append(a.activity_id)

    result: List[Dict] = []
    for a in network.real_activities():
        # All events that logically precede this activity's from_event
        ancestor_events = _dummy_ancestors(a.from_event) | {a.from_event}

        predecessors: List[str] = []
        for eid in ancestor_events:
            for pred_id in event_arrivals.get(eid, []):
                if pred_id != a.activity_id:
                    predecessors.append(pred_id)

        result.append(
            {
                "id": a.activity_id,
                "name": a.name,
                "duration": a.duration,
                "predecessors": sorted(predecessors),
            }
        )

    return result
