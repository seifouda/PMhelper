"""
Phase 6 tests — Risk Assessment Matrix & Response Planning.

Covers:
  TestRiskPhase6Dataclass   — new fields and auto-computation
  TestRiskPhase6Validation  — 1-5 bounds + response_cost
  TestRiskPhase6Serialization — to_dict / from_dict round-trip
  TestBackwardCompatibility   — old dict (no Phase 6 fields) loads cleanly
  TestRiskZoneFunctions      — risk_zone(), zone_color()
  TestRiskRegisterScoring    — recompute_scores(), update_ranks(), risks_by_score()
  TestRiskRegisterZones      — zone_counts(), risks_in_cell()
  TestRiskRegisterEffectiveness — total_residual_exposure(), response_effectiveness()
  TestStepGenerators         — smoke tests for risk_step_generator.py
"""

import pytest
from pmhelper.core.risk_register_edu import (
    Risk, RiskCategory, RiskRegister,
    ResponseStrategy, risk_zone, zone_color,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_risk(rid="R01", ps=3, is_=3, **kwargs):
    """Convenience factory for Risk with sensible defaults."""
    return Risk(
        id=rid, name=f"Risk-{rid}",
        probability=0.2, impact=10000,
        prob_score=ps, impact_score=is_,
        **kwargs,
    )


def make_register(*specs):
    """Make a RiskRegister with given (prob_score, impact_score) pairs."""
    reg = RiskRegister(bac=200_000)
    for i, (ps, is_) in enumerate(specs, 1):
        reg.add_risk(make_risk(rid=f"R{i:02d}", ps=ps, is_=is_))
    return reg


# ============================================================================
# TestRiskPhase6Dataclass
# ============================================================================

class TestRiskPhase6Dataclass:
    def test_default_scores(self):
        r = make_risk()
        assert r.prob_score == 3
        assert r.impact_score == 3

    def test_risk_score_auto_computed(self):
        r = make_risk(ps=4, is_=5)
        assert r.risk_score == pytest.approx(20.0)

    def test_risk_score_min(self):
        r = make_risk(ps=1, is_=1)
        assert r.risk_score == pytest.approx(1.0)

    def test_risk_score_max(self):
        r = make_risk(ps=5, is_=5)
        assert r.risk_score == pytest.approx(25.0)

    def test_residual_score_auto_computed(self):
        r = Risk(
            id="R1", name="x", probability=0.2, impact=1000,
            prob_score=4, impact_score=5,
            residual_probability=2.0, residual_impact=3.0,
        )
        assert r.residual_score == pytest.approx(6.0)

    def test_risk_rank_default_zero(self):
        r = make_risk()
        assert r.risk_rank == 0

    def test_response_strategy_default_none(self):
        r = make_risk()
        assert r.response_strategy is None

    def test_response_fields_default_empty(self):
        r = make_risk()
        assert r.response_description == ""
        assert r.response_owner == ""
        assert r.response_cost == 0.0

    def test_narrative_fields_default_empty(self):
        r = make_risk()
        assert r.trigger_conditions == ""
        assert r.contingency_plan == ""

    def test_zone_property_critical(self):
        r = make_risk(ps=5, is_=5)   # score 25
        assert r.zone == "Critical"

    def test_zone_property_high(self):
        r = make_risk(ps=3, is_=4)   # score 12
        assert r.zone == "High"

    def test_zone_property_medium(self):
        r = make_risk(ps=3, is_=2)   # score 6
        assert r.zone == "Medium"

    def test_zone_property_low(self):
        r = make_risk(ps=1, is_=2)   # score 2
        assert r.zone == "Low"

    def test_residual_zone_property(self):
        r = Risk(
            id="R1", name="x", probability=0.2, impact=1000,
            prob_score=5, impact_score=5,
            residual_probability=1.0, residual_impact=2.0,
        )
        assert r.residual_zone == "Low"   # residual_score = 2


# ============================================================================
# TestRiskPhase6Validation
# ============================================================================

class TestRiskPhase6Validation:
    def test_prob_score_too_low(self):
        with pytest.raises(ValueError, match="prob_score"):
            make_risk(ps=0)

    def test_prob_score_too_high(self):
        with pytest.raises(ValueError, match="prob_score"):
            make_risk(ps=6)

    def test_impact_score_too_low(self):
        with pytest.raises(ValueError, match="impact_score"):
            Risk(id="R1", name="x", probability=0.2, impact=1000,
                 prob_score=3, impact_score=0)

    def test_impact_score_too_high(self):
        with pytest.raises(ValueError, match="impact_score"):
            Risk(id="R1", name="x", probability=0.2, impact=1000,
                 prob_score=3, impact_score=6)

    def test_residual_probability_too_low(self):
        with pytest.raises(ValueError, match="residual_probability"):
            Risk(id="R1", name="x", probability=0.2, impact=1000,
                 prob_score=3, impact_score=3, residual_probability=0.0)

    def test_residual_impact_too_high(self):
        with pytest.raises(ValueError, match="residual_impact"):
            Risk(id="R1", name="x", probability=0.2, impact=1000,
                 prob_score=3, impact_score=3, residual_impact=6.0)

    def test_response_cost_negative(self):
        with pytest.raises(ValueError, match="response_cost"):
            Risk(id="R1", name="x", probability=0.2, impact=1000,
                 prob_score=3, impact_score=3, response_cost=-1.0)

    def test_response_cost_zero_allowed(self):
        r = Risk(id="R1", name="x", probability=0.2, impact=1000,
                 prob_score=3, impact_score=3, response_cost=0.0)
        assert r.response_cost == 0.0


# ============================================================================
# TestRiskPhase6Serialization
# ============================================================================

class TestRiskPhase6Serialization:
    def _full_risk(self):
        return Risk(
            id="R1", name="Vendor Failure",
            description="Supplier collapses.",
            probability=0.35, impact=50000,
            category=RiskCategory.COST,
            prob_score=4, impact_score=5,
            response_strategy=ResponseStrategy.MITIGATE,
            response_description="Qualify backup supplier.",
            response_owner="Procurement",
            response_cost=5000.0,
            residual_probability=2.0, residual_impact=3.0,
            trigger_conditions="Two missed deliveries.",
            contingency_plan="Activate secondary supplier.",
        )

    def test_to_dict_includes_new_fields(self):
        r = self._full_risk()
        d = r.to_dict()
        assert d["prob_score"] == 4
        assert d["impact_score"] == 5
        assert d["response_strategy"] == "Mitigate"
        assert d["response_description"] == "Qualify backup supplier."
        assert d["response_owner"] == "Procurement"
        assert d["response_cost"] == pytest.approx(5000.0)
        assert d["residual_probability"] == pytest.approx(2.0)
        assert d["residual_impact"] == pytest.approx(3.0)
        assert d["trigger_conditions"] == "Two missed deliveries."
        assert d["contingency_plan"] == "Activate secondary supplier."

    def test_to_dict_strategy_serialized_as_value_string(self):
        r = self._full_risk()
        d = r.to_dict()
        assert d["response_strategy"] == "Mitigate"
        assert isinstance(d["response_strategy"], str)

    def test_to_dict_none_strategy(self):
        r = make_risk()
        d = r.to_dict()
        assert d["response_strategy"] is None

    def test_from_dict_roundtrip(self):
        r = self._full_risk()
        d = r.to_dict()
        r2 = Risk.from_dict(d)
        assert r2.id == r.id
        assert r2.prob_score == r.prob_score
        assert r2.impact_score == r.impact_score
        assert r2.response_strategy == ResponseStrategy.MITIGATE
        assert r2.response_description == r.response_description
        assert r2.residual_probability == pytest.approx(r.residual_probability)
        assert r2.residual_impact == pytest.approx(r.residual_impact)

    def test_from_dict_scores_recomputed(self):
        r = self._full_risk()
        d = r.to_dict()
        # Corrupt scores in dict — from_dict must recompute them
        d["risk_score"] = 999
        d["residual_score"] = 999
        r2 = Risk.from_dict(d)
        assert r2.risk_score == pytest.approx(4 * 5)     # 20
        assert r2.residual_score == pytest.approx(2 * 3)  # 6


# ============================================================================
# TestBackwardCompatibility
# ============================================================================

class TestBackwardCompatibility:
    def test_old_dict_loads_without_new_fields(self):
        """A V1 dict (no Phase 6 fields) loads cleanly with defaults."""
        old_dict = {
            "id": "R1", "name": "Old Risk",
            "description": "Legacy entry",
            "probability": 0.2, "impact": 10000,
            "category": "Schedule",
        }
        r = Risk.from_dict(old_dict)
        assert r.prob_score == 3    # default
        assert r.impact_score == 3  # default
        assert r.response_strategy is None
        assert r.risk_score == pytest.approx(9.0)  # 3×3

    def test_unknown_keys_stripped_gracefully(self):
        d = {
            "id": "R1", "name": "x",
            "probability": 0.1, "impact": 1000,
            "category": "Other",
            "some_future_field": "ignored",
        }
        r = Risk.from_dict(d)
        assert r.id == "R1"

    def test_register_from_dict_backward_compat(self):
        """RiskRegister.from_dict with V1 data works."""
        data = {
            "bac": 100000,
            "high_exposure_threshold_pct": 0.05,
            "risks": [
                {"id": "R1", "name": "A",
                 "probability": 0.3, "impact": 10000, "category": "Cost"},
                {"id": "R2", "name": "B",
                 "probability": 0.1, "impact": 5000,  "category": "Other"},
            ],
        }
        reg = RiskRegister.from_dict(data)
        assert len(reg.risks) == 2
        assert reg.risks[0].prob_score == 3  # default


# ============================================================================
# TestRiskZoneFunctions
# ============================================================================

class TestRiskZoneFunctions:
    def test_zone_critical(self):
        assert risk_zone(16) == "Critical"
        assert risk_zone(25) == "Critical"
        assert risk_zone(20) == "Critical"

    def test_zone_high(self):
        assert risk_zone(10) == "High"
        assert risk_zone(15) == "High"
        assert risk_zone(12) == "High"

    def test_zone_medium(self):
        assert risk_zone(5)  == "Medium"
        assert risk_zone(9)  == "Medium"
        assert risk_zone(7)  == "Medium"

    def test_zone_low(self):
        assert risk_zone(1)  == "Low"
        assert risk_zone(4)  == "Low"
        assert risk_zone(3)  == "Low"

    def test_zone_color_returns_hex(self):
        assert zone_color(25).startswith("#")
        assert zone_color(12).startswith("#")
        assert zone_color(7).startswith("#")
        assert zone_color(2).startswith("#")

    def test_zone_color_critical_red(self):
        assert zone_color(25) == "#e74c3c"

    def test_zone_color_low_green(self):
        assert zone_color(1) == "#27ae60"


# ============================================================================
# TestRiskRegisterScoring
# ============================================================================

class TestRiskRegisterScoring:
    def test_recompute_scores_updates_risk_score(self):
        reg = make_register((3, 3))
        r = reg.risks[0]
        r.prob_score = 5
        r.impact_score = 5
        # Before recompute, risk_score is stale (9.0 from construction)
        reg.recompute_scores()
        assert r.risk_score == pytest.approx(25.0)

    def test_recompute_scores_updates_residual_score(self):
        reg = make_register((3, 3))
        r = reg.risks[0]
        r.residual_probability = 1.0
        r.residual_impact = 2.0
        reg.recompute_scores()
        assert r.residual_score == pytest.approx(2.0)

    def test_update_ranks_assigns_rank_one_to_highest_score(self):
        reg = make_register((5, 5), (2, 2), (3, 3))  # scores 25, 4, 9
        reg.recompute_scores()
        reg.update_ranks()
        ranks = {r.risk_score: r.risk_rank for r in reg.risks}
        assert ranks[25.0] == 1
        assert ranks[9.0] == 2
        assert ranks[4.0] == 3

    def test_risks_by_score_descending_order(self):
        reg = make_register((1, 1), (5, 5), (3, 3))   # scores 1, 25, 9
        reg.recompute_scores()
        scores = [r.risk_score for r in reg.risks_by_score()]
        assert scores == sorted(scores, reverse=True)

    def test_update_risk_triggers_recompute(self):
        reg = make_register((3, 3))
        reg.update_risk(reg.risks[0].id, prob_score=5, impact_score=5)
        assert reg.risks[0].risk_score == pytest.approx(25.0)

    def test_update_risk_response_strategy_string_to_enum(self):
        reg = make_register((3, 3))
        reg.update_risk(reg.risks[0].id, response_strategy="Mitigate")
        assert reg.risks[0].response_strategy == ResponseStrategy.MITIGATE


# ============================================================================
# TestRiskRegisterZones
# ============================================================================

class TestRiskRegisterZones:
    def _build_zone_register(self):
        """Build a register with known zone distribution."""
        # 2 Critical (25, 20), 1 High (12), 2 Medium (9, 6), 1 Low (2)
        reg = RiskRegister(bac=500_000)
        data = [
            ("C1", 5, 5),  # 25 Critical
            ("C2", 4, 5),  # 20 Critical
            ("H1", 3, 4),  # 12 High
            ("M1", 3, 3),  # 9  Medium
            ("M2", 2, 3),  # 6  Medium
            ("L1", 1, 2),  # 2  Low
        ]
        for rid, ps, is_ in data:
            reg.add_risk(Risk(id=rid, name=rid, probability=0.2, impact=1000,
                             prob_score=ps, impact_score=is_))
        return reg

    def test_zone_counts_critical(self):
        reg = self._build_zone_register()
        counts = reg.zone_counts()
        assert counts["Critical"] == 2

    def test_zone_counts_high(self):
        counts = self._build_zone_register().zone_counts()
        assert counts["High"] == 1

    def test_zone_counts_medium(self):
        counts = self._build_zone_register().zone_counts()
        assert counts["Medium"] == 2

    def test_zone_counts_low(self):
        counts = self._build_zone_register().zone_counts()
        assert counts["Low"] == 1

    def test_risks_in_cell_exact_match(self):
        reg = self._build_zone_register()
        cell_35 = reg.risks_in_cell(5, 5)   # p=5, i=5
        assert len(cell_35) == 1
        assert cell_35[0].id == "C1"

    def test_risks_in_cell_empty(self):
        reg = self._build_zone_register()
        assert reg.risks_in_cell(1, 1) == []

    def test_risks_in_cell_multiple(self):
        reg = RiskRegister(bac=100_000)
        for i in range(3):
            reg.add_risk(Risk(id=f"R{i}", name=f"R{i}",
                             probability=0.1, impact=1000,
                             prob_score=3, impact_score=3))
        assert len(reg.risks_in_cell(3, 3)) == 3


# ============================================================================
# TestRiskRegisterEffectiveness
# ============================================================================

class TestRiskRegisterEffectiveness:
    def _build_response_register(self):
        """Build a register with known original and residual scores."""
        reg = RiskRegister(bac=300_000)
        r1 = Risk(id="R1", name="A", probability=0.2, impact=1000,
                  prob_score=5, impact_score=5,   # original 25
                  residual_probability=2.0, residual_impact=2.0)  # residual 4
        r2 = Risk(id="R2", name="B", probability=0.1, impact=500,
                  prob_score=3, impact_score=3,   # original 9
                  residual_probability=1.0, residual_impact=3.0)  # residual 3
        reg.add_risk(r1)
        reg.add_risk(r2)
        return reg

    def test_total_residual_exposure(self):
        reg = self._build_response_register()
        # r1: residual 4, r2: residual 3 → total 7
        assert reg.total_residual_exposure() == pytest.approx(7.0)

    def test_response_effectiveness_percentage(self):
        reg = self._build_response_register()
        # original: 25+9=34, residual: 4+3=7 → (34-7)/34 × 100 ≈ 79.41%
        eff = reg.response_effectiveness()
        assert eff == pytest.approx((34 - 7) / 34 * 100, rel=1e-3)

    def test_response_effectiveness_no_response(self):
        """If residual = original (no response), effectiveness = 0%."""
        reg = make_register((3, 3))  # prob=3, impact=3 → 9; residual default = 3×3=9
        eff = reg.response_effectiveness()
        assert eff == pytest.approx(0.0)

    def test_response_effectiveness_empty_register(self):
        reg = RiskRegister()
        assert reg.response_effectiveness() == pytest.approx(0.0)


# ============================================================================
# TestStepGenerators
# ============================================================================

class TestStepGenerators:
    def test_theory_steps_returns_list(self):
        from pmhelper.core.risk_step_generator import risk_assessment_theory_steps
        steps = risk_assessment_theory_steps()
        assert isinstance(steps, list)
        assert len(steps) >= 4

    def test_theory_steps_have_title(self):
        from pmhelper.core.risk_step_generator import risk_assessment_theory_steps
        for step in risk_assessment_theory_steps():
            assert step.title

    def test_risk_scoring_steps_returns_list(self):
        from pmhelper.core.risk_step_generator import risk_scoring_steps
        r = make_risk(ps=4, is_=3)
        steps = risk_scoring_steps(r)
        assert isinstance(steps, list)
        assert len(steps) >= 3

    def test_risk_scoring_steps_contain_score(self):
        from pmhelper.core.risk_step_generator import risk_scoring_steps
        r = make_risk(ps=4, is_=3)  # score 12
        steps = risk_scoring_steps(r)
        combined = " ".join(s.formula + s.result for s in steps)
        assert "12" in combined

    def test_response_strategy_steps_returns_list(self):
        from pmhelper.core.risk_step_generator import response_strategy_steps
        r = Risk(id="R1", name="x", probability=0.2, impact=1000,
                 prob_score=5, impact_score=4,
                 response_strategy=ResponseStrategy.MITIGATE,
                 response_description="Run tests early.",
                 residual_probability=2.0, residual_impact=2.0)
        steps = response_strategy_steps(r)
        assert isinstance(steps, list)
        assert len(steps) >= 3

    def test_full_register_steps_returns_list(self):
        from pmhelper.core.risk_step_generator import full_register_steps
        reg = make_register((4, 5), (2, 3), (1, 1))
        steps = full_register_steps(reg)
        assert isinstance(steps, list)
        assert len(steps) >= 3
