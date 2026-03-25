"""
Integration tests for optimization CLI commands.
Tests all four CLI commands: time-cost, resources, npv, pareto.
"""

import pytest
import sys
import json
import csv
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pmhelper.cli import optimization_cli
from pmhelper.core.cpm_analyzer import CPMAnalyzer


@pytest.fixture
def temp_dir():
    """Create and cleanup a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_project_file(temp_dir):
    """Create a sample project CSV file for testing."""
    csv_path = temp_dir / "sample_project.csv"
    
    # Create a simple project CSV
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Activity', 'Duration', 'Predecessors', 'NormalCost', 'CrashCost', 'CrashTime', 'Resources'])
        writer.writerow(['A', '5', '', '1000', '1500', '3', 'Worker:2,Equipment:1'])
        writer.writerow(['B', '3', 'A', '800', '1100', '2', 'Worker:3'])
        writer.writerow(['C', '4', 'A', '1200', '1600', '3', 'Worker:1,Equipment:2'])
        writer.writerow(['D', '2', 'B,C', '600', '800', '1', 'Worker:2'])
    
    return csv_path


class TestOptimizeCLILoading:
    """Test CLI module loading and command structure."""
    
    def test_module_imports(self):
        """Test that optimization CLI module imports successfully."""
        assert hasattr(optimization_cli, 'main')
        assert hasattr(optimization_cli, 'optimize_time_cost')
        assert hasattr(optimization_cli, 'optimize_resources')
        assert hasattr(optimization_cli, 'optimize_npv')
        assert hasattr(optimization_cli, 'optimize_pareto')
    
    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        assert callable(optimization_cli.main)


class TestTimeCostCLI:
    """Test time-cost optimization CLI command."""
    
    def test_time_cost_with_valid_project(self, sample_project_file, temp_dir):
        """Test time-cost optimization with valid project file."""
        output_prefix = temp_dir / "timecost"
        
        # Mock command line arguments
        args = [
            'optimize',
            'time-cost',
            str(sample_project_file),
            '--indirect-cost', '2000',
            '--output', str(output_prefix)
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # Check that output files were created
                assert (temp_dir / "timecost_curve.csv").exists()
                assert (temp_dir / "timecost_curve.png").exists()
                
            except SystemExit as e:
                # Exit code 0 is success
                assert e.code == 0
    
    def test_time_cost_breakdown_costs(self, sample_project_file, temp_dir):
        """Test time-cost optimization with breakdown of indirect costs."""
        output_prefix = temp_dir / "timecost_breakdown"
        
        args = [
            'optimize',
            'time-cost',
            str(sample_project_file),
            '--facilities', '500',
            '--equipment', '300',
            '--utilities', '200',
            '--overhead', '1000',
            '--output', str(output_prefix)
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # Verify outputs exist
                assert (temp_dir / "timecost_breakdown_curve.csv").exists()
                
                # Read CSV and verify structure
                with open(temp_dir / "timecost_breakdown_curve.csv", 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    assert len(rows) > 0
                    assert 'duration' in rows[0]
                    assert 'direct_cost' in rows[0]
                    assert 'indirect_cost' in rows[0]
                    assert 'total_cost' in rows[0]
                
            except SystemExit as e:
                assert e.code == 0
    
    def test_time_cost_json_export(self, sample_project_file, temp_dir):
        """Test time-cost optimization with JSON export."""
        output_prefix = temp_dir / "timecost_json"
        
        args = [
            'optimize',
            'time-cost',
            str(sample_project_file),
            '--indirect-cost', '2000',
            '--output', str(output_prefix),
            '--format', 'json'
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # Check JSON file exists
                json_file = temp_dir / "timecost_json_curve.json"
                assert json_file.exists()
                
                # Verify JSON structure
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                    assert 'curve' in data
                    assert isinstance(data['curve'], list)
                    assert len(data['curve']) > 0
                    
            except SystemExit as e:
                assert e.code == 0


class TestResourcesCLI:
    """Test resource leveling CLI command."""
    
    def test_resources_minimum_moment(self, sample_project_file, temp_dir):
        """Test resource leveling with minimum moment method."""
        output_prefix = temp_dir / "resources_mm"
        
        args = [
            'optimize',
            'resources',
            str(sample_project_file),
            '--method', 'minimum_moment',
            '--output', str(output_prefix)
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # Verify outputs
                assert (temp_dir / "resources_mm_profile.png").exists()
                assert (temp_dir / "resources_mm_schedule.csv").exists()
                
                # Read schedule CSV
                with open(temp_dir / "resources_mm_schedule.csv", 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    assert len(rows) > 0
                    assert 'activity' in rows[0]
                    assert 'start' in rows[0]
                    
            except SystemExit as e:
                assert e.code == 0
    
    def test_resources_burgess(self, sample_project_file, temp_dir):
        """Test resource leveling with Burgess method."""
        output_prefix = temp_dir / "resources_burgess"
        
        args = [
            'optimize',
            'resources',
            str(sample_project_file),
            '--method', 'burgess',
            '--output', str(output_prefix)
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # Verify outputs exist
                assert (temp_dir / "resources_burgess_profile.png").exists()
                assert (temp_dir / "resources_burgess_schedule.csv").exists()
                
            except SystemExit as e:
                assert e.code == 0
    
    def test_resources_with_limit(self, sample_project_file, temp_dir):
        """Test resource leveling with resource limit."""
        output_prefix = temp_dir / "resources_limited"
        
        args = [
            'optimize',
            'resources',
            str(sample_project_file),
            '--method', 'minimum_moment',
            '--limit', '5',
            '--output', str(output_prefix)
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # Verify outputs
                assert (temp_dir / "resources_limited_profile.png").exists()
                
            except SystemExit as e:
                assert e.code == 0


class TestNPVCLI:
    """Test NPV optimization CLI command."""
    
    def test_npv_basic(self, sample_project_file, temp_dir):
        """Test basic NPV optimization."""
        output_prefix = temp_dir / "npv_basic"
        
        args = [
            'optimize',
            'npv',
            str(sample_project_file),
            '--discount-rate', '0.1',
            '--output', str(output_prefix)
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # Verify outputs
                assert (temp_dir / "npv_basic_schedule.csv").exists()
                assert (temp_dir / "npv_basic_cashflow.csv").exists()
                
                # Read cashflow CSV
                with open(temp_dir / "npv_basic_cashflow.csv", 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    assert len(rows) > 0
                    assert 'period' in rows[0]
                    assert 'cost' in rows[0]
                    
            except SystemExit as e:
                assert e.code == 0
    
    def test_npv_with_sensitivity(self, sample_project_file, temp_dir):
        """Test NPV optimization with sensitivity analysis."""
        output_prefix = temp_dir / "npv_sensitivity"
        
        args = [
            'optimize',
            'npv',
            str(sample_project_file),
            '--discount-rate', '0.1',
            '--sensitivity',
            '--output', str(output_prefix)
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # Verify outputs including sensitivity
                assert (temp_dir / "npv_sensitivity_schedule.csv").exists()
                assert (temp_dir / "npv_sensitivity_cashflow.csv").exists()
                assert (temp_dir / "npv_sensitivity_analysis.png").exists()
                
            except SystemExit as e:
                assert e.code == 0
    
    def test_npv_different_rates(self, sample_project_file, temp_dir):
        """Test NPV optimization with different discount rates."""
        rates = [0.05, 0.10, 0.15]
        
        for rate in rates:
            output_prefix = temp_dir / f"npv_{int(rate*100)}"
            
            args = [
                'optimize',
                'npv',
                str(sample_project_file),
                '--discount-rate', str(rate),
                '--output', str(output_prefix)
            ]
            
            with patch('sys.argv', args):
                try:
                    optimization_cli.main()
                    
                    # Verify outputs
                    assert (temp_dir / f"npv_{int(rate*100)}_schedule.csv").exists()
                    
                except SystemExit as e:
                    assert e.code == 0


class TestParetoCLI:
    """Test multi-objective Pareto optimization CLI command."""
    
    def test_pareto_duration_cost(self, sample_project_file, temp_dir):
        """Test Pareto optimization with duration and cost objectives."""
        output_prefix = temp_dir / "pareto_dc"
        
        args = [
            'optimize',
            'pareto',
            str(sample_project_file),
            '--objectives', 'duration', 'cost',
            '--samples', '50',
            '--output', str(output_prefix)
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # Verify outputs
                assert (temp_dir / "pareto_dc_frontier.png").exists()
                assert (temp_dir / "pareto_dc_solutions.csv").exists()
                
                # Read solutions CSV
                with open(temp_dir / "pareto_dc_solutions.csv", 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    assert len(rows) > 0
                    assert 'duration' in rows[0]
                    assert 'cost' in rows[0]
                    
            except SystemExit as e:
                assert e.code == 0
    
    def test_pareto_all_objectives(self, sample_project_file, temp_dir):
        """Test Pareto optimization with all three objectives."""
        output_prefix = temp_dir / "pareto_all"
        
        args = [
            'optimize',
            'pareto',
            str(sample_project_file),
            '--objectives', 'duration', 'cost', 'npv',
            '--discount-rate', '0.1',
            '--samples', '30',
            '--output', str(output_prefix)
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # Verify outputs
                assert (temp_dir / "pareto_all_frontier.png").exists()
                assert (temp_dir / "pareto_all_solutions.csv").exists()
                
                # Read solutions
                with open(temp_dir / "pareto_all_solutions.csv", 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    assert len(rows) > 0
                    assert 'duration' in rows[0]
                    assert 'cost' in rows[0]
                    assert 'npv' in rows[0]
                    
            except SystemExit as e:
                assert e.code == 0
    
    def test_pareto_sample_sizes(self, sample_project_file, temp_dir):
        """Test Pareto optimization with different sample sizes."""
        sample_sizes = [20, 50, 100]
        
        for size in sample_sizes:
            output_prefix = temp_dir / f"pareto_{size}"
            
            args = [
                'optimize',
                'pareto',
                str(sample_project_file),
                '--objectives', 'duration', 'cost',
                '--samples', str(size),
                '--output', str(output_prefix)
            ]
            
            with patch('sys.argv', args):
                try:
                    optimization_cli.main()
                    
                    # Verify outputs
                    assert (temp_dir / f"pareto_{size}_solutions.csv").exists()
                    
                except SystemExit as e:
                    assert e.code == 0


class TestCLIErrorHandling:
    """Test CLI error handling and validation."""
    
    def test_invalid_project_file(self, temp_dir):
        """Test handling of invalid project file."""
        args = [
            'optimize',
            'time-cost',
            str(temp_dir / "nonexistent.csv"),
            '--indirect-cost', '2000'
        ]
        
        with patch('sys.argv', args):
            with pytest.raises(SystemExit) as exc_info:
                optimization_cli.main()
            
            # Should exit with error
            assert exc_info.value.code != 0
    
    def test_invalid_method(self, sample_project_file, temp_dir):
        """Test handling of invalid leveling method."""
        args = [
            'optimize',
            'resources',
            str(sample_project_file),
            '--method', 'invalid_method',
            '--output', str(temp_dir / "test")
        ]
        
        with patch('sys.argv', args):
            # argparse should catch this
            with pytest.raises(SystemExit):
                optimization_cli.main()
    
    def test_missing_objectives(self, sample_project_file, temp_dir):
        """Test handling of missing objectives in Pareto."""
        args = [
            'optimize',
            'pareto',
            str(sample_project_file),
            '--samples', '50',
            '--output', str(temp_dir / "test")
        ]
        
        with patch('sys.argv', args):
            # Should require at least 2 objectives
            with pytest.raises(SystemExit):
                optimization_cli.main()


class TestCLIOutputFormats:
    """Test CLI output format options."""
    
    def test_csv_output_format(self, sample_project_file, temp_dir):
        """Test CSV output format (default)."""
        output_prefix = temp_dir / "csv_test"
        
        args = [
            'optimize',
            'time-cost',
            str(sample_project_file),
            '--indirect-cost', '2000',
            '--output', str(output_prefix),
            '--format', 'csv'
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # CSV files should be created
                assert (temp_dir / "csv_test_curve.csv").exists()
                
            except SystemExit as e:
                assert e.code == 0
    
    def test_json_output_format(self, sample_project_file, temp_dir):
        """Test JSON output format."""
        output_prefix = temp_dir / "json_test"
        
        args = [
            'optimize',
            'time-cost',
            str(sample_project_file),
            '--indirect-cost', '2000',
            '--output', str(output_prefix),
            '--format', 'json'
        ]
        
        with patch('sys.argv', args):
            try:
                optimization_cli.main()
                
                # JSON files should be created
                json_file = temp_dir / "json_test_curve.json"
                assert json_file.exists()
                
                # Verify valid JSON
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    assert isinstance(data, dict)
                
            except SystemExit as e:
                assert e.code == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
