"""Tests for EVM data models — Phase 1."""

import pytest
from pmhelper.core.evm_models_edu import (
    EVMTask, EVMPeriod, EVMProject, PVSpread,
    compute_pv_schedule, _spread_weights,
)


class TestEVMTask:
    def test_basic_creation(self):
        t = EVMTask(task_id="A", name="Task A", budget=1000,
                    planned_start=0, planned_finish=3)
        assert t.task_id == "A"
        assert t.budget == 1000
        assert t.pv_spread == PVSpread.UNIFORM

    def test_ev_property(self):
        t = EVMTask(task_id="A", name="A", budget=1000, pct_complete=50,
                    planned_start=0, planned_finish=2)
        assert t.ev == 500.0

    def test_ev_zero_complete(self):
        t = EVMTask(task_id="A", name="A", budget=1000,
                    planned_start=0, planned_finish=0)
        assert t.ev == 0.0

    def test_ev_full_complete(self):
        t = EVMTask(task_id="A", name="A", budget=1000, pct_complete=100,
                    planned_start=0, planned_finish=0)
        assert t.ev == 1000.0

    def test_duration_periods(self):
        t = EVMTask(task_id="A", name="A", budget=100,
                    planned_start=2, planned_finish=5)
        assert t.duration_periods == 4

    def test_negative_budget_raises(self):
        with pytest.raises(ValueError, match="budget cannot be negative"):
            EVMTask(task_id="A", name="A", budget=-100,
                    planned_start=0, planned_finish=0)

    def test_pct_complete_over_100_raises(self):
        with pytest.raises(ValueError, match="pct_complete must be"):
            EVMTask(task_id="A", name="A", budget=100, pct_complete=101,
                    planned_start=0, planned_finish=0)

    def test_pct_complete_negative_raises(self):
        with pytest.raises(ValueError, match="pct_complete must be"):
            EVMTask(task_id="A", name="A", budget=100, pct_complete=-1,
                    planned_start=0, planned_finish=0)

    def test_finish_before_start_raises(self):
        with pytest.raises(ValueError, match="planned_finish.*< planned_start"):
            EVMTask(task_id="A", name="A", budget=100,
                    planned_start=5, planned_finish=2)

    def test_to_dict_roundtrip(self):
        t = EVMTask(task_id="X", name="Prep", budget=500, pct_complete=25,
                    planned_start=1, planned_finish=4, pv_spread=PVSpread.FRONT)
        d = t.to_dict()
        t2 = EVMTask.from_dict(d)
        assert t2.task_id == "X"
        assert t2.budget == 500
        assert t2.pv_spread == PVSpread.FRONT
        assert t2.pct_complete == 25

    def test_from_dict_defaults(self):
        d = {"task_id": "Z", "name": "Z"}
        t = EVMTask.from_dict(d)
        assert t.budget == 0.0
        assert t.pct_complete == 0.0
        assert t.pv_spread == PVSpread.UNIFORM
        assert t.predecessors == []

    def test_optional_fields(self):
        t = EVMTask(task_id="A", name="A", budget=100,
                    planned_start=0, planned_finish=2,
                    actual_start=1, actual_finish=3,
                    baseline_start=0, baseline_finish=2,
                    cpm_task_id="CPM_A")
        assert t.actual_start == 1
        assert t.baseline_finish == 2
        assert t.cpm_task_id == "CPM_A"


class TestEVMPeriod:
    def test_basic_creation(self):
        p = EVMPeriod(index=0, label="Week 1", pv_cumulative=100,
                      ev_cumulative=90, ac_cumulative=95)
        assert p.index == 0
        assert p.label == "Week 1"
        assert p.pv_cumulative == 100

    def test_negative_index_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            EVMPeriod(index=-1)

    def test_defaults(self):
        p = EVMPeriod(index=0)
        assert p.label == ""
        assert p.pv_cumulative == 0.0
        assert p.ev_cumulative == 0.0
        assert p.ac_cumulative == 0.0
        assert p.ev_source == "manual"

    def test_to_dict_roundtrip(self):
        p = EVMPeriod(index=3, label="Q1", pv_cumulative=500,
                      ev_cumulative=450, ac_cumulative=510, ev_source="computed")
        d = p.to_dict()
        p2 = EVMPeriod.from_dict(d)
        assert p2.index == 3
        assert p2.label == "Q1"
        assert p2.ev_source == "computed"


class TestEVMProject:
    def test_empty_project(self):
        proj = EVMProject()
        assert proj.project_name == "New Project"
        assert proj.bac == 0.0
        assert proj.current_ev() == 0.0
        assert proj.current_pv() == 0.0
        assert proj.current_ac() == 0.0
        assert proj.task_ev() == 0.0
        assert proj.ev_discrepancy() == 0.0

    def test_bac_auto_compute(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=100,
                    planned_start=0, planned_finish=1),
            EVMTask(task_id="B", name="B", budget=200,
                    planned_start=0, planned_finish=1),
        ]
        proj = EVMProject(tasks=tasks)
        assert proj.bac == 300.0

    def test_bac_manual(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=100,
                    planned_start=0, planned_finish=1),
        ]
        proj = EVMProject(bac=500, bac_auto_compute=False, tasks=tasks)
        assert proj.bac == 500.0  # not overridden

    def test_recompute_bac(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=100,
                    planned_start=0, planned_finish=0),
        ]
        proj = EVMProject(tasks=tasks)
        proj.tasks.append(EVMTask(task_id="B", name="B", budget=50,
                                   planned_start=0, planned_finish=0))
        proj.recompute_bac()
        assert proj.bac == 150.0

    def test_recompute_bac_manual_mode_no_change(self):
        proj = EVMProject(bac=999, bac_auto_compute=False)
        proj.tasks.append(EVMTask(task_id="A", name="A", budget=100,
                                   planned_start=0, planned_finish=0))
        proj.recompute_bac()
        assert proj.bac == 999  # no change because auto is off

    def test_negative_bac_raises(self):
        with pytest.raises(ValueError, match="BAC cannot be negative"):
            EVMProject(bac=-1, bac_auto_compute=False)

    def test_current_values_from_periods(self):
        periods = [
            EVMPeriod(index=0, pv_cumulative=100, ev_cumulative=80, ac_cumulative=90),
            EVMPeriod(index=1, pv_cumulative=200, ev_cumulative=190, ac_cumulative=210),
        ]
        proj = EVMProject(periods=periods)
        assert proj.current_pv() == 200
        assert proj.current_ev() == 190
        assert proj.current_ac() == 210

    def test_task_ev(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=1000, pct_complete=50,
                    planned_start=0, planned_finish=0),
            EVMTask(task_id="B", name="B", budget=500, pct_complete=100,
                    planned_start=0, planned_finish=0),
        ]
        proj = EVMProject(tasks=tasks)
        assert proj.task_ev() == 1000.0  # 500 + 500

    def test_ev_discrepancy(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=1000, pct_complete=50,
                    planned_start=0, planned_finish=0),
        ]
        periods = [
            EVMPeriod(index=0, ev_cumulative=400),  # task says 500
        ]
        proj = EVMProject(tasks=tasks, periods=periods)
        assert proj.ev_discrepancy() == pytest.approx(100.0)

    def test_to_dict_roundtrip(self):
        tasks = [
            EVMTask(task_id="A", name="Alpha", budget=1000, pct_complete=30,
                    planned_start=0, planned_finish=3, pv_spread=PVSpread.FRONT),
        ]
        periods = [
            EVMPeriod(index=0, label="W1", pv_cumulative=250,
                      ev_cumulative=200, ac_cumulative=230),
        ]
        proj = EVMProject(project_name="Test", tasks=tasks, periods=periods,
                          currency_symbol="€")
        d = proj.to_dict()
        proj2 = EVMProject.from_dict(d)
        assert proj2.project_name == "Test"
        assert proj2.currency_symbol == "€"
        assert len(proj2.tasks) == 1
        assert proj2.tasks[0].pv_spread == PVSpread.FRONT
        assert len(proj2.periods) == 1
        assert proj2.periods[0].label == "W1"

    def test_schema_version_preserved(self):
        proj = EVMProject(schema_version=2)
        d = proj.to_dict()
        assert d["schema_version"] == 2
        proj2 = EVMProject.from_dict(d)
        assert proj2.schema_version == 2


class TestComputePVSchedule:
    def test_uniform_single_task(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=400,
                    planned_start=0, planned_finish=3),
        ]
        pv = compute_pv_schedule(tasks, 4)
        assert len(pv) == 4
        assert pv[-1] == pytest.approx(400.0)
        # Uniform: each period gets 100, cumulative: 100, 200, 300, 400
        assert pv[0] == pytest.approx(100.0)
        assert pv[1] == pytest.approx(200.0)
        assert pv[2] == pytest.approx(300.0)
        assert pv[3] == pytest.approx(400.0)

    def test_two_tasks_overlap(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=200,
                    planned_start=0, planned_finish=1),
            EVMTask(task_id="B", name="B", budget=300,
                    planned_start=1, planned_finish=2),
        ]
        pv = compute_pv_schedule(tasks, 3)
        assert pv[-1] == pytest.approx(500.0)

    def test_empty_tasks(self):
        pv = compute_pv_schedule([], 5)
        assert pv == [0.0] * 5

    def test_task_beyond_periods(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=100,
                    planned_start=10, planned_finish=15),
        ]
        pv = compute_pv_schedule(tasks, 5)
        assert pv[-1] == 0.0

    def test_front_loaded(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=600,
                    planned_start=0, planned_finish=5,
                    pv_spread=PVSpread.FRONT),
        ]
        pv = compute_pv_schedule(tasks, 6)
        # Front loaded: more PV in first third
        assert pv[-1] == pytest.approx(600.0)
        third = 6 // 3  # 2
        first_third_pv = pv[third - 1]
        last_third_pv = pv[-1] - pv[2 * third - 1]
        assert first_third_pv > last_third_pv

    def test_back_loaded(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=600,
                    planned_start=0, planned_finish=5,
                    pv_spread=PVSpread.BACK),
        ]
        pv = compute_pv_schedule(tasks, 6)
        assert pv[-1] == pytest.approx(600.0)
        third = 6 // 3
        first_third_pv = pv[third - 1]
        last_third_pv = pv[-1] - pv[2 * third - 1]
        assert last_third_pv > first_third_pv


class TestSpreadWeights:
    def test_uniform(self):
        w = _spread_weights(4, PVSpread.UNIFORM)
        assert len(w) == 4
        assert sum(w) == pytest.approx(1.0)
        assert w[0] == pytest.approx(0.25)

    def test_single_period(self):
        w = _spread_weights(1, PVSpread.FRONT)
        assert w == [1.0]

    def test_front_sums_to_one(self):
        w = _spread_weights(9, PVSpread.FRONT)
        assert sum(w) == pytest.approx(1.0)

    def test_back_sums_to_one(self):
        w = _spread_weights(12, PVSpread.BACK)
        assert sum(w) == pytest.approx(1.0)
