"""Tests for Risk Register — Phase 3."""

import json
import csv
import os
import tempfile
import pytest

from pmhelper.core.risk_register_edu import Risk, RiskCategory, RiskRegister
from pmhelper.utils.risk_io_edu import (
    save_register, load_register, export_to_csv, import_from_csv,
)


# ---------------------------------------------------------------
# Risk dataclass
# ---------------------------------------------------------------

class TestRisk:
    def test_basic_creation(self):
        r = Risk(id="R1", name="delay", probability=0.3, impact=10000)
        assert r.exposure == pytest.approx(3000.0)
        assert r.category == RiskCategory.OTHER

    def test_exposure_auto_computed(self):
        r = Risk(id="R1", name="x", probability=0.5, impact=20000)
        assert r.exposure == pytest.approx(10000.0)

    def test_zero_probability(self):
        r = Risk(id="R1", name="x", probability=0.0, impact=5000)
        assert r.exposure == pytest.approx(0.0)

    def test_zero_impact(self):
        r = Risk(id="R1", name="x", probability=0.8, impact=0.0)
        assert r.exposure == pytest.approx(0.0)

    def test_full_probability(self):
        r = Risk(id="R1", name="x", probability=1.0, impact=1000)
        assert r.exposure == pytest.approx(1000.0)

    def test_invalid_probability_high(self):
        with pytest.raises(ValueError, match="probability must be 0"):
            Risk(id="R1", name="x", probability=1.1, impact=100)

    def test_invalid_probability_negative(self):
        with pytest.raises(ValueError, match="probability must be 0"):
            Risk(id="R1", name="x", probability=-0.1, impact=100)

    def test_invalid_impact_negative(self):
        with pytest.raises(ValueError, match="impact must be >= 0"):
            Risk(id="R1", name="x", probability=0.5, impact=-100)

    def test_validate_called_on_init(self):
        """validate() is called in __post_init__."""
        with pytest.raises(ValueError):
            Risk(id="R1", name="x", probability=2.0, impact=100)

    def test_category_enum(self):
        r = Risk(id="R1", name="x", category=RiskCategory.COST)
        assert r.category == RiskCategory.COST
        assert r.category.value == "Cost"

    def test_to_dict(self):
        r = Risk(id="R1", name="delay", probability=0.4, impact=5000,
                 category=RiskCategory.SCHEDULE)
        d = r.to_dict()
        assert d["id"] == "R1"
        assert d["category"] == "Schedule"
        assert d["exposure"] == pytest.approx(2000.0)

    def test_from_dict_roundtrip(self):
        r = Risk(id="R2", name="skill gap", description="Need training",
                 probability=0.6, impact=8000, category=RiskCategory.QUALITY)
        d = r.to_dict()
        r2 = Risk.from_dict(d)
        assert r2.id == r.id
        assert r2.name == r.name
        assert r2.description == r.description
        assert r2.probability == r.probability
        assert r2.impact == r.impact
        assert r2.category == r.category
        assert r2.exposure == pytest.approx(r.exposure)

    def test_all_categories(self):
        for cat in RiskCategory:
            r = Risk(id="R1", name="x", category=cat)
            assert r.category == cat


# ---------------------------------------------------------------
# RiskRegister
# ---------------------------------------------------------------

class TestRiskRegister:
    def _sample_register(self):
        reg = RiskRegister(bac=100000)
        reg.add_risk(Risk(id="R1", name="A", probability=0.3, impact=10000,
                          category=RiskCategory.COST))
        reg.add_risk(Risk(id="R2", name="B", probability=0.5, impact=20000,
                          category=RiskCategory.SCHEDULE))
        reg.add_risk(Risk(id="R3", name="C", probability=0.1, impact=2000,
                          category=RiskCategory.QUALITY))
        return reg

    def test_add_risk(self):
        reg = RiskRegister()
        reg.add_risk(Risk(id="R1", name="A", probability=0.5, impact=1000))
        assert len(reg.risks) == 1

    def test_add_duplicate_id_raises(self):
        reg = RiskRegister()
        reg.add_risk(Risk(id="R1", name="A"))
        with pytest.raises(ValueError, match="Duplicate risk ID"):
            reg.add_risk(Risk(id="R1", name="B"))

    def test_remove_risk(self):
        reg = self._sample_register()
        reg.remove_risk("R2")
        assert len(reg.risks) == 2
        assert reg.get_risk("R2") is None

    def test_get_risk(self):
        reg = self._sample_register()
        r = reg.get_risk("R1")
        assert r is not None
        assert r.name == "A"

    def test_get_risk_missing(self):
        reg = self._sample_register()
        assert reg.get_risk("R99") is None

    def test_update_risk(self):
        reg = self._sample_register()
        reg.update_risk("R1", probability=0.8, impact=15000)
        r = reg.get_risk("R1")
        assert r.probability == 0.8
        assert r.impact == 15000
        assert r.exposure == pytest.approx(12000.0)

    def test_update_risk_not_found(self):
        reg = self._sample_register()
        with pytest.raises(ValueError, match="Risk not found"):
            reg.update_risk("R99", probability=0.5)

    def test_update_risk_invalid_probability(self):
        reg = self._sample_register()
        with pytest.raises(ValueError, match="probability must be 0"):
            reg.update_risk("R1", probability=1.5)

    def test_total_exposure(self):
        reg = self._sample_register()
        # R1: 0.3*10000=3000, R2: 0.5*20000=10000, R3: 0.1*2000=200
        assert reg.total_exposure() == pytest.approx(13200.0)

    def test_contingency_reserve(self):
        reg = self._sample_register()
        assert reg.contingency_reserve() == pytest.approx(reg.total_exposure())

    def test_risks_by_exposure_sorted_desc(self):
        reg = self._sample_register()
        sorted_risks = reg.risks_by_exposure()
        exposures = [r.exposure for r in sorted_risks]
        assert exposures == sorted(exposures, reverse=True)
        assert sorted_risks[0].id == "R2"  # highest exposure

    def test_flag_high_exposure(self):
        reg = self._sample_register()  # bac=100000, threshold=5%
        # Threshold = 100000 * 0.05 = 5000
        # R1: 3000 (below), R2: 10000 (above), R3: 200 (below)
        flagged = reg.flag_high_exposure()
        assert len(flagged) == 1
        assert flagged[0].id == "R2"

    def test_flag_boundary_at_threshold(self):
        """Exposure exactly at threshold should NOT be flagged (> not >=)."""
        reg = RiskRegister(bac=100000, high_exposure_threshold_pct=0.05)
        reg.add_risk(Risk(id="R1", name="boundary", probability=0.5, impact=10000))
        # exposure = 5000, threshold = 5000 → NOT flagged (> not >=)
        flagged = reg.flag_high_exposure()
        assert len(flagged) == 0

    def test_flag_just_above_threshold(self):
        reg = RiskRegister(bac=100000, high_exposure_threshold_pct=0.05)
        reg.add_risk(Risk(id="R1", name="above", probability=0.5, impact=10001))
        # exposure = 5000.5, threshold = 5000 → flagged
        flagged = reg.flag_high_exposure()
        assert len(flagged) == 1

    def test_empty_register(self):
        reg = RiskRegister()
        assert reg.total_exposure() == 0.0
        assert reg.contingency_reserve() == 0.0
        assert reg.risks_by_exposure() == []
        assert reg.flag_high_exposure() == []

    def test_recompute_exposures(self):
        reg = RiskRegister()
        r = Risk(id="R1", name="x", probability=0.5, impact=1000)
        reg.risks.append(r)
        # Manually change probability without going through __post_init__
        r.probability = 0.9
        reg.recompute_exposures()
        assert r.exposure == pytest.approx(900.0)

    def test_to_dict_from_dict_roundtrip(self):
        reg = self._sample_register()
        d = reg.to_dict()
        reg2 = RiskRegister.from_dict(d)
        assert len(reg2.risks) == len(reg.risks)
        assert reg2.bac == reg.bac
        assert reg2.high_exposure_threshold_pct == reg.high_exposure_threshold_pct
        for r1, r2 in zip(reg.risks, reg2.risks):
            assert r1.id == r2.id
            assert r1.exposure == pytest.approx(r2.exposure)

    def test_update_risk_category_string(self):
        """update_risk accepts category as string."""
        reg = self._sample_register()
        reg.update_risk("R1", category="Cost")
        assert reg.get_risk("R1").category == RiskCategory.COST


# ---------------------------------------------------------------
# Risk I/O
# ---------------------------------------------------------------

class TestRiskIO:
    def _sample_register(self):
        reg = RiskRegister(bac=50000)
        reg.add_risk(Risk(id="R1", name="delay", probability=0.4, impact=5000,
                          category=RiskCategory.SCHEDULE))
        reg.add_risk(Risk(id="R2", name="cost overrun", probability=0.6, impact=8000,
                          category=RiskCategory.COST))
        return reg

    def test_json_roundtrip(self, tmp_path):
        reg = self._sample_register()
        fp = str(tmp_path / "risk.json")
        save_register(reg, fp)
        loaded = load_register(fp)
        assert len(loaded.risks) == 2
        assert loaded.bac == 50000
        assert loaded.risks[0].id == "R1"
        assert loaded.risks[0].exposure == pytest.approx(2000.0)

    def test_json_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_register(str(tmp_path / "nope.json"))

    def test_csv_roundtrip(self, tmp_path):
        reg = self._sample_register()
        fp = str(tmp_path / "risk.csv")
        export_to_csv(reg, fp)
        # Verify CSV structure
        with open(fp, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["id"] == "R1"
        # Import back
        imported = import_from_csv(fp)
        assert len(imported.risks) == 2
        assert imported.risks[0].name == "delay"
        assert imported.risks[0].exposure == pytest.approx(2000.0)

    def test_csv_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            import_from_csv(str(tmp_path / "nope.csv"))

    def test_json_preserves_all_fields(self, tmp_path):
        reg = self._sample_register()
        fp = str(tmp_path / "risk.json")
        save_register(reg, fp)
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "bac" in data
        assert "risks" in data
        assert len(data["risks"]) == 2
        assert data["risks"][0]["category"] == "Schedule"

    def test_csv_invalid_rows_skipped(self, tmp_path):
        """Rows with invalid data are skipped during CSV import."""
        fp = str(tmp_path / "bad.csv")
        with open(fp, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "description", "probability",
                             "impact", "category", "exposure"])
            writer.writerow(["R1", "ok", "", "0.5", "1000", "Cost", "500"])
            writer.writerow(["R2", "bad prob", "", "not_a_number", "1000", "Cost", "0"])
        imported = import_from_csv(fp)
        assert len(imported.risks) == 1
        assert imported.risks[0].id == "R1"
