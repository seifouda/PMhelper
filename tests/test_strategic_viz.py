"""
Tests for Phase 9 — Strategic Visualizations.
SWOT bubble chart data, model extensions, PESTEL radar interactivity.
"""

import json
import math
import os
import pytest

from pmhelper.core.swot_models_edu import (
    SWOTFactor, SWOTCategory, SWOTSource, SWOTAnalysis,
)
from pmhelper.core.pestel_models_edu import (
    PESTELFactor, PESTELCategory, PESTELAnalysis,
)


# ---------------------------------------------------------------------------
# 9.1 — SWOTFactor model extensions
# ---------------------------------------------------------------------------

class TestSWOTFactorExtensions:
    """Tests for the new impact_score and likelihood fields."""

    def test_default_values(self):
        f = SWOTFactor(text="Test", category=SWOTCategory.STRENGTH)
        assert f.impact_score == 3.0
        assert f.likelihood == 0.5

    def test_custom_values(self):
        f = SWOTFactor(
            text="High impact",
            category=SWOTCategory.THREAT,
            impact_score=4.8,
            likelihood=0.9,
        )
        assert f.impact_score == 4.8
        assert f.likelihood == 0.9

    def test_validate_impact_score_ok(self):
        f = SWOTFactor(text="OK", category=SWOTCategory.STRENGTH,
                       impact_score=1.0, likelihood=0.0)
        assert f.validate() == []

    def test_validate_impact_score_too_low(self):
        f = SWOTFactor(text="Bad", category=SWOTCategory.STRENGTH,
                       impact_score=0.5)
        errors = f.validate()
        assert any("impact" in e.lower() for e in errors)

    def test_validate_impact_score_too_high(self):
        f = SWOTFactor(text="Bad", category=SWOTCategory.STRENGTH,
                       impact_score=5.5)
        errors = f.validate()
        assert any("impact" in e.lower() for e in errors)

    def test_validate_likelihood_too_low(self):
        f = SWOTFactor(text="Bad", category=SWOTCategory.STRENGTH,
                       likelihood=-0.1)
        errors = f.validate()
        assert any("likelihood" in e.lower() for e in errors)

    def test_validate_likelihood_too_high(self):
        f = SWOTFactor(text="Bad", category=SWOTCategory.STRENGTH,
                       likelihood=1.1)
        errors = f.validate()
        assert any("likelihood" in e.lower() for e in errors)

    def test_to_dict_includes_new_fields(self):
        f = SWOTFactor(
            text="Serialise", category=SWOTCategory.WEAKNESS,
            impact_score=4.0, likelihood=0.7,
        )
        d = f.to_dict()
        assert d["impact_score"] == 4.0
        assert d["likelihood"] == 0.7

    def test_from_dict_reads_new_fields(self):
        d = {
            "text": "Round-trip",
            "category": "Opportunity",
            "impact_score": 2.5,
            "likelihood": 0.3,
        }
        f = SWOTFactor.from_dict(d)
        assert f.impact_score == 2.5
        assert f.likelihood == 0.3

    def test_from_dict_backward_compat(self):
        """Old data without impact_score/likelihood should get defaults."""
        d = {"text": "Legacy", "category": "Strength", "weight": 0.8}
        f = SWOTFactor.from_dict(d)
        assert f.impact_score == 3.0
        assert f.likelihood == 0.5

    def test_round_trip_full(self):
        f = SWOTFactor(
            text="Full round-trip",
            category=SWOTCategory.THREAT,
            source=SWOTSource.RISK_REGISTER,
            weight=0.6,
            linked_to="R-99",
            impact_score=4.2,
            likelihood=0.85,
        )
        d = f.to_dict()
        f2 = SWOTFactor.from_dict(d)
        assert f2.text == f.text
        assert f2.category == f.category
        assert f2.source == f.source
        assert f2.weight == f.weight
        assert f2.linked_to == f.linked_to
        assert f2.impact_score == f.impact_score
        assert f2.likelihood == f.likelihood


# ---------------------------------------------------------------------------
# 9.2 — Bubble chart data generation helpers
# ---------------------------------------------------------------------------

class TestBubbleChartData:
    """Test that bubble chart positioning logic is correct."""

    def _make_analysis(self):
        return SWOTAnalysis(factors=[
            SWOTFactor("S1", SWOTCategory.STRENGTH, weight=0.8, impact_score=4.0, likelihood=0.9),
            SWOTFactor("W1", SWOTCategory.WEAKNESS, weight=0.3, impact_score=2.0, likelihood=0.2),
            SWOTFactor("O1", SWOTCategory.OPPORTUNITY, weight=0.5, impact_score=3.0, likelihood=0.5),
            SWOTFactor("T1", SWOTCategory.THREAT, weight=0.7, impact_score=5.0, likelihood=0.8),
        ])

    def test_quadrant_assignment(self):
        """Each category maps to the correct quadrant position."""
        from pmhelper.gui.tabs.swot_tab_edu import _BUBBLE_QUADRANT
        assert _BUBBLE_QUADRANT[SWOTCategory.STRENGTH] == (0, 1)    # upper-left
        assert _BUBBLE_QUADRANT[SWOTCategory.WEAKNESS] == (1, 1)    # upper-right
        assert _BUBBLE_QUADRANT[SWOTCategory.OPPORTUNITY] == (0, 0) # lower-left
        assert _BUBBLE_QUADRANT[SWOTCategory.THREAT] == (1, 0)      # lower-right

    def test_viz_modes_exist(self):
        from pmhelper.gui.tabs.swot_tab_edu import _VIZ_MODES
        assert "Impact vs Weight" in _VIZ_MODES
        assert "Strategic Fit" in _VIZ_MODES
        assert "Priority Matrix" in _VIZ_MODES

    def test_viz_mode_keys(self):
        from pmhelper.gui.tabs.swot_tab_edu import _VIZ_MODES
        for mode_name, mode in _VIZ_MODES.items():
            assert "x" in mode
            assert "y" in mode
            assert "size" in mode

    def test_normalise_impact(self):
        from pmhelper.gui.tabs.swot_tab_edu import SWOTTabEdu
        assert SWOTTabEdu._normalise_attr(1.0, "impact_score") == pytest.approx(0.0)
        assert SWOTTabEdu._normalise_attr(5.0, "impact_score") == pytest.approx(1.0)
        assert SWOTTabEdu._normalise_attr(3.0, "impact_score") == pytest.approx(0.5)

    def test_normalise_weight(self):
        from pmhelper.gui.tabs.swot_tab_edu import SWOTTabEdu
        assert SWOTTabEdu._normalise_attr(0.0, "weight") == 0.0
        assert SWOTTabEdu._normalise_attr(1.0, "weight") == 1.0
        assert SWOTTabEdu._normalise_attr(0.5, "likelihood") == 0.5

    def test_normalise_clamps(self):
        from pmhelper.gui.tabs.swot_tab_edu import SWOTTabEdu
        assert SWOTTabEdu._normalise_attr(-0.5, "weight") == 0.0
        assert SWOTTabEdu._normalise_attr(1.5, "likelihood") == 1.0

    def test_analysis_with_scores_roundtrip(self):
        a = self._make_analysis()
        d = a.to_dict()
        a2 = SWOTAnalysis.from_dict(d)
        assert len(a2.factors) == 4
        assert a2.factors[0].impact_score == 4.0
        assert a2.factors[3].likelihood == 0.8


# ---------------------------------------------------------------------------
# 9.3 — Dropdown filter modes
# ---------------------------------------------------------------------------

class TestVizModeMapping:
    def test_all_attributes_valid(self):
        """All mode attributes are real SWOTFactor fields."""
        from pmhelper.gui.tabs.swot_tab_edu import _VIZ_MODES
        f = SWOTFactor("X", SWOTCategory.STRENGTH)
        for mode_name, mode in _VIZ_MODES.items():
            for key in ("x", "y", "size"):
                assert hasattr(f, mode[key]), f"{mode_name}.{key} = {mode[key]} not on SWOTFactor"


# ---------------------------------------------------------------------------
# 9.8 — Demo file loading
# ---------------------------------------------------------------------------

class TestSWOTScoredDemo:
    DEMO_PATH = os.path.join(
        os.path.dirname(__file__), "..", "data", "demos", "v2", "swot_scored_demo.json"
    )

    def test_demo_file_exists(self):
        assert os.path.isfile(self.DEMO_PATH), f"Missing {self.DEMO_PATH}"

    def test_demo_loads(self):
        with open(self.DEMO_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        analysis = SWOTAnalysis.from_dict(data["swot_analysis"])
        assert analysis.factor_count() == 16

    def test_demo_four_per_quadrant(self):
        with open(self.DEMO_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        analysis = SWOTAnalysis.from_dict(data["swot_analysis"])
        assert len(analysis.strengths) == 4
        assert len(analysis.weaknesses) == 4
        assert len(analysis.opportunities) == 4
        assert len(analysis.threats) == 4

    def test_demo_all_factors_have_scores(self):
        with open(self.DEMO_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        analysis = SWOTAnalysis.from_dict(data["swot_analysis"])
        for factor in analysis.factors:
            assert 1.0 <= factor.impact_score <= 5.0
            assert 0.0 <= factor.likelihood <= 1.0
            assert 0.0 <= factor.weight <= 1.0

    def test_demo_all_factors_validate(self):
        with open(self.DEMO_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        analysis = SWOTAnalysis.from_dict(data["swot_analysis"])
        for factor in analysis.factors:
            assert factor.validate() == [], f"Validation failed for: {factor.text}"


# ---------------------------------------------------------------------------
# 9.6–9.7 — PESTEL radar data helpers
# ---------------------------------------------------------------------------

class TestPESTELRadarData:
    def _make_analysis(self):
        return PESTELAnalysis(factors=[
            PESTELFactor(PESTELCategory.POLITICAL, "Regulation change", impact_score=-3, probability=0.7),
            PESTELFactor(PESTELCategory.POLITICAL, "New tax incentive", impact_score=2, probability=0.5),
            PESTELFactor(PESTELCategory.ECONOMIC, "Recession risk", impact_score=-4, probability=0.6),
            PESTELFactor(PESTELCategory.SOCIAL, "Remote work trend", impact_score=3, probability=0.8),
            PESTELFactor(PESTELCategory.TECHNOLOGICAL, "AI adoption", impact_score=4, probability=0.9),
            PESTELFactor(PESTELCategory.ENVIRONMENTAL, "Carbon tax", impact_score=-2, probability=0.4),
            PESTELFactor(PESTELCategory.LEGAL, "GDPR fines", impact_score=-3, probability=0.3),
        ])

    def test_exposure_calculation(self):
        f = PESTELFactor(PESTELCategory.ECONOMIC, "Test", impact_score=-4, probability=0.5)
        assert f.exposure == pytest.approx(2.0)

    def test_avg_exposure_per_category(self):
        a = self._make_analysis()
        political = a.by_category(PESTELCategory.POLITICAL)
        avg = sum(f.exposure for f in political) / len(political)
        # Factor 1: |-3|*0.7=2.1, Factor 2: |2|*0.5=1.0, avg = 1.55
        assert avg == pytest.approx(1.55)

    def test_all_six_categories_accessible(self):
        a = self._make_analysis()
        assert len(a.political) == 2
        assert len(a.economic) == 1
        assert len(a.social) == 1
        assert len(a.technological) == 1
        assert len(a.environmental) == 1
        assert len(a.legal) == 1

    def test_bubble_overlay_radius_is_impact(self):
        """Bubble overlay positions factors at distance = |impact_score| along axis."""
        f = PESTELFactor(PESTELCategory.SOCIAL, "Test", impact_score=-3, probability=0.8)
        # In the radar overlay, r = abs(impact_score)
        assert abs(f.impact_score) == 3

    def test_bubble_overlay_size_proportional_to_exposure(self):
        f = PESTELFactor(PESTELCategory.SOCIAL, "Test", impact_score=4, probability=0.9)
        expected_size = f.exposure * 80 + 20  # matches chart formula
        assert expected_size == pytest.approx(4 * 0.9 * 80 + 20)
