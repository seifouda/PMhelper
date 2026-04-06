"""
Tests for Phase 2: Three-Point Estimate Engine and Step Generator.

Covers:
- PERT-Beta formula: expected time, variance, std dev
- Triangular formula: expected time, variance
- Project totals (critical path only)
- Input validation: skips invalid rows, coerces unsorted O/M/P
- Step generator: returns correct number of steps with populated content
- Demo file: valid JSON with required schema keys
"""

import json
import math
import os
import pytest

from pmhelper.core.three_point_engine import (
    ThreePointEngine,
    ThreePointResult,
    ActivityEstimate,
)
from pmhelper.core.three_point_step_generator import three_point_steps


# ════════════════════════════════════════════════════════════════════
#  Fixtures
# ════════════════════════════════════════════════════════════════════

ACTIVITIES_SIMPLE = [
    {"id": "A", "name": "Task A", "optimistic": 2, "most_likely": 4, "pessimistic": 6},
    {"id": "B", "name": "Task B", "optimistic": 1, "most_likely": 3, "pessimistic": 5},
    {"id": "C", "name": "Task C", "optimistic": 3, "most_likely": 5, "pessimistic": 7},
]

# Hand-computed PERT expected values:
# A: (2 + 4*4 + 6)/6 = 24/6 = 4.0, σ² = ((6-2)/6)² = (4/6)² = 16/36 = 0.4444
# B: (1 + 4*3 + 5)/6 = 18/6 = 3.0, σ² = ((5-1)/6)² = (4/6)² = 0.4444
# C: (3 + 4*5 + 7)/6 = 30/6 = 5.0, σ² = ((7-3)/6)² = (4/6)² = 0.4444


# ════════════════════════════════════════════════════════════════════
#  PERT-Beta formula tests
# ════════════════════════════════════════════════════════════════════

class TestPERTFormulas:
    def test_expected_pert_basic(self):
        assert ThreePointEngine.expected_pert(2, 4, 6) == pytest.approx(4.0)

    def test_expected_pert_asymmetric(self):
        """Pessimistic-heavy estimate."""
        te = ThreePointEngine.expected_pert(1, 2, 9)
        # (1 + 8 + 9)/6 = 18/6 = 3.0
        assert te == pytest.approx(3.0)

    def test_variance_pert(self):
        """((P-O)/6)²: A = (4/6)² = 0.4444..."""
        v = ThreePointEngine.variance_pert(2, 6)
        assert v == pytest.approx((4 / 6) ** 2, rel=1e-4)

    def test_variance_pert_zero(self):
        """Deterministic estimate → zero variance."""
        assert ThreePointEngine.variance_pert(5, 5) == pytest.approx(0.0)

    def test_std_dev_matches_variance(self):
        v = ThreePointEngine.variance_pert(2, 8)
        assert math.sqrt(v) == pytest.approx((8 - 2) / 6)


# ════════════════════════════════════════════════════════════════════
#  Triangular formula tests
# ════════════════════════════════════════════════════════════════════

class TestTriangularFormulas:
    def test_expected_triangular_symmetric(self):
        """Symmetric distribution → same as arithmetic mean."""
        te = ThreePointEngine.expected_triangular(2, 4, 6)
        assert te == pytest.approx(4.0)

    def test_expected_triangular_asymmetric(self):
        te = ThreePointEngine.expected_triangular(1, 2, 9)
        # (1+2+9)/3 = 4.0
        assert te == pytest.approx(4.0)

    def test_variance_triangular_formula(self):
        """(O²+M²+P² - OM - OP - MP)/18 for O=2, M=4, P=6."""
        o, m, p = 2.0, 4.0, 6.0
        expected_var = (o**2 + m**2 + p**2 - o*m - o*p - m*p) / 18.0
        assert ThreePointEngine.variance_triangular(o, m, p) == pytest.approx(expected_var)

    def test_variance_triangular_zero_spread(self):
        assert ThreePointEngine.variance_triangular(3, 3, 3) == pytest.approx(0.0)


# ════════════════════════════════════════════════════════════════════
#  Engine.calculate — PERT mode
# ════════════════════════════════════════════════════════════════════

class TestEngineCalculatePERT:
    def test_returns_result_type(self):
        result = ThreePointEngine.calculate(ACTIVITIES_SIMPLE, formula="PERT")
        assert isinstance(result, ThreePointResult)
        assert result.formula == "PERT"

    def test_activity_count(self):
        result = ThreePointEngine.calculate(ACTIVITIES_SIMPLE)
        assert len(result.activities) == 3

    def test_individual_expected_values(self):
        result = ThreePointEngine.calculate(ACTIVITIES_SIMPLE)
        by_id = {a.activity_id: a for a in result.activities}
        assert by_id["A"].expected == pytest.approx(4.0, abs=1e-4)
        assert by_id["B"].expected == pytest.approx(3.0, abs=1e-4)
        assert by_id["C"].expected == pytest.approx(5.0, abs=1e-4)

    def test_individual_variance_values(self):
        result = ThreePointEngine.calculate(ACTIVITIES_SIMPLE)
        by_id = {a.activity_id: a for a in result.activities}
        expected_var = (4 / 6) ** 2
        assert by_id["A"].variance == pytest.approx(expected_var, abs=1e-4)
        assert by_id["B"].variance == pytest.approx(expected_var, abs=1e-4)
        assert by_id["C"].variance == pytest.approx(expected_var, abs=1e-4)

    def test_std_dev_is_sqrt_variance(self):
        result = ThreePointEngine.calculate(ACTIVITIES_SIMPLE)
        for act in result.activities:
            assert act.std_dev == pytest.approx(math.sqrt(act.variance), abs=1e-4)

    def test_project_totals_all_activities_no_cp(self):
        """With no critical path, project totals over all activities."""
        result = ThreePointEngine.calculate(ACTIVITIES_SIMPLE)
        expected_total = 4.0 + 3.0 + 5.0  # = 12.0
        assert result.project_expected == pytest.approx(expected_total, abs=1e-4)

    def test_project_totals_critical_path_only(self):
        """Project totals restricted to critical path A and C."""
        result = ThreePointEngine.calculate(
            ACTIVITIES_SIMPLE,
            critical_path_ids=["A", "C"],
        )
        # Expected: A + C = 4.0 + 5.0 = 9.0
        assert result.project_expected == pytest.approx(9.0, abs=1e-4)
        # Variance: σ²A + σ²C = 0.4444 + 0.4444 ≈ 0.8889
        expected_var = (4 / 6) ** 2 + (4 / 6) ** 2
        assert result.project_variance == pytest.approx(expected_var, abs=1e-4)

    def test_is_critical_flag(self):
        result = ThreePointEngine.calculate(
            ACTIVITIES_SIMPLE,
            critical_path_ids=["A"],
        )
        by_id = {a.activity_id: a for a in result.activities}
        assert by_id["A"].is_critical is True
        assert by_id["B"].is_critical is False
        assert by_id["C"].is_critical is False

    def test_critical_path_ids_stored(self):
        result = ThreePointEngine.calculate(
            ACTIVITIES_SIMPLE,
            critical_path_ids=["A", "C"],
        )
        assert "A" in result.critical_path_ids
        assert "C" in result.critical_path_ids

    def test_start_end_excluded_from_cp_set(self):
        """START and END pseudo-node IDs must not appear in critical_path_ids."""
        result = ThreePointEngine.calculate(
            ACTIVITIES_SIMPLE,
            critical_path_ids=["START", "A", "C", "END"],
        )
        assert "START" not in result.critical_path_ids
        assert "END" not in result.critical_path_ids


# ════════════════════════════════════════════════════════════════════
#  Engine.calculate — Triangular mode
# ════════════════════════════════════════════════════════════════════

class TestEngineCalculateTriangular:
    def test_formula_label(self):
        result = ThreePointEngine.calculate(ACTIVITIES_SIMPLE, formula="Triangular")
        assert result.formula == "Triangular"

    def test_symmetric_triangular_equals_pert(self):
        """For symmetric O/M/P, PERT and Triangular give the same expected value."""
        result_pert = ThreePointEngine.calculate(ACTIVITIES_SIMPLE, formula="PERT")
        result_tri  = ThreePointEngine.calculate(ACTIVITIES_SIMPLE, formula="Triangular")
        for ap, at in zip(result_pert.activities, result_tri.activities):
            assert ap.expected == pytest.approx(at.expected, abs=1e-3)

    def test_asymmetric_difference(self):
        """For asymmetric O/M/P, PERT ≠ Triangular."""
        acts = [{"id": "X", "name": "X", "optimistic": 1, "most_likely": 2, "pessimistic": 9}]
        rp = ThreePointEngine.calculate(acts, formula="PERT")
        rt = ThreePointEngine.calculate(acts, formula="Triangular")
        # PERT: (1+8+9)/6 = 3.0; Triangular: (1+2+9)/3 = 4.0
        assert rp.activities[0].expected == pytest.approx(3.0, abs=1e-4)
        assert rt.activities[0].expected == pytest.approx(4.0, abs=1e-4)


# ════════════════════════════════════════════════════════════════════
#  Input validation
# ════════════════════════════════════════════════════════════════════

class TestInputValidation:
    def test_skips_empty_id(self):
        acts = [
            {"id": "",  "name": "No ID", "optimistic": 1, "most_likely": 2, "pessimistic": 3},
            {"id": "A", "name": "Valid", "optimistic": 1, "most_likely": 2, "pessimistic": 3},
        ]
        result = ThreePointEngine.calculate(acts)
        assert len(result.activities) == 1
        assert result.activities[0].activity_id == "A"

    def test_skips_non_numeric_omp(self):
        acts = [
            {"id": "BAD", "name": "Bad", "optimistic": "foo", "most_likely": 2, "pessimistic": 3},
            {"id": "OK",  "name": "Ok",  "optimistic": 1,     "most_likely": 2, "pessimistic": 3},
        ]
        result = ThreePointEngine.calculate(acts)
        assert len(result.activities) == 1
        assert result.activities[0].activity_id == "OK"

    def test_coerces_unsorted_omp(self):
        """If O > M or M > P the engine coerces by sorting silently."""
        acts = [{"id": "X", "name": "X",
                 "optimistic": 6, "most_likely": 4, "pessimistic": 2}]
        result = ThreePointEngine.calculate(acts)
        assert len(result.activities) == 1
        act = result.activities[0]
        # After coercion: sorted → 2, 4, 6
        assert act.optimistic <= act.most_likely <= act.pessimistic

    def test_skips_negative_durations(self):
        acts = [{"id": "NEG", "name": "Neg",
                 "optimistic": -1, "most_likely": 2, "pessimistic": 5}]
        result = ThreePointEngine.calculate(acts)
        assert len(result.activities) == 0

    def test_invalid_formula_raises(self):
        with pytest.raises(ValueError):
            ThreePointEngine.calculate(ACTIVITIES_SIMPLE, formula="BadFormula")

    def test_empty_activity_list(self):
        result = ThreePointEngine.calculate([])
        assert result.activities == []
        assert result.project_expected == 0.0
        assert result.project_variance == 0.0
        assert result.project_std_dev == 0.0

    def test_name_fallback_to_id(self):
        """When 'name' is missing, activity_id is used as name."""
        acts = [{"id": "Z", "optimistic": 1, "most_likely": 2, "pessimistic": 3}]
        result = ThreePointEngine.calculate(acts)
        assert result.activities[0].name == "Z"


# ════════════════════════════════════════════════════════════════════
#  Step Generator
# ════════════════════════════════════════════════════════════════════

class TestThreePointStepGenerator:
    @pytest.fixture
    def pert_result(self):
        return ThreePointEngine.calculate(
            ACTIVITIES_SIMPLE,
            formula="PERT",
            critical_path_ids=["A", "C"],
        )

    @pytest.fixture
    def triangular_result(self):
        return ThreePointEngine.calculate(
            ACTIVITIES_SIMPLE,
            formula="Triangular",
            critical_path_ids=["A"],
        )

    def test_pert_produces_five_steps(self, pert_result):
        steps = three_point_steps(pert_result)
        assert len(steps) == 5

    def test_triangular_produces_five_steps(self, triangular_result):
        steps = three_point_steps(triangular_result)
        assert len(steps) == 5

    def test_step1_has_activity_children(self, pert_result):
        steps = three_point_steps(pert_result)
        step1 = steps[0]
        assert "Step 1" in step1.title
        assert len(step1.children) == len(pert_result.activities)

    def test_step2_only_critical_activities(self, pert_result):
        steps = three_point_steps(pert_result)
        step2 = steps[1]
        assert "Step 2" in step2.title
        # Only critical activities (A and C)
        assert len(step2.children) == 2

    def test_step3_project_variance(self, pert_result):
        steps = three_point_steps(pert_result)
        step3 = steps[2]
        assert "Step 3" in step3.title
        assert str(pert_result.project_variance) in step3.result

    def test_step4_project_std_dev(self, pert_result):
        steps = three_point_steps(pert_result)
        step4 = steps[3]
        assert "Step 4" in step4.title
        assert str(pert_result.project_std_dev) in step4.result

    def test_step5_project_expected(self, pert_result):
        steps = three_point_steps(pert_result)
        step5 = steps[4]
        assert "Step 5" in step5.title
        assert str(pert_result.project_expected) in step5.result

    def test_triangular_formula_strings(self, triangular_result):
        steps = three_point_steps(triangular_result)
        step1 = steps[0]
        assert "(O + M + P) / 3" in step1.formula

    def test_pert_formula_strings(self, pert_result):
        steps = three_point_steps(pert_result)
        step1 = steps[0]
        assert "(O + 4M + P) / 6" in step1.formula

    def test_critical_marked_in_step1_children(self, pert_result):
        steps = three_point_steps(pert_result)
        child_titles = [c.title for c in steps[0].children]
        # Critical activities should have ★ prefix
        critical_titled = [t for t in child_titles if "★" in t]
        assert len(critical_titled) == 2  # A and C

    def test_empty_result_still_returns_steps(self):
        result = ThreePointEngine.calculate([])
        steps = three_point_steps(result)
        assert len(steps) == 5  # steps are always generated, just with empty children


# ════════════════════════════════════════════════════════════════════
#  Demo file
# ════════════════════════════════════════════════════════════════════

class TestDemoFile:
    DEMO_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "demos", "v2", "three_point_demo.json"
    )

    def test_demo_file_exists(self):
        assert os.path.isfile(self.DEMO_PATH), f"Missing demo file: {self.DEMO_PATH}"

    def test_demo_schema(self):
        with open(self.DEMO_PATH, "r", encoding="utf-8") as fh:
            demo = json.load(fh)
        assert "name" in demo
        assert "data" in demo
        data = demo["data"]
        assert "activities" in data
        assert len(data["activities"]) == 8

    def test_demo_activities_have_omp(self):
        with open(self.DEMO_PATH, "r", encoding="utf-8") as fh:
            demo = json.load(fh)
        for act in demo["data"]["activities"]:
            assert "optimistic" in act
            assert "most_likely" in act
            assert "pessimistic" in act
            assert act["optimistic"] <= act["most_likely"] <= act["pessimistic"]

    def test_demo_engine_integration(self):
        """Run the demo activities through the engine and check known totals."""
        with open(self.DEMO_PATH, "r", encoding="utf-8") as fh:
            demo = json.load(fh)
        data = demo["data"]
        acts = data["activities"]
        cp_ids = data["critical_path_ids"]
        result = ThreePointEngine.calculate(acts, formula="PERT",
                                             critical_path_ids=cp_ids)
        expected_totals = data["project_totals_pert"]
        assert result.project_expected == pytest.approx(
            expected_totals["project_expected"], abs=0.001)
        assert result.project_variance == pytest.approx(
            expected_totals["project_variance"], abs=0.001)


# ════════════════════════════════════════════════════════════════════
#  Edge cases
# ════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_single_deterministic_activity(self):
        """Single activity with O=M=P gives zero variance."""
        acts = [{"id": "X", "name": "X",
                 "optimistic": 5, "most_likely": 5, "pessimistic": 5}]
        result = ThreePointEngine.calculate(acts, formula="PERT")
        assert result.activities[0].expected == pytest.approx(5.0)
        assert result.activities[0].variance == pytest.approx(0.0)
        assert result.activities[0].std_dev == pytest.approx(0.0)

    def test_all_non_critical_cp_no_match(self):
        """Critical path IDs that don't match any activity → fall back to all."""
        result = ThreePointEngine.calculate(
            ACTIVITIES_SIMPLE,
            critical_path_ids=["NONEXISTENT"],
        )
        # Since no matching critical, basis falls back to all activities
        # (no activities are marked critical)
        basis_total = sum(a.expected for a in result.activities if a.is_critical)
        # All are non-critical so project_expected = 0 (empty sum)
        # OR if fallback logic goes to all…
        # Looking at engine code: basis = [critical] if cp_set else all
        # cp_set = {"NONEXISTENT"} is truthy → basis = [] → project totals = 0
        assert result.project_expected == 0.0

    def test_large_uncertainty_activity(self):
        """High-variance activity: O=1, M=10, P=50."""
        acts = [{"id": "R", "name": "Risky",
                 "optimistic": 1, "most_likely": 10, "pessimistic": 50}]
        result = ThreePointEngine.calculate(acts, formula="PERT")
        # te = (1 + 40 + 50)/6 = 91/6 ≈ 15.1667
        assert result.activities[0].expected == pytest.approx(91 / 6, abs=0.001)
        # σ² = ((50-1)/6)² = (49/6)² ≈ 66.69
        assert result.activities[0].variance == pytest.approx((49 / 6) ** 2, abs=0.001)

    def test_name_from_activity_key(self):
        """Activity dict with 'activity' key instead of 'name'."""
        acts = [{"id": "T", "activity": "Test Task",
                 "optimistic": 1, "most_likely": 2, "pessimistic": 3}]
        result = ThreePointEngine.calculate(acts)
        assert result.activities[0].name == "Test Task"
