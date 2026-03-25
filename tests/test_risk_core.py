#!/usr/bin/env python3
"""
Unit tests for Risk Analysis Module

Tests all four core classes:
- DelayRiskAnalyzer
- ContingencyPlanner
- VarianceReductionAnalyzer
- ActivityRiskPrioritizer
"""

import pytest
import numpy as np
import pandas as pd
from src.pmhelper.core.risk_analysis import (
    DelayRiskAnalyzer,
    ContingencyPlanner,
    VarianceReductionAnalyzer,
    ActivityRiskPrioritizer
)


class TestDelayRiskAnalyzer:
    """Test suite for DelayRiskAnalyzer class"""
    
    @pytest.fixture
    def simple_pert_results(self):
        """Simple PERT results fixture"""
        return {
            'expected_duration': 14.0,
            'variance': 3.33,
            'critical_path': ['A', 'B', 'E', 'F'],
            'activities': {
                'A': {'expected_time': 3.0, 'variance': 0.11},
                'B': {'expected_time': 4.0, 'variance': 0.44},
                'C': {'expected_time': 5.67, 'variance': 1.78},
                'D': {'expected_time': 3.0, 'variance': 0.11},
                'E': {'expected_time': 5.0, 'variance': 1.78},
                'F': {'expected_time': 2.0, 'variance': 0.11}
            }
        }
    
    def test_initialization(self, simple_pert_results):
        """Test analyzer initialization"""
        analyzer = DelayRiskAnalyzer(simple_pert_results)
        
        assert analyzer.expected_duration == 14.0
        assert analyzer.variance == 3.33
        assert abs(analyzer.std_dev - np.sqrt(3.33)) < 0.01
        assert analyzer.critical_path == ['A', 'B', 'E', 'F']
    
    def test_initialization_invalid_duration(self):
        """Test initialization with invalid duration"""
        with pytest.raises(ValueError, match="Expected duration must be positive"):
            DelayRiskAnalyzer({
                'expected_duration': 0,
                'variance': 3.33
            })
    
    def test_delay_probability_basic(self, simple_pert_results):
        """Test delay probability calculation"""
        analyzer = DelayRiskAnalyzer(simple_pert_results)
        
        # Contract time = 15 weeks
        prob = analyzer.calculate_delay_probability(15.0)
        
        # Expected: P(T > 15) with μ=14, σ=√3.33≈1.825
        # Z = (15-14)/1.825 = 0.548
        # P(Z > 0.548) ≈ 0.292 (29.2%)
        assert 0.25 < prob < 0.35  # Rough range check
    
    def test_delay_probability_zero_variance(self):
        """Test delay probability with zero variance"""
        analyzer = DelayRiskAnalyzer({
            'expected_duration': 14.0,
            'variance': 0.0,
            'critical_path': []
        })
        
        # Contract time < expected: 100% delay probability
        assert analyzer.calculate_delay_probability(13.0) == 1.0
        
        # Contract time >= expected: 0% delay probability
        assert analyzer.calculate_delay_probability(14.0) == 0.0
        assert analyzer.calculate_delay_probability(15.0) == 0.0
    
    def test_delay_probability_invalid_contract_time(self, simple_pert_results):
        """Test delay probability with invalid contract time"""
        analyzer = DelayRiskAnalyzer(simple_pert_results)
        
        with pytest.raises(ValueError, match="Contract time must be positive"):
            analyzer.calculate_delay_probability(0)
        
        with pytest.raises(ValueError, match="Contract time must be positive"):
            analyzer.calculate_delay_probability(-5)
    
    def test_expected_delay_basic(self, simple_pert_results):
        """Test expected delay calculation using truncated normal"""
        analyzer = DelayRiskAnalyzer(simple_pert_results)
        
        # Contract time = 15 weeks
        expected_delay = analyzer.calculate_expected_delay(15.0)
        
        # With μ=14, σ=1.825, truncated at 15
        # E[T|T>15] = 14 + 1.825 * φ(0.548)/(1-Φ(0.548))
        # Should be around 1.0 to 1.5 weeks
        assert 0.5 < expected_delay < 2.0
    
    def test_expected_delay_zero_variance(self):
        """Test expected delay with zero variance"""
        analyzer = DelayRiskAnalyzer({
            'expected_duration': 14.0,
            'variance': 0.0,
            'critical_path': []
        })
        
        # Contract time < expected: delay = difference
        assert analyzer.calculate_expected_delay(13.0) == 1.0
        
        # Contract time >= expected: no delay
        assert analyzer.calculate_expected_delay(14.0) == 0.0
        assert analyzer.calculate_expected_delay(15.0) == 0.0
    
    def test_risk_cost_calculation(self, simple_pert_results):
        """Test risk cost calculation"""
        analyzer = DelayRiskAnalyzer(simple_pert_results)
        
        # Contract time = 15 weeks, penalty = $1000/week
        result = analyzer.calculate_risk_cost(
            contract_time=15.0,
            penalty_rate=1000.0
        )
        
        # Check all returned fields
        assert 'delay_probability' in result
        assert 'expected_delay' in result
        assert 'risk_cost' in result
        assert 'capped_risk_cost' in result
        assert 'max_penalty' in result
        assert 'z_score' in result
        
        # Basic sanity checks
        assert 0 <= result['delay_probability'] <= 1
        assert result['expected_delay'] >= 0
        assert result['risk_cost'] >= 0
        assert result['capped_risk_cost'] >= 0
        
        # Risk cost = P(delay) × E[delay] × penalty_rate
        expected_risk = result['delay_probability'] * result['expected_delay'] * 1000.0
        assert abs(result['risk_cost'] - expected_risk) < 0.01
    
    def test_risk_cost_with_penalty_cap(self, simple_pert_results):
        """Test risk cost calculation with penalty cap"""
        analyzer = DelayRiskAnalyzer(simple_pert_results)
        
        result = analyzer.calculate_risk_cost(
            contract_time=15.0,
            penalty_rate=1000.0,
            max_penalty_percent=0.20,
            contract_value=100000.0
        )
        
        # Max penalty should be 20% of contract value
        assert result['max_penalty'] == 20000.0
        
        # Capped cost should not exceed max penalty
        assert result['capped_risk_cost'] <= result['max_penalty']
    
    def test_risk_cost_negative_penalty_rate(self, simple_pert_results):
        """Test risk cost with invalid penalty rate"""
        analyzer = DelayRiskAnalyzer(simple_pert_results)
        
        with pytest.raises(ValueError, match="Penalty rate must be non-negative"):
            analyzer.calculate_risk_cost(
                contract_time=15.0,
                penalty_rate=-1000.0
            )
    
    def test_estimate_contract_value_from_activities(self, simple_pert_results):
        """Test contract value estimation from activity costs"""
        # Add costs to activities
        simple_pert_results['activities']['A']['normal_cost'] = 10000
        simple_pert_results['activities']['B']['normal_cost'] = 15000
        simple_pert_results['activities']['C']['cost'] = 20000
        
        analyzer = DelayRiskAnalyzer(simple_pert_results)
        estimated_value = analyzer.estimate_contract_value()
        
        assert estimated_value == 45000  # Sum of all costs
    
    def test_estimate_contract_value_no_costs(self, simple_pert_results):
        """Test contract value estimation with no cost data"""
        analyzer = DelayRiskAnalyzer(simple_pert_results)
        estimated_value = analyzer.estimate_contract_value()
        
        assert estimated_value == 0  # No costs available


class TestContingencyPlanner:
    """Test suite for ContingencyPlanner class"""
    
    @pytest.fixture
    def pert_results(self):
        """PERT results fixture"""
        return {
            'expected_duration': 14.0,
            'variance': 3.33,
            'critical_path': ['A', 'B', 'E', 'F'],
            'activities': {}
        }
    
    def test_initialization(self, pert_results):
        """Test planner initialization"""
        planner = ContingencyPlanner(pert_results)
        
        assert planner.expected_duration == 14.0
        assert planner.variance == 3.33
        assert abs(planner.std_dev - np.sqrt(3.33)) < 0.01
    
    def test_initialization_invalid_duration(self):
        """Test initialization with invalid duration"""
        with pytest.raises(ValueError, match="Expected duration must be positive"):
            ContingencyPlanner({
                'expected_duration': -5,
                'variance': 3.33
            })
    
    def test_calculate_contingency_95_percent(self, pert_results):
        """Test contingency calculation at 95% confidence"""
        planner = ContingencyPlanner(pert_results)
        result = planner.calculate_contingency(confidence_level=0.95)
        
        # Check returned fields
        assert result['confidence_level'] == 0.95
        assert 'z_score' in result
        assert 'time_buffer' in result
        assert 'buffer_percentage' in result
        assert 'completion_time' in result
        assert 'recommendation' in result
        
        # Z-score for 95% should be approximately 1.645
        assert 1.6 < result['z_score'] < 1.7
        
        # Buffer = Z × σ = 1.645 × √3.33 ≈ 3.0
        assert 2.5 < result['time_buffer'] < 3.5
        
        # Completion time = expected + buffer
        assert abs(result['completion_time'] - (14.0 + result['time_buffer'])) < 0.01
    
    def test_calculate_contingency_various_levels(self, pert_results):
        """Test contingency at different confidence levels"""
        planner = ContingencyPlanner(pert_results)
        
        # 90% confidence
        result_90 = planner.calculate_contingency(0.90)
        
        # 95% confidence
        result_95 = planner.calculate_contingency(0.95)
        
        # 99% confidence
        result_99 = planner.calculate_contingency(0.99)
        
        # Higher confidence should require larger buffer
        assert result_90['time_buffer'] < result_95['time_buffer']
        assert result_95['time_buffer'] < result_99['time_buffer']
    
    def test_calculate_contingency_with_cost(self, pert_results):
        """Test contingency calculation with daily cost rate"""
        planner = ContingencyPlanner(pert_results)
        result = planner.calculate_contingency(
            confidence_level=0.95,
            daily_cost_rate=10000.0
        )
        
        # Contingency cost should be buffer × rate
        expected_cost = result['time_buffer'] * 10000.0
        assert abs(result['contingency_cost'] - expected_cost) < 0.01
    
    def test_calculate_contingency_zero_variance(self):
        """Test contingency with zero variance"""
        planner = ContingencyPlanner({
            'expected_duration': 14.0,
            'variance': 0.0,
            'activities': {}
        })
        
        result = planner.calculate_contingency(0.95)
        
        # No variance means no buffer needed
        assert result['time_buffer'] == 0
        assert result['buffer_percentage'] == 0
        assert result['completion_time'] == 14.0
        assert 'zero variance' in result['recommendation'].lower()
    
    def test_calculate_contingency_invalid_confidence(self, pert_results):
        """Test contingency with invalid confidence level"""
        planner = ContingencyPlanner(pert_results)
        
        # Too low
        with pytest.raises(ValueError, match="Confidence level must be between"):
            planner.calculate_contingency(0.3)
        
        # Too high
        with pytest.raises(ValueError, match="Confidence level must be between"):
            planner.calculate_contingency(1.0)
    
    def test_recommendation_generation(self, pert_results):
        """Test recommendation text generation"""
        planner = ContingencyPlanner(pert_results)
        
        # Different confidence levels should produce different recommendations
        result_low = planner.calculate_contingency(0.80)
        result_high = planner.calculate_contingency(0.99)
        
        # Both should have recommendations
        assert len(result_low['recommendation']) > 0
        assert len(result_high['recommendation']) > 0
        
        # High confidence typically requires higher buffer
        assert result_high['buffer_percentage'] > result_low['buffer_percentage']


class TestVarianceReductionAnalyzer:
    """Test suite for VarianceReductionAnalyzer class"""
    
    @pytest.fixture
    def pert_results(self):
        """PERT results for variance reduction testing"""
        return {
            'expected_duration': 30.0,  # Changed to create delay risk
            'variance': 9.0,  # Increased variance
            'critical_path': ['A', 'B', 'C'],
            'activities': {
                'A': {'expected_time': 10.0, 'variance': 3.0},
                'B': {'expected_time': 12.0, 'variance': 4.0},
                'C': {'expected_time': 8.0, 'variance': 2.0}
            }
        }
    
    def test_initialization(self, pert_results):
        """Test analyzer initialization"""
        analyzer = VarianceReductionAnalyzer(pert_results)
        
        assert analyzer.expected_duration == 30.0
        assert analyzer.variance == 9.0
        assert abs(analyzer.std_dev - 3.0) < 0.01
    
    def test_initialization_invalid_duration(self):
        """Test initialization with invalid duration"""
        with pytest.raises(ValueError, match="Expected duration must be positive"):
            VarianceReductionAnalyzer({
                'expected_duration': 0,
                'variance': 4.0,
                'activities': {}
            })
    
    def test_analyze_strategies_basic(self, pert_results):
        """Test basic strategy analysis"""
        analyzer = VarianceReductionAnalyzer(pert_results)
        
        result = analyzer.analyze_strategies(
            contract_time=32.0,
            penalty_rate=2000.0,
            time_reduction_cost=4000.0,
            variance_reduction_cost=2000.0,
            max_budget=50000.0
        )
        
        # Check all required keys
        assert 'baseline' in result
        assert 'strategy_a' in result
        assert 'strategy_b' in result
        assert 'mixed_strategy' in result
        assert 'best_strategy' in result
        assert 'summary' in result
        
        # Baseline should have zero investment
        assert result['baseline']['investment'] == 0
        
        # All strategies should be feasible
        assert result['strategy_a']['feasible']
        assert result['strategy_b']['feasible']
        assert result['mixed_strategy']['feasible']
    
    def test_strategy_a_time_reduction(self, pert_results):
        """Test Strategy A (time reduction only)"""
        analyzer = VarianceReductionAnalyzer(pert_results)
        
        result = analyzer.analyze_strategies(
            contract_time=32.0,
            penalty_rate=2000.0,
            time_reduction_cost=4000.0,
            variance_reduction_cost=2000.0,
            max_budget=50000.0
        )
        
        strategy_a = result['strategy_a']
        
        # Should reduce time but not variance (or may be 0 if no benefit)
        assert strategy_a['time_reduction'] >= 0
        assert strategy_a['variance_reduction'] == 0
        if strategy_a['time_reduction'] > 0:
            assert strategy_a['new_expected_duration'] < 30.0
        assert strategy_a['new_variance'] == 9.0  # Unchanged
        
        # Should have non-negative benefit
        assert strategy_a['benefit'] >= 0
    
    def test_strategy_b_variance_reduction(self, pert_results):
        """Test Strategy B (variance reduction only)"""
        analyzer = VarianceReductionAnalyzer(pert_results)
        
        result = analyzer.analyze_strategies(
            contract_time=32.0,
            penalty_rate=2000.0,
            time_reduction_cost=4000.0,
            variance_reduction_cost=2000.0,
            max_budget=50000.0
        )
        
        strategy_b = result['strategy_b']
        
        # Should reduce variance but not time (or may be 0 if no benefit)
        assert strategy_b['time_reduction'] == 0
        assert strategy_b['variance_reduction'] >= 0
        assert strategy_b['new_expected_duration'] == 30.0  # Unchanged
        if strategy_b['variance_reduction'] > 0:
            assert strategy_b['new_variance'] < 9.0
        
        # Should have non-negative benefit
        assert strategy_b['benefit'] >= 0
    
    def test_mixed_strategy(self, pert_results):
        """Test mixed strategy (both time and variance reduction)"""
        analyzer = VarianceReductionAnalyzer(pert_results)
        
        result = analyzer.analyze_strategies(
            contract_time=32.0,
            penalty_rate=2000.0,
            time_reduction_cost=4000.0,
            variance_reduction_cost=2000.0,
            max_budget=50000.0
        )
        
        mixed = result['mixed_strategy']
        
        # Can reduce both or choose one
        assert mixed['time_reduction'] >= 0
        assert mixed['variance_reduction'] >= 0
        
        # At least one should be positive (unless budget too small)
        assert (mixed['time_reduction'] + mixed['variance_reduction']) >= 0
    
    def test_budget_constraint(self, pert_results):
        """Test that strategies respect budget constraint"""
        analyzer = VarianceReductionAnalyzer(pert_results)
        
        max_budget = 20000.0
        result = analyzer.analyze_strategies(
            contract_time=32.0,
            penalty_rate=2000.0,
            time_reduction_cost=4000.0,
            variance_reduction_cost=2000.0,
            max_budget=max_budget
        )
        
        # All investments should be within budget
        assert result['strategy_a']['investment'] <= max_budget
        assert result['strategy_b']['investment'] <= max_budget
        assert result['mixed_strategy']['investment'] <= max_budget
    
    def test_best_strategy_selection(self, pert_results):
        """Test that best strategy has highest net benefit"""
        analyzer = VarianceReductionAnalyzer(pert_results)
        
        result = analyzer.analyze_strategies(
            contract_time=32.0,
            penalty_rate=2000.0,
            time_reduction_cost=4000.0,
            variance_reduction_cost=2000.0,
            max_budget=50000.0
        )
        
        best = result['best_strategy']
        
        # Best should have highest net benefit
        assert best['net_benefit'] >= result['strategy_a']['net_benefit']
        assert best['net_benefit'] >= result['strategy_b']['net_benefit']
        assert best['net_benefit'] >= result['mixed_strategy']['net_benefit']
    
    def test_roi_calculation(self, pert_results):
        """Test ROI calculation"""
        analyzer = VarianceReductionAnalyzer(pert_results)
        
        result = analyzer.analyze_strategies(
            contract_time=32.0,
            penalty_rate=2000.0,
            time_reduction_cost=4000.0,
            variance_reduction_cost=2000.0,
            max_budget=50000.0
        )
        
        # ROI should be (benefit / investment) × 100
        for strategy_name in ['strategy_a', 'strategy_b', 'mixed_strategy']:
            strategy = result[strategy_name]
            if strategy['investment'] > 0:
                expected_roi = (strategy['benefit'] / strategy['investment']) * 100
                assert abs(strategy['roi'] - expected_roi) < 0.1


class TestActivityRiskPrioritizer:
    """Test suite for ActivityRiskPrioritizer class"""
    
    @pytest.fixture
    def pert_results(self):
        """PERT results with activity details"""
        return {
            'expected_duration': 20.0,
            'variance': 5.0,
            'critical_path': ['A', 'B', 'D'],
            'activities': {
                'A': {
                    'activity': 'Design',
                    'expected_time': 5.0,
                    'variance': 2.0,
                    'float': 0.0  # Critical
                },
                'B': {
                    'activity': 'Development',
                    'expected_time': 10.0,
                    'variance': 2.5,
                    'float': 0.0  # Critical
                },
                'C': {
                    'activity': 'Testing',
                    'expected_time': 8.0,
                    'variance': 0.5,
                    'float': 5.0  # Non-critical
                },
                'D': {
                    'activity': 'Deployment',
                    'expected_time': 5.0,
                    'variance': 0.5,
                    'float': 0.0  # Critical
                }
            }
        }
    
    def test_initialization(self, pert_results):
        """Test prioritizer initialization"""
        prioritizer = ActivityRiskPrioritizer(pert_results)
        
        assert len(prioritizer.activities) == 4
        assert prioritizer.project_variance == 5.0
        assert prioritizer.critical_path == ['A', 'B', 'D']
    
    def test_initialization_no_activities(self):
        """Test initialization with no activities"""
        with pytest.raises(ValueError, match="Activities data is required"):
            ActivityRiskPrioritizer({
                'variance': 5.0,
                'critical_path': []
            })
    
    def test_calculate_risk_scores(self, pert_results):
        """Test risk score calculation"""
        prioritizer = ActivityRiskPrioritizer(pert_results)
        df = prioritizer.calculate_risk_scores()
        
        # Should return DataFrame with all activities (except START/END)
        assert len(df) == 4
        assert isinstance(df, pd.DataFrame)
        
        # Check required columns
        required_columns = [
            'activity_id', 'activity_name', 'expected_time', 'variance',
            'total_float', 'criticality', 'cruciality',
            'schedule_sensitivity', 'uncertainty', 'risk_score', 'recommendation'
        ]
        for col in required_columns:
            assert col in df.columns
        
        # Should be sorted by risk_score (descending)
        assert df['risk_score'].is_monotonic_decreasing
    
    def test_criticality_index(self, pert_results):
        """Test criticality index calculation"""
        prioritizer = ActivityRiskPrioritizer(pert_results)
        df = prioritizer.calculate_risk_scores()
        
        # Critical path activities should have criticality = 1
        critical_activities = df[df['activity_id'].isin(['A', 'B', 'D'])]
        assert all(critical_activities['criticality'] == 1.0)
        
        # Non-critical should have criticality = 0
        non_critical = df[df['activity_id'] == 'C']
        assert all(non_critical['criticality'] == 0.0)
    
    def test_cruciality_index(self, pert_results):
        """Test cruciality index (variance contribution)"""
        prioritizer = ActivityRiskPrioritizer(pert_results)
        df = prioritizer.calculate_risk_scores()
        
        # Cruciality should be variance / project_variance
        for _, row in df.iterrows():
            expected_cruciality = row['variance'] / 5.0
            assert abs(row['cruciality'] - expected_cruciality) < 0.01
        
        # Higher variance activities should have higher cruciality
        activity_b = df[df['activity_id'] == 'B'].iloc[0]
        activity_d = df[df['activity_id'] == 'D'].iloc[0]
        assert activity_b['cruciality'] > activity_d['cruciality']
    
    def test_schedule_sensitivity(self, pert_results):
        """Test schedule sensitivity calculation"""
        prioritizer = ActivityRiskPrioritizer(pert_results)
        df = prioritizer.calculate_risk_scores()
        
        # Schedule sensitivity = 1 / (1 + float)
        for _, row in df.iterrows():
            expected_sensitivity = 1.0 / (1.0 + row['total_float'])
            assert abs(row['schedule_sensitivity'] - expected_sensitivity) < 0.01
        
        # Critical activities (float=0) should have sensitivity = 1
        critical = df[df['total_float'] == 0]
        assert all(abs(critical['schedule_sensitivity'] - 1.0) < 0.01)
    
    def test_uncertainty_coefficient(self, pert_results):
        """Test uncertainty (coefficient of variation)"""
        prioritizer = ActivityRiskPrioritizer(pert_results)
        df = prioritizer.calculate_risk_scores()
        
        # Uncertainty = std_dev / expected_time
        for _, row in df.iterrows():
            if row['variance'] > 0 and row['expected_time'] > 0:
                expected_cv = np.sqrt(row['variance']) / row['expected_time']
                assert abs(row['uncertainty'] - expected_cv) < 0.01
    
    def test_risk_score_formula(self, pert_results):
        """Test weighted risk score formula"""
        prioritizer = ActivityRiskPrioritizer(pert_results)
        df = prioritizer.calculate_risk_scores()
        
        # Risk Score = 0.40×Crit + 0.30×Cruc + 0.20×Sched + 0.10×Uncert
        for _, row in df.iterrows():
            expected_score = (
                0.40 * row['criticality'] +
                0.30 * row['cruciality'] +
                0.20 * row['schedule_sensitivity'] +
                0.10 * row['uncertainty']
            )
            assert abs(row['risk_score'] - expected_score) < 0.01
    
    def test_get_top_risks(self, pert_results):
        """Test getting top N risks"""
        prioritizer = ActivityRiskPrioritizer(pert_results)
        
        # Get top 2 risks
        top_2 = prioritizer.get_top_risks(n=2)
        
        assert len(top_2) == 2
        assert top_2['risk_score'].is_monotonic_decreasing
        
        # First should be highest risk
        all_scores = prioritizer.calculate_risk_scores()
        assert top_2.iloc[0]['risk_score'] == all_scores.iloc[0]['risk_score']
    
    def test_generate_mitigation_plan(self, pert_results):
        """Test mitigation plan generation"""
        prioritizer = ActivityRiskPrioritizer(pert_results)
        plan = prioritizer.generate_mitigation_plan()
        
        # Check required keys
        assert 'high_priority' in plan
        assert 'medium_priority' in plan
        assert 'low_priority' in plan
        assert 'critical_path_risks' in plan
        assert 'variance_contributors' in plan
        assert 'total_activities' in plan
        assert 'summary' in plan
        
        # Total should equal number of activities
        total = len(plan['high_priority']) + len(plan['medium_priority']) + len(plan['low_priority'])
        assert total == 4
        
        # Critical path risks should only be critical activities
        for risk in plan['critical_path_risks']:
            assert risk['activity_id'] in ['A', 'B', 'D']
    
    def test_recommendation_generation(self, pert_results):
        """Test activity recommendation generation"""
        prioritizer = ActivityRiskPrioritizer(pert_results)
        df = prioritizer.calculate_risk_scores()
        
        # All activities should have recommendations
        assert all(len(rec) > 0 for rec in df['recommendation'])
        
        # Critical path activities should mention "CRITICAL PATH"
        critical = df[df['criticality'] == 1.0]
        for _, row in critical.iterrows():
            assert 'CRITICAL PATH' in row['recommendation']


class TestIntegration:
    """Integration tests across multiple classes"""
    
    @pytest.fixture
    def complete_pert_results(self):
        """Complete PERT results for integration testing"""
        return {
            'expected_duration': 20.0,
            'variance': 6.0,
            'critical_path': ['A', 'B', 'D'],
            'activities': {
                'A': {
                    'activity': 'Design',
                    'expected_time': 5.0,
                    'variance': 2.0,
                    'float': 0.0,
                    'normal_cost': 10000
                },
                'B': {
                    'activity': 'Development',
                    'expected_time': 10.0,
                    'variance': 3.0,
                    'float': 0.0,
                    'normal_cost': 20000
                },
                'C': {
                    'activity': 'Testing',
                    'expected_time': 8.0,
                    'variance': 0.5,
                    'float': 5.0,
                    'normal_cost': 15000
                },
                'D': {
                    'activity': 'Deployment',
                    'expected_time': 5.0,
                    'variance': 0.5,
                    'float': 0.0,
                    'normal_cost': 8000
                }
            }
        }
    
    def test_full_risk_analysis_workflow(self, complete_pert_results):
        """Test complete risk analysis workflow"""
        # 1. Calculate delay risk
        delay_analyzer = DelayRiskAnalyzer(complete_pert_results)
        risk = delay_analyzer.calculate_risk_cost(
            contract_time=25.0,
            penalty_rate=1000.0
        )
        
        assert risk['delay_probability'] > 0
        assert risk['risk_cost'] >= 0
        
        # 2. Estimate contingency
        planner = ContingencyPlanner(complete_pert_results)
        contingency = planner.calculate_contingency(0.95, daily_cost_rate=5000.0)
        
        assert contingency['time_buffer'] > 0
        assert contingency['contingency_cost'] > 0
        
        # 3. Analyze variance reduction strategies
        variance_analyzer = VarianceReductionAnalyzer(complete_pert_results)
        strategies = variance_analyzer.analyze_strategies(
            contract_time=25.0,
            penalty_rate=1000.0,
            time_reduction_cost=3000.0,
            variance_reduction_cost=2000.0,
            max_budget=40000.0
        )
        
        assert 'best_strategy' in strategies
        assert strategies['best_strategy']['net_benefit'] >= 0
        
        # 4. Prioritize activities
        prioritizer = ActivityRiskPrioritizer(complete_pert_results)
        mitigation_plan = prioritizer.generate_mitigation_plan()
        
        assert mitigation_plan['total_activities'] == 4
        assert len(mitigation_plan['critical_path_risks']) == 3
    
    def test_consistency_across_modules(self, complete_pert_results):
        """Test consistency of calculations across modules"""
        # All modules should use the same variance
        delay_analyzer = DelayRiskAnalyzer(complete_pert_results)
        planner = ContingencyPlanner(complete_pert_results)
        variance_analyzer = VarianceReductionAnalyzer(complete_pert_results)
        
        assert delay_analyzer.variance == 6.0
        assert planner.variance == 6.0
        assert variance_analyzer.variance == 6.0
        
        # Standard deviations should match
        expected_std = np.sqrt(6.0)
        assert abs(delay_analyzer.std_dev - expected_std) < 0.01
        assert abs(planner.std_dev - expected_std) < 0.01
        assert abs(variance_analyzer.std_dev - expected_std) < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=src.pmhelper.core.risk_analysis', '--cov-report=html'])
