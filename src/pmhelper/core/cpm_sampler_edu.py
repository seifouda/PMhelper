"""
PMhelper Edu — Lightweight CPM on sampled durations.
Forward + backward pass to find project duration and critical path.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple


def run_cpm_on_sample(
    activities: List[dict],
    sampled_durations: Dict[str, float],
) -> Tuple[float, Set[str]]:
    """Run forward/backward pass CPM on pre-sampled durations.

    Parameters
    ----------
    activities : list[dict]
        Activity dicts with at least 'id' and 'predecessors' keys.
        'predecessors' is a list of activity id strings (may be empty).
    sampled_durations : dict[str, float]
        Mapping of activity id → sampled duration for this trial.

    Returns
    -------
    (project_duration, critical_path_set)
        project_duration: float — total project duration for this sample.
        critical_path_set: set[str] — set of activity ids on the critical path.
    """
    if not activities:
        return 0.0, set()

    # Build lookup structures
    act_by_id: Dict[str, dict] = {}
    successors: Dict[str, List[str]] = {}
    for act in activities:
        aid = act["id"]
        act_by_id[aid] = act
        successors[aid] = []

    # Build predecessor/successor maps
    for act in activities:
        aid = act["id"]
        preds = act.get("predecessors", [])
        if isinstance(preds, str):
            preds = [p.strip() for p in preds.split(",") if p.strip()]
        for pred_id in preds:
            if pred_id in successors:
                successors[pred_id].append(aid)

    # Topological sort (Kahn's algorithm)
    in_degree: Dict[str, int] = {act["id"]: 0 for act in activities}
    for act in activities:
        preds = act.get("predecessors", [])
        if isinstance(preds, str):
            preds = [p.strip() for p in preds.split(",") if p.strip()]
        for pred_id in preds:
            if pred_id in in_degree:
                in_degree[act["id"]] += 1

    queue = [aid for aid, deg in in_degree.items() if deg == 0]
    topo_order: List[str] = []
    while queue:
        node = queue.pop(0)
        topo_order.append(node)
        for succ in successors.get(node, []):
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    # Forward pass — compute ES (early start) and EF (early finish)
    es: Dict[str, float] = {}
    ef: Dict[str, float] = {}
    for aid in topo_order:
        act = act_by_id[aid]
        dur = sampled_durations.get(aid, 0.0)
        preds = act.get("predecessors", [])
        if isinstance(preds, str):
            preds = [p.strip() for p in preds.split(",") if p.strip()]
        if not preds:
            es[aid] = 0.0
        else:
            es[aid] = max(ef.get(p, 0.0) for p in preds if p in ef) if preds else 0.0
        ef[aid] = es[aid] + dur

    project_duration = max(ef.values()) if ef else 0.0

    # Backward pass — compute LS (late start) and LF (late finish)
    ls: Dict[str, float] = {}
    lf: Dict[str, float] = {}
    for aid in reversed(topo_order):
        dur = sampled_durations.get(aid, 0.0)
        succs = successors.get(aid, [])
        if not succs:
            lf[aid] = project_duration
        else:
            lf[aid] = min(ls[s] for s in succs if s in ls) if succs else project_duration
        ls[aid] = lf[aid] - dur

    # Critical path — activities with zero total float
    critical_set: Set[str] = set()
    eps = 1e-9
    for aid in topo_order:
        total_float = ls[aid] - es[aid]
        if abs(total_float) < eps:
            critical_set.add(aid)

    return project_duration, critical_set
