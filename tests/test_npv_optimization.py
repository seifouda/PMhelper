"""
Tests for NPV Optimization Module

Comprehensive tests for NPV calculation, maximization, and sensitivity analysis.
"""

import pytest
import pandas as pd
import numpy as np
from src.pmhelper.core.npv_optimization import (
    NPVOptimizer, CashFlowActivity, activities_from_cpm_with_cashflows
)


class TestCashFlowActivity:
    """Tests for CashFlowActivity dataclass"""
    
    def test_create_activity(self):
        """Test creating a cash flow activity"""
        activity = CashFlowActivity(
            id='A',
            duration=5,
            cash_flow=10000,
            es=0, ef=5, ls=0, lf=5,
            float=0,
            predecessors=[],
            successors=['B']
        )
        
        assert activity.id == 'A'
        assert activity.duration == 5
        assert activity.cash_flow == 10000
        assert activity.float == 0


class TestNPVOptimizer:
    """Tests for NPVOptimizer class"""
    
    @pytest.fixture
    def simple_activities(self):
        """Create a simple set of activities for testing"""
        activities = [
            CashFlowActivity('A', 3, 10000, 0, 3, 0, 3, 0, [], ['B']),
            CashFlowActivity('B', 2, -5000, 3, 5, 3, 5, 0, ['A'], ['C']),
            CashFlowActivity('C', 4, 15000, 5, 9, 7, 11, 2, ['B'], [])
        ]
        return activities
    
    @pytest.fixture
    def optimizer(self, simple_activities):
        """Create NPV optimizer for testing"""
        return NPVOptimizer(simple_activities, discount_rate=0.10)
    
    def test_initialization(self, optimizer):
        """Test NPV optimizer initialization"""
        assert len(optimizer.activities) == 3
        assert optimizer.discount_rate == 0.10
        assert 'A' in optimizer.activities
        assert 'B' in optimizer.activities
        assert 'C' in optimizer.activities
    
    def test_calculate_npv_early_schedule(self, optimizer):
        """Test NPV calculation for early start schedule"""
        schedule = {'A': 0, 'B': 3, 'C': 5}
        npv = optimizer.calculate_npv(schedule)
        
        # Manual calculation:
        # A: 10000 / (1.1^3) = 7513.15
        # B: -5000 / (1.1^5) = -3104.61
        # C: 15000 / (1.1^9) = 6360.23
        # Total ≈ 10768.77
        
        assert npv > 0
        assert abs(npv - 10768.77) < 2  # Allow small rounding difference
    
    def test_calculate_npv_late_schedule(self, optimizer):
        """Test NPV calculation for late start schedule"""
        schedule = {'A': 0, 'B': 3, 'C': 7}
        npv = optimizer.calculate_npv(schedule)
        
        # C finishes at 11 instead of 9, more discounting
        # Should be less than early schedule NPV
        early_npv = optimizer.calculate_npv({'A': 0, 'B': 3, 'C': 5})
        
        # Late schedule should have lower NPV for positive cash flow
        assert npv < early_npv
    
    def test_maximize_npv_simple(self, optimizer):
        """Test NPV maximization on simple project"""
        result = optimizer.maximize_npv()
        
        assert 'optimal_schedule' in result
        assert 'optimal_npv' in result
        assert 'original_npv' in result
        assert 'improvement' in result
        assert 'iterations' in result
        
        # Optimal NPV should be >= original
        assert result['optimal_npv'] >= result['original_npv']
    
    def test_maximize_npv_positive_cashflow_early(self):
        """Test that positive cash flows are scheduled early"""
        activities = [
            CashFlowActivity('A', 2, 20000, 0, 2, 0, 2, 0, [], ['B']),
            CashFlowActivity('B', 3, 30000, 2, 5, 4, 7, 2, ['A'], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.12)
        result = optimizer.maximize_npv()
        
        # B has positive cash flow and 2 days float
        # Should be scheduled early (at ES=2) for max NPV
        assert result['optimal_schedule']['B'] == 2  # Early start
    
    def test_maximize_npv_negative_cashflow_late(self):
        """Test that negative cash flows are scheduled late"""
        activities = [
            CashFlowActivity('A', 2, 10000, 0, 2, 0, 2, 0, [], ['B']),
            CashFlowActivity('B', 3, -8000, 2, 5, 4, 7, 2, ['A'], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.12)
        result = optimizer.maximize_npv()
        
        # B has negative cash flow and 2 days float
        # Should be scheduled late (at LS=4) to minimize impact
        assert result['optimal_schedule']['B'] == 4  # Late start
    
    def test_no_improvement_all_critical(self):
        """Test no improvement when all activities are critical"""
        activities = [
            CashFlowActivity('A', 3, 10000, 0, 3, 0, 3, 0, [], ['B']),
            CashFlowActivity('B', 2, 5000, 3, 5, 3, 5, 0, ['A'], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.10)
        result = optimizer.maximize_npv()
        
        # No float = no room for optimization
        assert result['improvement'] == 0
        assert result['improvement_pct'] == 0
    
    def test_sensitivity_analysis(self, optimizer):
        """Test discount rate sensitivity analysis"""
        rates = [0.05, 0.10, 0.15]
        sensitivity = optimizer.sensitivity_analysis(rates)
        
        assert isinstance(sensitivity, pd.DataFrame)
        assert len(sensitivity) == 3
        assert 'discount_rate' in sensitivity.columns
        assert 'npv_original' in sensitivity.columns
        assert 'npv_optimal' in sensitivity.columns
        assert 'improvement' in sensitivity.columns
        
        # NPV should decrease as discount rate increases
        assert sensitivity.iloc[0]['npv_original'] > sensitivity.iloc[2]['npv_original']
    
    def test_sensitivity_analysis_restores_rate(self, optimizer):
        """Test that sensitivity analysis restores original discount rate"""
        original_rate = optimizer.discount_rate
        
        rates = [0.08, 0.12, 0.16]
        optimizer.sensitivity_analysis(rates)
        
        assert optimizer.discount_rate == original_rate
    
    def test_get_cash_flow_schedule(self, optimizer):
        """Test getting detailed cash flow schedule"""
        schedule = {'A': 0, 'B': 3, 'C': 5}
        cf_schedule = optimizer.get_cash_flow_schedule(schedule)
        
        assert isinstance(cf_schedule, pd.DataFrame)
        assert 'time' in cf_schedule.columns
        assert 'activity' in cf_schedule.columns
        assert 'cash_flow' in cf_schedule.columns
        assert 'discounted_value' in cf_schedule.columns
        assert 'discount_factor' in cf_schedule.columns
        
        # Should have 3 cash flows
        assert len(cf_schedule) == 3
    
    def test_check_precedence_valid(self, optimizer):
        """Test precedence checking with valid schedule"""
        schedule = {'A': 0, 'B': 3, 'C': 5}
        activity_c = optimizer.activities['C']
        
        # C starts at 5, B finishes at 5, valid
        assert optimizer._check_precedence(schedule, activity_c)
    
    def test_check_precedence_invalid(self, optimizer):
        """Test precedence checking with invalid schedule"""
        schedule = {'A': 0, 'B': 3, 'C': 4}  # C starts before B finishes!
        activity_c = optimizer.activities['C']
        
        # Invalid precedence
        assert not optimizer._check_precedence(schedule, activity_c)
    
    def test_moved_activities_tracking(self):
        """Test that moved activities are tracked in results"""
        activities = [
            CashFlowActivity('A', 2, 5000, 0, 2, 0, 2, 0, [], ['B']),
            CashFlowActivity('B', 3, 10000, 2, 5, 3, 6, 1, ['A'], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.10)
        result = optimizer.maximize_npv()
        
        if result['improvement'] > 0:
            assert 'moved_activities' in result
            assert len(result['moved_activities']) > 0
    
    def test_zero_cash_flows(self):
        """Test handling of activities with zero cash flows"""
        activities = [
            CashFlowActivity('A', 3, 0, 0, 3, 0, 3, 0, [], ['B']),
            CashFlowActivity('B', 2, 0, 3, 5, 3, 5, 0, ['A'], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.10)
        schedule = {'A': 0, 'B': 3}
        npv = optimizer.calculate_npv(schedule)
        
        assert npv == 0
    
    def test_high_discount_rate(self):
        """Test with very high discount rate"""
        activities = [
            CashFlowActivity('A', 5, 10000, 0, 5, 0, 5, 0, [], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.50)  # 50%!
        schedule = {'A': 0}
        npv = optimizer.calculate_npv(schedule)
        
        # High discounting should reduce NPV significantly
        # 10000 / (1.5^5) = 1316.87
        assert npv < 10000
        assert abs(npv - 1316.87) < 1
    
    def test_negative_npv_project(self):
        """Test project with negative overall NPV"""
        activities = [
            CashFlowActivity('A', 3, -15000, 0, 3, 0, 3, 0, [], ['B']),
            CashFlowActivity('B', 2, 5000, 3, 5, 3, 5, 0, ['A'], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.10)
        schedule = {'A': 0, 'B': 3}
        npv = optimizer.calculate_npv(schedule)
        
        assert npv < 0  # Negative NPV project


class TestActivitiesFromCPMWithCashflows:
    """Tests for CPM integration function"""
    
    @pytest.fixture
    def mock_cpm_analyzer(self):
        """Create mock CPM analyzer with graph"""
        import networkx as nx
        
        class MockCPM:
            def __init__(self):
                self.G = nx.DiGraph()
                
                # Add nodes with CPM data
                self.G.add_node('A', duration=3, ES=0, EF=3, LS=0, LF=3, float=0)
                self.G.add_node('B', duration=2, ES=3, EF=5, LS=4, LF=6, float=1)
                self.G.add_node('C', duration=4, ES=5, EF=9, LS=6, LF=10, float=1)
                
                # Add edges (precedence)
                self.G.add_edge('Start', 'A')
                self.G.add_edge('A', 'B')
                self.G.add_edge('B', 'C')
                self.G.add_edge('C', 'End')
        
        return MockCPM()
    
    def test_activities_from_cpm(self, mock_cpm_analyzer):
        """Test converting CPM results to CashFlowActivity objects"""
        cash_flows = {'A': 10000, 'B': -5000, 'C': 15000}
        
        activities = activities_from_cpm_with_cashflows(mock_cpm_analyzer, cash_flows)
        
        assert len(activities) == 3
        
        # Check activity A
        act_a = next(a for a in activities if a.id == 'A')
        assert act_a.duration == 3
        assert act_a.cash_flow == 10000
        assert act_a.es == 0
        assert act_a.float == 0
    
    def test_missing_cash_flows(self, mock_cpm_analyzer):
        """Test with missing cash flow data (should default to 0)"""
        cash_flows = {'A': 10000}  # Only A has cash flow
        
        activities = activities_from_cpm_with_cashflows(mock_cpm_analyzer, cash_flows)
        
        act_b = next(a for a in activities if a.id == 'B')
        assert act_b.cash_flow == 0.0
    
    def test_no_cpm_analysis_error(self):
        """Test error when CPM analysis hasn't been performed"""
        class MockCPMNoAnalysis:
            G = None
        
        cpm = MockCPMNoAnalysis()
        
        with pytest.raises(ValueError, match="CPM analysis must be performed first"):
            activities_from_cpm_with_cashflows(cpm, {})
    
    def test_predecessors_successors_extracted(self, mock_cpm_analyzer):
        """Test that predecessors and successors are correctly extracted"""
        cash_flows = {'A': 10000, 'B': -5000, 'C': 15000}
        
        activities = activities_from_cpm_with_cashflows(mock_cpm_analyzer, cash_flows)
        
        act_b = next(a for a in activities if a.id == 'B')
        assert 'A' in act_b.predecessors
        assert 'C' in act_b.successors


class TestNPVEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_empty_schedule(self):
        """Test with empty schedule"""
        activities = [
            CashFlowActivity('A', 3, 10000, 0, 3, 0, 3, 0, [], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.10)
        npv = optimizer.calculate_npv({})
        
        assert npv == 0
    
    def test_max_iterations_limit(self):
        """Test that max iterations limit is respected"""
        activities = [
            CashFlowActivity('A', 2, 10000, 0, 2, 0, 2, 0, [], ['B']),
            CashFlowActivity('B', 3, 5000, 2, 5, 2, 10, 5, ['A'], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.10)
        result = optimizer.maximize_npv(max_iterations=10)
        
        # Should complete within 10 iterations
        assert result['iterations'] <= 10
    
    def test_single_activity_project(self):
        """Test with single activity"""
        activities = [
            CashFlowActivity('A', 5, 10000, 0, 5, 0, 5, 0, [], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.10)
        result = optimizer.maximize_npv()
        
        # No optimization possible
        assert result['improvement'] == 0
    
    def test_very_large_project_duration(self):
        """Test with long project duration"""
        activities = [
            CashFlowActivity('A', 100, 100000, 0, 100, 0, 100, 0, [], [])
        ]
        
        optimizer = NPVOptimizer(activities, discount_rate=0.10)
        schedule = {'A': 0}
        npv = optimizer.calculate_npv(schedule)
        
        # Heavy discounting over 100 periods
        # 100000 / (1.1^100) should be very small
        assert npv > 0
        assert npv < 1000  # Heavily discounted
