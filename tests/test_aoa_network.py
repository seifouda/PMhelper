"""
Tests for Phase 7 — AOA (Activity-on-Arrow) Dual Network Mode.

Covers:
  TestAOAEvent                — AOAEvent properties (slack, is_critical)
  TestAOAActivity             — AOAActivity defaults
  TestAOANetworkTopology      — topo sort, _incoming, _outgoing helpers
  TestAOANetworkCPMChain      — CPM on a simple chain
  TestAOANetworkCPMParallel   — CPM on two parallel paths
  TestAOANetworkCPMDemo       — CPM on the 6-activity demo project
  TestNetworkConverterAONtoAOA— aon_to_aoa: chain, fan-out, merge, multi-end
  TestNetworkConverterAOAtoAON— aoa_to_aon: strips dummies correctly
  TestConverterRoundTrip      — AON→AOA→AON preserves critical path
  TestAOACPMGroundTruth       — Verify against aoa_demo.json expected values
  TestAOAStepGenerators       — Smoke tests for step-generator functions
"""

from __future__ import annotations

import json
import os
from typing import Dict, List

import pytest

# ---------------------------------------------------------------------------
# Core imports
# ---------------------------------------------------------------------------

from pmhelper.core.aoa_network_builder import AOAActivity, AOAEvent, AOANetwork
from pmhelper.core.network_converter import aon_to_aoa, aoa_to_aon


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chain(durations: List[float]) -> AOANetwork:
    """Build a linear AOA chain:  1 -[d0]-> 2 -[d1]-> 3 ...  """
    n = len(durations) + 1
    events = {i: AOAEvent(id=i) for i in range(1, n + 1)}
    events[1].label = "Start"
    events[n].label = "End"
    activities = [
        AOAActivity(
            from_event=i,
            to_event=i + 1,
            activity_id=chr(64 + i),   # A, B, C …
            duration=durations[i - 1],
        )
        for i in range(1, n)
    ]
    return AOANetwork(
        events=events,
        activities=activities,
        start_event_id=1,
        end_event_id=n,
    )


def _six_activity_aon() -> List[Dict]:
    """The canonical 6-activity demo project (used throughout these tests)."""
    return [
        {"id": "A", "name": "Site Preparation", "duration": 3,  "predecessors": []},
        {"id": "B", "name": "Procurement",       "duration": 4,  "predecessors": []},
        {"id": "C", "name": "Foundation",        "duration": 5,  "predecessors": ["A"]},
        {"id": "D", "name": "Framing",           "duration": 6,  "predecessors": ["A"]},
        {"id": "E", "name": "Plumbing",          "duration": 2,  "predecessors": ["B", "C"]},
        {"id": "F", "name": "Finishing",         "duration": 3,  "predecessors": ["D", "E"]},
    ]


# ---------------------------------------------------------------------------
# TestAOAEvent
# ---------------------------------------------------------------------------

class TestAOAEvent:
    def test_slack_zero_when_equal_times(self):
        ev = AOAEvent(id=1, earliest_time=5.0, latest_time=5.0)
        assert ev.slack == 0.0

    def test_slack_positive(self):
        ev = AOAEvent(id=1, earliest_time=3.0, latest_time=7.0)
        assert ev.slack == pytest.approx(4.0)

    def test_is_critical_zero_slack(self):
        ev = AOAEvent(id=1, earliest_time=5.0, latest_time=5.0)
        assert ev.is_critical is True

    def test_is_critical_positive_slack(self):
        ev = AOAEvent(id=1, earliest_time=3.0, latest_time=7.0)
        assert ev.is_critical is False

    def test_default_times_are_zero(self):
        ev = AOAEvent(id=99)
        assert ev.earliest_time == 0.0
        assert ev.latest_time == 0.0
        assert ev.is_critical is True   # 0-0=0 → critical by default


# ---------------------------------------------------------------------------
# TestAOAActivity
# ---------------------------------------------------------------------------

class TestAOAActivity:
    def test_defaults(self):
        a = AOAActivity(from_event=1, to_event=2, activity_id="A")
        assert a.duration == 0.0
        assert a.is_dummy is False
        assert a.is_critical is False
        assert a.total_float == 0.0

    def test_dummy_flag(self):
        d = AOAActivity(from_event=1, to_event=3, activity_id="D_1_3", is_dummy=True)
        assert d.is_dummy is True


# ---------------------------------------------------------------------------
# TestAOANetworkTopology
# ---------------------------------------------------------------------------

class TestAOANetworkTopology:
    def test_topo_order_chain(self):
        net = _make_chain([3, 5])
        order = net._topo_event_order()
        assert order.index(1) < order.index(2) < order.index(3)

    def test_incoming_correct(self):
        net = _make_chain([3, 5])
        assert net._incoming(2)[0].activity_id == "A"
        assert net._incoming(1) == []

    def test_outgoing_correct(self):
        net = _make_chain([3, 5])
        assert net._outgoing(1)[0].activity_id == "A"
        assert net._outgoing(3) == []

    def test_real_activities_excludes_dummies(self):
        net = _make_chain([3])
        dummy = AOAActivity(from_event=1, to_event=2, activity_id="D_1_2", is_dummy=True)
        net.activities.append(dummy)
        real = net.real_activities()
        assert all(not a.is_dummy for a in real)
        assert len(real) == 1


# ---------------------------------------------------------------------------
# TestAOANetworkCPMChain
# ---------------------------------------------------------------------------

class TestAOANetworkCPMChain:
    """CPM on a simple A→B chain (1→2→3), dur 3+5=8."""

    def setup_method(self):
        self.net = _make_chain([3, 5])
        self.net.run_cpm()

    def test_project_duration(self):
        assert self.net.project_duration == pytest.approx(8.0)

    def test_forward_pass(self):
        assert self.net.events[1].earliest_time == pytest.approx(0.0)
        assert self.net.events[2].earliest_time == pytest.approx(3.0)
        assert self.net.events[3].earliest_time == pytest.approx(8.0)

    def test_backward_pass(self):
        assert self.net.events[3].latest_time == pytest.approx(8.0)
        assert self.net.events[2].latest_time == pytest.approx(3.0)
        assert self.net.events[1].latest_time == pytest.approx(0.0)

    def test_all_critical(self):
        for a in self.net.activities:
            assert a.total_float == pytest.approx(0.0)
            assert a.is_critical is True

    def test_free_float_is_zero_on_chain(self):
        for a in self.net.activities:
            assert a.free_float == pytest.approx(0.0)

    def test_early_finish(self):
        a_act = next(a for a in self.net.activities if a.activity_id == "A")
        assert a_act.early_finish == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# TestAOANetworkCPMParallel
# ---------------------------------------------------------------------------

class TestAOANetworkCPMParallel:
    """
    Two parallel paths: A(1→2, dur=3) and B(1→3, dur=6).
    Both converge to event 4 via dummies (2→4, 3→4, dur=0).
    Critical path: B (dur=6).  A has TF=3.
    """

    def setup_method(self):
        ev1 = AOAEvent(id=1, label="Start")
        ev2 = AOAEvent(id=2)
        ev3 = AOAEvent(id=3)
        ev4 = AOAEvent(id=4, label="End")
        a_act = AOAActivity(from_event=1, to_event=2, activity_id="A", duration=3)
        b_act = AOAActivity(from_event=1, to_event=3, activity_id="B", duration=6)
        d1    = AOAActivity(from_event=2, to_event=4, activity_id="D1", duration=0, is_dummy=True)
        d2    = AOAActivity(from_event=3, to_event=4, activity_id="D2", duration=0, is_dummy=True)
        self.net = AOANetwork(
            events={1: ev1, 2: ev2, 3: ev3, 4: ev4},
            activities=[a_act, b_act, d1, d2],
            start_event_id=1,
            end_event_id=4,
        )
        self.net.run_cpm()

    def test_project_duration(self):
        assert self.net.project_duration == pytest.approx(6.0)

    def test_event_times(self):
        assert self.net.events[1].earliest_time == pytest.approx(0.0)
        assert self.net.events[2].earliest_time == pytest.approx(3.0)
        assert self.net.events[3].earliest_time == pytest.approx(6.0)
        assert self.net.events[4].earliest_time == pytest.approx(6.0)

    def test_b_zero_float(self):
        b = next(a for a in self.net.activities if a.activity_id == "B")
        assert b.total_float == pytest.approx(0.0)
        assert b.is_critical is True

    def test_a_has_float(self):
        a = next(a for a in self.net.activities if a.activity_id == "A")
        assert a.total_float == pytest.approx(3.0)
        assert a.is_critical is False

    def test_critical_path_activities(self):
        cp_ids = {a.activity_id for a in self.net.critical_path_activities()}
        assert "B" in cp_ids
        assert "A" not in cp_ids


# ---------------------------------------------------------------------------
# TestAOANetworkCPMDemo
# ---------------------------------------------------------------------------

class TestAOANetworkCPMDemo:
    """CPM on the 6-activity demo project (verified against Ground Truth)."""

    def setup_method(self):
        net = aon_to_aoa(_six_activity_aon())
        net.run_cpm()
        self.net = net

    def test_project_duration_13(self):
        assert self.net.project_duration == pytest.approx(13.0)

    def test_critical_activities_A_C_E_F(self):
        cp = {a.activity_id for a in self.net.critical_path_activities()}
        assert cp == {"A", "C", "E", "F"}

    def test_activity_D_float_1(self):
        d = next(a for a in self.net.real_activities() if a.activity_id == "D")
        assert d.total_float == pytest.approx(1.0)
        assert d.is_critical is False

    def test_activity_B_float_4(self):
        b = next(a for a in self.net.real_activities() if a.activity_id == "B")
        assert b.total_float == pytest.approx(4.0)

    def test_start_event_ET_0(self):
        start = self.net.events[self.net.start_event_id]
        assert start.earliest_time == pytest.approx(0.0)

    def test_end_event_ET_13(self):
        end = self.net.events[self.net.end_event_id]
        assert end.earliest_time == pytest.approx(13.0)
        assert end.latest_time == pytest.approx(13.0)

    def test_dummy_activities_present(self):
        dummies = [a for a in self.net.activities if a.is_dummy]
        assert len(dummies) == 4   # 2 for E's merge + 2 for F's merge

    def test_critical_dummies(self):
        """The critical dummy D_4_8 (C -> merge for E) must have TF=0."""
        crit_dummies = [a for a in self.net.activities if a.is_dummy and a.is_critical]
        assert len(crit_dummies) >= 2   # at least 2 critical dummies


# ---------------------------------------------------------------------------
# TestNetworkConverterAONtoAOA
# ---------------------------------------------------------------------------

class TestNetworkConverterAONtoAOA:
    def test_empty_list_returns_minimal_network(self):
        net = aon_to_aoa([])
        assert len(net.events) == 2
        assert len(net.activities) == 0

    def test_single_activity_two_events(self):
        acts = [{"id": "A", "duration": 5, "predecessors": []}]
        net = aon_to_aoa(acts)
        assert len(net.real_activities()) == 1
        # Start event + A's exit event (labelled End)
        assert len(net.events) == 2

    def test_chain_simple(self):
        """A → B: A's exit event should be B's from_event (no dummy needed)."""
        acts = [
            {"id": "A", "duration": 3, "predecessors": []},
            {"id": "B", "duration": 5, "predecessors": ["A"]},
        ]
        net = aon_to_aoa(acts)
        real = net.real_activities()
        assert len(real) == 2
        a_act = next(a for a in real if a.activity_id == "A")
        b_act = next(a for a in real if a.activity_id == "B")
        # Simple chain: B starts from A's exit event directly
        assert a_act.to_event == b_act.from_event
        # No dummies required
        assert len(net.activities) == 2

    def test_fan_out_no_dummy(self):
        """A → B and A → C: both leave A's exit event, no dummies."""
        acts = [
            {"id": "A", "duration": 3, "predecessors": []},
            {"id": "B", "duration": 4, "predecessors": ["A"]},
            {"id": "C", "duration": 2, "predecessors": ["A"]},
        ]
        net = aon_to_aoa(acts)
        b_act = next(a for a in net.real_activities() if a.activity_id == "B")
        c_act = next(a for a in net.real_activities() if a.activity_id == "C")
        a_act = next(a for a in net.real_activities() if a.activity_id == "A")
        assert b_act.from_event == a_act.to_event
        assert c_act.from_event == a_act.to_event

    def test_merge_inserts_dummies(self):
        """C depends on A and B → at least one dummy is inserted."""
        acts = [
            {"id": "A", "duration": 3, "predecessors": []},
            {"id": "B", "duration": 4, "predecessors": []},
            {"id": "C", "duration": 2, "predecessors": ["A", "B"]},
        ]
        net = aon_to_aoa(acts)
        dummies = [a for a in net.activities if a.is_dummy]
        assert len(dummies) >= 1

    def test_merge_inserts_two_dummies_for_two_parallel_preds(self):
        """C with preds={A,B} → exactly 2 dummies (one from each)."""
        acts = [
            {"id": "A", "duration": 3, "predecessors": []},
            {"id": "B", "duration": 4, "predecessors": []},
            {"id": "C", "duration": 2, "predecessors": ["A", "B"]},
        ]
        net = aon_to_aoa(acts)
        # A and B exit to different events → merge event + 2 dummies
        dummies = [a for a in net.activities if a.is_dummy]
        assert len(dummies) == 2

    def test_multiple_end_activities_get_single_end_event(self):
        """Two unconnected activities both end → one end event with dummies."""
        acts = [
            {"id": "A", "duration": 3, "predecessors": []},
            {"id": "B", "duration": 4, "predecessors": []},
        ]
        net = aon_to_aoa(acts)
        # Should have exactly one end event
        end_evs = [eid for eid, ev in net.events.items()
                   if ev.label == "End"]
        assert len(end_evs) == 1
        # Should have 2 dummies (one from each activity to end event)
        dummies = [a for a in net.activities if a.is_dummy]
        assert len(dummies) == 2

    def test_predecessors_as_comma_string(self):
        """Predecessors given as 'A,B' string should parse correctly."""
        acts = [
            {"id": "A", "duration": 3, "predecessors": []},
            {"id": "B", "duration": 4, "predecessors": []},
            {"id": "C", "duration": 2, "predecessors": "A,B"},
        ]
        net = aon_to_aoa(acts)
        net.run_cpm()
        # Should succeed; CPM should give a valid project duration
        assert net.project_duration > 0

    def test_starts_and_end_labels(self):
        acts = [{"id": "A", "duration": 5, "predecessors": []}]
        net = aon_to_aoa(acts)
        assert net.events[net.start_event_id].label == "Start"
        assert net.events[net.end_event_id].label == "End"

    def test_cycle_raises_value_error(self):
        acts = [
            {"id": "A", "duration": 3, "predecessors": ["B"]},
            {"id": "B", "duration": 4, "predecessors": ["A"]},
        ]
        with pytest.raises(ValueError, match="cycle"):
            aon_to_aoa(acts)

    def test_start_end_nodes_in_activity_list_ignored(self):
        """If the caller passes START/END pseudo-activities, they are skipped."""
        acts = [
            {"id": "START", "duration": 0, "predecessors": []},
            {"id": "A",     "duration": 5, "predecessors": []},
            {"id": "END",   "duration": 0, "predecessors": ["A"]},
        ]
        net = aon_to_aoa(acts)
        real_ids = {a.activity_id for a in net.real_activities()}
        assert "A" in real_ids
        assert "START" not in real_ids
        assert "END" not in real_ids


# ---------------------------------------------------------------------------
# TestNetworkConverterAOAtoAON
# ---------------------------------------------------------------------------

class TestNetworkConverterAOAtoAON:
    def test_chain_back_to_single_predecessor(self):
        """A→B chain in AOA: aoa_to_aon should give B.predecessors == ['A']."""
        aon = [
            {"id": "A", "duration": 3, "predecessors": []},
            {"id": "B", "duration": 5, "predecessors": ["A"]},
        ]
        net   = aon_to_aoa(aon)
        back  = aoa_to_aon(net)
        b_rec = next(r for r in back if r["id"] == "B")
        assert sorted(b_rec["predecessors"]) == ["A"]

    def test_start_activities_have_no_predecessors(self):
        aon = _six_activity_aon()
        net = aon_to_aoa(aon)
        back = aoa_to_aon(net)
        start_acts = {r["id"]: r for r in back if not r["predecessors"]}
        assert "A" in start_acts
        assert "B" in start_acts

    def test_dummies_not_in_result(self):
        aon = _six_activity_aon()
        net = aon_to_aoa(aon)
        back = aoa_to_aon(net)
        ids = {r["id"] for r in back}
        assert not any(i.startswith("D_") for i in ids)

    def test_activity_count_matches_original(self):
        aon = _six_activity_aon()
        net = aon_to_aoa(aon)
        back = aoa_to_aon(net)
        assert len(back) == len(aon)


# ---------------------------------------------------------------------------
# TestConverterRoundTrip
# ---------------------------------------------------------------------------

class TestConverterRoundTrip:
    """AON → AOA → AON should preserve activity ids, durations, and
    relative precedence relationships."""

    def _round_trip(self, aon):
        net = aon_to_aoa(aon)
        net.run_cpm()
        return aoa_to_aon(net)

    def test_ids_preserved(self):
        aon = _six_activity_aon()
        back = self._round_trip(aon)
        original_ids = {a["id"] for a in aon}
        back_ids     = {a["id"] for a in back}
        assert original_ids == back_ids

    def test_durations_preserved(self):
        aon = _six_activity_aon()
        back = self._round_trip(aon)
        orig_dur = {a["id"]: a["duration"] for a in aon}
        for r in back:
            assert r["duration"] == pytest.approx(orig_dur[r["id"]]), \
                f"Duration mismatch for {r['id']}"

    def test_critical_path_same(self):
        aon = _six_activity_aon()
        net = aon_to_aoa(aon)
        net.run_cpm()
        cp_ids = {a.activity_id for a in net.critical_path_activities()}
        # CPM on round-tripped list must give the same critical path
        net2 = aon_to_aoa(aoa_to_aon(net))
        net2.run_cpm()
        cp_ids2 = {a.activity_id for a in net2.critical_path_activities()}
        assert cp_ids == cp_ids2

    def test_project_duration_same_after_round_trip(self):
        aon = _six_activity_aon()
        net = aon_to_aoa(aon)
        net.run_cpm()
        pd1 = net.project_duration

        net2 = aon_to_aoa(aoa_to_aon(net))
        net2.run_cpm()
        assert net2.project_duration == pytest.approx(pd1)


# ---------------------------------------------------------------------------
# TestAOACPMGroundTruth — verify against aoa_demo.json
# ---------------------------------------------------------------------------

class TestAOACPMGroundTruth:
    """Load the demo JSON and compare computed CPM against the embedded ground truth."""

    @pytest.fixture(autouse=True)
    def load_demo(self):
        demo_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "demos", "v2", "aoa_demo.json"
        )
        with open(demo_path, encoding="utf-8") as fh:
            self.demo = json.load(fh)
        acts = self.demo["data"]["activities"]
        self.net = aon_to_aoa(acts)
        self.net.run_cpm()
        self.gt = self.demo["data"]["aoa_ground_truth"]

    def test_project_duration(self):
        assert self.net.project_duration == pytest.approx(self.gt["project_duration"])

    def test_critical_path_ids(self):
        cp = {a.activity_id for a in self.net.critical_path_activities()}
        assert cp == set(self.gt["critical_path_activity_ids"])

    def test_event_ET_values(self):
        for ev_gt in self.gt["events"]:
            ev = self.net.events.get(ev_gt["id"])
            assert ev is not None, f"Event {ev_gt['id']} not found"
            assert ev.earliest_time == pytest.approx(ev_gt["ET"]), \
                f"ET mismatch for event {ev_gt['id']}"

    def test_event_LT_values(self):
        for ev_gt in self.gt["events"]:
            ev = self.net.events.get(ev_gt["id"])
            assert ev is not None
            assert ev.latest_time == pytest.approx(ev_gt["LT"]), \
                f"LT mismatch for event {ev_gt['id']}"

    def test_real_activity_total_floats(self):
        real_map = {a.activity_id: a for a in self.net.real_activities()}
        for ra_gt in self.gt["real_activities_aoa"]:
            aid = ra_gt["activity_id"]
            a = real_map.get(aid)
            assert a is not None, f"Activity {aid} not found"
            assert a.total_float == pytest.approx(ra_gt["TF"]), \
                f"TF mismatch for {aid}: got {a.total_float}, expected {ra_gt['TF']}"

    def test_dummy_count_matches(self):
        dummies = [a for a in self.net.activities if a.is_dummy]
        assert len(dummies) == len(self.gt["dummy_activities"])


# ---------------------------------------------------------------------------
# TestAOAStepGenerators  (smoke tests — verify no exceptions)
# ---------------------------------------------------------------------------

class TestAOAStepGenerators:
    @pytest.fixture(autouse=True)
    def build_network(self):
        self.net = aon_to_aoa(_six_activity_aon())
        self.net.run_cpm()

    def test_event_numbering_steps_returns_list(self):
        from pmhelper.core.aoa_step_generator import event_numbering_steps
        steps = event_numbering_steps(self.net)
        assert isinstance(steps, list)
        assert len(steps) >= 1

    def test_dummy_activity_steps_when_dummies_exist(self):
        from pmhelper.core.aoa_step_generator import dummy_activity_steps
        steps = dummy_activity_steps(self.net)
        assert isinstance(steps, list)
        assert len(steps) >= 1
        # Should mention the dummy count
        assert not any("no dummy" in s.result.lower() for s in steps)

    def test_dummy_activity_steps_no_dummies(self):
        """A simple chain has no dummies — step should say so."""
        from pmhelper.core.aoa_step_generator import dummy_activity_steps
        chain_net = _make_chain([3, 5])
        chain_net.run_cpm()
        steps = dummy_activity_steps(chain_net)
        assert any("no dummy" in s.result.lower() for s in steps)

    def test_forward_pass_steps_returns_list(self):
        from pmhelper.core.aoa_step_generator import forward_pass_steps
        steps = forward_pass_steps(self.net)
        assert isinstance(steps, list)
        assert len(steps) >= 2   # header + summary

    def test_backward_pass_steps_returns_list(self):
        from pmhelper.core.aoa_step_generator import backward_pass_steps
        steps = backward_pass_steps(self.net)
        assert isinstance(steps, list)
        assert len(steps) >= 2

    def test_critical_path_steps_returns_list(self):
        from pmhelper.core.aoa_step_generator import critical_path_steps
        steps = critical_path_steps(self.net)
        assert isinstance(steps, list)
        assert len(steps) >= 2

    def test_critical_path_steps_mention_duration(self):
        from pmhelper.core.aoa_step_generator import critical_path_steps
        steps = critical_path_steps(self.net)
        # The summary step should mention the project duration of 13 (in interpretation)
        summary = steps[-1]
        assert "13" in summary.interpretation

    def test_all_step_titles_are_strings(self):
        from pmhelper.core.aoa_step_generator import (
            event_numbering_steps, dummy_activity_steps,
            forward_pass_steps, backward_pass_steps, critical_path_steps,
        )
        all_fns = [
            event_numbering_steps, dummy_activity_steps,
            forward_pass_steps, backward_pass_steps, critical_path_steps,
        ]
        for fn in all_fns:
            for step in fn(self.net):
                assert isinstance(step.title, str) and step.title


# ---------------------------------------------------------------------------
# TestNetworkTabModule — smoke import tests (no GUI)
# ---------------------------------------------------------------------------

class TestNetworkTabModule:
    def test_network_tab_importable(self):
        from pmhelper.gui.tabs.network_tab import NetworkTab
        assert NetworkTab is not None

    def test_aoa_available_flag_is_true(self):
        from pmhelper.gui.tabs.network_tab import AOA_AVAILABLE
        assert AOA_AVAILABLE is True

    def test_network_tab_has_draw_aoa_diagram(self):
        from pmhelper.gui.tabs.network_tab import NetworkTab
        assert hasattr(NetworkTab, "_draw_aoa_diagram")

    def test_network_tab_has_aoa_event_layout(self):
        from pmhelper.gui.tabs.network_tab import NetworkTab
        assert hasattr(NetworkTab, "_aoa_event_layout")

    def test_aoa_network_builder_importable(self):
        from pmhelper.core.aoa_network_builder import AOAEvent, AOAActivity, AOANetwork
        assert AOAEvent and AOAActivity and AOANetwork

    def test_network_converter_importable(self):
        from pmhelper.core.network_converter import aon_to_aoa, aoa_to_aon
        assert aon_to_aoa and aoa_to_aon

    def test_aoa_step_generator_importable(self):
        from pmhelper.core.aoa_step_generator import (
            event_numbering_steps, dummy_activity_steps,
            forward_pass_steps, backward_pass_steps, critical_path_steps,
        )
        assert event_numbering_steps and critical_path_steps
