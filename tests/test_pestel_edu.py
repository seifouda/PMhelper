"""
Tests for PESTEL Analysis models.
"""

import pytest
from pmhelper.core.pestel_models_edu import (
    PESTELFactor, PESTELCategory, PESTELAnalysis,
)


# ---------------------------------------------------------------------------
# PESTELFactor tests
# ---------------------------------------------------------------------------

class TestPESTELFactor:
    def test_create_factor(self):
        f = PESTELFactor(
            category=PESTELCategory.ECONOMIC,
            description="Inflation rising",
            impact_score=-3.0,
            probability=0.7,
        )
        assert f.category == PESTELCategory.ECONOMIC
        assert f.impact_score == -3.0
        assert f.probability == 0.7

    def test_exposure(self):
        f = PESTELFactor(
            category=PESTELCategory.POLITICAL,
            description="New regulation",
            impact_score=-4.0,
            probability=0.5,
        )
        assert f.exposure == 2.0  # |−4| × 0.5

    def test_exposure_positive(self):
        f = PESTELFactor(
            category=PESTELCategory.TECHNOLOGICAL,
            description="New platform",
            impact_score=3.0,
            probability=0.8,
        )
        assert f.exposure == pytest.approx(2.4)

    def test_validate_ok(self):
        f = PESTELFactor(
            category=PESTELCategory.SOCIAL,
            description="Workforce training",
            impact_score=2.0,
            probability=0.5,
            timeframe="Medium-term",
        )
        assert f.validate() == []

    def test_validate_no_description(self):
        f = PESTELFactor(
            category=PESTELCategory.LEGAL,
            description="",
        )
        errors = f.validate()
        assert any("description" in e.lower() for e in errors)

    def test_validate_bad_impact(self):
        f = PESTELFactor(
            category=PESTELCategory.ECONOMIC,
            description="Test",
            impact_score=6.0,
        )
        errors = f.validate()
        assert any("impact" in e.lower() for e in errors)

    def test_validate_bad_probability(self):
        f = PESTELFactor(
            category=PESTELCategory.ECONOMIC,
            description="Test",
            probability=1.5,
        )
        errors = f.validate()
        assert any("probability" in e.lower() for e in errors)

    def test_validate_bad_timeframe(self):
        f = PESTELFactor(
            category=PESTELCategory.ECONOMIC,
            description="Test",
            timeframe="Unknown",
        )
        errors = f.validate()
        assert any("timeframe" in e.lower() for e in errors)

    def test_to_from_dict(self):
        f = PESTELFactor(
            category=PESTELCategory.ENVIRONMENTAL,
            description="Carbon tax",
            impact_score=-2.5,
            probability=0.6,
            timeframe="Long-term",
            mitigation="Switch to renewables",
        )
        d = f.to_dict()
        f2 = PESTELFactor.from_dict(d)
        assert f2.category == f.category
        assert f2.description == f.description
        assert f2.impact_score == f.impact_score
        assert f2.probability == f.probability
        assert f2.timeframe == f.timeframe
        assert f2.mitigation == f.mitigation


# ---------------------------------------------------------------------------
# PESTELAnalysis tests
# ---------------------------------------------------------------------------

class TestPESTELAnalysis:
    def _sample_analysis(self) -> PESTELAnalysis:
        a = PESTELAnalysis()
        a.add_factor(PESTELFactor(PESTELCategory.POLITICAL, "Regulation", -3, 0.7))
        a.add_factor(PESTELFactor(PESTELCategory.ECONOMIC, "Inflation", -2, 0.8))
        a.add_factor(PESTELFactor(PESTELCategory.SOCIAL, "Aging workforce", -1, 0.5))
        a.add_factor(PESTELFactor(PESTELCategory.TECHNOLOGICAL, "AI tools", 4, 0.9))
        a.add_factor(PESTELFactor(PESTELCategory.ENVIRONMENTAL, "Green mandate", -2, 0.6))
        a.add_factor(PESTELFactor(PESTELCategory.LEGAL, "GDPR", -3, 0.8))
        return a

    def test_empty(self):
        a = PESTELAnalysis()
        assert a.factor_count() == 0
        assert a.total_exposure() == 0

    def test_by_category(self):
        a = self._sample_analysis()
        assert len(a.political) == 1
        assert len(a.technological) == 1

    def test_total_exposure(self):
        a = self._sample_analysis()
        assert a.total_exposure() > 0

    def test_top_risks(self):
        a = self._sample_analysis()
        risks = a.top_risks(3)
        assert len(risks) == 3
        # Should be ordered by exposure descending
        for i in range(len(risks) - 1):
            assert risks[i].exposure >= risks[i + 1].exposure

    def test_top_opportunities(self):
        a = self._sample_analysis()
        opps = a.top_opportunities(2)
        assert len(opps) == 1  # only one positive factor
        assert opps[0].impact_score > 0

    def test_remove_factor(self):
        a = self._sample_analysis()
        count = a.factor_count()
        f = a.factors[0]
        assert a.remove_factor(f) is True
        assert a.factor_count() == count - 1

    def test_clear(self):
        a = self._sample_analysis()
        a.clear()
        assert a.factor_count() == 0

    def test_factors_for_risk_register(self):
        a = PESTELAnalysis()
        a.add_factor(PESTELFactor(PESTELCategory.POLITICAL, "Tariffs",
                                  -3, 0.7, mitigation="Diversify suppliers"))
        a.add_factor(PESTELFactor(PESTELCategory.TECHNOLOGICAL, "AI boost",
                                  4, 0.9, mitigation="Invest in training"))
        results = a.factors_for_risk_register()
        # Only negative-impact factors with mitigations
        assert len(results) == 1
        assert "POL" in results[0]["name"]

    def test_to_from_dict(self):
        a = self._sample_analysis()
        d = a.to_dict()
        a2 = PESTELAnalysis.from_dict(d)
        assert a2.factor_count() == a.factor_count()
        assert a2.political[0].description == a.political[0].description
