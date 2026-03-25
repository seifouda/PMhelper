"""
Phase 5 Tests — Project I/O, Chart Export, Dashboard, Demo Data.
Tests for project_io_edu, chart_export_edu, dashboard_tab_edu, and demo datasets.
"""

import json
import os
import tempfile
import pytest
from pathlib import Path

# ================================================================
# project_io_edu tests
# ================================================================
from pmhelper.utils.project_io_edu import (
    save_full_project, load_full_project, make_empty_project,
)
from pmhelper.core.evm_models_edu import EVMProject, EVMTask, EVMPeriod
from pmhelper.core.risk_register_edu import Risk, RiskCategory, RiskRegister


class FakeState:
    """Minimal state object for save/load testing."""
    def __init__(self):
        self.evm_project = None
        self.risk_register = None
        self.mc_results = None
        self.current_file_path = None
        self._mode = "UG"
        self._dirty = False

    def is_dirty(self):
        return self._dirty

    def mark_dirty(self):
        self._dirty = True

    def mark_clean(self):
        self._dirty = False


def _make_sample_project():
    """Create a sample project with tasks, periods, and risks."""
    tasks = [
        EVMTask(task_id="A", name="Task A", budget=1000, pct_complete=50,
                planned_start=0, planned_finish=2),
        EVMTask(task_id="B", name="Task B", budget=2000, pct_complete=25,
                planned_start=1, planned_finish=3, predecessors=["A"]),
    ]
    periods = [
        EVMPeriod(index=0, label="W1", pv_cumulative=500, ev_cumulative=500,
                  ac_cumulative=550),
        EVMPeriod(index=1, label="W2", pv_cumulative=1200, ev_cumulative=1000,
                  ac_cumulative=1300),
        EVMPeriod(index=2, label="W3", pv_cumulative=2000, ev_cumulative=1500,
                  ac_cumulative=1800),
    ]
    proj = EVMProject(project_name="Test Project", bac=3000,
                      bac_auto_compute=False, tasks=tasks, periods=periods)

    reg = RiskRegister(bac=3000)
    reg.add_risk(Risk(id="R1", name="Delay", probability=0.3, impact=500,
                      category=RiskCategory.SCHEDULE))
    reg.add_risk(Risk(id="R2", name="Cost Overrun", probability=0.5, impact=1000,
                      category=RiskCategory.COST))
    return proj, reg


class TestMakeEmptyProject:
    def test_returns_tuple(self):
        proj, reg = make_empty_project()
        assert isinstance(proj, EVMProject)
        assert isinstance(reg, RiskRegister)

    def test_empty_project_defaults(self):
        proj, reg = make_empty_project()
        assert proj.bac == 0.0
        assert proj.project_name == "New Project"
        assert len(proj.tasks) == 0
        assert len(proj.periods) == 0
        assert len(reg.risks) == 0

    def test_bac_auto_compute_off(self):
        proj, _ = make_empty_project()
        assert proj.bac_auto_compute is False


class TestSaveLoadRoundTrip:
    def test_save_and_load(self, tmp_path):
        proj, reg = _make_sample_project()
        state = FakeState()
        state.evm_project = proj
        state.risk_register = reg

        filepath = str(tmp_path / "test.pmproj")
        save_full_project(state, filepath)

        assert os.path.exists(filepath)

        data = load_full_project(filepath)
        assert data["version"] == 1
        loaded_proj = data["evm_project"]
        assert loaded_proj.project_name == "Test Project"
        assert loaded_proj.bac == 3000
        assert len(loaded_proj.tasks) == 2
        assert len(loaded_proj.periods) == 3

        loaded_reg = data["risk_register"]
        assert len(loaded_reg.risks) == 2

    def test_task_data_preserved(self, tmp_path):
        proj, reg = _make_sample_project()
        state = FakeState()
        state.evm_project = proj
        state.risk_register = reg

        filepath = str(tmp_path / "test2.pmproj")
        save_full_project(state, filepath)
        data = load_full_project(filepath)

        loaded_proj = data["evm_project"]
        assert loaded_proj.tasks[0].task_id == "A"
        assert loaded_proj.tasks[0].pct_complete == 50
        assert loaded_proj.tasks[1].predecessors == ["A"]

    def test_period_data_preserved(self, tmp_path):
        proj, reg = _make_sample_project()
        state = FakeState()
        state.evm_project = proj
        state.risk_register = reg

        filepath = str(tmp_path / "test3.pmproj")
        save_full_project(state, filepath)
        data = load_full_project(filepath)

        loaded_proj = data["evm_project"]
        assert loaded_proj.periods[0].label == "W1"
        assert loaded_proj.periods[2].ac_cumulative == 1800

    def test_risk_data_preserved(self, tmp_path):
        proj, reg = _make_sample_project()
        state = FakeState()
        state.evm_project = proj
        state.risk_register = reg

        filepath = str(tmp_path / "test4.pmproj")
        save_full_project(state, filepath)
        data = load_full_project(filepath)

        loaded_reg = data["risk_register"]
        assert loaded_reg.risks[0].name == "Delay"
        assert loaded_reg.risks[1].probability == 0.5
        assert loaded_reg.risks[1].category == RiskCategory.COST

    def test_app_config_saved(self, tmp_path):
        state = FakeState()
        state.evm_project, state.risk_register = _make_sample_project()
        state._mode = "PG"

        filepath = str(tmp_path / "test5.pmproj")
        save_full_project(state, filepath)
        data = load_full_project(filepath)

        assert data["app_config"]["mode"] == "PG"

    def test_empty_project_roundtrip(self, tmp_path):
        proj, reg = make_empty_project()
        state = FakeState()
        state.evm_project = proj
        state.risk_register = reg

        filepath = str(tmp_path / "empty.pmproj")
        save_full_project(state, filepath)
        data = load_full_project(filepath)

        assert data["evm_project"].project_name == "New Project"
        assert data["evm_project"].bac == 0.0
        assert len(data["risk_register"].risks) == 0


class TestLoadErrors:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_full_project("/nonexistent/path.pmproj")

    def test_corrupt_json(self, tmp_path):
        filepath = str(tmp_path / "corrupt.pmproj")
        Path(filepath).write_text("NOT VALID JSON {{{")
        with pytest.raises(ValueError, match="Cannot read"):
            load_full_project(filepath)

    def test_missing_optional_fields(self, tmp_path):
        """File with minimal data should load fine."""
        filepath = str(tmp_path / "minimal.pmproj")
        Path(filepath).write_text(json.dumps({
            "version": 1,
            "evm_project": {
                "project_name": "Minimal",
                "bac": 100,
                "tasks": [],
                "periods": [],
            }
        }))
        data = load_full_project(filepath)
        assert data["evm_project"].project_name == "Minimal"
        assert data["risk_register"] is None
        assert data["mc_results"] is None


# ================================================================
# chart_export_edu tests
# ================================================================
from pmhelper.utils.chart_export_edu import export_all_charts


class FakeTab:
    """Tab with a fake get_figures() returning a mock figure."""
    def __init__(self, name):
        self._name = name

    def get_figures(self):
        try:
            from matplotlib.figure import Figure
            fig = Figure(figsize=(4, 3))
            ax = fig.add_subplot(111)
            ax.plot([1, 2, 3], [1, 4, 9])
            ax.set_title(self._name)
            return [(self._name, fig)]
        except ImportError:
            return []


class FakeTabNoFigures:
    """Tab without get_figures()."""
    pass


class TestExportAllCharts:
    def test_export_creates_files(self, tmp_path):
        tabs = {"test_tab": FakeTab("chart")}
        saved = export_all_charts(tabs, str(tmp_path), fmt="png")
        # Matplotlib may not be available in CI
        if saved:
            assert len(saved) == 1
            assert os.path.exists(saved[0])
            assert saved[0].endswith(".png")

    def test_export_skips_tabs_without_get_figures(self, tmp_path):
        tabs = {"no_fig": FakeTabNoFigures()}
        saved = export_all_charts(tabs, str(tmp_path))
        assert len(saved) == 0

    def test_export_pdf_format(self, tmp_path):
        tabs = {"pdf_tab": FakeTab("pdf_chart")}
        saved = export_all_charts(tabs, str(tmp_path), fmt="pdf")
        if saved:
            assert saved[0].endswith(".pdf")

    def test_export_creates_output_dir(self, tmp_path):
        out_dir = str(tmp_path / "nested" / "output")
        tabs = {"tab": FakeTab("nested")}
        saved = export_all_charts(tabs, out_dir)
        assert os.path.isdir(out_dir)

    def test_empty_tabs_dict(self, tmp_path):
        saved = export_all_charts({}, str(tmp_path))
        assert saved == []


# ================================================================
# Demo dataset tests
# ================================================================

DEMO_DIR = os.path.join(os.path.dirname(__file__),
                        "..", "src", "pmhelper", "demos_edu")


class TestUGDemo:
    @pytest.fixture
    def ug_data(self):
        path = os.path.join(DEMO_DIR, "office_renovation_ug.pmproj")
        if not os.path.exists(path):
            pytest.skip("UG demo file not found")
        return load_full_project(path)

    def test_loads_successfully(self, ug_data):
        assert ug_data["version"] == 1

    def test_project_name(self, ug_data):
        assert "Office Renovation" in ug_data["evm_project"].project_name

    def test_has_8_tasks(self, ug_data):
        assert len(ug_data["evm_project"].tasks) == 8

    def test_bac_is_120k(self, ug_data):
        assert ug_data["evm_project"].bac == 120000.0

    def test_has_periods(self, ug_data):
        assert len(ug_data["evm_project"].periods) >= 5

    def test_has_risks(self, ug_data):
        assert len(ug_data["risk_register"].risks) >= 3

    def test_cpi_around_087(self, ug_data):
        """CPI should be approximately 0.87 (below 1 = over budget)."""
        proj = ug_data["evm_project"]
        ev = proj.current_ev()
        ac = proj.current_ac()
        if ac > 0:
            cpi = ev / ac
            assert 0.80 <= cpi <= 0.95, f"CPI={cpi:.3f} outside expected range"

    def test_spi_around_092(self, ug_data):
        """SPI should be approximately 0.92 (behind schedule)."""
        proj = ug_data["evm_project"]
        ev = proj.current_ev()
        pv = proj.current_pv()
        if pv > 0:
            spi = ev / pv
            assert 0.75 <= spi <= 0.95, f"SPI={spi:.3f} outside expected range"

    def test_has_flagged_risks(self, ug_data):
        """Should have at least 2 high-exposure risks."""
        reg = ug_data["risk_register"]
        flagged = reg.flag_high_exposure()
        assert len(flagged) >= 2

    def test_mode_is_ug(self, ug_data):
        assert ug_data["app_config"]["mode"] == "UG"


class TestPGDemo:
    @pytest.fixture
    def pg_data(self):
        path = os.path.join(DEMO_DIR, "software_development_pg.pmproj")
        if not os.path.exists(path):
            pytest.skip("PG demo file not found")
        return load_full_project(path)

    def test_loads_successfully(self, pg_data):
        assert pg_data["version"] == 1

    def test_project_name(self, pg_data):
        assert "Software Development" in pg_data["evm_project"].project_name

    def test_has_12_tasks(self, pg_data):
        assert len(pg_data["evm_project"].tasks) == 12

    def test_bac_is_500k(self, pg_data):
        assert pg_data["evm_project"].bac == 500000.0

    def test_has_periods(self, pg_data):
        assert len(pg_data["evm_project"].periods) >= 8

    def test_has_8_risks(self, pg_data):
        assert len(pg_data["risk_register"].risks) == 8

    def test_cpi_above_1(self, pg_data):
        """CPI > 1.0 means under budget."""
        proj = pg_data["evm_project"]
        ev = proj.current_ev()
        ac = proj.current_ac()
        if ac > 0:
            cpi = ev / ac
            assert cpi > 1.0, f"CPI={cpi:.3f} should be > 1.0"

    def test_mode_is_pg(self, pg_data):
        assert pg_data["app_config"]["mode"] == "PG"

    def test_tasks_have_predecessors(self, pg_data):
        """PG demo tasks should have predecessor links."""
        proj = pg_data["evm_project"]
        tasks_with_preds = [t for t in proj.tasks if t.predecessors]
        assert len(tasks_with_preds) >= 6

    def test_all_tasks_have_baseline(self, pg_data):
        """PG demo should have baselines set."""
        proj = pg_data["evm_project"]
        for t in proj.tasks:
            assert t.baseline_start is not None
            assert t.baseline_finish is not None


# ================================================================
# Dashboard tab smoke tests (without GUI)
# ================================================================

class TestDashboardImport:
    """Test that dashboard_tab_edu can be imported and has expected attributes."""

    def test_import(self):
        from pmhelper.gui.tabs.dashboard_tab_edu import DashboardTabEdu
        assert hasattr(DashboardTabEdu, "set_mode")
        assert hasattr(DashboardTabEdu, "on_tab_selected")
        assert hasattr(DashboardTabEdu, "get_figures")


# ================================================================
# Main window integration tests (import only, no GUI)
# ================================================================

class TestMainWindowImport:
    def test_import_main_window(self):
        from pmhelper.gui.main_window_edu import MainWindowEdu
        assert hasattr(MainWindowEdu, "_apply_mode")
        assert hasattr(MainWindowEdu, "_save_project")
        assert hasattr(MainWindowEdu, "_open_project")
        assert hasattr(MainWindowEdu, "_new_project")
        assert hasattr(MainWindowEdu, "_load_demo")
        assert hasattr(MainWindowEdu, "_export_all_charts")

    def test_pg_only_tabs_defined(self):
        from pmhelper.gui.main_window_edu import _PG_ONLY_TABS
        assert "probability" in _PG_ONLY_TABS
        assert "rcps" in _PG_ONLY_TABS
