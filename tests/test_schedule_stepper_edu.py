"""Tests for ScheduleStepperWidget detection logic.

These tests exercise the step-completion detection without
requiring a live Tk event loop — we mock the main_window
and input_tab objects to feed data into the stepper.
"""

import pytest
from unittest.mock import MagicMock, PropertyMock
from dataclasses import dataclass, field
from typing import List

# Import the stepper (no Tk dependency in detection logic)
from pmhelper.gui.widgets.schedule_stepper_edu import ScheduleStepperWidget


# ── Helpers ──────────────────────────────────────────────────────────

def _make_activity(id="A", duration="5", predecessors="",
                   resource_demand="0", optimistic="0",
                   most_likely="0", pessimistic="0"):
    """Build an activity dict matching get_activities_data() format."""
    return {
        "id": id,
        "activity": f"Task {id}",
        "duration": duration,
        "predecessors": predecessors,
        "min_duration": "",
        "crash_cost": "",
        "resource_demand": resource_demand,
        "normal_cost": "",
        "optimistic": optimistic,
        "most_likely": most_likely,
        "pessimistic": pessimistic,
    }


def _make_main_window(activities=None, results_data=None,
                      input_mode="deterministic", wbs_tree=None):
    """Build a mock main_window with the attributes the stepper reads."""
    mw = MagicMock()
    mw._input_tab_edu = MagicMock()
    mw._input_tab_edu.get_activities_data.return_value = activities or []
    mw._input_tab_edu.current_mode = input_mode
    mw.results_data = results_data
    mw.state = MagicMock()
    mw.state.wbs_tree = wbs_tree
    return mw


@dataclass
class _FakeWBSNode:
    id: str
    parent_id: str = ""
    sort_order: int = 0


@dataclass
class _FakeWBSTree:
    nodes: List[_FakeWBSNode] = field(default_factory=list)

    def get_roots(self):
        return [n for n in self.nodes if n.parent_id == ""]

    def get_children(self, parent_id):
        return sorted(
            [n for n in self.nodes if n.parent_id == parent_id],
            key=lambda n: n.sort_order)


def _make_stepper(main_window):
    """Create a stepper without Tk — we only test _detect_steps()."""
    # We can't instantiate the widget without Tk, so we create a
    # bare object and set the attributes manually.
    stepper = object.__new__(ScheduleStepperWidget)
    stepper._main_window = main_window
    stepper._badges = []
    stepper._tooltip_window = None
    return stepper


# ── Tests ────────────────────────────────────────────────────────────

class TestStepDetection:
    """Tests for _detect_steps() logic."""

    def test_empty_project_all_pending(self):
        """Empty project → steps 1,2,4,5 pending; step 3 optional."""
        mw = _make_main_window()
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[1] == "pending"
        assert states[2] == "pending"
        assert states[3] == "optional"
        assert states[4] == "pending"
        assert states[5] == "pending"

    def test_one_activity_steps_1_2_green(self):
        """One activity with duration → steps 1,2,4 complete (2 trivially)."""
        acts = [_make_activity("A", duration="5")]
        mw = _make_main_window(activities=acts)
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[1] == "complete"
        assert states[2] == "complete"  # ≤1 activity → trivially sequenced
        assert states[4] == "complete"

    def test_two_activities_no_predecessors_step2_pending(self):
        """Two activities, no predecessors → step 2 pending."""
        acts = [_make_activity("A"), _make_activity("B")]
        mw = _make_main_window(activities=acts)
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[1] == "complete"
        assert states[2] == "pending"

    def test_two_activities_with_predecessors_step2_complete(self):
        """Two activities, B depends on A → step 2 complete."""
        acts = [_make_activity("A"), _make_activity("B", predecessors="A")]
        mw = _make_main_window(activities=acts)
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[2] == "complete"

    def test_resources_optional_when_zero(self):
        """No resource demand → step 3 is 'optional', not 'pending'."""
        acts = [_make_activity("A", resource_demand="0")]
        mw = _make_main_window(activities=acts)
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[3] == "optional"

    def test_resources_complete_when_set(self):
        """Resource demand > 0 → step 3 complete."""
        acts = [_make_activity("A", resource_demand="3")]
        mw = _make_main_window(activities=acts)
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[3] == "complete"

    def test_durations_cpm_all_set(self):
        """CPM mode: all durations > 0 → step 4 complete."""
        acts = [_make_activity("A", duration="5"),
                _make_activity("B", duration="3")]
        mw = _make_main_window(activities=acts, input_mode="deterministic")
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[4] == "complete"

    def test_durations_cpm_missing_one(self):
        """CPM mode: one duration missing → step 4 pending."""
        acts = [_make_activity("A", duration="5"),
                _make_activity("B", duration="0")]
        mw = _make_main_window(activities=acts, input_mode="deterministic")
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[4] == "pending"

    def test_durations_pert_all_set(self):
        """PERT mode: all optimistic > 0 → step 4 complete."""
        acts = [_make_activity("A", optimistic="2", most_likely="5", pessimistic="8"),
                _make_activity("B", optimistic="1", most_likely="3", pessimistic="6")]
        mw = _make_main_window(activities=acts, input_mode="probabilistic")
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[4] == "complete"

    def test_durations_pert_missing(self):
        """PERT mode: one activity missing optimistic → step 4 pending."""
        acts = [_make_activity("A", optimistic="2"),
                _make_activity("B", optimistic="0")]
        mw = _make_main_window(activities=acts, input_mode="probabilistic")
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[4] == "pending"

    def test_step5_pending_no_results(self):
        """No results_data → step 5 pending."""
        acts = [_make_activity("A")]
        mw = _make_main_window(activities=acts, results_data=None)
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[5] == "pending"

    def test_step5_complete_with_results(self):
        """results_data present → step 5 complete."""
        acts = [_make_activity("A")]
        mw = _make_main_window(activities=acts, results_data={"graph": "G"})
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[5] == "complete"

    def test_wbs_tree_satisfies_step1(self):
        """PG mode: WBS tree with children → step 1 complete even with no activities."""
        root = _FakeWBSNode(id="root", parent_id="")
        child = _FakeWBSNode(id="c1", parent_id="root")
        wbs = _FakeWBSTree(nodes=[root, child])
        mw = _make_main_window(activities=[], wbs_tree=wbs)
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[1] == "complete"

    def test_wbs_tree_root_only_not_enough(self):
        """WBS tree with only root (no children) → step 1 still pending."""
        root = _FakeWBSNode(id="root", parent_id="")
        wbs = _FakeWBSTree(nodes=[root])
        mw = _make_main_window(activities=[], wbs_tree=wbs)
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[1] == "pending"

    def test_no_main_window_all_pending(self):
        """No main_window → all pending/optional."""
        s = _make_stepper(None)
        states = s._detect_steps()
        assert states[1] == "pending"
        assert states[5] == "pending"

    def test_non_numeric_duration_treated_as_zero(self):
        """Non-numeric duration → treated as 0 → step 4 pending."""
        acts = [_make_activity("A", duration="abc")]
        mw = _make_main_window(activities=acts)
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[4] == "pending"

    def test_non_numeric_resource_treated_as_zero(self):
        """Non-numeric resource_demand → treated as 0 → step 3 optional."""
        acts = [_make_activity("A", resource_demand="abc")]
        mw = _make_main_window(activities=acts)
        s = _make_stepper(mw)
        states = s._detect_steps()
        assert states[3] == "optional"


class TestToFloat:
    """Tests for the _to_float static helper."""

    def test_int(self):
        assert ScheduleStepperWidget._to_float(5) == 5.0

    def test_float_string(self):
        assert ScheduleStepperWidget._to_float("3.14") == 3.14

    def test_empty_string(self):
        assert ScheduleStepperWidget._to_float("") == 0.0

    def test_none(self):
        assert ScheduleStepperWidget._to_float(None) == 0.0

    def test_garbage(self):
        assert ScheduleStepperWidget._to_float("abc") == 0.0
