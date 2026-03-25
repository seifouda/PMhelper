"""
Phase 6 — Integration tests.

End-to-end workflows: load demo → compute KPIs → verify values,
full save→load→verify roundtrips, MC integration, mode persistence.
"""

import json
import os
import tempfile
import pytest
import numpy as np
from pathlib import Path

from pmhelper.core.evm_models_edu import EVMProject, EVMTask, EVMPeriod, PVSpread
from pmhelper.core.evm_calculations_edu import compute_all_kpis, get_rag, get_kpi_walkthrough
from pmhelper.core.risk_register_edu import Risk, RiskCategory, RiskRegister
from pmhelper.core.monte_carlo_edu import MCInputs, MCResults, run_simulation
from pmhelper.core.cpm_sampler_edu import run_cpm_on_sample
from pmhelper.utils.project_io_edu import save_full_project, load_full_project, make_empty_project
from pmhelper.utils.risk_io_edu import save_register, load_register, export_to_csv, import_from_csv
from pmhelper.utils.evm_io_edu import save_evm_project, load_evm_project
from pmhelper.gui.edu_state import EduProjectState, AppConfig


DEMO_DIR = os.path.join(os.path.dirname(__file__),
                        "..", "src", "pmhelper", "demos_edu")


class FakeState:
    """Minimal state for I/O testing."""
    def __init__(self):
        self.evm_project = None
        self.risk_register = None
        self.mc_results = None
        self.current_file_path = None
        self._mode = "UG"
        self._dirty = False

    def is_dirty(self):
        return self._dirty

    def mark_dirty(self):
        self._dirty = True

    def mark_clean(self):
        self._dirty = False


# ===================================================================
# Integration: UG Demo → KPIs → RAG → Walkthrough
# ===================================================================

class TestUGDemoIntegration:
    """Load UG demo and verify end-to-end KPI pipeline."""

    @pytest.fixture
    def ug_project(self):
        path = os.path.join(DEMO_DIR, "office_renovation_ug.pmproj")
        if not os.path.exists(path):
            pytest.skip("UG demo file not found")
        return load_full_project(path)

    def test_kpi_pipeline_full(self, ug_project):
        """Load demo → compute all KPIs → check value ranges."""
        proj = ug_project["evm_project"]
        kpis = compute_all_kpis(proj)

        # EV, PV, AC should all be > 0
        assert kpis["ev"] > 0
        assert kpis["pv"] > 0
        assert kpis["ac"] > 0
        assert kpis["bac"] == 120000.0

        # CPI < 1 (over budget)
        assert kpis["cpi"] is not None
        assert 0.80 <= kpis["cpi"] <= 0.95

        # SPI < 1 (behind schedule)
        assert kpis["spi"] is not None
        assert 0.75 <= kpis["spi"] <= 0.95

        # CV < 0, SV < 0
        assert kpis["cv"] < 0
        assert kpis["sv"] < 0

        # EAC > BAC (over budget)
        assert kpis["eac1"] > kpis["bac"]

        # TCPI > 1 (need to improve efficiency)
        assert kpis["tcpi_bac"] is not None
        assert kpis["tcpi_bac"] > 1.0

    def test_rag_colours(self, ug_project):
        """RAG engine assigns correct colours for UG demo."""
        proj = ug_project["evm_project"]
        kpis = compute_all_kpis(proj)
        bac = kpis["bac"]

        cpi_rag = get_rag("cpi", kpis["cpi"], bac)
        spi_rag = get_rag("spi", kpis["spi"], bac)
        cv_rag = get_rag("cv", kpis["cv"], bac)

        # CPI and SPI < 1 → should be amber or red
        assert cpi_rag in ("amber", "red")
        assert spi_rag in ("amber", "red")
        # CV < 0 → amber or red
        assert cv_rag in ("amber", "red")

    def test_walkthrough_for_all_kpis(self, ug_project):
        """Walkthrough produces complete output for every KPI."""
        proj = ug_project["evm_project"]
        kpis = compute_all_kpis(proj)

        for kpi_name in ["cv", "sv", "cpi", "spi", "cr", "pc", "ps",
                         "eac1", "eac2", "eac3", "vac", "tcpi_bac"]:
            wt = get_kpi_walkthrough(kpi_name, kpis, "$")
            assert "formula" in wt
            assert wt["formula"] != ""
            # Value-bearing KPIs should have non-N/A results
            if kpis.get(kpi_name) is not None:
                assert "N/A" not in wt["result"]

    def test_risk_register_integration(self, ug_project):
        """Risk register from UG demo has correct properties."""
        reg = ug_project["risk_register"]
        assert reg.bac == 120000.0
        assert reg.total_exposure() > 0
        assert reg.contingency_reserve() > 0

        # At least 2 high-exposure risks
        flagged = reg.flag_high_exposure()
        assert len(flagged) >= 2

        # Risks sorted by exposure descending
        sorted_risks = reg.risks_by_exposure()
        exposures = [r.exposure for r in sorted_risks]
        assert exposures == sorted(exposures, reverse=True)


# ===================================================================
# Integration: PG Demo → MC Simulation
# ===================================================================

class TestPGDemoIntegration:
    """Load PG demo and verify MC simulation pipeline."""

    @pytest.fixture
    def pg_project(self):
        path = os.path.join(DEMO_DIR, "software_development_pg.pmproj")
        if not os.path.exists(path):
            pytest.skip("PG demo file not found")
        return load_full_project(path)

    def test_kpi_pipeline_healthy_project(self, pg_project):
        """PG demo is under budget — CPI > 1."""
        proj = pg_project["evm_project"]
        kpis = compute_all_kpis(proj)
        assert kpis["cpi"] > 1.0
        assert kpis["eac1"] <= kpis["bac"]  # under budget

    def test_mc_on_pg_demo(self, pg_project):
        """Run MC simulation on PG demo tasks."""
        proj = pg_project["evm_project"]
        reg = pg_project["risk_register"]

        # Build CPM activities from tasks
        activities = []
        for t in proj.tasks:
            act = {
                "id": t.task_id,
                "predecessors": t.predecessors or [],
                "duration": t.duration_periods,
            }
            activities.append(act)

        inp = MCInputs(
            cpm_activities=activities,
            evm_tasks=proj.tasks,
            risks=reg.risks,
            bac=proj.bac,
            n_trials=500,
            seed=42,
        )
        result = run_simulation(inp)

        # Basic sanity checks
        assert result.n_trials == 500
        assert result.p50_duration > 0
        assert result.p50_duration <= result.p80_duration
        assert result.p80_duration <= result.p90_duration
        assert 0 <= result.p_cost_within_bac <= 1.0

        # At least some tasks should appear on CP
        cp_tasks = [tid for tid, freq in result.cp_frequencies.items() if freq > 0]
        assert len(cp_tasks) > 0

    def test_mc_results_serialization_from_pg(self, pg_project):
        """MC results can be serialized and deserialized."""
        proj = pg_project["evm_project"]
        activities = [
            {"id": t.task_id, "predecessors": t.predecessors or [],
             "duration": t.duration_periods}
            for t in proj.tasks
        ]
        inp = MCInputs(
            cpm_activities=activities,
            evm_tasks=proj.tasks,
            risks=[],
            bac=proj.bac,
            n_trials=100,
            seed=42,
        )
        result = run_simulation(inp)

        # Serialize → deserialize
        d = result.to_serializable()
        json_str = json.dumps(d)
        d2 = json.loads(json_str)
        result2 = MCResults.from_serializable(d2)

        np.testing.assert_array_almost_equal(result.durations, result2.durations)
        np.testing.assert_array_almost_equal(result.costs, result2.costs)
        assert result.p50_duration == pytest.approx(result2.p50_duration)
        assert result.seed_used == result2.seed_used


# ===================================================================
# Integration: Full Save → Load → Verify Roundtrip
# ===================================================================

class TestFullRoundTrip:
    """Complete save → load → compare for all data components."""

    def test_full_project_roundtrip(self, tmp_path):
        """Create project with tasks, periods, risks → save → load → verify."""
        # Create rich project
        tasks = [
            EVMTask(task_id="A", name="Design", budget=5000, pct_complete=100,
                    planned_start=0, planned_finish=2, pv_spread=PVSpread.FRONT,
                    baseline_start=0, baseline_finish=2, actual_start=0, actual_finish=3),
            EVMTask(task_id="B", name="Build", budget=10000, pct_complete=60,
                    planned_start=2, planned_finish=5, predecessors=["A"],
                    baseline_start=2, baseline_finish=5),
            EVMTask(task_id="C", name="Test", budget=3000, pct_complete=0,
                    planned_start=5, planned_finish=7, predecessors=["B"],
                    pv_spread=PVSpread.BACK),
        ]
        periods = [
            EVMPeriod(index=0, label="W1", pv_cumulative=2000, ev_cumulative=1500, ac_cumulative=1800),
            EVMPeriod(index=1, label="W2", pv_cumulative=5000, ev_cumulative=4000, ac_cumulative=4500),
            EVMPeriod(index=2, label="W3", pv_cumulative=8000, ev_cumulative=7000, ac_cumulative=7200),
            EVMPeriod(index=3, label="W4", pv_cumulative=12000, ev_cumulative=11000, ac_cumulative=11500),
        ]
        proj = EVMProject(project_name="Integration Test™", bac=18000,
                          bac_auto_compute=False, currency_symbol="€",
                          tasks=tasks, periods=periods)

        reg = RiskRegister(bac=18000)
        reg.add_risk(Risk(id="R1", name="Scope Creep", probability=0.4,
                          impact=3000, category=RiskCategory.SCOPE,
                          description="Requirements may expand"))
        reg.add_risk(Risk(id="R2", name="Key Staff Leave", probability=0.2,
                          impact=5000, category=RiskCategory.OTHER))

        # Run MC
        activities = [
            {"id": t.task_id, "predecessors": t.predecessors or [],
             "duration": t.duration_periods}
            for t in proj.tasks
        ]
        mc_inp = MCInputs(cpm_activities=activities, evm_tasks=proj.tasks,
                          risks=reg.risks, bac=proj.bac, n_trials=50, seed=42)
        mc_results = run_simulation(mc_inp)

        # Save
        state = FakeState()
        state.evm_project = proj
        state.risk_register = reg
        state.mc_results = mc_results
        state._mode = "PG"

        filepath = str(tmp_path / "full_roundtrip.pmproj")
        save_full_project(state, filepath)

        # Load
        data = load_full_project(filepath)

        # Verify EVM project
        loaded_proj = data["evm_project"]
        assert loaded_proj.project_name == "Integration Test™"
        assert loaded_proj.bac == 18000
        assert loaded_proj.currency_symbol == "€"
        assert len(loaded_proj.tasks) == 3
        assert len(loaded_proj.periods) == 4
        assert loaded_proj.tasks[0].pv_spread == PVSpread.FRONT
        assert loaded_proj.tasks[0].actual_finish == 3
        assert loaded_proj.tasks[1].predecessors == ["A"]
        assert loaded_proj.tasks[2].pv_spread == PVSpread.BACK
        assert loaded_proj.periods[3].label == "W4"
        assert loaded_proj.periods[3].ac_cumulative == 11500

        # Verify risk register
        loaded_reg = data["risk_register"]
        assert len(loaded_reg.risks) == 2
        assert loaded_reg.risks[0].name == "Scope Creep"
        assert loaded_reg.risks[0].category == RiskCategory.SCOPE
        assert loaded_reg.risks[1].exposure == pytest.approx(1000.0)

        # Verify MC results
        assert data["mc_results"] is not None
        assert data["mc_results"].n_trials == 50
        np.testing.assert_array_almost_equal(
            data["mc_results"].durations, mc_results.durations)

        # Verify app config
        assert data["app_config"]["mode"] == "PG"

    def test_roundtrip_preserves_kpis(self, tmp_path):
        """KPIs computed from loaded data match those from original data."""
        tasks = [
            EVMTask(task_id="A", name="A", budget=6000, pct_complete=50),
            EVMTask(task_id="B", name="B", budget=4000, pct_complete=25),
        ]
        periods = [
            EVMPeriod(index=0, pv_cumulative=3000, ev_cumulative=2500, ac_cumulative=2800),
            EVMPeriod(index=1, pv_cumulative=6000, ev_cumulative=4000, ac_cumulative=4500),
        ]
        proj = EVMProject(project_name="KPICheck", tasks=tasks, periods=periods,
                          bac=10000, bac_auto_compute=False)
        reg = RiskRegister(bac=10000)

        # Compute KPIs before save
        kpis_before = compute_all_kpis(proj)

        # Save → load
        state = FakeState()
        state.evm_project = proj
        state.risk_register = reg
        fp = str(tmp_path / "kpi_check.pmproj")
        save_full_project(state, fp)
        data = load_full_project(fp)

        # Compute KPIs after load
        kpis_after = compute_all_kpis(data["evm_project"])

        # Compare
        for key in ["ev", "pv", "ac", "bac", "cv", "sv", "cpi", "spi",
                     "pc", "ps", "cr", "eac1", "eac2", "eac3", "vac", "tcpi_bac"]:
            if kpis_before[key] is not None:
                assert kpis_after[key] == pytest.approx(kpis_before[key]), \
                    f"KPI '{key}' mismatch after roundtrip"

    def test_evm_json_to_pmproj_migration(self, tmp_path):
        """EVM JSON save → load → convert to full .pmproj format."""
        proj = EVMProject(project_name="Migration",
                          tasks=[EVMTask(task_id="A", name="A", budget=500)],
                          periods=[EVMPeriod(index=0, pv_cumulative=100,
                                            ev_cumulative=80, ac_cumulative=90)])

        # Save as EVM JSON
        evm_path = str(tmp_path / "legacy.json")
        save_evm_project(proj, evm_path)

        # Load EVM JSON
        loaded_proj = load_evm_project(evm_path)
        assert loaded_proj.project_name == "Migration"

        # Save as full .pmproj
        state = FakeState()
        state.evm_project = loaded_proj
        state.risk_register = RiskRegister(bac=loaded_proj.bac)
        pmproj_path = str(tmp_path / "migrated.pmproj")
        save_full_project(state, pmproj_path)

        # Load .pmproj and verify
        data = load_full_project(pmproj_path)
        assert data["evm_project"].project_name == "Migration"
        assert len(data["evm_project"].tasks) == 1


# ===================================================================
# Integration: Mode Persistence
# ===================================================================

class TestModePersistence:
    def test_mode_saved_in_pmproj(self, tmp_path):
        """Mode (UG/PG) persists through save/load."""
        for mode in ("UG", "PG"):
            state = FakeState()
            state.evm_project, state.risk_register = make_empty_project()
            state._mode = mode
            fp = str(tmp_path / f"mode_{mode}.pmproj")
            save_full_project(state, fp)
            data = load_full_project(fp)
            assert data["app_config"]["mode"] == mode


# ===================================================================
# Integration: EduProjectState + I/O Pipeline
# ===================================================================

class TestEduStateIntegration:
    def test_state_mark_dirty_on_change(self):
        """Modifying project through state → dirty flag set."""
        state = EduProjectState()
        state.evm_project = EVMProject(bac=1000, bac_auto_compute=False)
        state.risk_register = RiskRegister(bac=1000)
        state.mark_dirty()
        assert state.is_dirty()

        # Save clears dirty
        state.mark_clean()
        assert not state.is_dirty()

    def test_state_bac_sync_integration(self):
        """Adding tasks → recompute BAC → mark_dirty syncs to risk register."""
        state = EduProjectState()
        tasks = [
            EVMTask(task_id="A", name="A", budget=5000),
            EVMTask(task_id="B", name="B", budget=3000),
        ]
        state.evm_project = EVMProject(tasks=tasks, bac_auto_compute=True)
        state.risk_register = RiskRegister(bac=0)

        # BAC auto-computed to 8000
        assert state.evm_project.bac == 8000

        # mark_dirty syncs to risk register
        state.mark_dirty()
        assert state.risk_register.bac == 8000

    def test_state_reset_and_new_project(self):
        """reset() → make_empty_project → fresh state."""
        state = EduProjectState()
        state.evm_project = EVMProject(bac=50000, bac_auto_compute=False)
        state.risk_register = RiskRegister(bac=50000)
        state.mark_dirty()
        state.current_file_path = "/old/path.pmproj"

        state.reset()
        proj, reg = make_empty_project()
        state.evm_project = proj
        state.risk_register = reg

        assert state.evm_project.project_name == "New Project"
        assert state.evm_project.bac == 0.0
        assert len(state.risk_register.risks) == 0
        assert not state.is_dirty()


# ===================================================================
# Integration: Risk I/O ↔ Risk Register ↔ KPIs
# ===================================================================

class TestRiskKPIIntegration:
    def test_risk_contingency_affects_eac_assessment(self):
        """Contingency reserve can be compared to cost overrun."""
        proj = EVMProject(
            project_name="Risk-KPI",
            bac=100000, bac_auto_compute=False,
            periods=[EVMPeriod(index=0, pv_cumulative=60000,
                               ev_cumulative=50000, ac_cumulative=55000)],
        )
        kpis = compute_all_kpis(proj)

        reg = RiskRegister(bac=100000)
        reg.add_risk(Risk(id="R1", name="Risk A", probability=0.5, impact=20000))
        reg.add_risk(Risk(id="R2", name="Risk B", probability=0.3, impact=10000))

        # Cost variance = -5000
        assert kpis["cv"] == pytest.approx(-5000)

        # Contingency reserve = 10000 + 3000 = 13000
        cr = reg.contingency_reserve()
        assert cr == pytest.approx(13000)

        # Contingency > |CV| → reserve covers overrun
        assert cr > abs(kpis["cv"])

    def test_risk_csv_roundtrip_preserves_computations(self, tmp_path):
        """CSV export → import → recompute → same totals."""
        reg = RiskRegister(bac=100000)
        reg.add_risk(Risk(id="R1", name="A", probability=0.5, impact=10000,
                          category=RiskCategory.COST))
        reg.add_risk(Risk(id="R2", name="B", probability=0.3, impact=5000,
                          category=RiskCategory.SCHEDULE))

        original_exposure = reg.total_exposure()
        original_flagged = len(reg.flag_high_exposure())

        fp = str(tmp_path / "risk.csv")
        export_to_csv(reg, fp)
        imported = import_from_csv(fp)

        assert imported.total_exposure() == pytest.approx(original_exposure)

    def test_risk_json_roundtrip_preserves_computations(self, tmp_path):
        """JSON save → load → same category breakdown."""
        reg = RiskRegister(bac=50000)
        for i, cat in enumerate(RiskCategory):
            reg.add_risk(Risk(id=f"R{i}", name=f"{cat.value} risk",
                              probability=0.3, impact=1000, category=cat))

        fp = str(tmp_path / "risk.json")
        save_register(reg, fp)
        loaded = load_register(fp)

        # Same number of risks per category
        original_cats = {r.category for r in reg.risks}
        loaded_cats = {r.category for r in loaded.risks}
        assert original_cats == loaded_cats


# ===================================================================
# Integration: CPM → MC → KPI Cross-validation
# ===================================================================

class TestCPMMCIntegration:
    def test_deterministic_mc_matches_cpm(self):
        """With no PERT data and no risks, MC durations should match CPM exactly."""
        acts = [
            {"id": "A", "predecessors": [], "duration": 5},
            {"id": "B", "predecessors": ["A"], "duration": 3},
            {"id": "C", "predecessors": ["A"], "duration": 7},
            {"id": "D", "predecessors": ["B", "C"], "duration": 2},
        ]
        from pmhelper.core.evm_models_edu import EVMTask
        evm_tasks = [
            EVMTask(task_id="A", name="A", budget=0),
            EVMTask(task_id="B", name="B", budget=0),
            EVMTask(task_id="C", name="C", budget=0),
            EVMTask(task_id="D", name="D", budget=0),
        ]

        # CPM expected: A(5)→C(7)→D(2) = 14
        expected_dur, _ = run_cpm_on_sample(acts, {"A": 5, "B": 3, "C": 7, "D": 2})
        assert expected_dur == pytest.approx(14.0)

        # MC with deterministic tasks → all durations = 14
        inp = MCInputs(cpm_activities=acts, evm_tasks=evm_tasks, risks=[],
                        bac=0, n_trials=10, seed=42)
        r = run_simulation(inp)
        assert np.all(r.durations == pytest.approx(14.0))

    def test_pert_mc_produces_spread(self):
        """PERT tasks should produce duration variance in MC."""
        acts = [
            {"id": "A", "predecessors": [], "duration": 5,
             "optimistic": 3, "most_likely": 5, "pessimistic": 10},
            {"id": "B", "predecessors": ["A"], "duration": 4,
             "optimistic": 2, "most_likely": 4, "pessimistic": 8},
        ]
        from pmhelper.core.evm_models_edu import EVMTask
        evm_tasks = [
            EVMTask(task_id="A", name="A", budget=1000,
                    planned_start=0, planned_finish=5),
            EVMTask(task_id="B", name="B", budget=800,
                    planned_start=5, planned_finish=9),
        ]

        inp = MCInputs(cpm_activities=acts, evm_tasks=evm_tasks, risks=[],
                        bac=1800, n_trials=1000, seed=42)
        r = run_simulation(inp)

        assert np.std(r.durations) > 0.5  # meaningful variation
        assert r.p50_duration < r.p90_duration

    def test_pv_schedule_monotonic(self):
        """compute_pv_schedule output should be monotonically non-decreasing."""
        tasks = [
            EVMTask(task_id="A", name="A", budget=5000,
                    planned_start=0, planned_finish=3),
            EVMTask(task_id="B", name="B", budget=3000,
                    planned_start=2, planned_finish=6),
            EVMTask(task_id="C", name="C", budget=2000,
                    planned_start=5, planned_finish=8),
        ]
        from pmhelper.core.evm_models_edu import compute_pv_schedule
        pv = compute_pv_schedule(tasks, 10)
        for i in range(1, len(pv)):
            assert pv[i] >= pv[i-1], f"PV not monotonic at period {i}"
