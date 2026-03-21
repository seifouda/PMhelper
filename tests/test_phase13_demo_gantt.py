"""Tests for Phase 13 — UG Demo expansion + Gantt professional restyle."""

import json
import os
import sys
import pytest

# ---------------------------------------------------------------------------
# Locate the demo file
# ---------------------------------------------------------------------------
_DEMO_DIR = os.path.join(
    os.path.dirname(__file__), os.pardir,
    "src", "pmhelper", "demos_edu")
_UG_DEMO = os.path.join(_DEMO_DIR, "office_renovation_ug.pmproj")


# ===================================================================
# 13.1  UG Demo — structure & completeness
# ===================================================================

class TestUGDemoStructure:
    """Verify the expanded UG demo file is well-formed."""

    @pytest.fixture(autouse=True)
    def _load(self):
        with open(_UG_DEMO, encoding="utf-8") as f:
            self.data = json.load(f)
        self.cpm = self.data["cpm_activities"]
        self.evm = self.data["evm_project"]

    # --- CPM activities ---

    def test_at_least_15_cpm_activities(self):
        assert len(self.cpm) >= 15

    def test_all_ids_unique(self):
        ids = [a["id"] for a in self.cpm]
        assert len(ids) == len(set(ids))

    def test_durations_range(self):
        durations = [int(a["duration"]) for a in self.cpm]
        assert min(durations) >= 2, "Min duration should be >= 2"
        assert max(durations) >= 6, "Max duration should be >= 6"

    def test_min_duration_populated(self):
        for a in self.cpm:
            assert a["min_duration"] not in ("", None), \
                f"{a['id']} missing min_duration"
            assert int(a["min_duration"]) < int(a["duration"]), \
                f"{a['id']}: min_duration must be < duration"

    def test_crash_cost_populated(self):
        for a in self.cpm:
            assert a["crash_cost"] not in ("", None), \
                f"{a['id']} missing crash_cost"
            assert int(a["crash_cost"]) > int(a["normal_cost"]), \
                f"{a['id']}: crash_cost must be > normal_cost"

    def test_resource_demand_populated(self):
        for a in self.cpm:
            assert a["resource_demand"] not in ("", None), \
                f"{a['id']} missing resource_demand"

    def test_normal_cost_populated(self):
        for a in self.cpm:
            assert a["normal_cost"] not in ("", None), \
                f"{a['id']} missing normal_cost"

    def test_predecessor_references_valid(self):
        all_ids = {a["id"] for a in self.cpm}
        for a in self.cpm:
            preds = [p.strip() for p in a["predecessors"].split(",") if p.strip()]
            for p in preds:
                assert p in all_ids, f"{a['id']} references unknown predecessor {p}"

    def test_at_least_one_start_activity(self):
        """At least one activity has no predecessors."""
        starts = [a for a in self.cpm if not a["predecessors"].strip()]
        assert len(starts) >= 1

    # --- EVM data ---

    def test_evm_task_count_matches_cpm(self):
        assert len(self.evm["tasks"]) == len(self.cpm)

    def test_bac_at_least_200k(self):
        assert self.evm["bac"] >= 200000

    def test_evm_periods_at_least_14(self):
        assert len(self.evm["periods"]) >= 14

    def test_evm_periods_monotonically_increasing(self):
        pvs = [p["pv_cumulative"] for p in self.evm["periods"]]
        for i in range(1, len(pvs)):
            assert pvs[i] > pvs[i - 1], f"PV not increasing at period {i}"

    # --- Risk register ---

    def test_risk_register_bac_matches(self):
        assert self.data["risk_register"]["bac"] == self.evm["bac"]

    def test_at_least_5_risks(self):
        assert len(self.data["risk_register"]["risks"]) >= 5

    # --- Config ---

    def test_mode_is_ug(self):
        assert self.data["app_config"]["mode"] == "UG"

    def test_cpm_mode_is_deterministic(self):
        assert self.data["cpm_mode"] == "deterministic"


# ===================================================================
# 13.2 / 13.3  Gantt Tab Edu — imports, figure size, export method
# ===================================================================

class TestGanttTabEduModule:
    """Verify Gantt tab module can be imported and key attributes exist."""

    def test_import(self):
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        assert GanttTabEdu is not None

    def test_has_export_data_method(self):
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        assert hasattr(GanttTabEdu, '_export_data')

    def test_has_draw_cpm_gantt_method(self):
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        assert hasattr(GanttTabEdu, '_draw_cpm_gantt')

    def test_has_draw_predecessor_arrows_method(self):
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        assert hasattr(GanttTabEdu, '_draw_predecessor_arrows')
