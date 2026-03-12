"""
Tests for SWOT Analysis — models and extractor.
"""

import pytest
from pmhelper.core.swot_models_edu import (
    SWOTFactor, SWOTCategory, SWOTSource, SWOTAnalysis,
)
from pmhelper.utils.swot_extractor_edu import SWOTExtractor


# ---------------------------------------------------------------------------
# SWOTFactor tests
# ---------------------------------------------------------------------------

class TestSWOTFactor:
    def test_create_factor(self):
        f = SWOTFactor(text="Strong team", category=SWOTCategory.STRENGTH,
                       source=SWOTSource.MANUAL)
        assert f.text == "Strong team"
        assert f.category == SWOTCategory.STRENGTH
        assert f.source == SWOTSource.MANUAL
        assert f.weight == 0.5
        assert f.linked_to == ""

    def test_validate_ok(self):
        f = SWOTFactor(text="Test", category=SWOTCategory.WEAKNESS,
                       source=SWOTSource.MANUAL, weight=0.8)
        assert f.validate() == []

    def test_validate_empty_text(self):
        f = SWOTFactor(text="", category=SWOTCategory.STRENGTH,
                       source=SWOTSource.MANUAL)
        errors = f.validate()
        assert len(errors) == 1
        assert "required" in errors[0].lower()

    def test_validate_bad_weight(self):
        f = SWOTFactor(text="X", category=SWOTCategory.STRENGTH,
                       source=SWOTSource.MANUAL, weight=1.5)
        errors = f.validate()
        assert any("weight" in e.lower() for e in errors)

    def test_to_from_dict(self):
        f = SWOTFactor(text="Risk A", category=SWOTCategory.THREAT,
                       source=SWOTSource.RISK_REGISTER, weight=0.7,
                       linked_to="R-001")
        d = f.to_dict()
        f2 = SWOTFactor.from_dict(d)
        assert f2.text == f.text
        assert f2.category == f.category
        assert f2.source == f.source
        assert f2.weight == f.weight
        assert f2.linked_to == f.linked_to


# ---------------------------------------------------------------------------
# SWOTAnalysis tests
# ---------------------------------------------------------------------------

class TestSWOTAnalysis:
    def test_empty_analysis(self):
        a = SWOTAnalysis()
        assert a.factor_count() == 0
        assert a.strengths == []

    def test_add_and_query(self):
        a = SWOTAnalysis()
        a.add_factor(SWOTFactor(text="S1", category=SWOTCategory.STRENGTH,
                                source=SWOTSource.MANUAL))
        a.add_factor(SWOTFactor(text="W1", category=SWOTCategory.WEAKNESS,
                                source=SWOTSource.MANUAL))
        a.add_factor(SWOTFactor(text="O1", category=SWOTCategory.OPPORTUNITY,
                                source=SWOTSource.CHARTER))
        a.add_factor(SWOTFactor(text="T1", category=SWOTCategory.THREAT,
                                source=SWOTSource.EVM))

        assert a.factor_count() == 4
        assert len(a.strengths) == 1
        assert len(a.weaknesses) == 1
        assert len(a.opportunities) == 1
        assert len(a.threats) == 1

    def test_remove_factor(self):
        a = SWOTAnalysis()
        f = SWOTFactor(text="S1", category=SWOTCategory.STRENGTH,
                       source=SWOTSource.MANUAL)
        a.add_factor(f)
        assert a.factor_count() == 1
        a.remove_factor(f)
        assert a.factor_count() == 0

    def test_clear(self):
        a = SWOTAnalysis()
        for i in range(5):
            a.add_factor(SWOTFactor(text=f"F{i}", category=SWOTCategory.STRENGTH,
                                    source=SWOTSource.MANUAL))
        a.clear()
        assert a.factor_count() == 0

    def test_to_from_dict(self):
        a = SWOTAnalysis()
        a.add_factor(SWOTFactor(text="S1", category=SWOTCategory.STRENGTH,
                                source=SWOTSource.MANUAL, weight=0.9))
        a.add_factor(SWOTFactor(text="T1", category=SWOTCategory.THREAT,
                                source=SWOTSource.EVM, weight=0.3))
        d = a.to_dict()
        a2 = SWOTAnalysis.from_dict(d)
        assert a2.factor_count() == 2
        assert a2.strengths[0].text == "S1"
        assert a2.threats[0].source == SWOTSource.EVM


# ---------------------------------------------------------------------------
# SWOTExtractor tests
# ---------------------------------------------------------------------------

class TestSWOTExtractor:
    def test_from_charter_basic(self):
        charter = {
            "business_case": "AI-driven automation",
            "constraints": ["Budget limited to $1M"],
            "assumptions": ["Stable market"],
            "dependencies": ["Third-party API"],
        }
        factors = SWOTExtractor.from_charter(charter)
        assert len(factors) >= 4
        cats = {f.category for f in factors}
        assert SWOTCategory.OPPORTUNITY in cats
        assert SWOTCategory.WEAKNESS in cats
        assert SWOTCategory.THREAT in cats

    def test_from_charter_empty(self):
        factors = SWOTExtractor.from_charter({})
        assert factors == []

    def test_from_charter_stakeholders(self):
        charter = {
            "stakeholders": [
                {"name": "CEO", "influence": "high"},
                {"name": "User", "influence": "low"},
            ],
        }
        factors = SWOTExtractor.from_charter(charter)
        strengths = [f for f in factors if f.category == SWOTCategory.STRENGTH]
        assert len(strengths) == 1
        assert "CEO" in strengths[0].text

    def test_from_evm_healthy(self):
        kpis = {"cpi": 1.1, "spi": 1.05}
        factors = SWOTExtractor.from_evm(kpis)
        assert len(factors) == 2
        assert all(f.category == SWOTCategory.STRENGTH for f in factors)

    def test_from_evm_unhealthy(self):
        kpis = {"cpi": 0.80, "spi": 0.85}
        factors = SWOTExtractor.from_evm(kpis)
        assert len(factors) == 2
        assert all(f.category == SWOTCategory.WEAKNESS for f in factors)

    def test_from_evm_eac_overrun(self):
        kpis = {"eac1": 1200000}
        factors = SWOTExtractor.from_evm(kpis, bac=1000000)
        assert len(factors) == 1
        assert factors[0].category == SWOTCategory.WEAKNESS
        assert "overrun" in factors[0].text.lower()

    def test_from_risk_register_none(self):
        factors = SWOTExtractor.from_risk_register(None)
        assert factors == []

    def test_extract_all(self):
        charter = {"business_case": "Growth"}
        kpis = {"cpi": 0.9, "spi": 1.1}
        analysis = SWOTExtractor.extract_all(
            charter_data=charter, kpis=kpis, bac=100000)
        assert analysis.factor_count() >= 2
        assert isinstance(analysis, SWOTAnalysis)
