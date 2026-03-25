"""Tests for CPM Sampler and Monte Carlo engine — Phase 4."""

import pytest
import numpy as np

from pmhelper.core.cpm_sampler_edu import run_cpm_on_sample
from pmhelper.core.monte_carlo_edu import (
    MCInputs, MCResults, run_simulation,
    _sample_pert_beta, _get_task_duration,
)


# ---------------------------------------------------------------
# CPM Sampler
# ---------------------------------------------------------------

class TestCPMSampler:
    def test_empty_activities(self):
        dur, cp = run_cpm_on_sample([], {})
        assert dur == 0.0
        assert cp == set()

    def test_single_task(self):
        acts = [{"id": "A", "predecessors": []}]
        dur, cp = run_cpm_on_sample(acts, {"A": 5.0})
        assert dur == pytest.approx(5.0)
        assert cp == {"A"}

    def test_serial_chain(self):
        """A → B → C, durations 3, 4, 5 → total = 12, all critical."""
        acts = [
            {"id": "A", "predecessors": []},
            {"id": "B", "predecessors": ["A"]},
            {"id": "C", "predecessors": ["B"]},
        ]
        dur, cp = run_cpm_on_sample(acts, {"A": 3, "B": 4, "C": 5})
        assert dur == pytest.approx(12.0)
        assert cp == {"A", "B", "C"}

    def test_parallel_paths(self):
        """Two parallel paths from start to end.
        Path 1: A(4) → C(3) = 7
        Path 2: B(5) → D(1) = 6
        Critical path: A → C (duration 7).
        """
        acts = [
            {"id": "A", "predecessors": []},
            {"id": "B", "predecessors": []},
            {"id": "C", "predecessors": ["A"]},
            {"id": "D", "predecessors": ["B"]},
        ]
        dur, cp = run_cpm_on_sample(acts, {"A": 4, "B": 5, "C": 3, "D": 1})
        assert dur == pytest.approx(7.0)
        assert "A" in cp
        assert "C" in cp

    def test_diamond_network(self):
        """A → B, A → C, B → D, C → D.
        A=2, B=5, C=3, D=2
        Path A-B-D = 9, Path A-C-D = 7 → CP = {A, B, D}
        """
        acts = [
            {"id": "A", "predecessors": []},
            {"id": "B", "predecessors": ["A"]},
            {"id": "C", "predecessors": ["A"]},
            {"id": "D", "predecessors": ["B", "C"]},
        ]
        dur, cp = run_cpm_on_sample(acts, {"A": 2, "B": 5, "C": 3, "D": 2})
        assert dur == pytest.approx(9.0)
        assert "A" in cp
        assert "B" in cp
        assert "D" in cp

    def test_predecessors_as_string(self):
        """Predecessors given as comma-separated string."""
        acts = [
            {"id": "A", "predecessors": ""},
            {"id": "B", "predecessors": "A"},
            {"id": "C", "predecessors": "A, B"},
        ]
        dur, cp = run_cpm_on_sample(acts, {"A": 3, "B": 4, "C": 2})
        # A(3) → B(4) → C(2) = 9
        assert dur == pytest.approx(9.0)

    def test_zero_duration_task(self):
        acts = [
            {"id": "A", "predecessors": []},
            {"id": "B", "predecessors": ["A"]},
        ]
        dur, cp = run_cpm_on_sample(acts, {"A": 0, "B": 5})
        assert dur == pytest.approx(5.0)

    def test_all_zero_durations(self):
        acts = [
            {"id": "A", "predecessors": []},
            {"id": "B", "predecessors": ["A"]},
        ]
        dur, cp = run_cpm_on_sample(acts, {"A": 0, "B": 0})
        assert dur == pytest.approx(0.0)


# ---------------------------------------------------------------
# Sampling helpers
# ---------------------------------------------------------------

class TestSamplingHelpers:
    def test_pert_beta_basic(self):
        rng = np.random.default_rng(42)
        samples = [_sample_pert_beta(rng, 2, 5, 10) for _ in range(1000)]
        mean = np.mean(samples)
        pert_mean = (2 + 4 * 5 + 10) / 6  # 5.33
        assert abs(mean - pert_mean) < 0.5

    def test_pert_beta_equal_bounds(self):
        """When O == P, should return most_likely."""
        rng = np.random.default_rng(42)
        sample = _sample_pert_beta(rng, 5, 5, 5)
        assert sample == pytest.approx(5.0)

    def test_get_task_duration_from_key(self):
        assert _get_task_duration({"duration": 7}) == 7.0

    def test_get_task_duration_from_start_finish(self):
        assert _get_task_duration({"planned_start": 2, "planned_finish": 6}) == 4.0

    def test_get_task_duration_default(self):
        assert _get_task_duration({}) == 1.0


# ---------------------------------------------------------------
# Monte Carlo simulation
# ---------------------------------------------------------------

class TestMonteCarlo:
    def _simple_inputs(self, n_trials=500):
        acts = [
            {"id": "A", "predecessors": [], "duration": 5},
            {"id": "B", "predecessors": ["A"], "duration": 3},
            {"id": "C", "predecessors": ["A"], "duration": 4},
            {"id": "D", "predecessors": ["B", "C"], "duration": 2},
        ]
        from pmhelper.core.evm_models_edu import EVMTask
        evm_tasks = [
            EVMTask(task_id="A", name="A", budget=1000, planned_start=0, planned_finish=5),
            EVMTask(task_id="B", name="B", budget=600, planned_start=5, planned_finish=8),
            EVMTask(task_id="C", name="C", budget=800, planned_start=5, planned_finish=9),
            EVMTask(task_id="D", name="D", budget=400, planned_start=9, planned_finish=11),
        ]
        return MCInputs(
            cpm_activities=acts,
            evm_tasks=evm_tasks,
            risks=[],
            bac=2800,
            n_trials=n_trials,
            seed=42,
        )

    def test_deterministic_seed_reproducibility(self):
        """Same seed → identical results."""
        inp = self._simple_inputs(n_trials=100)
        r1 = run_simulation(inp)
        r2 = run_simulation(inp)
        np.testing.assert_array_equal(r1.durations, r2.durations)
        np.testing.assert_array_equal(r1.costs, r2.costs)

    def test_output_shapes(self):
        inp = self._simple_inputs(n_trials=200)
        r = run_simulation(inp)
        assert r.durations.shape == (200,)
        assert r.costs.shape == (200,)
        assert r.n_trials == 200

    def test_percentile_ordering(self):
        """P50 <= P80 <= P90."""
        inp = self._simple_inputs(n_trials=500)
        r = run_simulation(inp)
        assert r.p50_duration <= r.p80_duration
        assert r.p80_duration <= r.p90_duration

    def test_deterministic_tasks_fixed_duration(self):
        """Tasks with only duration (no O/M/P) → zero-variance durations."""
        acts = [{"id": "A", "predecessors": [], "duration": 10}]
        from pmhelper.core.evm_models_edu import EVMTask
        evm = [EVMTask(task_id="A", name="A", budget=100, planned_start=0, planned_finish=10)]
        inp = MCInputs(cpm_activities=acts, evm_tasks=evm, risks=[], bac=100,
                        n_trials=50, seed=1)
        r = run_simulation(inp)
        # All durations should be exactly 10
        assert np.all(r.durations == 10.0)

    def test_pert_tasks_have_variance(self):
        """Tasks with O/M/P produce duration variance."""
        acts = [
            {"id": "A", "predecessors": [],
             "optimistic": 3, "most_likely": 5, "pessimistic": 10, "duration": 5},
        ]
        from pmhelper.core.evm_models_edu import EVMTask
        evm = [EVMTask(task_id="A", name="A", budget=1000, planned_start=0, planned_finish=5)]
        inp = MCInputs(cpm_activities=acts, evm_tasks=evm, risks=[], bac=1000,
                        n_trials=500, seed=42)
        r = run_simulation(inp)
        assert np.std(r.durations) > 0.1  # Some variance

    def test_n_trials_1(self):
        """N=1 should not crash."""
        inp = self._simple_inputs(n_trials=1)
        r = run_simulation(inp)
        assert r.n_trials == 1
        assert r.durations.shape == (1,)

    def test_cost_within_bac_percentage(self):
        inp = self._simple_inputs(n_trials=200)
        r = run_simulation(inp)
        assert 0.0 <= r.p_cost_within_bac <= 1.0

    def test_cp_frequencies_sum(self):
        """At least one task should appear on CP in every trial."""
        inp = self._simple_inputs(n_trials=100)
        r = run_simulation(inp)
        # For this deterministic network, all tasks in serial chain are always on CP
        assert any(f > 0 for f in r.cp_frequencies.values())

    def test_progress_callback(self):
        """Progress callback is invoked."""
        inp = self._simple_inputs(n_trials=200)
        progress_values = []
        r = run_simulation(inp, progress_callback=lambda p: progress_values.append(p))
        assert len(progress_values) > 0
        assert progress_values[-1] == pytest.approx(1.0)

    def test_risks_affect_cost(self):
        """Adding risks should increase average cost."""
        from pmhelper.core.risk_register_edu import Risk, RiskCategory
        inp_no_risk = self._simple_inputs(n_trials=200)
        r_no = run_simulation(inp_no_risk)

        inp_risk = self._simple_inputs(n_trials=200)
        inp_risk.risks = [
            Risk(id="R1", name="risk1", probability=1.0, impact=500,
                 category=RiskCategory.COST),
        ]
        r_risk = run_simulation(inp_risk)
        assert np.mean(r_risk.costs) > np.mean(r_no.costs)

    def test_serialization_roundtrip(self):
        inp = self._simple_inputs(n_trials=50)
        r = run_simulation(inp)
        d = r.to_serializable()
        r2 = MCResults.from_serializable(d)
        np.testing.assert_array_almost_equal(r.durations, r2.durations)
        np.testing.assert_array_almost_equal(r.costs, r2.costs)
        assert r.p50_duration == pytest.approx(r2.p50_duration)
        assert r.p80_duration == pytest.approx(r2.p80_duration)
        assert r.p90_duration == pytest.approx(r2.p90_duration)
        assert r.n_trials == r2.n_trials
        assert r.seed_used == r2.seed_used

    def test_convergence(self):
        """With more trials, mean should be close to PERT expected value."""
        acts = [
            {"id": "A", "predecessors": [],
             "optimistic": 2, "most_likely": 5, "pessimistic": 8, "duration": 5},
        ]
        from pmhelper.core.evm_models_edu import EVMTask
        evm = [EVMTask(task_id="A", name="A", budget=1000, planned_start=0, planned_finish=5)]
        inp = MCInputs(cpm_activities=acts, evm_tasks=evm, risks=[], bac=1000,
                        n_trials=5000, seed=42)
        r = run_simulation(inp)
        pert_mean = (2 + 4 * 5 + 8) / 6  # 5.0
        assert abs(np.mean(r.durations) - pert_mean) < 0.25  # within 5%

    def test_empty_activities(self):
        """Empty activity list should not crash."""
        inp = MCInputs(cpm_activities=[], evm_tasks=[], risks=[], bac=0,
                        n_trials=10, seed=1)
        r = run_simulation(inp)
        assert r.n_trials == 10
        assert np.all(r.durations == 0.0)
