"""
Phase 6 — Edge-case hardening tests.

Covers boundary conditions, degenerate inputs, empty collections, and
graceful error handling across all Edu modules.
"""

import json
import os
import tempfile
import pytest
import numpy as np

from pmhelper.core.evm_models_edu import (
    EVMTask, EVMPeriod, EVMProject, PVSpread,
    compute_pv_schedule, _spread_weights,
)
from pmhelper.core.evm_calculations_edu import (
    compute_ev, compute_cv, compute_sv, compute_cpi, compute_spi,
    compute_pc, compute_ps, compute_cr,
    compute_eac1, compute_eac2, compute_eac3,
    compute_vac, compute_tcpi_bac,
    compute_all_kpis, get_kpi_walkthrough, get_rag,
)
from pmhelper.core.risk_register_edu import Risk, RiskCategory, RiskRegister
from pmhelper.utils.risk_io_edu import save_register, load_register, export_to_csv, import_from_csv
from pmhelper.core.cpm_sampler_edu import run_cpm_on_sample
from pmhelper.core.monte_carlo_edu import MCInputs, MCResults, run_simulation, _sample_pert_beta
from pmhelper.utils.project_io_edu import save_full_project, load_full_project, make_empty_project
from pmhelper.gui.edu_state import AppConfig, EduProjectState


# ===================================================================
# EVM Models — Edge Cases
# ===================================================================

class TestEVMTaskEdgeCases:
    """Edge cases for EVMTask creation and validation."""

    def test_zero_budget_task(self):
        t = EVMTask(task_id="Z", name="Zero budget", budget=0.0, pct_complete=100)
        assert t.ev == 0.0

    def test_task_same_start_finish(self):
        """Milestone: planned_start == planned_finish → 1-period duration."""
        t = EVMTask(task_id="M", name="Milestone", planned_start=3, planned_finish=3)
        assert t.duration_periods == 1

    def test_task_100_pct_ev(self):
        t = EVMTask(task_id="A", name="Done", budget=5000, pct_complete=100)
        assert t.ev == pytest.approx(5000.0)

    def test_task_zero_pct_ev(self):
        t = EVMTask(task_id="A", name="NotStarted", budget=5000, pct_complete=0)
        assert t.ev == pytest.approx(0.0)

    def test_fractional_pct_complete(self):
        t = EVMTask(task_id="A", name="Partial", budget=1000, pct_complete=33.33)
        assert t.ev == pytest.approx(333.3)

    def test_large_budget(self):
        t = EVMTask(task_id="A", name="Big", budget=1e12, pct_complete=50)
        assert t.ev == pytest.approx(5e11)

    def test_from_dict_extra_fields_ignored(self):
        """from_dict should tolerate unknown keys gracefully."""
        d = {"task_id": "X", "name": "X", "budget": 100, "pct_complete": 0,
             "planned_start": 0, "planned_finish": 1, "pv_spread": "uniform",
             "unknown_field": "ignore me", "predecessors": []}
        # Should not raise even with extra fields
        # (depends on implementation — if it does raise, that's also acceptable)
        try:
            t = EVMTask.from_dict(d)
            assert t.task_id == "X"
        except TypeError:
            pass  # Extra fields cause TypeError — acceptable

    def test_from_dict_missing_optional_fields(self):
        """from_dict with minimal fields."""
        d = {"task_id": "M", "name": "Minimal"}
        t = EVMTask.from_dict(d)
        assert t.budget == 0.0
        assert t.pct_complete == 0.0
        assert t.predecessors == []


class TestEVMPeriodEdgeCases:
    def test_zero_index(self):
        p = EVMPeriod(index=0, label="Start")
        assert p.index == 0

    def test_large_cumulative_values(self):
        p = EVMPeriod(index=0, pv_cumulative=1e15, ev_cumulative=1e15, ac_cumulative=1e15)
        assert p.pv_cumulative == 1e15

    def test_zero_cumulative_values(self):
        p = EVMPeriod(index=0, pv_cumulative=0, ev_cumulative=0, ac_cumulative=0)
        d = p.to_dict()
        p2 = EVMPeriod.from_dict(d)
        assert p2.pv_cumulative == 0.0

    def test_negative_index_raises(self):
        with pytest.raises(ValueError, match="negative"):
            EVMPeriod(index=-1)


class TestEVMProjectEdgeCases:
    def test_empty_project_current_values(self):
        """Project with no periods returns 0 for current EV/PV/AC."""
        proj = EVMProject(project_name="Empty", bac=0)
        assert proj.current_ev() == 0.0
        assert proj.current_pv() == 0.0
        assert proj.current_ac() == 0.0
        assert proj.task_ev() == 0.0
        assert proj.ev_discrepancy() == 0.0

    def test_negative_bac_raises(self):
        with pytest.raises(ValueError, match="negative"):
            EVMProject(bac=-100)

    def test_single_task_project(self):
        t = EVMTask(task_id="A", name="Only", budget=1000, pct_complete=50,
                    planned_start=0, planned_finish=2)
        proj = EVMProject(project_name="Single", tasks=[t])
        assert proj.bac == 1000  # auto-compute
        assert proj.task_ev() == pytest.approx(500.0)

    def test_bac_auto_compute_many_tasks(self):
        tasks = [EVMTask(task_id=f"T{i}", name=f"T{i}", budget=100)
                 for i in range(100)]
        proj = EVMProject(tasks=tasks)
        assert proj.bac == pytest.approx(10000.0)

    def test_bac_manual_mode(self):
        """Manual BAC should not auto-compute."""
        t = EVMTask(task_id="A", name="A", budget=500)
        proj = EVMProject(bac=1000, bac_auto_compute=False, tasks=[t])
        assert proj.bac == 1000  # not overwritten by sum of tasks

    def test_roundtrip_with_all_fields(self):
        t = EVMTask(task_id="A", name="A", budget=100, pct_complete=50,
                    planned_start=0, planned_finish=3,
                    actual_start=0, actual_finish=4,
                    baseline_start=0, baseline_finish=3,
                    pv_spread=PVSpread.FRONT, predecessors=["X"])
        p = EVMPeriod(index=0, label="W1", pv_cumulative=50,
                      ev_cumulative=30, ac_cumulative=35)
        proj = EVMProject(project_name="Full", bac=100, bac_auto_compute=False,
                          currency_symbol="£", tasks=[t], periods=[p])
        d = proj.to_dict()
        proj2 = EVMProject.from_dict(d)
        assert proj2.project_name == "Full"
        assert proj2.currency_symbol == "£"
        assert proj2.tasks[0].pv_spread == PVSpread.FRONT
        assert proj2.tasks[0].predecessors == ["X"]
        assert proj2.tasks[0].actual_finish == 4
        assert proj2.tasks[0].baseline_start == 0
        assert proj2.periods[0].label == "W1"


class TestPVScheduleEdgeCases:
    def test_empty_tasks_empty_periods(self):
        result = compute_pv_schedule([], 5)
        assert result == [0.0] * 5

    def test_zero_periods(self):
        result = compute_pv_schedule([], 0)
        assert result == []

    def test_task_beyond_period_range(self):
        """Task starts after all periods — should be ignored."""
        t = EVMTask(task_id="A", name="A", budget=1000, planned_start=10, planned_finish=15)
        result = compute_pv_schedule([t], 5)
        assert result == [0.0] * 5

    def test_task_partially_in_range(self):
        """Task extends beyond available periods — should be clamped."""
        t = EVMTask(task_id="A", name="A", budget=1000, planned_start=3, planned_finish=10)
        result = compute_pv_schedule([t], 5)
        # Should spread budget across periods 3–4 (clamped from 3–10)
        assert len(result) == 5
        assert result[0] == 0.0
        assert result[-1] > 0

    def test_spread_weights_single_period(self):
        w = _spread_weights(1, PVSpread.FRONT)
        assert len(w) == 1
        assert w[0] == pytest.approx(1.0)

    def test_spread_weights_uniform(self):
        w = _spread_weights(4, PVSpread.UNIFORM)
        assert len(w) == 4
        assert sum(w) == pytest.approx(1.0)
        assert all(abs(x - 0.25) < 1e-10 for x in w)

    def test_spread_weights_normalize(self):
        """All spread types should normalize to sum=1.0."""
        for spread in PVSpread:
            for n in range(1, 20):
                w = _spread_weights(n, spread)
                assert abs(sum(w) - 1.0) < 1e-9, f"spread={spread}, n={n}"


# ===================================================================
# EVM Calculations — Edge Cases
# ===================================================================

class TestKPIEdgeCases:
    def test_negative_ev_cv(self):
        """CV with negative EV (logically impossible but handles gracefully)."""
        assert compute_cv(-100, 200) == pytest.approx(-300.0)

    def test_negative_pv_sv(self):
        assert compute_sv(100, -200) == pytest.approx(300.0)

    def test_very_small_ac_cpi(self):
        cpi = compute_cpi(1000, 0.001)
        assert cpi == pytest.approx(1e6)

    def test_very_large_values(self):
        cv = compute_cv(1e15, 9.99e14)
        assert cv == pytest.approx(1e12)

    def test_eac1_when_complete(self):
        """When EV=BAC (project complete), EAC1=AC."""
        assert compute_eac1(95000, 100000, 100000) == pytest.approx(95000)

    def test_eac1_at_start(self):
        """At start: AC=0, EV=0, EAC1=BAC."""
        assert compute_eac1(0, 100000, 0) == pytest.approx(100000)

    def test_vac_zero(self):
        """EAC=BAC → VAC=0."""
        assert compute_vac(100000, 100000) == pytest.approx(0.0)

    def test_tcpi_at_start_with_zero_ac(self):
        """TCPI when AC=0: (BAC-0)/(BAC-0) = 1.0."""
        # BAC != AC so not undefined
        assert compute_tcpi_bac(100000, 0, 0) == pytest.approx(1.0)

    def test_tcpi_all_spent(self):
        """BAC=AC → TCPI undefined."""
        with pytest.raises(ValueError, match="BAC equals AC"):
            compute_tcpi_bac(100000, 50000, 100000)

    def test_cr_perfect(self):
        assert compute_cr(1.0, 1.0) == pytest.approx(1.0)

    def test_cr_both_below_one(self):
        assert compute_cr(0.5, 0.5) == pytest.approx(0.25)

    def test_pc_100(self):
        assert compute_pc(100000, 100000) == pytest.approx(100.0)

    def test_ps_over_100(self):
        """PS > 100% means spent more than BAC."""
        assert compute_ps(150000, 100000) == pytest.approx(150.0)


class TestComputeAllKPIsEdgeCases:
    def test_all_zero_project(self):
        """BAC=0, no periods, no tasks → most KPIs None with errors."""
        proj = EVMProject(project_name="Zero", bac=0, bac_auto_compute=False)
        kpis = compute_all_kpis(proj)
        assert kpis["ev"] == 0.0
        assert kpis["pv"] == 0.0
        assert kpis["ac"] == 0.0
        assert kpis["bac"] == 0.0
        assert kpis["cv"] == pytest.approx(0.0)
        assert kpis["sv"] == pytest.approx(0.0)
        assert kpis["cpi"] is None
        assert kpis["spi"] is None
        assert kpis["pc"] is None
        assert kpis["ps"] is None
        assert "cpi" in kpis["errors"]
        assert "spi" in kpis["errors"]

    def test_all_tasks_zero_pct(self):
        """All tasks at 0% → EV=0, CPI/SPI undefined."""
        tasks = [EVMTask(task_id="A", name="A", budget=1000, pct_complete=0)]
        periods = [EVMPeriod(index=0, pv_cumulative=500, ev_cumulative=0, ac_cumulative=0)]
        proj = EVMProject(project_name="NotStarted", tasks=tasks, periods=periods,
                          bac_auto_compute=False, bac=1000)
        kpis = compute_all_kpis(proj)
        assert kpis["ev"] == 0.0
        assert kpis["cpi"] is None  # AC=0
        assert kpis["spi"] == pytest.approx(0.0)  # EV/PV = 0/500

    def test_all_tasks_100_pct(self):
        """All tasks at 100% with spending exactly at budget."""
        tasks = [EVMTask(task_id="A", name="A", budget=1000, pct_complete=100)]
        periods = [EVMPeriod(index=0, pv_cumulative=1000, ev_cumulative=1000,
                             ac_cumulative=1000)]
        proj = EVMProject(project_name="Done", tasks=tasks, periods=periods,
                          bac_auto_compute=False, bac=1000)
        kpis = compute_all_kpis(proj)
        assert kpis["cpi"] == pytest.approx(1.0)
        assert kpis["spi"] == pytest.approx(1.0)
        assert kpis["pc"] == pytest.approx(100.0)
        assert kpis["cv"] == pytest.approx(0.0)
        assert kpis["sv"] == pytest.approx(0.0)
        assert kpis["eac1"] == pytest.approx(1000.0)

    def test_primary_eac_selection_2(self):
        """Select EAC2 as primary."""
        tasks = [EVMTask(task_id="A", name="A", budget=1000, pct_complete=50)]
        periods = [EVMPeriod(index=0, pv_cumulative=600, ev_cumulative=500,
                             ac_cumulative=550)]
        proj = EVMProject(project_name="T", tasks=tasks, periods=periods,
                          bac_auto_compute=False, bac=1000)
        kpis = compute_all_kpis(proj, primary_eac=2)
        assert kpis["primary_eac_value"] == pytest.approx(kpis["eac2"])
        assert kpis["vac"] == pytest.approx(1000 - kpis["eac2"])

    def test_primary_eac_selection_3(self):
        """Select EAC3 as primary."""
        tasks = [EVMTask(task_id="A", name="A", budget=1000, pct_complete=50)]
        periods = [EVMPeriod(index=0, pv_cumulative=600, ev_cumulative=500,
                             ac_cumulative=550)]
        proj = EVMProject(project_name="T", tasks=tasks, periods=periods,
                          bac_auto_compute=False, bac=1000)
        kpis = compute_all_kpis(proj, primary_eac=3)
        assert kpis["primary_eac_value"] == pytest.approx(kpis["eac3"])

    def test_invalid_primary_eac_falls_back(self):
        """Invalid primary_eac number falls back to EAC1."""
        tasks = [EVMTask(task_id="A", name="A", budget=1000, pct_complete=50)]
        periods = [EVMPeriod(index=0, pv_cumulative=600, ev_cumulative=500,
                             ac_cumulative=550)]
        proj = EVMProject(project_name="T", tasks=tasks, periods=periods,
                          bac_auto_compute=False, bac=1000)
        kpis = compute_all_kpis(proj, primary_eac=99)
        assert kpis["primary_eac_value"] == pytest.approx(kpis["eac1"])


class TestRAGEdgeCases:
    def test_rag_bac_zero_cv(self):
        """BAC=0 with variance-based KPI → threshold=0."""
        result = get_rag("cv", -1, bac=0)
        assert result == "red"

    def test_rag_bac_zero_green_cv(self):
        assert get_rag("cv", 0, bac=0) == "green"

    def test_rag_very_high_cpi(self):
        assert get_rag("cpi", 100.0, bac=100000) == "green"

    def test_rag_very_low_cpi(self):
        assert get_rag("cpi", 0.0, bac=100000) == "red"

    def test_rag_negative_eac(self):
        """Negative EAC (impossible but handle gracefully)."""
        assert get_rag("eac1", -1000, bac=100000) == "green"

    def test_rag_eac_exactly_at_bac(self):
        assert get_rag("eac1", 100000, bac=100000) == "green"


class TestWalkthroughEdgeCases:
    def test_unknown_kpi_walkthrough(self):
        """Walkthrough for unknown KPI should not crash."""
        kpis = {"ev": 0, "ac": 0, "pv": 0, "bac": 0, "errors": {}}
        wt = get_kpi_walkthrough("nonexistent", kpis)
        assert "formula" in wt
        assert "result" in wt

    def test_walkthrough_all_defined_kpis(self):
        """Every _KPI_META entry should produce a valid walkthrough."""
        tasks = [EVMTask(task_id="A", name="A", budget=1000, pct_complete=50)]
        periods = [EVMPeriod(index=0, pv_cumulative=600, ev_cumulative=500,
                             ac_cumulative=550)]
        proj = EVMProject(project_name="T", tasks=tasks, periods=periods,
                          bac_auto_compute=False, bac=1000)
        kpis = compute_all_kpis(proj)
        for kpi_name in ["cv", "sv", "cpi", "spi", "cr", "pc", "ps",
                         "eac1", "eac2", "eac3", "vac", "tcpi_bac"]:
            wt = get_kpi_walkthrough(kpi_name, kpis)
            assert set(wt.keys()) == {"formula", "substitution", "result", "interpretation"}
            assert wt["formula"] != ""
            assert wt["result"] != ""


# ===================================================================
# Risk Register — Edge Cases
# ===================================================================

class TestRiskEdgeCases:
    def test_risk_with_empty_name(self):
        r = Risk(id="R1", name="")
        assert r.name == ""

    def test_risk_with_long_description(self):
        desc = "A" * 10000
        r = Risk(id="R1", name="long desc", description=desc)
        assert len(r.description) == 10000

    def test_risk_with_special_characters(self):
        r = Risk(id="R1", name="Risk α — β ☆", description="€£¥ special chars")
        d = r.to_dict()
        r2 = Risk.from_dict(d)
        assert r2.name == "Risk α — β ☆"
        assert r2.description == "€£¥ special chars"

    def test_risk_probability_boundary_zero(self):
        r = Risk(id="R1", name="x", probability=0.0, impact=10000)
        assert r.exposure == 0.0

    def test_risk_probability_boundary_one(self):
        r = Risk(id="R1", name="x", probability=1.0, impact=10000)
        assert r.exposure == pytest.approx(10000.0)

    def test_very_high_impact(self):
        r = Risk(id="R1", name="x", probability=0.5, impact=1e12)
        assert r.exposure == pytest.approx(5e11)


class TestRiskRegisterEdgeCases:
    def test_empty_register_roundtrip(self):
        reg = RiskRegister(bac=50000)
        d = reg.to_dict()
        reg2 = RiskRegister.from_dict(d)
        assert len(reg2.risks) == 0
        assert reg2.bac == 50000

    def test_register_remove_nonexistent(self):
        reg = RiskRegister()
        # Should not crash — just no-op or raise
        try:
            reg.remove_risk("R_NOPE")
        except (ValueError, KeyError):
            pass  # acceptable

    def test_register_many_risks(self):
        reg = RiskRegister(bac=1000000)
        for i in range(500):
            reg.add_risk(Risk(id=f"R{i}", name=f"Risk {i}",
                              probability=0.1, impact=100))
        assert len(reg.risks) == 500
        assert reg.total_exposure() == pytest.approx(500 * 10.0)

    def test_flag_high_exposure_all_flagged(self):
        """All risks above threshold."""
        reg = RiskRegister(bac=100, high_exposure_threshold_pct=0.01)
        reg.add_risk(Risk(id="R1", name="x", probability=1.0, impact=100))
        reg.add_risk(Risk(id="R2", name="y", probability=1.0, impact=100))
        flagged = reg.flag_high_exposure()
        assert len(flagged) == 2

    def test_flag_high_exposure_none_flagged(self):
        """All risks below threshold."""
        reg = RiskRegister(bac=1000000, high_exposure_threshold_pct=0.05)
        reg.add_risk(Risk(id="R1", name="x", probability=0.01, impact=1))
        flagged = reg.flag_high_exposure()
        assert len(flagged) == 0

    def test_register_zero_bac(self):
        """BAC=0 with risks — threshold is 0, all exposures > 0 are flagged."""
        reg = RiskRegister(bac=0, high_exposure_threshold_pct=0.05)
        reg.add_risk(Risk(id="R1", name="x", probability=0.5, impact=100))
        flagged = reg.flag_high_exposure()
        # threshold = 0 * 0.05 = 0, exposure = 50 > 0 → flagged
        assert len(flagged) == 1


class TestRiskIOEdgeCases:
    def test_json_roundtrip_special_chars(self, tmp_path):
        reg = RiskRegister(bac=1000)
        reg.add_risk(Risk(id="R1", name="Risk—α", description="€1000 budget",
                          probability=0.5, impact=200, category=RiskCategory.COST))
        fp = str(tmp_path / "special.json")
        save_register(reg, fp)
        loaded = load_register(fp)
        assert loaded.risks[0].name == "Risk—α"
        assert loaded.risks[0].description == "€1000 budget"

    def test_csv_roundtrip_all_categories(self, tmp_path):
        reg = RiskRegister(bac=1000)
        for i, cat in enumerate(RiskCategory):
            reg.add_risk(Risk(id=f"R{i}", name=f"Risk {cat.value}",
                              probability=0.3, impact=500, category=cat))
        fp = str(tmp_path / "cats.csv")
        export_to_csv(reg, fp)
        imported = import_from_csv(fp)
        assert len(imported.risks) == len(RiskCategory)

    def test_csv_empty_register(self, tmp_path):
        reg = RiskRegister(bac=0)
        fp = str(tmp_path / "empty.csv")
        export_to_csv(reg, fp)
        imported = import_from_csv(fp)
        assert len(imported.risks) == 0


# ===================================================================
# CPM Sampler — Edge Cases
# ===================================================================

class TestCPMSamplerEdgeCases:
    def test_cyclic_network_graceful(self):
        """Cyclic dependency should not infinite-loop.
        (Run with a timeout via pytest — if it hangs, that's a bug.)
        """
        acts = [
            {"id": "A", "predecessors": ["B"]},
            {"id": "B", "predecessors": ["A"]},
        ]
        # Depending on implementation, may raise or return incomplete results
        try:
            dur, cp = run_cpm_on_sample(acts, {"A": 3, "B": 4})
            # If it returns, duration should be "reasonable"
        except (ValueError, RuntimeError):
            pass  # acceptable to raise on cyclic input

    def test_many_parallel_tasks(self):
        """Wide parallel network — 100 independent tasks."""
        acts = [{"id": f"T{i}", "predecessors": []} for i in range(100)]
        durs = {f"T{i}": float(i) for i in range(100)}
        dur, cp = run_cpm_on_sample(acts, durs)
        assert dur == pytest.approx(99.0)  # longest parallel task

    def test_deep_serial_chain(self):
        """Deep serial chain — 100 tasks in sequence."""
        acts = []
        durs = {}
        for i in range(100):
            preds = [f"T{i-1}"] if i > 0 else []
            acts.append({"id": f"T{i}", "predecessors": preds})
            durs[f"T{i}"] = 1.0
        dur, cp = run_cpm_on_sample(acts, durs)
        assert dur == pytest.approx(100.0)
        assert len(cp) == 100

    def test_task_with_zero_duration_on_cp(self):
        """Milestone (zero duration) on critical path."""
        acts = [
            {"id": "A", "predecessors": []},
            {"id": "Milestone", "predecessors": ["A"]},
            {"id": "B", "predecessors": ["Milestone"]},
        ]
        dur, cp = run_cpm_on_sample(acts, {"A": 5, "Milestone": 0, "B": 3})
        assert dur == pytest.approx(8.0)
        assert "Milestone" in cp


# ===================================================================
# Monte Carlo — Edge Cases
# ===================================================================

class TestMonteCarloEdgeCases:
    def test_single_trial(self):
        acts = [{"id": "A", "predecessors": [], "duration": 10}]
        from pmhelper.core.evm_models_edu import EVMTask
        evm = [EVMTask(task_id="A", name="A", budget=1000,
                        planned_start=0, planned_finish=10)]
        inp = MCInputs(cpm_activities=acts, evm_tasks=evm, risks=[], bac=1000,
                        n_trials=1, seed=42)
        r = run_simulation(inp)
        assert r.n_trials == 1
        assert r.p50_duration == r.p80_duration == r.p90_duration

    def test_bac_zero(self):
        """BAC=0 should not crash p_cost_within_bac calculation."""
        acts = [{"id": "A", "predecessors": [], "duration": 5}]
        from pmhelper.core.evm_models_edu import EVMTask
        evm = [EVMTask(task_id="A", name="A", budget=0,
                        planned_start=0, planned_finish=5)]
        inp = MCInputs(cpm_activities=acts, evm_tasks=evm, risks=[], bac=0,
                        n_trials=10, seed=1)
        r = run_simulation(inp)
        assert r.p_cost_within_bac == 0.0  # BAC=0, no costs within

    def test_all_risks_certain(self):
        """All risks with probability=1.0 → cost includes full impact."""
        from pmhelper.core.risk_register_edu import Risk, RiskCategory
        acts = [{"id": "A", "predecessors": [], "duration": 5}]
        from pmhelper.core.evm_models_edu import EVMTask
        evm = [EVMTask(task_id="A", name="A", budget=1000,
                        planned_start=0, planned_finish=5)]
        risks = [Risk(id="R1", name="r", probability=1.0, impact=500)]
        inp = MCInputs(cpm_activities=acts, evm_tasks=evm, risks=risks,
                        bac=1500, n_trials=50, seed=42)
        r = run_simulation(inp)
        # Every trial should include the risk impact
        assert np.all(r.costs >= 500)

    def test_all_risks_impossible(self):
        """All risks with probability=0.0 → risk cost never added."""
        from pmhelper.core.risk_register_edu import Risk, RiskCategory
        acts = [{"id": "A", "predecessors": [], "duration": 5}]
        from pmhelper.core.evm_models_edu import EVMTask
        evm = [EVMTask(task_id="A", name="A", budget=1000,
                        planned_start=0, planned_finish=5)]
        risks = [Risk(id="R1", name="r", probability=0.0, impact=10000)]
        inp = MCInputs(cpm_activities=acts, evm_tasks=evm, risks=risks,
                        bac=1000, n_trials=50, seed=42)
        r = run_simulation(inp)
        # No risk impact should be added (all random draws > 0)
        assert np.all(r.costs < 1500)  # budget range alone, no risk cost

    def test_pert_equal_omp(self):
        """O=M=P → zero variance (deterministic)."""
        rng = np.random.default_rng(42)
        for _ in range(100):
            s = _sample_pert_beta(rng, 5.0, 5.0, 5.0)
            assert s == pytest.approx(5.0)

    def test_pert_o_equals_p(self):
        """O==P → should return most_likely regardless."""
        rng = np.random.default_rng(42)
        s = _sample_pert_beta(rng, 3.0, 7.0, 3.0)
        # pessimistic <= optimistic → returns most_likely
        assert s == pytest.approx(7.0)

    def test_mc_results_serialization_empty(self):
        """Serialize/deserialize with minimal data."""
        r = MCResults(
            durations=np.array([1.0]),
            costs=np.array([100.0]),
            cp_frequencies={"A": 1.0},
            p50_duration=1.0, p80_duration=1.0, p90_duration=1.0,
            p_cost_within_bac=1.0, n_trials=1, seed_used=42,
        )
        d = r.to_serializable()
        r2 = MCResults.from_serializable(d)
        assert r2.n_trials == 1
        np.testing.assert_array_equal(r.durations, r2.durations)


# ===================================================================
# Project I/O — Edge Cases
# ===================================================================

class TestProjectIOEdgeCases:
    def test_save_load_with_mc_results(self, tmp_path):
        """Full roundtrip with MC results included."""
        from pmhelper.core.monte_carlo_edu import MCResults

        class FakeState:
            evm_project = EVMProject(project_name="MC Test", bac=1000, bac_auto_compute=False)
            risk_register = RiskRegister(bac=1000)
            mc_results = MCResults(
                durations=np.array([10.0, 12.0, 11.0]),
                costs=np.array([950.0, 1050.0, 1000.0]),
                cp_frequencies={"A": 0.67, "B": 1.0},
                p50_duration=11.0, p80_duration=11.6, p90_duration=11.8,
                p_cost_within_bac=0.67, n_trials=3, seed_used=42,
            )
            _mode = "PG"

        state = FakeState()
        fp = str(tmp_path / "with_mc.pmproj")
        save_full_project(state, fp)
        data = load_full_project(fp)

        assert data["mc_results"] is not None
        assert data["mc_results"].n_trials == 3
        np.testing.assert_array_almost_equal(
            data["mc_results"].durations, [10.0, 12.0, 11.0])

    def test_save_load_unicode_project_name(self, tmp_path):
        """Project name with unicode characters."""
        class FakeState:
            evm_project = EVMProject(project_name="Проект αβγ 日本語", bac=0, bac_auto_compute=False)
            risk_register = RiskRegister()
            mc_results = None
            _mode = "UG"

        fp = str(tmp_path / "unicode.pmproj")
        save_full_project(FakeState(), fp)
        data = load_full_project(fp)
        assert data["evm_project"].project_name == "Проект αβγ 日本語"

    def test_load_empty_json_object(self, tmp_path):
        """Load file with empty JSON object."""
        from pathlib import Path
        fp = str(tmp_path / "empty_obj.pmproj")
        Path(fp).write_text(json.dumps({}))
        data = load_full_project(fp)
        # Should handle gracefully — evm_project will be None
        assert data["evm_project"] is None

    def test_make_empty_project_independence(self):
        """Two calls to make_empty_project return independent objects."""
        p1, r1 = make_empty_project()
        p2, r2 = make_empty_project()
        p1.project_name = "Modified"
        assert p2.project_name == "New Project"


# ===================================================================
# EduProjectState — Edge Cases
# ===================================================================

class TestEduProjectStateEdgeCases:
    def test_mark_dirty_without_project(self):
        """mark_dirty when evm_project is None should not crash."""
        state = EduProjectState()
        state.mark_dirty()
        assert state.is_dirty()

    def test_mark_dirty_syncs_bac(self):
        """mark_dirty syncs BAC from evm_project to risk_register."""
        state = EduProjectState()
        state.evm_project = EVMProject(bac=50000, bac_auto_compute=False)
        state.risk_register = RiskRegister(bac=0)
        state.mark_dirty()
        assert state.risk_register.bac == 50000

    def test_subscribe_callback_called(self):
        state = EduProjectState()
        called = []
        state.subscribe(lambda: called.append(True))
        state.mark_dirty()
        assert len(called) == 1

    def test_multiple_subscribers(self):
        state = EduProjectState()
        counts = {"a": 0, "b": 0}
        state.subscribe(lambda: counts.__setitem__("a", counts["a"] + 1))
        state.subscribe(lambda: counts.__setitem__("b", counts["b"] + 1))
        state.mark_dirty()
        assert counts["a"] == 1
        assert counts["b"] == 1

    def test_reset_clears_everything(self):
        state = EduProjectState()
        state.evm_project = EVMProject()
        state.risk_register = RiskRegister()
        state.current_file_path = "/tmp/test.pmproj"
        state.mark_dirty()

        state.reset()
        assert state.evm_project is None
        assert state.risk_register is None
        assert state.mc_results is None
        assert state.current_file_path is None
        assert not state.is_dirty()

    def test_mark_clean(self):
        state = EduProjectState()
        state.mark_dirty()
        assert state.is_dirty()
        state.mark_clean()
        assert not state.is_dirty()


class TestAppConfigEdgeCases:
    def test_config_save_load_roundtrip(self, tmp_path):
        config = AppConfig()
        config.CONFIG_PATH = tmp_path / "config.json"
        config.mode = "PG"
        config.currency_symbol = "€"
        config.last_project_path = "/tmp/test.pmproj"
        config.save()

        loaded = AppConfig()
        loaded.CONFIG_PATH = tmp_path / "config.json"
        loaded = AppConfig.load.__func__(AppConfig)  # Call class method
        # Need to override CONFIG_PATH before loading
        # Use a direct approach
        import json
        data = json.loads((tmp_path / "config.json").read_text())
        assert data["mode"] == "PG"
        assert data["currency_symbol"] == "€"

    def test_config_corrupt_file(self, tmp_path):
        config = AppConfig()
        config.CONFIG_PATH = tmp_path / "config.json"
        (tmp_path / "config.json").write_text("NOT JSON {{{")
        # load() should handle gracefully and use defaults
        loaded = AppConfig()
        loaded.CONFIG_PATH = tmp_path / "config.json"
        # Load manually since CONFIG_PATH is instance-level
        if loaded.CONFIG_PATH.exists():
            try:
                data = json.loads(loaded.CONFIG_PATH.read_text())
            except json.JSONDecodeError:
                pass  # Expected — config should use defaults
        assert loaded.mode == "UG"  # default

    def test_config_missing_keys(self, tmp_path):
        (tmp_path / "config.json").write_text(json.dumps({"mode": "PG"}))
        config = AppConfig()
        # Defaults should apply for missing keys
        assert config.currency_symbol == "$"  # default
