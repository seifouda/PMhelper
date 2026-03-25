"""Tests for EVM I/O — Phase 1."""

import os
import tempfile
import pytest
from pmhelper.core.evm_models_edu import EVMTask, EVMPeriod, EVMProject, PVSpread
from pmhelper.utils.evm_io_edu import (
    save_evm_project, load_evm_project,
    export_periods_to_csv, import_periods_from_csv,
    export_tasks_to_csv, import_tasks_from_csv,
)


@pytest.fixture
def sample_project():
    tasks = [
        EVMTask(task_id="A", name="Design", budget=5000, pct_complete=100,
                planned_start=0, planned_finish=2),
        EVMTask(task_id="B", name="Build", budget=10000, pct_complete=50,
                planned_start=1, planned_finish=4, pv_spread=PVSpread.FRONT),
    ]
    periods = [
        EVMPeriod(index=0, label="Jan", pv_cumulative=2000,
                  ev_cumulative=2000, ac_cumulative=2100),
        EVMPeriod(index=1, label="Feb", pv_cumulative=5000,
                  ev_cumulative=4500, ac_cumulative=4800),
        EVMPeriod(index=2, label="Mar", pv_cumulative=8000,
                  ev_cumulative=7000, ac_cumulative=7500),
    ]
    return EVMProject(
        project_name="IO Test", tasks=tasks, periods=periods,
        currency_symbol="€",
    )


class TestProjectIO:
    def test_save_load_roundtrip(self, sample_project, tmp_path):
        fp = str(tmp_path / "test.pmproj")
        save_evm_project(sample_project, fp)
        loaded = load_evm_project(fp)
        assert loaded.project_name == "IO Test"
        assert loaded.currency_symbol == "€"
        assert loaded.bac == pytest.approx(15000.0)
        assert len(loaded.tasks) == 2
        assert len(loaded.periods) == 3
        assert loaded.tasks[1].pv_spread == PVSpread.FRONT

    def test_load_nonexistent_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_evm_project(str(tmp_path / "nope.pmproj"))

    def test_save_creates_file(self, sample_project, tmp_path):
        fp = str(tmp_path / "new.pmproj")
        assert not os.path.exists(fp)
        save_evm_project(sample_project, fp)
        assert os.path.exists(fp)

    def test_schema_version_preserved(self, tmp_path):
        proj = EVMProject(schema_version=2)
        fp = str(tmp_path / "v2.pmproj")
        save_evm_project(proj, fp)
        loaded = load_evm_project(fp)
        assert loaded.schema_version == 2


class TestPeriodsCSV:
    def test_export_import_roundtrip(self, sample_project, tmp_path):
        fp = str(tmp_path / "periods.csv")
        export_periods_to_csv(sample_project, fp)
        periods = import_periods_from_csv(fp)
        assert len(periods) == 3
        assert periods[0].label == "Jan"
        assert periods[1].pv_cumulative == pytest.approx(5000.0)
        assert periods[2].ac_cumulative == pytest.approx(7500.0)

    def test_import_nonexistent_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            import_periods_from_csv(str(tmp_path / "nope.csv"))

    def test_import_skips_bad_rows(self, tmp_path):
        fp = str(tmp_path / "bad.csv")
        with open(fp, "w", newline="") as f:
            f.write("index,label,pv_cumulative,ev_cumulative,ac_cumulative,ev_source\n")
            f.write("0,Good,100,90,95,manual\n")
            f.write("not_a_number,Bad,x,y,z,manual\n")
            f.write("1,OK,200,180,190,computed\n")
        periods = import_periods_from_csv(fp)
        assert len(periods) == 2
        assert periods[0].label == "Good"
        assert periods[1].label == "OK"


class TestTasksCSV:
    def test_export_import_roundtrip(self, sample_project, tmp_path):
        fp = str(tmp_path / "tasks.csv")
        export_tasks_to_csv(sample_project, fp)
        tasks = import_tasks_from_csv(fp)
        assert len(tasks) == 2
        assert tasks[0].task_id == "A"
        assert tasks[0].budget == pytest.approx(5000.0)
        assert tasks[1].pv_spread == PVSpread.FRONT

    def test_import_nonexistent_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            import_tasks_from_csv(str(tmp_path / "nope.csv"))

    def test_import_skips_invalid_tasks(self, tmp_path):
        fp = str(tmp_path / "bad_tasks.csv")
        with open(fp, "w", newline="") as f:
            f.write("task_id,name,budget,pct_complete,planned_start,planned_finish,pv_spread\n")
            f.write("A,Good,1000,50,0,2,uniform\n")
            f.write("B,Bad,-100,0,0,0,uniform\n")  # negative budget → validation error
            f.write("C,OK,500,25,1,3,back\n")
        tasks = import_tasks_from_csv(fp)
        assert len(tasks) == 2
        assert tasks[0].task_id == "A"
        assert tasks[1].task_id == "C"
