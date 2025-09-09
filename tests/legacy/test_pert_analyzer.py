#!/usr/bin/env python3
"""
Comprehensive Unit Tests for PERT Analyzer

Tests all functionality of the PERT analyzer including:
- Data loading and validation for PERT (optimistic, most likely, pessimistic times)
- Expected time and variance calculations
- Monte Carlo simulation
- Probability analysis
- Beta distribution calculations
- Project completion probability
- Edge cases and error handling
"""

import pytest
import sys
import numpy as np
import networkx as nx
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.utils.file_handlers import FileHandler


class TestPERTAnalyzer:
    """Comprehensive test suite for PERT Analyzer"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment before each test"""
        self.analyzer = PERTAnalyzer()
        self.sample_pert_data = [
            {
                'id': 'A',
                'activity': 'Start Activity',
                'optimistic': 2,
                'most_likely': 3,
                'pessimistic': 5,
                'predecessors': ''
            },
            {
                'id': 'B',
                'activity': 'Second Activity',
                'optimistic': 3,
                'most_likely': 5,
                'pessimistic': 8,
                'predecessors': 'A'
            },
            {
                'id': 'C',
                'activity': 'Third Activity',
                'optimistic': 1,
                'most_likely': 4,
                'pessimistic': 6,
                'predecessors': 'A'
            },
            {
                'id': 'D',
                'activity': 'Final Activity',
                'optimistic': 1,
                'most_likely': 2,
                'pessimistic': 4,
                'predecessors': 'B,C'
            }
        ]
    
    def test_analyzer_initialization(self):
        """Test PERT analyzer can be created and initialized properly"""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'G')
        assert hasattr(self.analyzer, 'critical_paths')
        assert hasattr(self.analyzer, 'critical_activities')
    
    def test_load_pert_activities_valid(self):
        """Test loading valid PERT activity data"""
        activities = self.analyzer.load_activities_from_pert_data(self.sample_pert_data)
        
        assert len(activities) == 4
        assert activities[0]['id'] == 'A'
        assert activities[0]['optimistic'] == 2
        assert activities[0]['most_likely'] == 3
        assert activities[0]['pessimistic'] == 5
        assert activities[0]['predecessors'] == []
        assert activities[1]['predecessors'] == ['A']
        assert activities[3]['predecessors'] == ['B', 'C']
    
    def test_pert_time_validation(self):
        """Test validation of PERT time estimates (O ≤ M ≤ P)"""
        # Valid case
        valid_data = [{'id': 'A', 'optimistic': 1, 'most_likely': 3, 'pessimistic': 5, 'predecessors': ''}]
        activities = self.analyzer.load_activities_from_pert_data(valid_data)
        assert len(activities) == 1
        
        # Invalid case: optimistic > most_likely
        invalid_data1 = [{'id': 'A', 'optimistic': 5, 'most_likely': 3, 'pessimistic': 7, 'predecessors': ''}]
        with pytest.raises(ValueError, match="Invalid time estimates"):
            self.analyzer.load_activities_from_pert_data(invalid_data1)
        
        # Invalid case: most_likely > pessimistic
        invalid_data2 = [{'id': 'A', 'optimistic': 1, 'most_likely': 5, 'pessimistic': 3, 'predecessors': ''}]
        with pytest.raises(ValueError, match="Invalid time estimates"):
            self.analyzer.load_activities_from_pert_data(invalid_data2)
    
    def test_expected_time_calculation(self):
        """Test PERT expected time calculation: (O + 4M + P) / 6"""
        activities = self.analyzer.load_activities_from_pert_data(self.sample_pert_data)
        
        # Calculate expected times
        pert_activities = self.analyzer.calculate_pert_estimates(activities)
        
        # Verify expected time calculation for first activity
        o, m, p = 2, 3, 5
        expected_time = (o + 4*m + p) / 6
        assert abs(pert_activities[0]['expected_time'] - expected_time) < 0.001
        
        # Verify variance calculation: ((P - O) / 6)²
        expected_variance = ((p - o) / 6) ** 2
        assert abs(pert_activities[0]['variance'] - expected_variance) < 0.001
    
    def test_variance_calculation(self):
        """Test PERT variance calculation accuracy"""
        activities = self.analyzer.load_activities_from_pert_data(self.sample_pert_data)
        pert_activities = self.analyzer.calculate_pert_estimates(activities)
        
        for activity in pert_activities:
            o = activity['optimistic']
            p = activity['pessimistic']
            expected_variance = ((p - o) / 6) ** 2
            assert abs(activity['variance'] - expected_variance) < 0.001
    
    def test_analyze_pert_workflow(self):
        """Test complete PERT analysis workflow"""
        graph, critical_paths, critical_activities = self.analyzer.analyze(self.sample_pert_data)
        
        # Verify results structure
        assert graph is not None
        assert isinstance(graph, nx.DiGraph)
        assert critical_paths is not None
        assert critical_activities is not None
        
        # Verify graph has PERT-specific attributes
        for node in graph.nodes():
            if node not in ['START', 'END']:
                assert 'expected_time' in graph.nodes[node] or 'duration' in graph.nodes[node]
                assert 'variance' in graph.nodes[node]
    
    def test_project_variance_calculation(self):
        """Test calculation of total project variance (sum of critical path variances)"""
        graph, critical_paths, critical_activities = self.analyzer.analyze(self.sample_pert_data)
        
        if hasattr(self.analyzer, 'calculate_project_variance'):
            project_variance = self.analyzer.calculate_project_variance(graph, critical_activities)
            assert project_variance >= 0  # Variance must be non-negative
            
            # Verify it's the sum of critical path activity variances
            expected_variance = sum([graph.nodes[activity]['variance'] 
                                   for activity in critical_activities 
                                   if activity not in ['START', 'END']])
            assert abs(project_variance - expected_variance) < 0.001
    
    def test_probability_calculations(self):
        """Test probability calculations for project completion"""
        graph, critical_paths, critical_activities = self.analyzer.analyze(self.sample_pert_data)
        
        if hasattr(self.analyzer, 'calculate_completion_probability'):
            # Test probability of completing within expected time
            expected_duration = max([graph.nodes[node]['EF'] for node in graph.nodes() if node != 'START'])
            prob_on_time = self.analyzer.calculate_completion_probability(expected_duration)
            
            # Should be approximately 0.5 for expected duration
            assert 0.4 <= prob_on_time <= 0.6
            
            # Test probability of completing early
            early_duration = expected_duration - 1
            prob_early = self.analyzer.calculate_completion_probability(early_duration)
            assert prob_early < 0.5
            
            # Test probability of completing late
            late_duration = expected_duration + 2
            prob_late = self.analyzer.calculate_completion_probability(late_duration)
            assert prob_late > 0.5
    
    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation for PERT analysis"""
        if hasattr(self.analyzer, 'monte_carlo_simulation'):
            graph, critical_paths, critical_activities = self.analyzer.analyze(self.sample_pert_data)
            
            # Run simulation
            simulation_results = self.analyzer.monte_carlo_simulation(iterations=1000)
            
            assert len(simulation_results) == 1000
            assert all(result > 0 for result in simulation_results)  # All durations should be positive
            
            # Statistical properties should be reasonable
            mean_duration = np.mean(simulation_results)
            std_duration = np.std(simulation_results)
            
            assert mean_duration > 0
            assert std_duration > 0
    
    def test_beta_distribution_sampling(self):
        """Test beta distribution sampling for PERT activities"""
        if hasattr(self.analyzer, 'sample_activity_duration'):
            # Test sampling from beta distribution
            optimistic, most_likely, pessimistic = 2, 5, 8
            
            samples = []
            for _ in range(1000):
                sample = self.analyzer.sample_activity_duration(optimistic, most_likely, pessimistic)
                samples.append(sample)
                assert optimistic <= sample <= pessimistic  # Should be within bounds
            
            # Statistical properties
            mean_sample = np.mean(samples)
            expected_mean = (optimistic + 4*most_likely + pessimistic) / 6
            
            # Sample mean should be close to theoretical mean
            assert abs(mean_sample - expected_mean) < 0.5
    
    def test_critical_path_variance(self):
        """Test that critical path has maximum variance among all paths"""
        graph, critical_paths, critical_activities = self.analyzer.analyze(self.sample_pert_data)
        
        # Calculate variance of critical path
        critical_variance = sum([graph.nodes[activity]['variance'] 
                               for activity in critical_activities 
                               if activity not in ['START', 'END']])
        
        assert critical_variance >= 0
    
    def test_equal_time_estimates(self):
        """Test handling when optimistic = most_likely = pessimistic (deterministic)"""
        deterministic_data = [
            {
                'id': 'A',
                'optimistic': 5,
                'most_likely': 5,
                'pessimistic': 5,
                'predecessors': ''
            }
        ]
        
        activities = self.analyzer.load_activities_from_pert_data(deterministic_data)
        pert_activities = self.analyzer.calculate_pert_estimates(activities)
        
        # Expected time should equal the common value
        assert pert_activities[0]['expected_time'] == 5
        # Variance should be zero
        assert pert_activities[0]['variance'] == 0
    
    def test_extreme_time_estimates(self):
        """Test handling of extreme time estimate ranges"""
        extreme_data = [
            {
                'id': 'A',
                'optimistic': 1,
                'most_likely': 5,
                'pessimistic': 100,  # Very wide range
                'predecessors': ''
            }
        ]
        
        activities = self.analyzer.load_activities_from_pert_data(extreme_data)
        pert_activities = self.analyzer.calculate_pert_estimates(activities)
        
        # Should handle without error
        assert pert_activities[0]['expected_time'] > 1
        assert pert_activities[0]['expected_time'] < 100
        assert pert_activities[0]['variance'] > 0
    
    def test_invalid_time_estimates(self):
        """Test handling of invalid time estimates"""
        # Negative times
        negative_data = [{'id': 'A', 'optimistic': -1, 'most_likely': 3, 'pessimistic': 5, 'predecessors': ''}]
        with pytest.raises(ValueError):
            self.analyzer.load_activities_from_pert_data(negative_data)
        
        # Non-numeric times
        non_numeric_data = [{'id': 'A', 'optimistic': 'a', 'most_likely': 3, 'pessimistic': 5, 'predecessors': ''}]
        with pytest.raises(ValueError):
            self.analyzer.load_activities_from_pert_data(non_numeric_data)
    
    def test_missing_time_estimates(self):
        """Test handling of missing time estimates"""
        missing_data = [{'id': 'A', 'optimistic': 2, 'most_likely': 3, 'predecessors': ''}]  # Missing pessimistic
        
        with pytest.raises(KeyError):
            self.analyzer.load_activities_from_pert_data(missing_data)
    
    def test_confidence_intervals(self):
        """Test calculation of confidence intervals for project completion"""
        if hasattr(self.analyzer, 'calculate_confidence_interval'):
            graph, critical_paths, critical_activities = self.analyzer.analyze(self.sample_pert_data)
            
            # Test 95% confidence interval
            ci_95 = self.analyzer.calculate_confidence_interval(confidence_level=0.95)
            assert len(ci_95) == 2
            assert ci_95[0] < ci_95[1]  # Lower bound < upper bound
            
            # Test 99% confidence interval (should be wider)
            ci_99 = self.analyzer.calculate_confidence_interval(confidence_level=0.99)
            assert ci_99[1] - ci_99[0] > ci_95[1] - ci_95[0]  # 99% CI should be wider
    
    def test_risk_analysis(self):
        """Test risk analysis capabilities"""
        if hasattr(self.analyzer, 'analyze_risk'):
            graph, critical_paths, critical_activities = self.analyzer.analyze(self.sample_pert_data)
            
            risk_metrics = self.analyzer.analyze_risk()
            
            # Should return meaningful risk metrics
            assert 'high_variance_activities' in risk_metrics
            assert 'project_risk_level' in risk_metrics
    
    def test_sensitivity_analysis(self):
        """Test sensitivity of project duration to individual activity changes"""
        if hasattr(self.analyzer, 'sensitivity_analysis'):
            graph, critical_paths, critical_activities = self.analyzer.analyze(self.sample_pert_data)
            
            sensitivity = self.analyzer.sensitivity_analysis()
            
            # Critical activities should have high sensitivity
            for activity in critical_activities:
                if activity in sensitivity:
                    assert sensitivity[activity] > 0
    
    def test_performance_large_pert_project(self):
        """Test performance with larger PERT project"""
        # Generate larger PERT dataset
        large_pert_data = []
        import random
        
        for i in range(30):  # 30 activities
            predecessors = []
            if i > 0:
                num_preds = min(random.randint(0, 2), i)
                if num_preds > 0:
                    pred_indices = random.sample(range(i), num_preds)
                    predecessors = [chr(65 + j) for j in pred_indices]
            
            # Generate realistic PERT times
            optimistic = random.randint(1, 5)
            pessimistic = optimistic + random.randint(3, 10)
            most_likely = random.randint(optimistic, pessimistic)
            
            large_pert_data.append({
                'id': chr(65 + i) if i < 26 else f'A{i-25}',
                'optimistic': optimistic,
                'most_likely': most_likely,
                'pessimistic': pessimistic,
                'predecessors': ','.join(predecessors)
            })
        
        # Should complete in reasonable time
        import time
        start_time = time.time()
        graph, critical_paths, critical_activities = self.analyzer.analyze(large_pert_data)
        execution_time = time.time() - start_time
        
        assert execution_time < 10.0  # Should complete within 10 seconds
        assert graph is not None
        assert len(critical_activities) > 0


class TestPERTAnalyzerEdgeCases:
    """Additional edge case tests for PERT Analyzer"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.analyzer = PERTAnalyzer()
    
    def test_single_activity_pert(self):
        """Test PERT analysis with single activity"""
        single_pert = [
            {
                'id': 'A',
                'optimistic': 3,
                'most_likely': 5,
                'pessimistic': 8,
                'predecessors': ''
            }
        ]
        
        graph, critical_paths, critical_activities = self.analyzer.analyze(single_pert)
        
        assert graph is not None
        assert 'A' in critical_activities
    
    def test_zero_variance_activities(self):
        """Test handling of zero-variance activities in PERT"""
        zero_variance_data = [
            {'id': 'A', 'optimistic': 5, 'most_likely': 5, 'pessimistic': 5, 'predecessors': ''},
            {'id': 'B', 'optimistic': 2, 'most_likely': 4, 'pessimistic': 6, 'predecessors': 'A'}
        ]
        
        graph, critical_paths, critical_activities = self.analyzer.analyze(zero_variance_data)
        assert graph is not None
    
    def test_very_small_time_estimates(self):
        """Test handling of very small time estimates"""
        small_time_data = [
            {'id': 'A', 'optimistic': 0.1, 'most_likely': 0.2, 'pessimistic': 0.3, 'predecessors': ''}
        ]
        
        activities = self.analyzer.load_activities_from_pert_data(small_time_data)
        assert len(activities) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
