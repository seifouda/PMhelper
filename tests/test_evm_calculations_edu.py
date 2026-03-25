"""Tests for EVM calculations — Phase 2."""

import pytest
from pmhelper.core.evm_models_edu import EVMTask, EVMPeriod, EVMProject
from pmhelper.core.evm_calculations_edu import (
    compute_ev, compute_cv, compute_sv, compute_cpi, compute_spi,
    compute_pc, compute_ps, compute_cr,
    compute_eac1, compute_eac2, compute_eac3,
    compute_vac, compute_tcpi_bac,
    compute_all_kpis, get_kpi_walkthrough,
)


# ── Known-value test fixture ──────────────────────────────────────
# Project: BAC=$100k, 5 periods, current (last period):
#   PV=$60k, EV=$50k, AC=$55k
# Expected KPIs (manual calculation):
#   CV = 50000 - 55000 = -5000
#   SV = 50000 - 60000 = -10000
#   CPI = 50000 / 55000 ≈ 0.9091
#   SPI = 50000 / 60000 ≈ 0.8333
#   PC = 50000 / 100000 * 100 = 50.0
#   PS = 55000 / 100000 * 100 = 55.0
#   CR = 0.9091 * 0.8333 ≈ 0.7576
#   EAC1 = 55000 + (100000 - 50000) = 105000
#   EAC2 = 100000 / 0.9091 ≈ 110000
#   EAC3 = 55000 + (100000 - 50000) / (0.9091 * 0.8333) ≈ 120999.94
#   TCPI = (100000 - 50000) / (100000 - 55000) ≈ 1.1111


@pytest.fixture
def sample_project():
    tasks = [
        EVMTask(task_id="A", name="A", budget=60000, pct_complete=50,
                planned_start=0, planned_finish=4),
        EVMTask(task_id="B", name="B", budget=40000, pct_complete=50,
                planned_start=0, planned_finish=4),
    ]
    periods = [
        EVMPeriod(index=0, pv_cumulative=20000, ev_cumulative=15000, ac_cumulative=16000),
        EVMPeriod(index=1, pv_cumulative=35000, ev_cumulative=28000, ac_cumulative=30000),
        EVMPeriod(index=2, pv_cumulative=60000, ev_cumulative=50000, ac_cumulative=55000),
    ]
    return EVMProject(project_name="Test", tasks=tasks, periods=periods)


class TestCoreFormulas:
    # ── EV ──
    def test_compute_ev(self):
        tasks = [
            EVMTask(task_id="A", name="A", budget=1000, pct_complete=50,
                    planned_start=0, planned_finish=0),
            EVMTask(task_id="B", name="B", budget=500, pct_complete=100,
                    planned_start=0, planned_finish=0),
        ]
        assert compute_ev(tasks) == pytest.approx(1000.0)

    def test_compute_ev_empty(self):
        assert compute_ev([]) == 0.0

    # ── CV / SV ──
    def test_compute_cv(self):
        assert compute_cv(50000, 55000) == pytest.approx(-5000)

    def test_compute_sv(self):
        assert compute_sv(50000, 60000) == pytest.approx(-10000)

    def test_cv_positive(self):
        assert compute_cv(100, 80) == pytest.approx(20)

    def test_sv_positive(self):
        assert compute_sv(100, 80) == pytest.approx(20)

    # ── CPI / SPI ──
    def test_compute_cpi(self):
        assert compute_cpi(50000, 55000) == pytest.approx(0.9091, rel=1e-3)

    def test_compute_spi(self):
        assert compute_spi(50000, 60000) == pytest.approx(0.8333, rel=1e-3)

    def test_cpi_zero_ac_raises(self):
        with pytest.raises(ValueError, match="AC is zero"):
            compute_cpi(50000, 0)

    def test_spi_zero_pv_raises(self):
        with pytest.raises(ValueError, match="PV is zero"):
            compute_spi(50000, 0)

    # ── PC / PS ──
    def test_compute_pc(self):
        assert compute_pc(50000, 100000) == pytest.approx(50.0)

    def test_compute_ps(self):
        assert compute_ps(55000, 100000) == pytest.approx(55.0)

    def test_pc_zero_bac_raises(self):
        with pytest.raises(ValueError, match="BAC is zero"):
            compute_pc(50000, 0)

    def test_ps_zero_bac_raises(self):
        with pytest.raises(ValueError, match="BAC is zero"):
            compute_ps(55000, 0)

    # ── CR ──
    def test_compute_cr(self):
        cpi = 50000 / 55000
        spi = 50000 / 60000
        assert compute_cr(cpi, spi) == pytest.approx(cpi * spi)

    # ── EAC variants ──
    def test_compute_eac1(self):
        assert compute_eac1(55000, 100000, 50000) == pytest.approx(105000)

    def test_compute_eac2(self):
        cpi = 50000 / 55000
        assert compute_eac2(100000, cpi) == pytest.approx(110000, rel=1e-2)

    def test_compute_eac2_zero_cpi_raises(self):
        with pytest.raises(ValueError, match="CPI is zero"):
            compute_eac2(100000, 0)

    def test_compute_eac3(self):
        cpi = 50000 / 55000
        spi = 50000 / 60000
        expected = 55000 + (100000 - 50000) / (cpi * spi)
        assert compute_eac3(55000, 100000, 50000, cpi, spi) == pytest.approx(expected)

    def test_compute_eac3_zero_cr_raises(self):
        with pytest.raises(ValueError, match="CPI × SPI is zero"):
            compute_eac3(55000, 100000, 50000, 0, 0.8)

    # ── VAC ──
    def test_compute_vac(self):
        assert compute_vac(100000, 105000) == pytest.approx(-5000)

    def test_compute_vac_positive(self):
        assert compute_vac(100000, 90000) == pytest.approx(10000)

    # ── TCPI ──
    def test_compute_tcpi_bac(self):
        assert compute_tcpi_bac(100000, 50000, 55000) == pytest.approx(1.1111, rel=1e-3)

    def test_tcpi_bac_equals_ac_raises(self):
        with pytest.raises(ValueError, match="BAC equals AC"):
            compute_tcpi_bac(100000, 50000, 100000)


class TestComputeAllKPIs:
    def test_all_kpis_returned(self, sample_project):
        kpis = compute_all_kpis(sample_project)
        expected_keys = {"ev", "pv", "ac", "bac", "cv", "sv",
                         "cpi", "spi", "pc", "ps", "cr",
                         "eac1", "eac2", "eac3", "vac",
                         "tcpi_bac", "primary_eac_value", "errors"}
        assert expected_keys.issubset(set(kpis.keys()))

    def test_known_values(self, sample_project):
        kpis = compute_all_kpis(sample_project)
        assert kpis["ev"] == pytest.approx(50000)
        assert kpis["pv"] == pytest.approx(60000)
        assert kpis["ac"] == pytest.approx(55000)
        assert kpis["bac"] == pytest.approx(100000)
        assert kpis["cv"] == pytest.approx(-5000)
        assert kpis["sv"] == pytest.approx(-10000)
        assert kpis["cpi"] == pytest.approx(0.9091, rel=1e-3)
        assert kpis["spi"] == pytest.approx(0.8333, rel=1e-3)
        assert kpis["eac1"] == pytest.approx(105000)

    def test_primary_eac_selection(self, sample_project):
        k1 = compute_all_kpis(sample_project, primary_eac=1)
        k2 = compute_all_kpis(sample_project, primary_eac=2)
        assert k1["primary_eac_value"] == pytest.approx(k1["eac1"])
        assert k2["primary_eac_value"] == pytest.approx(k2["eac2"])

    def test_zero_ac_produces_none_cpi(self):
        proj = EVMProject(
            bac=1000, bac_auto_compute=False,
            periods=[EVMPeriod(index=0, pv_cumulative=500,
                               ev_cumulative=400, ac_cumulative=0)],
        )
        kpis = compute_all_kpis(proj)
        assert kpis["cpi"] is None
        assert "cpi" in kpis["errors"]

    def test_zero_pv_produces_none_spi(self):
        proj = EVMProject(
            bac=1000, bac_auto_compute=False,
            periods=[EVMPeriod(index=0, pv_cumulative=0,
                               ev_cumulative=0, ac_cumulative=100)],
        )
        kpis = compute_all_kpis(proj)
        assert kpis["spi"] is None
        assert "spi" in kpis["errors"]

    def test_empty_project(self):
        proj = EVMProject()
        kpis = compute_all_kpis(proj)
        assert kpis["ev"] == 0
        assert kpis["bac"] == 0
        # BAC=0 means PC/PS/TCPI should be None
        assert kpis["pc"] is None
        assert kpis["ps"] is None


class TestKPIWalkthrough:
    def test_cv_walkthrough(self, sample_project):
        kpis = compute_all_kpis(sample_project)
        wt = get_kpi_walkthrough("cv", kpis, "$")
        assert "CV = EV − AC" in wt["formula"]
        assert wt["result"] is not None
        assert wt["interpretation"] != ""

    def test_none_kpi_walkthrough(self):
        kpis = {"cpi": None, "errors": {"cpi": "AC is zero — CPI undefined"},
                "ev": 0, "ac": 0, "pv": 0, "bac": 0}
        wt = get_kpi_walkthrough("cpi", kpis, "$")
        assert "N/A" in wt["result"]
        assert "AC is zero" in wt["interpretation"]

    def test_walkthrough_keys(self, sample_project):
        kpis = compute_all_kpis(sample_project)
        wt = get_kpi_walkthrough("spi", kpis)
        assert set(wt.keys()) == {"formula", "substitution", "result", "interpretation"}
