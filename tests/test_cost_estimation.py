"""
Tests for PMhelper Edu V2 Phase 5 — Cost Estimation Engine.

Covers:
  TestAnalogous        — AnalogousEstimator
  TestBottomUp         — BottomUpEstimator
  TestWorkElement      — WorkElementEstimator
  TestPowerSizing      — PowerSizingEstimator / CostCapacityEstimator
  TestUnitFactor       — UnitFactorEstimator
  TestLearningCurve    — LearningCurveEstimator
  TestEdgeCases        — Empty inputs, invalid inputs, zero values
  TestStepGenerators   — Step generators produce non-empty output
"""

from __future__ import annotations

import math
import pytest

from pmhelper.core.cost_estimation import (
    AdjustmentFactor, AnalogousEstimator,
    WorkPackage, BottomUpEstimator,
    WorkElement, WorkElementEstimator,
    PowerSizingEstimator, CostCapacityEstimator,
    UnitFactorItem, UnitFactorEstimator,
    LearningCurveEstimator,
    CostEstimateResult, METHOD_LABELS,
)


# ─────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────

def _approx(a: float, b: float, tol: float = 1e-6) -> bool:
    """True when relative difference < tol (handles zero)."""
    denom = max(abs(b), 1e-12)
    return abs(a - b) / denom < tol


# ─────────────────────────────────────────────────────────────────────
#  Technique 1 — Analogous
# ─────────────────────────────────────────────────────────────────────

class TestAnalogous:
    """AnalogousEstimator tests."""

    def _est(self, ref: float, factors: list) -> CostEstimateResult:
        fobjs = [AdjustmentFactor(f"F{i}", f) for i, f in enumerate(factors, 1)]
        return AnalogousEstimator().estimate(ref, fobjs)

    def test_no_factors_returns_reference_cost(self):
        r = AnalogousEstimator().estimate(100_000.0, [])
        assert r.total_cost == pytest.approx(100_000.0)

    def test_single_factor(self):
        r = self._est(200_000, [1.25])
        assert r.total_cost == pytest.approx(250_000.0)

    def test_multiple_factors(self):
        # 500000 × 1.10 × 0.95 × 1.15 = 600875.0
        r = AnalogousEstimator().estimate(
            500_000,
            [
                AdjustmentFactor("Complexity", 1.10),
                AdjustmentFactor("Productivity", 0.95),
                AdjustmentFactor("Technology", 1.15),
            ],
        )
        assert r.total_cost == pytest.approx(600_875.0, rel=1e-6)

    def test_result_fields_populated(self):
        r = self._est(100_000, [1.1, 0.9])
        assert r.formula_text
        assert r.substitution_text
        assert r.interpretation
        assert len(r.breakdown) > 0

    def test_breakdown_contains_reference_and_total(self):
        r = self._est(100_000, [1.1])
        labels = [item[0] for item in r.breakdown]
        assert any("Reference" in lbl for lbl in labels)
        assert any("Estimated" in lbl or "Cost" in lbl for lbl in labels)

    def test_factor_greater_than_one_increases_cost(self):
        r = self._est(100_000, [1.5])
        assert r.total_cost > 100_000

    def test_factor_less_than_one_decreases_cost(self):
        r = self._est(100_000, [0.8])
        assert r.total_cost < 100_000

    def test_total_cost_matches_product(self):
        factors = [1.10, 0.90, 1.20]
        expected = 80_000 * math.prod(factors)
        r = self._est(80_000, factors)
        assert r.total_cost == pytest.approx(expected)

    def test_returns_cost_estimate_result(self):
        r = self._est(50_000, [1.0])
        assert isinstance(r, CostEstimateResult)


# ─────────────────────────────────────────────────────────────────────
#  Technique 2 — Bottom-Up
# ─────────────────────────────────────────────────────────────────────

class TestBottomUp:
    """BottomUpEstimator tests."""

    def _wp(self, name: str, l: float, m: float, e: float,
             o: float = 0) -> WorkPackage:
        return WorkPackage(name=name, labour_cost=l, material_cost=m,
                           equipment_cost=e, overhead_pct=o)

    def test_empty_packages_returns_zero(self):
        r = BottomUpEstimator().estimate([])
        assert r.total_cost == 0.0

    def test_single_package_no_overhead(self):
        wp = self._wp("A", 10_000, 2_000, 1_000, 0)
        r = BottomUpEstimator().estimate([wp])
        assert r.total_cost == pytest.approx(13_000.0)

    def test_single_package_with_overhead(self):
        wp = self._wp("A", 10_000, 0, 0, 20)
        r = BottomUpEstimator().estimate([wp])
        assert r.total_cost == pytest.approx(12_000.0)

    def test_multiple_packages_sum(self):
        wps = [
            self._wp("Design",      8_000,  500,   0, 15),
            self._wp("Development", 35_000, 2_000, 1_000, 15),
            self._wp("Testing",     10_000, 500,   500, 15),
        ]
        expected = sum(wp.total for wp in wps)
        r = BottomUpEstimator().estimate(wps)
        assert r.total_cost == pytest.approx(expected)

    def test_demo_scenario(self):
        # Matches cost_estimation_demo.json bottom_up expected_total = 86825
        wps = [
            self._wp("Requirements Analysis", 8000,  500,  0,    15),
            self._wp("System Design",         12000, 1000, 500,  15),
            self._wp("Development",           35000, 2000, 1000, 15),
            self._wp("Testing & QA",          10000, 500,  500,  15),
            self._wp("Deployment",            4000,  200,  300,  15),
        ]
        r = BottomUpEstimator().estimate(wps)
        assert r.total_cost == pytest.approx(86_825.0)

    def test_work_package_properties(self):
        wp = self._wp("Test", 1000, 500, 200, 10)
        assert wp.direct_cost   == pytest.approx(1700.0)
        assert wp.overhead_amount == pytest.approx(170.0)
        assert wp.total         == pytest.approx(1870.0)

    def test_result_fields_populated(self):
        r = BottomUpEstimator().estimate([self._wp("X", 100, 0, 0, 0)])
        assert r.formula_text
        assert r.interpretation
        assert len(r.breakdown) > 0


# ─────────────────────────────────────────────────────────────────────
#  Technique 3 — Work Element
# ─────────────────────────────────────────────────────────────────────

class TestWorkElement:
    """WorkElementEstimator tests."""

    def _el(self, name: str, h: float, r: float,
             m: float = 0, e: float = 0) -> WorkElement:
        return WorkElement(name=name, hours=h, hourly_rate=r,
                           material_cost=m, equipment_cost=e)

    def test_empty_elements_returns_zero(self):
        r = WorkElementEstimator().estimate([])
        assert r.total_cost == 0.0

    def test_labour_only(self):
        el = self._el("Labour", 100, 50)
        r  = WorkElementEstimator().estimate([el])
        assert r.total_cost == pytest.approx(5_000.0)

    def test_full_element(self):
        el = self._el("Full", 80, 40, 2000, 1500)
        # labour = 80*40=3200, +2000+1500 = 6700
        assert el.total == pytest.approx(6700.0)

    def test_demo_scenario(self):
        # Matches cost_estimation_demo.json work_element expected_total = 126800
        els = [
            self._el("Site Preparation",  100, 40, 2000,  1500),
            self._el("Foundation Work",   200, 45, 15000, 3000),
            self._el("Structural Frame",  350, 50, 40000, 5000),
            self._el("Mechanical / Elec", 150, 60, 8000,  2000),
            self._el("Finishing Works",   120, 40, 5000,  1000),
        ]
        r = WorkElementEstimator().estimate(els)
        assert r.total_cost == pytest.approx(126_800.0)

    def test_extra_contains_sub_totals(self):
        els = [self._el("A", 100, 50, 200, 100)]
        r   = WorkElementEstimator().estimate(els)
        assert "labour_total"    in r.extra
        assert "material_total"  in r.extra
        assert "equipment_total" in r.extra

    def test_labour_total_in_extra(self):
        els = [self._el("A", 100, 50, 200, 100)]
        r   = WorkElementEstimator().estimate(els)
        assert r.extra["labour_total"] == pytest.approx(5000.0)


# ─────────────────────────────────────────────────────────────────────
#  Technique 4 & 6 — Power Sizing / Cost-Capacity Index
# ─────────────────────────────────────────────────────────────────────

class TestPowerSizing:
    """PowerSizingEstimator (and CostCapacityEstimator alias) tests."""

    def _est(self, ref_c, ref_s, new_s, x=0.6):
        return PowerSizingEstimator().estimate(ref_c, ref_s, new_s, x)

    def test_same_capacity_returns_reference_cost(self):
        r = self._est(500_000, 100, 100)
        assert r.total_cost == pytest.approx(500_000.0)

    def test_linear_exponent_scales_linearly(self):
        # x=1 → C2 = C1 × (S2/S1)
        r = self._est(100_000, 50, 100, x=1.0)
        assert r.total_cost == pytest.approx(200_000.0)

    def test_typical_0_6_exponent(self):
        # 800000 × (250/100)^0.6
        expected = 800_000 * (250 / 100) ** 0.6
        r = self._est(800_000, 100, 250, 0.6)
        assert r.total_cost == pytest.approx(expected, rel=1e-5)

    def test_demo_scenario(self):
        expected = 800_000 * (250 / 100) ** 0.6
        r = self._est(800_000, 100, 250, 0.6)
        assert r.total_cost == pytest.approx(expected, rel=1e-5)

    def test_cost_capacity_alias_same_result(self):
        r1 = PowerSizingEstimator().estimate(200_000, 50, 120, 0.7)
        r2 = CostCapacityEstimator().estimate(200_000, 50, 120, 0.7)
        assert r1.total_cost == pytest.approx(r2.total_cost)

    def test_raises_on_zero_reference_capacity(self):
        with pytest.raises(ValueError, match="Capacities must be positive"):
            self._est(100_000, 0, 100)

    def test_raises_on_zero_new_capacity(self):
        with pytest.raises(ValueError, match="Capacities must be positive"):
            self._est(100_000, 100, 0)

    def test_raises_on_negative_capacities(self):
        with pytest.raises(ValueError):
            self._est(100_000, -10, 100)

    def test_scale_factor_in_extra(self):
        r = self._est(100_000, 50, 100, 0.6)
        assert "scale_factor" in r.extra
        assert r.extra["scale_factor"] == pytest.approx(2 ** 0.6, rel=1e-5)

    def test_result_fields_populated(self):
        r = self._est(100_000, 100, 200)
        assert r.formula_text
        assert r.substitution_text
        assert r.interpretation


# ─────────────────────────────────────────────────────────────────────
#  Technique 5 — Unit / Factor
# ─────────────────────────────────────────────────────────────────────

class TestUnitFactor:
    """UnitFactorEstimator tests."""

    def _item(self, name: str, uc: float, qty: float,
               f: float = 1.0) -> UnitFactorItem:
        return UnitFactorItem(name=name, unit_cost=uc, quantity=qty, factor=f)

    def test_empty_returns_zero(self):
        r = UnitFactorEstimator().estimate([])
        assert r.total_cost == 0.0

    def test_single_item_no_factor(self):
        item = self._item("Concrete", 120, 500, 1.0)
        r = UnitFactorEstimator().estimate([item])
        assert r.total_cost == pytest.approx(60_000.0)

    def test_single_item_with_factor(self):
        item = self._item("Steel", 900, 80, 1.10)
        assert item.extended_cost == pytest.approx(79_200.0)

    def test_demo_scenario(self):
        # expected = 337950.0
        items = [
            self._item("Concrete (m³)",             150, 500, 1.05),
            self._item("Steel reinforcement (ton)",  900,  80, 1.10),
            self._item("Formwork (m²)",               40, 1200, 1.0),
            self._item("Labour skilled (days)",       320, 300, 1.0),
            self._item("Labour unskilled (days)",     180, 200, 1.0),
        ]
        r = UnitFactorEstimator().estimate(items)
        assert r.total_cost == pytest.approx(337_950.0)

    def test_extended_cost_property(self):
        item = self._item("X", 100, 10, 2.5)
        assert item.extended_cost == pytest.approx(2500.0)

    def test_result_fields_populated(self):
        r = UnitFactorEstimator().estimate([self._item("A", 50, 10)])
        assert r.formula_text
        assert r.interpretation
        assert len(r.breakdown) > 0


# ─────────────────────────────────────────────────────────────────────
#  Technique 7 — Learning Curves
# ─────────────────────────────────────────────────────────────────────

class TestLearningCurve:
    """LearningCurveEstimator tests."""

    _EST = LearningCurveEstimator()

    def test_unit_1_always_equals_t1(self):
        r = LearningCurveEstimator().estimate(1000, 0.8, 1)
        assert r.total_cost == pytest.approx(1000.0)

    def test_unit_2_equals_learning_rate_times_t1(self):
        # At unit 2, T_2 = T_1 × 2^b, b = ln(0.8)/ln(2)
        # Note: T_2 is NOT 800 for Wright unit model; T_2 = 1000×2^b
        # Only cumulative average halves for perfect 80% curve at doubling
        t1, rate = 1000, 0.8
        b = math.log(rate) / math.log(2)
        expected = t1 * 2 ** b
        r = LearningCurveEstimator().estimate(t1, rate, 2)
        assert r.total_cost == pytest.approx(expected, rel=1e-5)

    def test_demo_scenario_unit_16(self):
        # T_16 = 1000 × 16^b = 409.6000
        b = math.log(0.8) / math.log(2)
        expected = 1000 * 16 ** b
        r = LearningCurveEstimator().estimate(1000, 0.80, 16)
        assert r.total_cost == pytest.approx(expected, rel=1e-5)
        assert r.total_cost == pytest.approx(409.6, rel=1e-4)

    def test_cumulative_total_in_extra(self):
        r = LearningCurveEstimator().estimate(1000, 0.80, 16, build_curve=True)
        assert "cumulative_total" in r.extra
        assert r.extra["cumulative_total"] == pytest.approx(8920.1369, rel=1e-4)

    def test_cumulative_average_in_extra(self):
        r = LearningCurveEstimator().estimate(1000, 0.80, 16)
        cum_avg = r.extra.get("cumulative_average")
        expected = r.extra["cumulative_total"] / 16
        assert cum_avg == pytest.approx(expected, rel=1e-8)

    def test_b_exponent_in_extra(self):
        r = LearningCurveEstimator().estimate(1000, 0.80, 10)
        b_expected = math.log(0.80) / math.log(2)
        assert r.extra["b"] == pytest.approx(b_expected, rel=1e-8)

    def test_curve_data_when_build_curve_true(self):
        r = LearningCurveEstimator().estimate(1000, 0.80, 5, build_curve=True)
        curve = r.extra.get("curve", [])
        assert len(curve) == 5
        assert curve[0]["n"] == 1
        assert curve[-1]["n"] == 5

    def test_curve_data_absent_when_build_curve_false(self):
        r = LearningCurveEstimator().estimate(1000, 0.80, 5, build_curve=False)
        # curve key should either be absent or empty
        assert len(r.extra.get("curve", [])) == 0

    def test_unit_time_decreasing(self):
        r = LearningCurveEstimator().estimate(1000, 0.80, 10, build_curve=True)
        times = [pt["unit_time"] for pt in r.extra["curve"]]
        for a, b in zip(times, times[1:]):
            assert a > b, "Unit times should decrease monotonically"

    def test_80_percent_unit_time_at_doubling(self):
        # Wright unit-time model: T_N = T1 × N^b, b = ln(rate)/ln(2)
        # At N=2: T_2 = T1 × 2^b = T1 × rate  (this is the 80% definition)
        # i.e. unit time at N=2 equals 80% of T1
        r2 = LearningCurveEstimator().estimate(1000, 0.80, 2, build_curve=True)
        unit_time_at_2 = r2.extra["curve"][1]["unit_time"]
        assert unit_time_at_2 == pytest.approx(800.0, rel=1e-5)

    def test_raises_on_invalid_learning_rate_above_1(self):
        with pytest.raises(ValueError, match="learning_rate"):
            LearningCurveEstimator().estimate(1000, 1.1, 5)

    def test_raises_on_zero_learning_rate(self):
        with pytest.raises(ValueError, match="learning_rate"):
            LearningCurveEstimator().estimate(1000, 0.0, 5)

    def test_raises_on_negative_learning_rate(self):
        with pytest.raises(ValueError):
            LearningCurveEstimator().estimate(1000, -0.5, 5)

    def test_raises_on_target_unit_less_than_1(self):
        with pytest.raises(ValueError, match="target_unit"):
            LearningCurveEstimator().estimate(1000, 0.8, 0)

    def test_learning_rate_1_no_learning_all_units_equal_t1(self):
        # Rate = 1.0 → no learning → b = 0 → T_N = T1 for all N
        r = LearningCurveEstimator().estimate(500, 1.0, 10, build_curve=True)
        for pt in r.extra["curve"]:
            assert pt["unit_time"] == pytest.approx(500.0, rel=1e-8)


# ─────────────────────────────────────────────────────────────────────
#  Edge Cases
# ─────────────────────────────────────────────────────────────────────

class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_analogous_identity_factor(self):
        r = AnalogousEstimator().estimate(100_000, [AdjustmentFactor("ID", 1.0)])
        assert r.total_cost == pytest.approx(100_000.0)

    def test_bottom_up_zero_overhead(self):
        wp = WorkPackage("A", 10_000, 0, 0, overhead_pct=0)
        r  = BottomUpEstimator().estimate([wp])
        assert r.total_cost == pytest.approx(10_000.0)

    def test_work_element_zero_hours(self):
        el = WorkElement("E", hours=0, hourly_rate=100,
                          material_cost=500, equipment_cost=0)
        assert el.labour_cost == pytest.approx(0.0)
        assert el.total       == pytest.approx(500.0)

    def test_unit_factor_zero_quantity(self):
        item = UnitFactorItem("A", unit_cost=100, quantity=0, factor=1.5)
        assert item.extended_cost == pytest.approx(0.0)

    def test_power_sizing_small_exponent(self):
        r = PowerSizingEstimator().estimate(100_000, 100, 200, exponent=0.0)
        assert r.total_cost == pytest.approx(100_000.0)

    def test_cost_estimate_result_total_positive(self):
        r = UnitFactorEstimator().estimate([
            UnitFactorItem("A", 100, 50, 1.0)])
        assert r.total_cost > 0

    def test_all_estimators_return_cost_estimate_result(self):
        results = [
            AnalogousEstimator().estimate(100, []),
            BottomUpEstimator().estimate([WorkPackage("A", 100, 0, 0)]),
            WorkElementEstimator().estimate([WorkElement("A", 1, 100)]),
            PowerSizingEstimator().estimate(100, 10, 20, 0.6),
            UnitFactorEstimator().estimate([UnitFactorItem("A", 10, 5)]),
            LearningCurveEstimator().estimate(100, 0.9, 5),
        ]
        for r in results:
            assert isinstance(r, CostEstimateResult)


# ─────────────────────────────────────────────────────────────────────
#  METHOD_LABELS
# ─────────────────────────────────────────────────────────────────────

class TestMethodLabels:
    """Validate the METHOD_LABELS constant."""

    def test_has_seven_labels(self):
        assert len(METHOD_LABELS) == 7

    def test_all_strings(self):
        assert all(isinstance(lbl, str) for lbl in METHOD_LABELS)

    def test_no_empty_labels(self):
        assert all(lbl.strip() for lbl in METHOD_LABELS)


# ─────────────────────────────────────────────────────────────────────
#  Step Generators
# ─────────────────────────────────────────────────────────────────────

class TestStepGenerators:
    """Smoke tests: step generators return non-empty Step lists."""

    def setup_method(self):
        from pmhelper.core.cost_estimation_step_generator import (
            cost_estimation_theory_steps,
            analogous_steps,
            bottom_up_steps,
            work_element_steps,
            power_sizing_steps,
            unit_factor_steps,
            learning_curve_steps,
        )
        self._theory    = cost_estimation_theory_steps
        self._analogous = analogous_steps
        self._bottom_up = bottom_up_steps
        self._work_el   = work_element_steps
        self._power_sz  = power_sizing_steps
        self._unit_fac  = unit_factor_steps
        self._lc        = learning_curve_steps

    def test_theory_steps_not_empty(self):
        steps = self._theory()
        assert len(steps) >= 1

    def test_analogous_steps(self):
        result = AnalogousEstimator().estimate(
            100_000, [AdjustmentFactor("A", 1.1)])
        steps = self._analogous(result, 100_000,
                                 [AdjustmentFactor("A", 1.1)])
        assert len(steps) >= 1
        for s in steps:
            assert s.title

    def test_bottom_up_steps(self):
        wps    = [WorkPackage("A", 10_000, 0, 0, 10)]
        result = BottomUpEstimator().estimate(wps)
        steps  = self._bottom_up(result, wps)
        assert len(steps) >= 1

    def test_work_element_steps(self):
        els    = [WorkElement("A", 100, 50, 200, 0)]
        result = WorkElementEstimator().estimate(els)
        steps  = self._work_el(result, els)
        assert len(steps) >= 1

    def test_power_sizing_steps(self):
        result = PowerSizingEstimator().estimate(500_000, 100, 200, 0.6)
        steps  = self._power_sz(result, 500_000, 100, 200, 0.6)
        assert len(steps) >= 1

    def test_unit_factor_steps(self):
        items  = [UnitFactorItem("A", 100, 50, 1.0)]
        result = UnitFactorEstimator().estimate(items)
        steps  = self._unit_fac(result, items)
        assert len(steps) >= 1

    def test_learning_curve_steps(self):
        result = LearningCurveEstimator().estimate(1000, 0.8, 16)
        steps  = self._lc(result, 1000, 0.8, 16)
        assert len(steps) >= 1
        first_step = steps[0]
        assert first_step.title
