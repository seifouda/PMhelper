"""
Tests for Cost Optimization Visualizations

Tests plotting and reporting functions for cost optimization.
"""

import pytest
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt

from src.pmhelper.core.cost_visualizations import (
    plot_time_cost_curve,
    generate_cost_report,
    plot_cost_breakdown,
    plot_savings_analysis,
    export_optimization_results
)


@pytest.fixture
def sample_curve_data():
    """Sample time-cost curve data"""
    return pd.DataFrame({
        'duration': [10, 9, 8, 7, 6],
        'direct_cost': [5000, 5200, 5450, 5750, 6200],
        'indirect_cost': [5000, 4500, 4000, 3500, 3000],
        'total_cost': [10000, 9700, 9450, 9250, 9200],
        'activities_crashed': [[], ['A'], ['A', 'B'], ['A', 'B', 'C'], ['A', 'B', 'C', 'D']]
    })


@pytest.fixture
def sample_optimal_point():
    """Sample optimal point data"""
    return {
        'optimal_duration': 6,
        'optimal_total_cost': 9200,
        'direct_cost': 6200,
        'indirect_cost': 3000,
        'activities_crashed': ['A', 'B', 'C', 'D'],
        'normal_duration': 10,
        'normal_total': 10000,
        'normal_direct': 5000,
        'normal_indirect': 5000,
        'savings_vs_normal': 800,
        'savings_pct': 8.0
    }


@pytest.fixture
def mock_cpm_result():
    """Mock CPM result object"""
    class MockCPM:
        def __init__(self):
            self.project_name = 'Test Project'
            self.project_duration = 10
    
    return MockCPM()


class TestPlotTimeCostCurve:
    """Test time-cost curve plotting"""

    def test_plot_creation(self, sample_curve_data, sample_optimal_point):
        """Test that plot is created successfully"""
        fig = plot_time_cost_curve(sample_curve_data, sample_optimal_point)
        
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 1
        plt.close(fig)

    def test_plot_has_three_lines(self, sample_curve_data, sample_optimal_point):
        """Test that plot has direct, indirect, and total cost lines"""
        fig = plot_time_cost_curve(sample_curve_data, sample_optimal_point)
        ax = fig.axes[0]
        
        # Should have 3 lines + 1 scatter (optimal point)
        lines = ax.get_lines()
        assert len(lines) >= 3
        plt.close(fig)

    def test_plot_has_optimal_marker(self, sample_curve_data, sample_optimal_point):
        """Test that optimal point is marked"""
        fig = plot_time_cost_curve(sample_curve_data, sample_optimal_point)
        ax = fig.axes[0]
        
        # Check for scatter plots (optimal point marker)
        collections = ax.collections
        assert len(collections) > 0
        plt.close(fig)

    def test_plot_has_labels(self, sample_curve_data, sample_optimal_point):
        """Test that plot has proper labels"""
        fig = plot_time_cost_curve(sample_curve_data, sample_optimal_point)
        ax = fig.axes[0]
        
        assert ax.get_xlabel() != ''
        assert ax.get_ylabel() != ''
        assert ax.get_title() != ''
        assert ax.get_legend() is not None
        plt.close(fig)


class TestGenerateCostReport:
    """Test cost report generation"""

    def test_report_creation(self, mock_cpm_result, sample_optimal_point):
        """Test that report is created successfully"""
        report = generate_cost_report(mock_cpm_result, sample_optimal_point)
        
        assert isinstance(report, str)
        assert len(report) > 0

    def test_report_contains_key_sections(self, mock_cpm_result, sample_optimal_point):
        """Test that report contains all key sections"""
        report = generate_cost_report(mock_cpm_result, sample_optimal_point)
        
        assert 'COST OPTIMIZATION REPORT' in report
        assert 'NORMAL SCHEDULE' in report
        assert 'OPTIMIZED SCHEDULE' in report
        assert 'SAVINGS ANALYSIS' in report
        assert 'ACTIVITIES CRASHED' in report
        assert 'RECOMMENDATION' in report

    def test_report_contains_values(self, mock_cpm_result, sample_optimal_point):
        """Test that report contains actual values"""
        report = generate_cost_report(mock_cpm_result, sample_optimal_point)
        
        assert '10 days' in report  # Normal duration
        assert '6 days' in report   # Optimal duration
        assert '$9,200.00' in report or '$9200' in report  # Total cost
        assert '8.0%' in report     # Savings percentage

    def test_report_recommendation_with_savings(self, mock_cpm_result, sample_optimal_point):
        """Test recommendation when there are savings"""
        report = generate_cost_report(mock_cpm_result, sample_optimal_point)
        
        assert 'RECOMMENDED: Crash project' in report

    def test_report_recommendation_without_savings(self, mock_cpm_result, sample_optimal_point):
        """Test recommendation when there are no savings"""
        no_savings_point = sample_optimal_point.copy()
        no_savings_point['savings_vs_normal'] = 0
        
        report = generate_cost_report(mock_cpm_result, no_savings_point)
        
        assert 'Maintain normal schedule' in report


class TestPlotCostBreakdown:
    """Test cost breakdown plotting"""

    def test_breakdown_plot_creation(self, sample_optimal_point):
        """Test that breakdown plot is created"""
        fig = plot_cost_breakdown(sample_optimal_point)
        
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 1
        plt.close(fig)

    def test_breakdown_has_two_bars(self, sample_optimal_point):
        """Test that plot has bars for normal and optimized"""
        fig = plot_cost_breakdown(sample_optimal_point)
        ax = fig.axes[0]
        
        # Should have 2 sets of stacked bars
        patches = ax.patches
        assert len(patches) == 4  # 2 schedules × 2 cost types
        plt.close(fig)

    def test_breakdown_has_labels(self, sample_optimal_point):
        """Test that breakdown plot has labels"""
        fig = plot_cost_breakdown(sample_optimal_point)
        ax = fig.axes[0]
        
        assert ax.get_ylabel() != ''
        assert ax.get_title() != ''
        assert ax.get_legend() is not None
        plt.close(fig)


class TestPlotSavingsAnalysis:
    """Test savings analysis plotting"""

    def test_savings_plot_creation(self, sample_curve_data, sample_optimal_point):
        """Test that savings plot is created"""
        fig = plot_savings_analysis(sample_curve_data, sample_optimal_point)
        
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 2  # Two subplots
        plt.close(fig)

    def test_savings_plot_structure(self, sample_curve_data, sample_optimal_point):
        """Test that savings plot has correct structure"""
        fig = plot_savings_analysis(sample_curve_data, sample_optimal_point)
        
        # Should have 2 subplots
        assert len(fig.axes) == 2
        
        # Both should have titles
        assert all(ax.get_title() != '' for ax in fig.axes)
        plt.close(fig)


class TestExportOptimizationResults:
    """Test exporting optimization results"""

    def test_export_csv(self, sample_curve_data, sample_optimal_point, tmp_path):
        """Test CSV export"""
        filepath = tmp_path / "results.csv"
        
        export_optimization_results(
            sample_curve_data, 
            sample_optimal_point,
            str(filepath),
            format='csv'
        )
        
        assert filepath.exists()
        
        # Verify content
        df = pd.read_csv(filepath)
        assert len(df) == len(sample_curve_data)
        assert 'duration' in df.columns

    def test_export_json(self, sample_curve_data, sample_optimal_point, tmp_path):
        """Test JSON export"""
        filepath = tmp_path / "results.json"
        
        export_optimization_results(
            sample_curve_data,
            sample_optimal_point,
            str(filepath),
            format='json'
        )
        
        assert filepath.exists()
        
        # Verify content
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert 'curve_data' in data
        assert 'optimal_point' in data
        assert len(data['curve_data']) == len(sample_curve_data)

    def test_export_excel(self, sample_curve_data, sample_optimal_point, tmp_path):
        """Test Excel export"""
        filepath = tmp_path / "results.xlsx"
        
        export_optimization_results(
            sample_curve_data,
            sample_optimal_point,
            str(filepath),
            format='excel'
        )
        
        assert filepath.exists()
        
        # Verify content
        df = pd.read_excel(filepath, sheet_name='Time-Cost Curve')
        assert len(df) == len(sample_curve_data)

    def test_export_invalid_format(self, sample_curve_data, sample_optimal_point, tmp_path):
        """Test that invalid format raises error"""
        filepath = tmp_path / "results.txt"
        
        with pytest.raises(ValueError, match="Unsupported format"):
            export_optimization_results(
                sample_curve_data,
                sample_optimal_point,
                str(filepath),
                format='txt'
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
