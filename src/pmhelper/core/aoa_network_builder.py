"""
PMhelper Edu — Activity-on-Arrow (AOA) Network Builder (V2 Phase 7).

Provides:
  AOAEvent     — project event (node in AOA graph)
  AOAActivity  — activity or dummy arrow between two events
  AOANetwork   — full AOA network with CPM engine
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class AOAEvent:
    """A project event (circle/node) in an AOA network diagram."""
    id: int
    label: str = ""
    earliest_time: float = 0.0   # ET — forward pass result
    latest_time: float = 0.0     # LT — backward pass result

    @property
    def slack(self) -> float:
        """Event slack = LT − ET.  0 on the critical path."""
        return self.latest_time - self.earliest_time

    @property
    def is_critical(self) -> bool:
        return self.slack == 0.0


@dataclass
class AOAActivity:
    """An activity (or dummy) on an arrow between two AOA events."""
    from_event: int          # tail event id
    to_event: int            # head event id
    activity_id: str         # e.g. "A", "B" or "D_2_4" for a dummy
    name: str = ""
    duration: float = 0.0
    is_dummy: bool = False

    # CPM results (populated by AOANetwork.run_cpm())
    early_start: float = 0.0
    early_finish: float = 0.0
    late_start: float = 0.0
    late_finish: float = 0.0
    total_float: float = 0.0
    free_float: float = 0.0
    is_critical: bool = False


@dataclass
class AOANetwork:
    """
    Activity-on-Arrow network with built-in CPM engine.

    events     : {event_id: AOAEvent}
    activities : list of AOAActivity (real activities + dummy arrows)
    """
    events: Dict[int, AOAEvent] = field(default_factory=dict)
    activities: List[AOAActivity] = field(default_factory=list)

    # Computed by run_cpm()
    project_duration: float = 0.0
    start_event_id: int = 1
    end_event_id: int = 1

    # ---------------------------------------------------------------------------
    # Topology helpers
    # ---------------------------------------------------------------------------

    def real_activities(self) -> List[AOAActivity]:
        """Return non-dummy activities only."""
        return [a for a in self.activities if not a.is_dummy]

    def critical_path_activities(self) -> List[AOAActivity]:
        """Return real activities on the critical path."""
        return [a for a in self.activities if a.is_critical and not a.is_dummy]

    def _incoming(self, event_id: int) -> List[AOAActivity]:
        return [a for a in self.activities if a.to_event == event_id]

    def _outgoing(self, event_id: int) -> List[AOAActivity]:
        return [a for a in self.activities if a.from_event == event_id]

    def _topo_event_order(self) -> List[int]:
        """Return event ids in topological order (via Kahn's algorithm)."""
        in_degree: Dict[int, int] = {eid: 0 for eid in self.events}
        for a in self.activities:
            in_degree[a.to_event] = in_degree.get(a.to_event, 0) + 1
        queue = sorted(
            [eid for eid, deg in in_degree.items() if deg == 0])
        order: List[int] = []
        while queue:
            v = queue.pop(0)
            order.append(v)
            for a in self._outgoing(v):
                in_degree[a.to_event] -= 1
                if in_degree[a.to_event] == 0:
                    queue.append(a.to_event)
                    queue.sort()
        return order

    # ---------------------------------------------------------------------------
    # CPM engine
    # ---------------------------------------------------------------------------

    def run_cpm(self) -> "AOANetwork":
        """Run full CPM: forward pass, backward pass, float calculation."""
        self._forward_pass()
        self._backward_pass()
        self._calculate_floats()
        return self

    def _forward_pass(self) -> None:
        """Compute earliest event times (ET) for all events."""
        for ev in self.events.values():
            ev.earliest_time = 0.0

        for eid in self._topo_event_order():
            incoming = self._incoming(eid)
            if not incoming:
                self.events[eid].earliest_time = 0.0
            else:
                self.events[eid].earliest_time = max(
                    self.events[a.from_event].earliest_time + a.duration
                    for a in incoming
                )

        # Project duration = ET of the end event
        end_ids = [eid for eid in self.events
                   if not self._outgoing(eid)]
        if end_ids:
            self.end_event_id = max(
                end_ids, key=lambda e: self.events[e].earliest_time)
        self.project_duration = self.events[self.end_event_id].earliest_time

    def _backward_pass(self) -> None:
        """Compute latest event times (LT) for all events."""
        for ev in self.events.values():
            ev.latest_time = self.project_duration

        for eid in reversed(self._topo_event_order()):
            outgoing = self._outgoing(eid)
            if not outgoing:
                self.events[eid].latest_time = self.project_duration
            else:
                self.events[eid].latest_time = min(
                    self.events[a.to_event].latest_time - a.duration
                    for a in outgoing
                )

    def _calculate_floats(self) -> None:
        """Compute total float, free float, and critical flag for each activity."""
        for a in self.activities:
            fe = self.events[a.from_event]
            te = self.events[a.to_event]
            a.early_start = fe.earliest_time
            a.early_finish = fe.earliest_time + a.duration
            a.late_finish = te.latest_time
            a.late_start = te.latest_time - a.duration
            a.total_float = te.latest_time - a.duration - fe.earliest_time
            a.free_float = te.earliest_time - a.duration - fe.earliest_time
            # Critical = zero total float (and both events on critical path)
            a.is_critical = (
                abs(a.total_float) < 1e-9
                and abs(fe.slack) < 1e-9
                and abs(te.slack) < 1e-9
            )

    # ---------------------------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "start_event_id": self.start_event_id,
            "end_event_id": self.end_event_id,
            "project_duration": self.project_duration,
            "events": [
                {
                    "id": e.id,
                    "label": e.label,
                    "earliest_time": e.earliest_time,
                    "latest_time": e.latest_time,
                }
                for e in self.events.values()
            ],
            "activities": [
                {
                    "from_event": a.from_event,
                    "to_event": a.to_event,
                    "activity_id": a.activity_id,
                    "name": a.name,
                    "duration": a.duration,
                    "is_dummy": a.is_dummy,
                    "total_float": a.total_float,
                    "free_float": a.free_float,
                    "is_critical": a.is_critical,
                }
                for a in self.activities
            ],
        }
