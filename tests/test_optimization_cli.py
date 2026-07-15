"""
Integration tests for optimization CLI commands.
Tests all four CLI commands: time-cost, resources, npv, pareto.

These drive `optimization_cli.main()` through `sys.argv`, the same way a user
invokes it. Every command exercised here has been verified to run end-to-end.

Note on the interface: each subcommand takes its project file via **--input**
(not positionally). `--indirect` and `--cash-flows` are paths to JSON files, not
numbers. See docs/guides/COST_OPTIMIZATION_USER_GUIDE.md (Part 2).
"""

import pytest
import sys
import json
import csv
from pathlib import Path
from unittest.mock import patch
import tempfile
import shutil

import matplotlib

# Headless: these commands render charts, and an interactive backend would try
# to open a window (or block) on a CI machine.
matplotlib.use("Agg")

from pmhelper.cli import optimization_cli


@pytest.fixture
def temp_dir():
    """Create and cleanup a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_project_file(temp_dir):
    """A sample project CSV in the schema FileHandler.load_csv actually reads."""
    csv_path = temp_dir / "sample_project.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'activity', 'duration', 'predecessors',
                         'min_duration', 'crash_cost', 'normal_cost',
                         'resource_demand'])
        writer.writerow(['A', 'Design', '5', '', '3', '1500', '1000', '2'])
        writer.writerow(['B', 'Build', '3', 'A', '2', '1100', '800', '3'])
        writer.writerow(['C', 'Test', '4', 'A', '3', '1600', '1200', '1'])
        writer.writerow(['D', 'Deploy', '2', 'B,C', '1', '800', '600', '2'])
    return csv_path


@pytest.fixture
def indirect_costs_file(temp_dir):
    """Indirect costs JSON: category -> daily rate."""
    path = temp_dir / "indirect_costs.json"
    path.write_text(json.dumps({
        "facilities": 200.0,
        "equipment": 150.0,
        "utilities": 50.0,
        "overhead": 100.0,
    }), encoding='utf-8')
    return path


@pytest.fixture
def cash_flows_file(temp_dir):
    """Cash flows JSON: activity id -> cash flow."""
    path = temp_dir / "cash_flows.json"
    path.write_text(json.dumps({
        "A": 5000.0,
        "B": -2000.0,
        "C": 8000.0,
        "D": 3000.0,
    }), encoding='utf-8')
    return path


def run_cli(args):
    """Invoke the CLI as a user would; return the exit code (0 = success).

    argv[0] is the program name and is discarded by argparse, so the subcommand
    must be argv[1].
    """
    with patch.object(sys, 'argv', ['optimization_cli'] + args):
        try:
            optimization_cli.main()
            return 0
        except SystemExit as e:
            return e.code if e.code is not None else 0


class TestOptimizeCLILoading:
    """Test CLI module loading."""

    def test_module_imports(self):
        assert optimization_cli is not None

    def test_main_function_exists(self):
        assert hasattr(optimization_cli, 'main')
        assert callable(optimization_cli.main)


class TestTimeCostCLI:
    """Test time-cost optimization CLI command."""

    def test_time_cost_with_valid_project(self, sample_project_file,
                                          indirect_costs_file, temp_dir):
        base = temp_dir / "timecost"
        code = run_cli(['time-cost',
                        '--input', str(sample_project_file),
                        '--indirect', str(indirect_costs_file),
                        '--output', str(base)])
        assert code == 0
        assert Path(f"{base}_curve.png").exists()
        assert Path(f"{base}_report.txt").exists()

    def test_time_cost_single_category_costs(self, sample_project_file, temp_dir):
        """Category names are free-form and summed, so one category is valid."""
        indirect = temp_dir / "simple_indirect.json"
        indirect.write_text(json.dumps({"indirect": 500.0}), encoding='utf-8')

        base = temp_dir / "timecost_simple"
        code = run_cli(['time-cost',
                        '--input', str(sample_project_file),
                        '--indirect', str(indirect),
                        '--output', str(base)])
        assert code == 0
        assert Path(f"{base}_curve.png").exists()

    def test_time_cost_csv_and_json_export(self, sample_project_file,
                                           indirect_costs_file, temp_dir):
        base = temp_dir / "timecost_export"
        code = run_cli(['time-cost',
                        '--input', str(sample_project_file),
                        '--indirect', str(indirect_costs_file),
                        '--output', str(base)])
        assert code == 0
        assert Path(f"{base}.csv").exists()
        assert Path(f"{base}.json").exists()

    def test_time_cost_requires_input_and_indirect(self, sample_project_file):
        """Both flags are required; argparse exits 2 when one is missing."""
        assert run_cli(['time-cost', '--input', str(sample_project_file)]) == 2

    def test_time_cost_rejects_positional_project_file(self, sample_project_file,
                                                       indirect_costs_file):
        """The project file is passed via --input, never positionally."""
        assert run_cli(['time-cost', str(sample_project_file),
                        '--indirect', str(indirect_costs_file)]) == 2


class TestResourcesCLI:
    """Test resource leveling CLI command."""

    def test_resources_minimum_moment(self, sample_project_file, temp_dir):
        base = temp_dir / "rl_mm"
        code = run_cli(['resources',
                        '--input', str(sample_project_file),
                        '--method', 'minimum_moment',
                        '--output', str(base)])
        assert code == 0
        assert Path(f"{base}_profile.png").exists()
        assert Path(f"{base}_report.txt").exists()

    def test_resources_burgess(self, sample_project_file, temp_dir):
        base = temp_dir / "rl_burgess"
        code = run_cli(['resources',
                        '--input', str(sample_project_file),
                        '--method', 'burgess',
                        '--output', str(base)])
        assert code == 0
        assert Path(f"{base}_profile.png").exists()

    def test_resources_with_limit(self, sample_project_file, temp_dir):
        base = temp_dir / "rl_limit"
        code = run_cli(['resources',
                        '--input', str(sample_project_file),
                        '--method', 'burgess',
                        '--limit', '8',
                        '--output', str(base)])
        assert code == 0
        assert Path(f"{base}_schedule.csv").exists()


class TestNPVCLI:
    """Test NPV optimization CLI command."""

    def test_npv_basic(self, sample_project_file, cash_flows_file, temp_dir):
        base = temp_dir / "npv"
        code = run_cli(['npv',
                        '--input', str(sample_project_file),
                        '--cash-flows', str(cash_flows_file),
                        '--output', str(base)])
        assert code == 0
        assert Path(f"{base}_schedule.csv").exists()

    def test_npv_with_sensitivity(self, sample_project_file, cash_flows_file,
                                  temp_dir):
        base = temp_dir / "npv_sens"
        code = run_cli(['npv',
                        '--input', str(sample_project_file),
                        '--cash-flows', str(cash_flows_file),
                        '--sensitivity',
                        '--output', str(base)])
        assert code == 0
        assert Path(f"{base}_sensitivity.csv").exists()
        assert Path(f"{base}_sensitivity.png").exists()

    def test_npv_different_rates(self, sample_project_file, cash_flows_file,
                                 temp_dir):
        for rate in ('0.05', '0.15'):
            base = temp_dir / f"npv_{rate.replace('.', '')}"
            code = run_cli(['npv',
                            '--input', str(sample_project_file),
                            '--cash-flows', str(cash_flows_file),
                            '--discount-rate', rate,
                            '--output', str(base)])
            assert code == 0, f"discount rate {rate} failed"
            assert Path(f"{base}_cashflows.csv").exists()

    def test_npv_requires_cash_flows(self, sample_project_file):
        """--cash-flows is required and has no default."""
        assert run_cli(['npv', '--input', str(sample_project_file)]) == 2


class TestParetoCLI:
    """Test multi-objective Pareto CLI command."""

    def test_pareto_duration_cost(self, sample_project_file, temp_dir):
        base = temp_dir / "pareto"
        code = run_cli(['pareto',
                        '--input', str(sample_project_file),
                        '--objectives', 'duration,cost',
                        '--samples', '15',
                        '--output', str(base)])
        assert code == 0
        assert Path(f"{base}_report.txt").exists()

    def test_pareto_sample_sizes(self, sample_project_file, temp_dir):
        for n in ('10', '25'):
            base = temp_dir / f"pareto_{n}"
            code = run_cli(['pareto',
                            '--input', str(sample_project_file),
                            '--objectives', 'duration,cost',
                            '--samples', n,
                            '--output', str(base)])
            assert code == 0, f"samples={n} failed"

    def test_pareto_requires_objectives(self, sample_project_file):
        assert run_cli(['pareto', '--input', str(sample_project_file)]) == 2


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_invalid_project_file(self, indirect_costs_file, temp_dir):
        """A missing input file is reported, not raised as a bare traceback."""
        code = run_cli(['time-cost',
                        '--input', str(temp_dir / "does_not_exist.csv"),
                        '--indirect', str(indirect_costs_file),
                        '--output', str(temp_dir / "out")])
        assert code != 0

    def test_invalid_method(self, sample_project_file, temp_dir):
        """--method is constrained by choices, so argparse exits 2."""
        code = run_cli(['resources',
                        '--input', str(sample_project_file),
                        '--method', 'not_a_method',
                        '--output', str(temp_dir / "out")])
        assert code == 2

    def test_unknown_subcommand(self):
        assert run_cli(['not-a-command']) == 2


class TestCLIOutputFormats:
    """Test CLI output formats."""

    def test_csv_output_format(self, sample_project_file, indirect_costs_file,
                               temp_dir):
        base = temp_dir / "fmt_csv"
        assert run_cli(['time-cost',
                        '--input', str(sample_project_file),
                        '--indirect', str(indirect_costs_file),
                        '--output', str(base)]) == 0

        csv_path = Path(f"{base}.csv")
        assert csv_path.exists()
        with open(csv_path, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        assert len(rows) > 1, "expected a header plus at least one data row"

    def test_json_output_format(self, sample_project_file, indirect_costs_file,
                                temp_dir):
        base = temp_dir / "fmt_json"
        assert run_cli(['time-cost',
                        '--input', str(sample_project_file),
                        '--indirect', str(indirect_costs_file),
                        '--output', str(base)]) == 0

        json_path = Path(f"{base}.json")
        assert json_path.exists()
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        assert data, "expected non-empty JSON export"
