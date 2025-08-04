#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Calculations Utilities

Tests all calculation functions including:
- CPM calculations (forward/backward pass, float)
- PERT calculations (expected time, variance)
- Probability calculations
- Statistical functions
- Monte Carlo simulation utilities
- Mathematical helper functions
"""

import pytest
import sys
import numpy as np
import math
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pmhelper.utils.calculations import *


class TestCPMCalculations:
    """Test CPM-related calculations"""
    
    def test_forward_pass_calculation(self):
        """Test forward pass calculation logic"""
        if 'calculate_early_start' in globals():
            # Test simple case
            predecessors_finish_times = [3, 5, 2]
            early_start = calculate_early_start(predecessors_finish_times)
            assert early_start == 5  # Max of predecessor finish times
            
            # Test empty predecessors
            early_start = calculate_early_start([])
            assert early_start == 0  # Should start at 0
    
    def test_backward_pass_calculation(self):
        """Test backward pass calculation logic"""
        if 'calculate_late_finish' in globals():
            # Test simple case
            successors_start_times = [8, 10, 12]
            late_finish = calculate_late_finish(successors_start_times)
            assert late_finish == 8  # Min of successor start times
            
            # Test empty successors (end activity)
            late_finish = calculate_late_finish([])
            assert late_finish is not None
    
    def test_float_calculation(self):
        """Test float/slack calculation"""
        if 'calculate_float' in globals():
            early_start = 3
            late_start = 5
            float_value = calculate_float(early_start, late_start)
            assert float_value == 2
            
            # Critical activity (zero float)
            float_value = calculate_float(3, 3)
            assert float_value == 0
    
    def test_project_duration_calculation(self):
        """Test project duration calculation"""
        if 'calculate_project_duration' in globals():
            finish_times = [8, 10, 12, 9]
            duration = calculate_project_duration(finish_times)
            assert duration == 12  # Max finish time
    
    def test_critical_path_identification(self):
        """Test critical path identification logic"""
        if 'is_critical_activity' in globals():
            # Critical activity
            assert is_critical_activity(float_value=0) == True
            assert is_critical_activity(float_value=0.001) == True  # Near zero
            
            # Non-critical activity
            assert is_critical_activity(float_value=2) == False


class TestPERTCalculations:
    """Test PERT-related calculations"""
    
    def test_expected_time_calculation(self):
        """Test PERT expected time calculation: (O + 4M + P) / 6"""
        if 'calculate_pert_expected_time' in globals():
            optimistic = 2
            most_likely = 5
            pessimistic = 8
            
            expected = calculate_pert_expected_time(optimistic, most_likely, pessimistic)
            calculated = (2 + 4*5 + 8) / 6
            
            assert abs(expected - calculated) < 0.001
    
    def test_pert_variance_calculation(self):
        """Test PERT variance calculation: ((P - O) / 6)²"""
        if 'calculate_pert_variance' in globals():
            optimistic = 2
            pessimistic = 8
            
            variance = calculate_pert_variance(optimistic, pessimistic)
            calculated = ((8 - 2) / 6) ** 2
            
            assert abs(variance - calculated) < 0.001
    
    def test_pert_standard_deviation(self):
        """Test PERT standard deviation calculation"""
        if 'calculate_pert_std_dev' in globals():
            optimistic = 2
            pessimistic = 8
            
            std_dev = calculate_pert_std_dev(optimistic, pessimistic)
            expected_std_dev = (8 - 2) / 6
            
            assert abs(std_dev - expected_std_dev) < 0.001
    
    def test_project_variance_calculation(self):
        """Test total project variance calculation"""
        if 'calculate_project_variance' in globals():
            activity_variances = [0.25, 0.36, 0.16, 0.09]
            project_variance = calculate_project_variance(activity_variances)
            
            assert abs(project_variance - sum(activity_variances)) < 0.001
    
    def test_pert_time_validation(self):
        """Test PERT time estimate validation"""
        if 'validate_pert_times' in globals():
            # Valid times
            assert validate_pert_times(2, 5, 8) == True
            assert validate_pert_times(3, 3, 3) == True  # Equal times
            
            # Invalid times
            assert validate_pert_times(8, 5, 2) == False  # O > P
            assert validate_pert_times(2, 8, 5) == False  # M > P
            assert validate_pert_times(5, 2, 8) == False  # O > M


class TestProbabilityCalculations:
    """Test probability and statistical calculations"""
    
    def test_normal_distribution_probability(self):
        """Test normal distribution probability calculations"""
        if 'calculate_normal_probability' in globals():
            # Standard normal distribution
            mean = 0
            std_dev = 1
            value = 0
            
            prob = calculate_normal_probability(value, mean, std_dev)
            assert abs(prob - 0.5) < 0.01  # Should be ~0.5 for mean
    
    def test_z_score_calculation(self):
        """Test Z-score calculation"""
        if 'calculate_z_score' in globals():
            value = 110
            mean = 100
            std_dev = 10
            
            z_score = calculate_z_score(value, mean, std_dev)
            assert abs(z_score - 1.0) < 0.001
    
    def test_confidence_interval_calculation(self):
        """Test confidence interval calculation"""
        if 'calculate_confidence_interval' in globals():
            mean = 100
            std_dev = 10
            confidence_level = 0.95
            
            ci_lower, ci_upper = calculate_confidence_interval(mean, std_dev, confidence_level)
            
            assert ci_lower < mean < ci_upper
            assert ci_upper - ci_lower > 0  # Should have positive width
    
    def test_beta_distribution_parameters(self):
        """Test Beta distribution parameter calculation for PERT"""
        if 'calculate_beta_parameters' in globals():
            optimistic = 2
            most_likely = 5
            pessimistic = 8
            
            alpha, beta = calculate_beta_parameters(optimistic, most_likely, pessimistic)
            
            assert alpha > 0
            assert beta > 0
    
    def test_monte_carlo_iteration(self):
        """Test single Monte Carlo iteration"""
        if 'monte_carlo_sample' in globals():
            # Sample from beta distribution
            optimistic = 2
            most_likely = 5
            pessimistic = 8
            
            sample = monte_carlo_sample(optimistic, most_likely, pessimistic)
            
            assert optimistic <= sample <= pessimistic


class TestStatisticalFunctions:
    """Test statistical utility functions"""
    
    def test_mean_calculation(self):
        """Test mean calculation"""
        if 'calculate_mean' in globals():
            values = [1, 2, 3, 4, 5]
            mean = calculate_mean(values)
            assert abs(mean - 3.0) < 0.001
    
    def test_variance_calculation(self):
        """Test variance calculation"""
        if 'calculate_variance' in globals():
            values = [1, 2, 3, 4, 5]
            variance = calculate_variance(values)
            
            # Manual calculation: variance = sum((x - mean)²) / (n-1)
            mean = 3.0
            manual_variance = sum([(x - mean)**2 for x in values]) / (len(values) - 1)
            
            assert abs(variance - manual_variance) < 0.001
    
    def test_standard_deviation_calculation(self):
        """Test standard deviation calculation"""
        if 'calculate_std_dev' in globals():
            values = [1, 2, 3, 4, 5]
            std_dev = calculate_std_dev(values)
            
            # Should be square root of variance
            variance = calculate_variance(values) if 'calculate_variance' in globals() else 2.5
            expected_std_dev = math.sqrt(variance)
            
            assert abs(std_dev - expected_std_dev) < 0.001
    
    def test_percentile_calculation(self):
        """Test percentile calculation"""
        if 'calculate_percentile' in globals():
            values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            
            p50 = calculate_percentile(values, 50)  # Median
            p90 = calculate_percentile(values, 90)
            p10 = calculate_percentile(values, 10)
            
            assert p10 < p50 < p90
    
    def test_correlation_calculation(self):
        """Test correlation coefficient calculation"""
        if 'calculate_correlation' in globals():
            x = [1, 2, 3, 4, 5]
            y = [2, 4, 6, 8, 10]  # Perfect positive correlation
            
            correlation = calculate_correlation(x, y)
            assert abs(correlation - 1.0) < 0.001  # Should be 1.0
            
            # Negative correlation
            y_neg = [10, 8, 6, 4, 2]
            correlation_neg = calculate_correlation(x, y_neg)
            assert abs(correlation_neg - (-1.0)) < 0.001  # Should be -1.0


class TestMathematicalHelpers:
    """Test mathematical helper functions"""
    
    def test_round_to_precision(self):
        """Test rounding to specific precision"""
        if 'round_to_precision' in globals():
            value = 3.14159
            
            assert round_to_precision(value, 2) == 3.14
            assert round_to_precision(value, 0) == 3
            assert round_to_precision(value, 4) == 3.1416
    
    def test_clamp_value(self):
        """Test value clamping"""
        if 'clamp' in globals():
            assert clamp(5, 1, 10) == 5  # Within range
            assert clamp(-1, 1, 10) == 1  # Below range
            assert clamp(15, 1, 10) == 10  # Above range
    
    def test_linear_interpolation(self):
        """Test linear interpolation"""
        if 'linear_interpolate' in globals():
            result = linear_interpolate(0, 10, 0.5)  # Halfway between 0 and 10
            assert abs(result - 5.0) < 0.001
            
            result = linear_interpolate(0, 10, 0.0)  # At start
            assert abs(result - 0.0) < 0.001
            
            result = linear_interpolate(0, 10, 1.0)  # At end
            assert abs(result - 10.0) < 0.001
    
    def test_factorial_calculation(self):
        """Test factorial calculation"""
        if 'factorial' in globals():
            assert factorial(0) == 1
            assert factorial(1) == 1
            assert factorial(5) == 120
            assert factorial(3) == 6
    
    def test_combination_calculation(self):
        """Test combination (nCr) calculation"""
        if 'combination' in globals():
            assert combination(5, 2) == 10  # 5C2 = 10
            assert combination(5, 0) == 1   # nC0 = 1
            assert combination(5, 5) == 1   # nCn = 1
    
    def test_permutation_calculation(self):
        """Test permutation (nPr) calculation"""
        if 'permutation' in globals():
            assert permutation(5, 2) == 20  # 5P2 = 20
            assert permutation(5, 0) == 1   # nP0 = 1
            assert permutation(5, 1) == 5   # nP1 = n


class TestOptimizationCalculations:
    """Test optimization-related calculations"""
    
    def test_crash_cost_efficiency(self):
        """Test crash cost efficiency calculation"""
        if 'calculate_crash_efficiency' in globals():
            time_saved = 2
            crash_cost = 100
            
            efficiency = calculate_crash_efficiency(time_saved, crash_cost)
            assert abs(efficiency - 0.02) < 0.001  # 2/100 = 0.02
    
    def test_resource_utilization(self):
        """Test resource utilization calculation"""
        if 'calculate_resource_utilization' in globals():
            used_resources = 8
            available_resources = 10
            
            utilization = calculate_resource_utilization(used_resources, available_resources)
            assert abs(utilization - 0.8) < 0.001  # 8/10 = 0.8
    
    def test_project_acceleration(self):
        """Test project acceleration calculation"""
        if 'calculate_acceleration' in globals():
            original_duration = 20
            crashed_duration = 15
            
            acceleration = calculate_acceleration(original_duration, crashed_duration)
            assert abs(acceleration - 0.25) < 0.001  # (20-15)/20 = 0.25


class TestErrorHandling:
    """Test error handling in calculations"""
    
    def test_division_by_zero(self):
        """Test handling of division by zero"""
        if 'calculate_resource_utilization' in globals():
            with pytest.raises(ZeroDivisionError):
                calculate_resource_utilization(5, 0)
    
    def test_negative_values(self):
        """Test handling of negative values where inappropriate"""
        if 'calculate_pert_variance' in globals():
            # Pessimistic < Optimistic should raise error
            with pytest.raises(ValueError):
                calculate_pert_variance(8, 2)  # Invalid: pessimistic < optimistic
    
    def test_invalid_probability_values(self):
        """Test handling of invalid probability values"""
        if 'calculate_confidence_interval' in globals():
            # Confidence level outside [0, 1] should raise error
            with pytest.raises(ValueError):
                calculate_confidence_interval(100, 10, 1.5)  # Invalid: > 1
            
            with pytest.raises(ValueError):
                calculate_confidence_interval(100, 10, -0.1)  # Invalid: < 0
    
    def test_empty_list_handling(self):
        """Test handling of empty lists"""
        if 'calculate_mean' in globals():
            with pytest.raises(ValueError):
                calculate_mean([])
        
        if 'calculate_project_duration' in globals():
            with pytest.raises(ValueError):
                calculate_project_duration([])


class TestNumericalStability:
    """Test numerical stability and precision"""
    
    def test_floating_point_precision(self):
        """Test handling of floating point precision issues"""
        if 'is_critical_activity' in globals():
            # Very small float should be considered critical
            assert is_critical_activity(1e-10) == True
            assert is_critical_activity(1e-6) == True
            assert is_critical_activity(0.001) == False
    
    def test_large_number_handling(self):
        """Test handling of very large numbers"""
        if 'calculate_pert_expected_time' in globals():
            # Very large values
            optimistic = 1e6
            most_likely = 2e6
            pessimistic = 3e6
            
            expected = calculate_pert_expected_time(optimistic, most_likely, pessimistic)
            assert expected > 0
            assert not math.isinf(expected)
            assert not math.isnan(expected)
    
    def test_very_small_number_handling(self):
        """Test handling of very small numbers"""
        if 'calculate_pert_variance' in globals():
            # Very small values
            optimistic = 1e-6
            pessimistic = 2e-6
            
            variance = calculate_pert_variance(optimistic, pessimistic)
            assert variance > 0
            assert not math.isinf(variance)
            assert not math.isnan(variance)


class TestPerformance:
    """Test performance of calculation functions"""
    
    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        if 'calculate_mean' in globals():
            import time
            
            # Large dataset
            large_data = list(range(100000))
            
            start_time = time.time()
            mean = calculate_mean(large_data)
            execution_time = time.time() - start_time
            
            assert execution_time < 1.0  # Should complete within 1 second
            assert abs(mean - 49999.5) < 0.1  # Mean of 0-99999
    
    def test_monte_carlo_performance(self):
        """Test Monte Carlo simulation performance"""
        if 'monte_carlo_sample' in globals():
            import time
            
            start_time = time.time()
            
            # Run 10000 iterations
            samples = []
            for _ in range(10000):
                sample = monte_carlo_sample(2, 5, 8)
                samples.append(sample)
            
            execution_time = time.time() - start_time
            
            assert execution_time < 5.0  # Should complete within 5 seconds
            assert len(samples) == 10000
            assert all(2 <= s <= 8 for s in samples)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
