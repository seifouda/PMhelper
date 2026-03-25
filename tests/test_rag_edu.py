"""Tests for RAG traffic-light engine — Phase 2."""

import pytest
from pmhelper.core.evm_calculations_edu import get_rag


class TestRAG:
    # ── CPI boundaries ──
    def test_cpi_green(self):
        assert get_rag("cpi", 1.0, bac=100000) == "green"

    def test_cpi_green_above(self):
        assert get_rag("cpi", 1.05, bac=100000) == "green"

    def test_cpi_amber_at_boundary(self):
        assert get_rag("cpi", 0.95, bac=100000) == "amber"

    def test_cpi_amber_between(self):
        assert get_rag("cpi", 0.97, bac=100000) == "amber"

    def test_cpi_red_below(self):
        assert get_rag("cpi", 0.949, bac=100000) == "red"

    def test_cpi_red_very_low(self):
        assert get_rag("cpi", 0.5, bac=100000) == "red"

    # ── SPI boundaries (same thresholds as CPI) ──
    def test_spi_green(self):
        assert get_rag("spi", 1.0, bac=100000) == "green"

    def test_spi_amber(self):
        assert get_rag("spi", 0.95, bac=100000) == "amber"

    def test_spi_red(self):
        assert get_rag("spi", 0.94, bac=100000) == "red"

    # ── CR boundaries ──
    def test_cr_green(self):
        assert get_rag("cr", 0.90, bac=100000) == "green"

    def test_cr_green_above(self):
        assert get_rag("cr", 1.0, bac=100000) == "green"

    def test_cr_amber(self):
        assert get_rag("cr", 0.80, bac=100000) == "amber"

    def test_cr_amber_between(self):
        assert get_rag("cr", 0.85, bac=100000) == "amber"

    def test_cr_red(self):
        assert get_rag("cr", 0.79, bac=100000) == "red"

    # ── TCPI boundaries ──
    def test_tcpi_green(self):
        assert get_rag("tcpi_bac", 1.0, bac=100000) == "green"

    def test_tcpi_green_at_boundary(self):
        assert get_rag("tcpi_bac", 1.10, bac=100000) == "green"

    def test_tcpi_amber(self):
        assert get_rag("tcpi_bac", 1.15, bac=100000) == "amber"

    def test_tcpi_amber_at_boundary(self):
        assert get_rag("tcpi_bac", 1.20, bac=100000) == "amber"

    def test_tcpi_red(self):
        assert get_rag("tcpi_bac", 1.21, bac=100000) == "red"

    # ── CV boundaries (variance based: green if >= 0) ──
    def test_cv_green(self):
        assert get_rag("cv", 0.0, bac=100000) == "green"

    def test_cv_green_positive(self):
        assert get_rag("cv", 5000, bac=100000) == "green"

    def test_cv_amber(self):
        # amber_pct = 0.05, threshold = 5000
        assert get_rag("cv", -1000, bac=100000) == "amber"

    def test_cv_amber_at_boundary(self):
        assert get_rag("cv", -5000, bac=100000) == "amber"

    def test_cv_red(self):
        assert get_rag("cv", -5001, bac=100000) == "red"

    # ── SV boundaries ──
    def test_sv_green(self):
        assert get_rag("sv", 0, bac=100000) == "green"

    def test_sv_red(self):
        assert get_rag("sv", -6000, bac=100000) == "red"

    # ── EAC boundaries ──
    def test_eac_green_at_bac(self):
        assert get_rag("eac1", 100000, bac=100000) == "green"

    def test_eac_green_under_bac(self):
        assert get_rag("eac2", 95000, bac=100000) == "green"

    def test_eac_amber(self):
        # amber_pct=0.10, limit = 110000
        assert get_rag("eac1", 105000, bac=100000) == "amber"

    def test_eac_amber_at_limit(self):
        assert get_rag("eac3", 110000, bac=100000) == "amber"

    def test_eac_red(self):
        assert get_rag("eac2", 110001, bac=100000) == "red"

    # ── VAC boundaries ──
    def test_vac_green(self):
        assert get_rag("vac", 0, bac=100000) == "green"

    def test_vac_amber(self):
        assert get_rag("vac", -5000, bac=100000) == "amber"

    def test_vac_red(self):
        assert get_rag("vac", -10001, bac=100000) == "red"

    # ── None value returns grey ──
    def test_none_returns_grey(self):
        assert get_rag("cpi", None, bac=100000) == "grey"

    def test_unknown_kpi_returns_grey(self):
        assert get_rag("unknown_metric", 42, bac=100000) == "grey"

    # ── Custom thresholds ──
    def test_custom_thresholds(self):
        custom = {"cpi": {"amber_lower": 0.90, "green_lower": 0.95}}
        # 0.92 would be red with defaults, but amber with custom
        assert get_rag("cpi", 0.92, bac=100000, thresholds=custom) == "amber"
        assert get_rag("cpi", 0.89, bac=100000, thresholds=custom) == "red"
