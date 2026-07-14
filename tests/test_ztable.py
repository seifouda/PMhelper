"""Tests for the Z-score table loader (Phase 10)."""
from __future__ import annotations

import os
import pytest
from pmhelper.core.ztable_loader import (
    ZTableData, ZLookupResult, load_ztable,
    lookup_forward, lookup_reverse,
)


# ── Fixture: load the real CSV once ────────────────────────────────

@pytest.fixture(scope="module")
def ztable() -> ZTableData:
    """Load the shipped ztable.csv."""
    # Walk up from this file to find the project root where ztable.csv lives
    here = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(here, "..", "ztable.csv")
    if not os.path.isfile(csv_path):
        csv_path = os.path.join(here, "..", "..", "ztable.csv")
    return load_ztable(csv_path)


# ════════════════════════════════════════════════════════════════════
#  CSV parsing
# ════════════════════════════════════════════════════════════════════

class TestCSVParsing:
    """Verify the CSV is loaded correctly."""

    def test_column_count(self, ztable: ZTableData):
        assert len(ztable.col_labels) == 10
        assert ztable.col_labels[0] == ".00"
        assert ztable.col_labels[-1] == ".09"

    def test_row_count(self, ztable: ZTableData):
        # -3.9 to +3.9 with -0.0 and 0.0 → 80 rows
        assert len(ztable.row_labels) >= 79

    def test_negative_rows_present(self, ztable: ZTableData):
        assert "-3.9" in ztable.negative_rows
        assert "-0.0" in ztable.negative_rows

    def test_positive_rows_present(self, ztable: ZTableData):
        assert "0.0" in ztable.positive_rows
        assert "3.9" in ztable.positive_rows

    def test_cells_populated(self, ztable: ZTableData):
        # Should have ~ 80 rows × 10 cols = 800 cells
        assert len(ztable.cells) >= 790

    def test_z_range(self, ztable: ZTableData):
        assert ztable.z_min == pytest.approx(-3.9, abs=0.01)
        assert ztable.z_max == pytest.approx(3.99, abs=0.01)


# ════════════════════════════════════════════════════════════════════
#  Forward lookup: Z → Probability
# ════════════════════════════════════════════════════════════════════

class TestForwardLookup:
    """Z → Probability tests against known textbook values."""

    def test_z_zero(self, ztable: ZTableData):
        result = lookup_forward(ztable, 0.00)
        assert result is not None
        assert result.probability == pytest.approx(0.5, abs=0.001)
        assert result.row_label == "0.0"
        assert result.col_label == ".00"
        assert result.is_exact is True

    def test_z_196(self, ztable: ZTableData):
        result = lookup_forward(ztable, 1.96)
        assert result is not None
        assert result.probability == pytest.approx(0.975, abs=0.001)
        assert result.row_label == "1.9"
        assert result.col_label == ".06"

    def test_z_123(self, ztable: ZTableData):
        result = lookup_forward(ztable, 1.23)
        assert result is not None
        assert result.row_label == "1.2"
        assert result.col_label == ".03"
        # P(Z ≤ 1.23) ≈ 0.8907
        assert result.probability == pytest.approx(0.8907, abs=0.002)

    def test_z_negative_123(self, ztable: ZTableData):
        result = lookup_forward(ztable, -1.23)
        assert result is not None
        assert result.row_label == "-1.2"
        assert result.col_label == ".03"
        # P(Z ≤ -1.23) ≈ 0.1093
        assert result.probability == pytest.approx(0.1093, abs=0.002)

    def test_z_negative_zero(self, ztable: ZTableData):
        result = lookup_forward(ztable, -0.05)
        assert result is not None
        assert result.row_label == "-0.0"
        assert result.col_label == ".05"

    def test_z_max_boundary(self, ztable: ZTableData):
        result = lookup_forward(ztable, 3.99)
        assert result is not None
        assert result.probability > 0.999

    def test_z_min_boundary(self, ztable: ZTableData):
        result = lookup_forward(ztable, -3.90)
        assert result is not None
        assert result.probability < 0.001

    def test_z_outside_range(self, ztable: ZTableData):
        result = lookup_forward(ztable, 5.0)
        assert result is None

    def test_z_below_range(self, ztable: ZTableData):
        result = lookup_forward(ztable, -5.0)
        assert result is None


# ════════════════════════════════════════════════════════════════════
#  Reverse lookup: Probability → Z (nearest)
# ════════════════════════════════════════════════════════════════════

class TestReverseLookup:
    """Probability → Z nearest-match tests."""

    def test_prob_0975(self, ztable: ZTableData):
        result = lookup_reverse(ztable, 0.975)
        assert result is not None
        assert result.z_value == pytest.approx(1.96, abs=0.01)
        assert result.row_label == "1.9"
        assert result.col_label == ".06"

    def test_prob_05(self, ztable: ZTableData):
        result = lookup_reverse(ztable, 0.5)
        assert result is not None
        assert result.z_value == pytest.approx(0.0, abs=0.01)

    def test_prob_08413(self, ztable: ZTableData):
        """P ≈ 0.8413 → Z ≈ 1.00"""
        result = lookup_reverse(ztable, 0.8413)
        assert result is not None
        assert result.z_value == pytest.approx(1.0, abs=0.02)

    def test_prob_exact_match_flag(self, ztable: ZTableData):
        """When probability matches a cell exactly, is_exact=True."""
        result = lookup_forward(ztable, 1.96)
        assert result is not None
        # Now reverse-lookup the exact probability
        rev = lookup_reverse(ztable, result.probability)
        assert rev is not None
        assert rev.is_exact is True

    def test_prob_near_match_flag(self, ztable: ZTableData):
        """Probabilities between cells get is_exact=False."""
        result = lookup_reverse(ztable, 0.9751)  # slightly above 0.9750
        assert result is not None
        # Should still land on Z ≈ 1.96
        assert result.z_value == pytest.approx(1.96, abs=0.02)

    def test_prob_out_of_range_zero(self, ztable: ZTableData):
        result = lookup_reverse(ztable, 0.0)
        assert result is None

    def test_prob_out_of_range_one(self, ztable: ZTableData):
        result = lookup_reverse(ztable, 1.0)
        assert result is None

    def test_prob_negative(self, ztable: ZTableData):
        result = lookup_reverse(ztable, -0.5)
        assert result is None


# ════════════════════════════════════════════════════════════════════
#  Edge cases
# ════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Boundary and error conditions."""

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_ztable("/nonexistent/path/ztable.csv")

    def test_z_rounded_to_2_decimals(self, ztable: ZTableData):
        """Z = 1.234567 should be treated as 1.23."""
        result = lookup_forward(ztable, 1.234567)
        assert result is not None
        assert result.z_value == 1.23
        assert result.row_label == "1.2"
        assert result.col_label == ".03"

    def test_reverse_index_sorted(self, ztable: ZTableData):
        """Internal reverse index must be sorted by probability."""
        for i in range(len(ztable._reverse_index) - 1):
            assert ztable._reverse_index[i][0] <= ztable._reverse_index[i + 1][0]
