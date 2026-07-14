"""
Tests for RACI Matrix data model (Phase 4, V2).

Coverage:
- Cell get/set / invalid value
- Row / col accessors
- Validation rules (E1: accountable, E2: responsible, W1: empty col)
- is_valid property
- count_by_type / summary_text
- to_dict / from_dict round-trip
- empty() convenience constructor
- Edge cases: empty matrix, single-cell, full matrix
"""

import pytest
from pmhelper.core.raci_model import (
    RACIMatrix,
    CELL_COLORS,
    ROLE_DESCRIPTIONS,
    VALID_VALUES,
)


# ════════════════════════════════════════════════════════════════════
#  Fixtures
# ════════════════════════════════════════════════════════════════════

@pytest.fixture
def simple_matrix():
    """2×2 matrix with one valid row and one incomplete row."""
    m = RACIMatrix(rows=["Design", "Build"], cols=["PM", "Dev"])
    m.set_cell(0, 0, "A")
    m.set_cell(0, 1, "R")
    # Row 1 left empty intentionally for partial-validity tests
    return m


@pytest.fixture
def valid_matrix():
    """3×3 matrix that satisfies all PM rules."""
    m = RACIMatrix(
        rows=["Planning", "Execution", "Closure"],
        cols=["PM", "Team Lead", "Sponsor"],
    )
    # Planning: PM=A, Team Lead=R, Sponsor=C
    m.set_cell(0, 0, "A")
    m.set_cell(0, 1, "R")
    m.set_cell(0, 2, "C")
    # Execution: PM=C, Team Lead=A, Sponsor=I  → Team Lead has R too? No, add R
    m.set_cell(1, 0, "C")
    m.set_cell(1, 1, "A")
    m.set_cell(1, 2, "I")
    m.set_cell(1, 0, "R")  # overwrite PM with R, Team Lead still A
    # Closure: PM=A, Team Lead=R, Sponsor=I
    m.set_cell(2, 0, "A")
    m.set_cell(2, 1, "R")
    m.set_cell(2, 2, "I")
    return m


# ════════════════════════════════════════════════════════════════════
#  Cell get / set
# ════════════════════════════════════════════════════════════════════

class TestCellAccess:
    def test_default_value_is_empty_string(self):
        m = RACIMatrix(rows=["A"], cols=["X"])
        assert m.get_cell(0, 0) == ""

    def test_set_and_get_R(self):
        m = RACIMatrix(rows=["A"], cols=["X"])
        m.set_cell(0, 0, "R")
        assert m.get_cell(0, 0) == "R"

    def test_set_all_valid_values(self):
        m = RACIMatrix(rows=["A", "B", "C", "D"], cols=["X"])
        for i, v in enumerate(("R", "A", "C", "I")):
            m.set_cell(i, 0, v)
            assert m.get_cell(i, 0) == v

    def test_set_empty_string_clears_cell(self):
        m = RACIMatrix(rows=["A"], cols=["X"])
        m.set_cell(0, 0, "R")
        m.set_cell(0, 0, "")
        assert m.get_cell(0, 0) == ""
        assert "0,0" not in m.cells  # should be removed from dict

    def test_invalid_value_raises_value_error(self):
        m = RACIMatrix(rows=["A"], cols=["X"])
        with pytest.raises(ValueError, match="Invalid RACI value"):
            m.set_cell(0, 0, "Z")

    def test_lowercase_invalid(self):
        m = RACIMatrix(rows=["A"], cols=["X"])
        with pytest.raises(ValueError):
            m.set_cell(0, 0, "r")

    def test_out_of_bounds_get_returns_empty(self):
        m = RACIMatrix(rows=["A"], cols=["X"])
        # The model doesn't enforce bounds on get — returns "" for missing key
        assert m.get_cell(99, 99) == ""


# ════════════════════════════════════════════════════════════════════
#  Row / Col accessors
# ════════════════════════════════════════════════════════════════════

class TestRowColAccessors:
    def test_get_row_returns_correct_values(self):
        m = RACIMatrix(rows=["Task"], cols=["PM", "Dev", "QA"])
        m.set_cell(0, 0, "A")
        m.set_cell(0, 1, "R")
        m.set_cell(0, 2, "I")
        assert m.get_row(0) == ["A", "R", "I"]

    def test_get_row_unset_cells_are_empty(self):
        m = RACIMatrix(rows=["Task"], cols=["PM", "Dev"])
        m.set_cell(0, 0, "A")
        row = m.get_row(0)
        assert row == ["A", ""]

    def test_get_col_returns_correct_values(self):
        m = RACIMatrix(rows=["T1", "T2", "T3"], cols=["PM"])
        m.set_cell(0, 0, "A")
        m.set_cell(1, 0, "R")
        m.set_cell(2, 0, "C")
        assert m.get_col(0) == ["A", "R", "C"]

    def test_empty_matrix_get_row(self):
        m = RACIMatrix(rows=["Task"], cols=[])
        assert m.get_row(0) == []


# ════════════════════════════════════════════════════════════════════
#  Validation
# ════════════════════════════════════════════════════════════════════

class TestValidation:
    def test_valid_matrix_has_no_issues(self, valid_matrix):
        issues = valid_matrix.validate()
        errors = [i for i in issues if i.level == "error"]
        assert errors == [], f"Unexpected errors: {errors}"

    def test_no_accountable_is_error(self):
        m = RACIMatrix(rows=["Design"], cols=["PM"])
        m.set_cell(0, 0, "R")  # R but no A
        issues = m.validate()
        errors = [i for i in issues if i.level == "error"]
        assert any("Accountable" in i.message for i in errors)

    def test_multiple_accountable_is_error(self):
        m = RACIMatrix(rows=["Design"], cols=["PM", "Dev"])
        m.set_cell(0, 0, "A")
        m.set_cell(0, 1, "A")  # two A's
        issues = m.validate()
        errors = [i for i in issues if i.level == "error"]
        assert any(
            "2" in i.message or "Accountable" in i.message for i in errors)

    def test_no_responsible_is_error(self):
        m = RACIMatrix(rows=["Design"], cols=["PM", "Dev"])
        m.set_cell(0, 0, "A")
        m.set_cell(0, 1, "C")  # A and C, no R
        issues = m.validate()
        errors = [i for i in issues if i.level == "error"]
        assert any("Responsible" in i.message for i in errors)

    def test_empty_column_is_warning(self):
        m = RACIMatrix(rows=["Task1", "Task2"], cols=["PM", "Ghost"])
        m.set_cell(0, 0, "A")
        m.set_cell(0, 1, "")
        m.set_cell(1, 0, "R")
        m.set_cell(1, 1, "")
        issues = m.validate()
        warnings = [i for i in issues if i.level == "warning"]
        assert any("Ghost" in i.message for i in warnings)

    def test_valid_activity_no_issues_for_that_row(self):
        m = RACIMatrix(rows=["Task"], cols=["PM", "Dev"])
        m.set_cell(0, 0, "A")
        m.set_cell(0, 1, "R")
        issues = m.validate()
        row_errors = [i for i in issues if i.level == "error" and i.row == 0]
        assert row_errors == []

    def test_empty_matrix_no_issues(self):
        m = RACIMatrix(rows=[], cols=[])
        assert m.validate() == []

    def test_multiple_rows_each_validated(self):
        m = RACIMatrix(rows=["T1", "T2"], cols=["PM"])
        # T1: valid (A+R combined in one person)
        m.set_cell(0, 0, "A")  # No R — should warn
        m.set_cell(1, 0, "R")  # No A — should warn
        issues = m.validate()
        errors = [i for i in issues if i.level == "error"]
        # Expect 2 errors: T1 no R, T2 no A
        assert len(errors) == 2

    def test_validation_issue_has_row_index(self):
        m = RACIMatrix(rows=["Step1", "Step2"], cols=["PM"])
        m.set_cell(1, 0, "R")  # Step2: no A
        issues = m.validate()
        # Issues for row 1 (Step2) should have row=1
        step2_issues = [i for i in issues if i.row == 1]
        assert step2_issues


# ════════════════════════════════════════════════════════════════════
#  is_valid property
# ════════════════════════════════════════════════════════════════════

class TestIsValid:
    def test_valid_matrix_is_valid(self, valid_matrix):
        assert valid_matrix.is_valid is True

    def test_error_matrix_not_valid(self):
        m = RACIMatrix(rows=["T"], cols=["P"])
        m.set_cell(0, 0, "R")  # no A
        assert m.is_valid is False

    def test_warning_only_still_valid(self):
        m = RACIMatrix(rows=["T"], cols=["PM", "Ghost"])
        m.set_cell(0, 0, "A")
        m.set_cell(0, 1, "R")
        # Ghost col empty → warning, but no errors
        assert m.is_valid is True

    def test_empty_matrix_is_valid(self):
        assert RACIMatrix().is_valid is True


# ════════════════════════════════════════════════════════════════════
#  Statistics
# ════════════════════════════════════════════════════════════════════

class TestStatistics:
    def test_count_by_type_correct(self):
        m = RACIMatrix(rows=["T1", "T2"], cols=["PM", "Dev"])
        m.set_cell(0, 0, "R")
        m.set_cell(0, 1, "A")
        m.set_cell(1, 0, "C")
        m.set_cell(1, 1, "I")
        counts = m.count_by_type()
        assert counts["R"] == 1
        assert counts["A"] == 1
        assert counts["C"] == 1
        assert counts["I"] == 1

    def test_count_includes_empty(self):
        m = RACIMatrix(rows=["T"], cols=["PM", "Dev"])
        m.set_cell(0, 0, "R")
        counts = m.count_by_type()
        assert counts[""] == 1  # Dev cell is empty

    def test_summary_text_all_types(self):
        m = RACIMatrix(rows=["T1", "T2"], cols=["P", "D"])
        m.set_cell(0, 0, "R")
        m.set_cell(0, 1, "A")
        m.set_cell(1, 0, "C")
        m.set_cell(1, 1, "I")
        s = m.summary_text()
        assert "R=1" in s and "A=1" in s and "C=1" in s and "I=1" in s

    def test_summary_text_empty_matrix(self):
        assert RACIMatrix().summary_text() == "No assignments"

    def test_count_by_type_empty_matrix(self):
        counts = RACIMatrix().count_by_type()
        assert counts["R"] == 0
        assert counts["A"] == 0


# ════════════════════════════════════════════════════════════════════
#  Persistence (to_dict / from_dict)
# ════════════════════════════════════════════════════════════════════

class TestPersistence:
    def test_round_trip_preserves_rows_cols(self):
        m = RACIMatrix(rows=["X", "Y"], cols=["A", "B"])
        restored = RACIMatrix.from_dict(m.to_dict())
        assert restored.rows == ["X", "Y"]
        assert restored.cols == ["A", "B"]

    def test_round_trip_preserves_cells(self):
        m = RACIMatrix(rows=["T"], cols=["PM", "Dev"])
        m.set_cell(0, 0, "A")
        m.set_cell(0, 1, "R")
        restored = RACIMatrix.from_dict(m.to_dict())
        assert restored.get_cell(0, 0) == "A"
        assert restored.get_cell(0, 1) == "R"

    def test_to_dict_is_json_serialisable(self):
        import json
        m = RACIMatrix(rows=["T"], cols=["P"])
        m.set_cell(0, 0, "R")
        json_str = json.dumps(m.to_dict())
        assert "0,0" in json_str

    def test_from_dict_missing_keys(self):
        """from_dict should handle empty/missing keys gracefully."""
        m = RACIMatrix.from_dict({})
        assert m.rows == []
        assert m.cols == []
        assert m.cells == {}

    def test_round_trip_empty_cells(self):
        m = RACIMatrix(rows=["T"], cols=["P"])
        # No cells set — empty string should not persist
        d = m.to_dict()
        assert d["cells"] == {}
        restored = RACIMatrix.from_dict(d)
        assert restored.get_cell(0, 0) == ""

    def test_demo_file_loads_correctly(self):
        import json
        import os
        demo_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "data",
            "demos",
            "v2",
            "raci_demo.json")
        demo_path = os.path.normpath(demo_path)
        with open(demo_path, encoding="utf-8") as fh:
            demo = json.load(fh)
        task_data = demo["data"]["task_role"]
        m = RACIMatrix.from_dict(task_data)
        assert len(m.rows) == 10
        assert len(m.cols) == 5
        # Demo should be valid
        assert m.is_valid, m.validate()


# ════════════════════════════════════════════════════════════════════
#  Convenience constructors
# ════════════════════════════════════════════════════════════════════

class TestConvenienceConstructors:
    def test_empty_no_args(self):
        m = RACIMatrix.empty()
        assert m.rows == []
        assert m.cols == []
        assert m.cells == {}

    def test_empty_with_labels(self):
        m = RACIMatrix.empty(["T1", "T2"], ["PM", "Dev"])
        assert m.rows == ["T1", "T2"]
        assert m.cols == ["PM", "Dev"]
        assert m.get_cell(0, 0) == ""


# ════════════════════════════════════════════════════════════════════
#  Constants
# ════════════════════════════════════════════════════════════════════

class TestConstants:
    def test_valid_values_contains_RACI_and_empty(self):
        assert {"R", "A", "C", "I", ""}.issubset(VALID_VALUES)

    def test_cell_colors_all_types_present(self):
        for k in ("R", "A", "C", "I", ""):
            assert k in CELL_COLORS

    def test_role_descriptions_all_types_present(self):
        for k in ("R", "A", "C", "I"):
            assert k in ROLE_DESCRIPTIONS


# ════════════════════════════════════════════════════════════════════
#  Edge cases
# ════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_single_cell_matrix_valid(self):
        m = RACIMatrix(rows=["Only Task"], cols=["Only Person"])
        # One person can be both R and A? That's a conflict.
        # Set A — no R → error
        m.set_cell(0, 0, "A")
        issues = m.validate()
        errors = [i for i in issues if i.level == "error"]
        # A without R is not valid
        assert any("Responsible" in i.message for i in errors)

    def test_overwrite_cell_value(self):
        m = RACIMatrix(rows=["T"], cols=["P"])
        m.set_cell(0, 0, "R")
        m.set_cell(0, 0, "A")
        assert m.get_cell(0, 0) == "A"

    def test_large_matrix_no_crash(self):
        rows = [f"Activity {i}" for i in range(20)]
        cols = [f"Role {j}" for j in range(10)]
        m = RACIMatrix(rows=rows, cols=cols)
        for r in range(20):
            m.set_cell(r, 0, "A")
            m.set_cell(r, 1, "R")
        errors = [i for i in m.validate() if i.level == "error"]
        assert len(errors) == 0  # cols 2–9 give warnings; no errors expected

    def test_whitespace_cell_value_invalid(self):
        m = RACIMatrix(rows=["T"], cols=["P"])
        with pytest.raises(ValueError):
            m.set_cell(0, 0, " R")

    def test_set_cell_none_raises(self):
        m = RACIMatrix(rows=["T"], cols=["P"])
        with pytest.raises((ValueError, TypeError)):
            m.set_cell(0, 0, None)  # type: ignore
