"""
Tests for Cost Optimization Module

Tests IndirectCostModel and TimeCostOptimizer functionality.
"""

import pytest
import pandas as pd
import numpy as np
from src.pmhelper.core.cost_optimization import (
    IndirectCostModel,
    TimeCostOptimizer,
    integrate_cost_optimization_with_cpm
)


class TestIndirectCostModel:
    """Test cases for IndirectCostModel"""

    def test_initialization(self):
        """Test IndirectCostModel initialization"""
        cost_categories = {
            'facilities': 200.0,
            'equipment': 150.0,
            'utilities': 50.0,
            'overhead': 100.0
        }
        model = IndirectCostModel(cost_categories)
        
        assert model.daily_rate == 500.0
        assert model.categories == cost_categories

    def test_calculate_cost(self):
        """Test cost calculation for different durations"""
        model = IndirectCostModel({'overhead': 100.0, 'facilities': 200.0})
        
        assert model.calculate_cost(10) == 3000.0
        assert model.calculate_cost(0) == 0.0
        assert model.calculate_cost(1) == 300.0

    def test_calculate_cost_negative_duration(self):
        """Test that negative duration raises error"""
        model = IndirectCostModel({'overhead': 100.0})
        
        with pytest.raises(ValueError):
            model.calculate_cost(-5)

    def test_breakdown_by_category(self):
        """Test cost breakdown by category"""
        cost_categories = {
            'facilities': 200.0,
            'equipment': 150.0,
            'overhead': 100.0
        }
        model = IndirectCostModel(cost_categories)
        
        breakdown = model.breakdown_by_category(10)
        
        assert breakdown['facilities'] == 2000.0
        assert breakdown['equipment'] == 1500.0
        assert breakdown['overhead'] == 1000.0
        assert sum(breakdown.values()) == 4500.0

    def test_cost_curve(self):
        """Test cost curve generation"""
        model = IndirectCostModel({'overhead': 100.0})
        
        curve = model.cost_curve(range(5, 11))
        
        assert len(curve) == 6
        assert list(curve.columns) == ['duration', 'indirect_cost']
        assert curve.iloc[0]['duration'] == 5
        assert curve.iloc[0]['indirect_cost'] == 500.0
        assert curve.iloc[-1]['duration'] == 10
        assert curve.iloc[-1]['indirect_cost'] == 1000.0


class MockCPMAnalyzer:
    """Mock CPM analyzer for testing"""
    
    def __init__(self):
        self.project_duration = 10
        self.critical_activities = ['A', 'B', 'C']
        self.G = self._create_mock_graph()
        
    def _create_mock_graph(self):
        """Create mock graph with activities"""
        import networkx as nx
        G = nx.DiGraph()
        
        # Add activities with cost and duration data. EF (early finish) is required —
        # TimeCostOptimizer.generate_curve() derives normal_duration from max(EF);
        # without it every node defaults to EF=0, so normal_duration is 0 and the
        # crash loop immediately goes negative (ValueError). Modeled as a simple
        # A -> B -> C chain (matches critical_activities below).
        G.add_node('A', duration=4, min_duration=3, normal_cost=1000, crash_cost=1200, EF=4)
        G.add_node('B', duration=6, min_duration=4, normal_cost=1500, crash_cost=2000, EF=10)
        G.add_node('C', duration=3, min_duration=2, normal_cost=800, crash_cost=1000, EF=13)
        G.add_node('Start')
        G.add_node('End')
        
        return G


class TestTimeCostOptimizer:
    """Test cases for TimeCostOptimizer"""

    def test_initialization(self):
        """Test TimeCostOptimizer initialization"""
        cpm = MockCPMAnalyzer()
        indirect_model = IndirectCostModel({'overhead': 500.0})
        
        optimizer = TimeCostOptimizer(cpm, indirect_model)
        
        assert optimizer.cpm == cpm
        assert optimizer.indirect_model == indirect_model
        assert optimizer.curve_data == []

    def test_find_crashable_activities(self):
        """Test finding crashable activities"""
        cpm = MockCPMAnalyzer()
        indirect_model = IndirectCostModel({'overhead': 500.0})
        optimizer = TimeCostOptimizer(cpm, indirect_model)
        
        crashable = optimizer._find_crashable_activities([])
        
        assert len(crashable) == 3
        assert all('id' in act for act in crashable)
        assert all('crash_cost_slope' in act for act in crashable)

    def test_find_crashable_excludes_already_crashed(self):
        """Test that already crashed activities are excluded"""
        cpm = MockCPMAnalyzer()
        indirect_model = IndirectCostModel({'overhead': 500.0})
        optimizer = TimeCostOptimizer(cpm, indirect_model)
        
        crashable = optimizer._find_crashable_activities(['A', 'B'])
        
        assert len(crashable) == 1
        assert crashable[0]['id'] == 'C'

    def test_generate_curve_basic(self):
        """Test basic curve generation"""
        cpm = MockCPMAnalyzer()
        indirect_model = IndirectCostModel({'overhead': 500.0})
        optimizer = TimeCostOptimizer(cpm, indirect_model)
        
        curve = optimizer.generate_curve()
        
        assert isinstance(curve, pd.DataFrame)
        assert 'duration' in curve.columns
        assert 'direct_cost' in curve.columns
        assert 'indirect_cost' in curve.columns
        assert 'total_cost' in curve.columns
        assert len(curve) > 0

    def test_find_optimal_duration(self):
        """Test finding optimal duration"""
        cpm = MockCPMAnalyzer()
        indirect_model = IndirectCostModel({'overhead': 500.0})
        optimizer = TimeCostOptimizer(cpm, indirect_model)
        
        result = optimizer.find_optimal_duration()
        
        assert 'optimal_duration' in result
        assert 'optimal_total_cost' in result
        assert 'direct_cost' in result
        assert 'indirect_cost' in result
        assert 'savings_vs_normal' in result
        assert 'savings_pct' in result
        assert isinstance(result['optimal_duration'], int)
        assert result['optimal_total_cost'] > 0

    def test_optimal_is_minimum_cost(self):
        """Test that optimal point has minimum total cost"""
        cpm = MockCPMAnalyzer()
        indirect_model = IndirectCostModel({'overhead': 500.0})
        optimizer = TimeCostOptimizer(cpm, indirect_model)
        
        curve = optimizer.generate_curve()
        result = optimizer.find_optimal_duration()
        
        min_cost = curve['total_cost'].min()
        assert result['optimal_total_cost'] == min_cost


class TestCPMIntegration:
    """Test integration with CPM analyzer"""

    def test_attach_indirect_costs(self):
        """Test attaching indirect costs to CPM analyzer"""
        cpm = MockCPMAnalyzer()
        integrate_cost_optimization_with_cpm(cpm)
        
        cost_categories = {'overhead': 100.0, 'facilities': 200.0}
        cpm.attach_indirect_costs(cost_categories)
        
        assert hasattr(cpm, 'indirect_model')
        assert isinstance(cpm.indirect_model, IndirectCostModel)
        assert cpm.indirect_model.daily_rate == 300.0

    def test_optimize_cost_method(self):
        """Test optimize_cost method on CPM analyzer"""
        cpm = MockCPMAnalyzer()
        integrate_cost_optimization_with_cpm(cpm)
        
        cpm.attach_indirect_costs({'overhead': 500.0})
        result = cpm.optimize_cost()
        
        assert isinstance(result, dict)
        assert 'optimal_duration' in result
        assert 'optimal_total_cost' in result

    def test_optimize_cost_without_indirect_costs_raises_error(self):
        """Test that optimize_cost raises error without indirect costs"""
        cpm = MockCPMAnalyzer()
        integrate_cost_optimization_with_cpm(cpm)
        
        with pytest.raises(ValueError, match="Must attach indirect costs first"):
            cpm.optimize_cost()

    def test_get_optimization_curve_method(self):
        """Test get_optimization_curve method"""
        cpm = MockCPMAnalyzer()
        integrate_cost_optimization_with_cpm(cpm)
        
        cpm.attach_indirect_costs({'overhead': 500.0})
        curve = cpm.get_optimization_curve()
        
        assert isinstance(curve, pd.DataFrame)
        assert 'duration' in curve.columns
        assert 'total_cost' in curve.columns


class TestCostCalculations:
    """Test actual cost calculations with known examples"""

    def test_example_calculation(self):
        """Test with a known example from documentation"""
        # Example: 10 days normal, $500/day indirect cost
        # Activities with crash costs
        
        cpm = MockCPMAnalyzer()
        cpm.project_duration = 10
        
        # Indirect cost: $500/day
        indirect_model = IndirectCostModel({'overhead': 500.0})
        
        # Normal schedule
        normal_duration = 10
        normal_direct = 3300  # Sum of normal costs
        normal_indirect = indirect_model.calculate_cost(normal_duration)
        normal_total = normal_direct + normal_indirect
        
        assert normal_indirect == 5000.0
        assert normal_total == 8300.0

    def test_savings_calculation(self):
        """Test savings calculation logic"""
        cpm = MockCPMAnalyzer()
        indirect_model = IndirectCostModel({'overhead': 500.0})
        optimizer = TimeCostOptimizer(cpm, indirect_model)
        
        result = optimizer.find_optimal_duration()
        
        # Savings should be non-negative
        assert result['savings_vs_normal'] >= 0
        
        # Verify savings calculation
        expected_savings = result['normal_total'] - result['optimal_total_cost']
        assert abs(result['savings_vs_normal'] - expected_savings) < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
