#!/usr/bin/env python3
"""
Calculations Module

Provides utility functions for various project management calculations.
Includes time calculations, cost analysis, and statistical functions.
"""

import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from scipy.stats import norm


class TimeCalculations:
    """Utility functions for time-related calculations"""
    
    @staticmethod
    def calculate_pert_estimates(optimistic: float, most_likely: float, pessimistic: float) -> Tuple[float, float]:
        """
        Calculate PERT expected time and variance
        
        Args:
            optimistic: Optimistic time estimate
            most_likely: Most likely time estimate  
            pessimistic: Pessimistic time estimate
            
        Returns:
            Tuple[float, float]: (expected_time, variance)
        """
        expected_time = (optimistic + 4 * most_likely + pessimistic) / 6
        variance = ((pessimistic - optimistic) / 6) ** 2
        
        return expected_time, variance
    
    @staticmethod
    def calculate_project_variance(variances: List[float]) -> float:
        """
        Calculate total project variance from individual activity variances
        
        Args:
            variances: List of activity variances
            
        Returns:
            float: Total project variance
        """
        return sum(variances)
    
    @staticmethod
    def calculate_standard_deviation(variance: float) -> float:
        """
        Calculate standard deviation from variance
        
        Args:
            variance: Variance value
            
        Returns:
            float: Standard deviation
        """
        return math.sqrt(variance)
    
    @staticmethod
    def calculate_confidence_interval(mean: float, std_dev: float, confidence_level: float = 0.95) -> Tuple[float, float]:
        """
        Calculate confidence interval for project duration
        
        Args:
            mean: Expected project duration
            std_dev: Standard deviation
            confidence_level: Confidence level (default 0.95 for 95%)
            
        Returns:
            Tuple[float, float]: (lower_bound, upper_bound)
        """
        z_score = norm.ppf((1 + confidence_level) / 2)
        margin_of_error = z_score * std_dev
        
        lower_bound = mean - margin_of_error
        upper_bound = mean + margin_of_error
        
        return lower_bound, upper_bound


class CostCalculations:
    """Utility functions for cost-related calculations"""
    
    @staticmethod
    def calculate_total_normal_cost(activities: List[Dict[str, Any]]) -> float:
        """
        Calculate total normal cost of the project
        
        Args:
            activities: List of activity dictionaries with 'normal_cost' key
            
        Returns:
            float: Total normal cost
        """
        return sum(activity.get('normal_cost', 0) for activity in activities)
    
    @staticmethod
    def calculate_total_crash_cost(crash_log: List[Dict[str, Any]]) -> float:
        """
        Calculate total crash cost from crash log
        
        Args:
            crash_log: List of crash entries with 'crash_cost' key
            
        Returns:
            float: Total crash cost
        """
        return sum(entry.get('crash_cost', 0) for entry in crash_log)
    
    @staticmethod
    def calculate_cost_per_time_saved(crash_cost: float, time_saved: float) -> float:
        """
        Calculate cost efficiency of crashing
        
        Args:
            crash_cost: Total cost of crashing
            time_saved: Total time saved
            
        Returns:
            float: Cost per unit time saved
        """
        if time_saved == 0:
            return float('inf')
        return crash_cost / time_saved
    
    @staticmethod
    def calculate_crash_efficiency(normal_duration: float, crashed_duration: float, 
                                 total_crash_cost: float) -> Dict[str, float]:
        """
        Calculate various crash efficiency metrics
        
        Args:
            normal_duration: Original project duration
            crashed_duration: Duration after crashing
            total_crash_cost: Total cost of crashing
            
        Returns:
            Dict[str, float]: Dictionary with efficiency metrics
        """
        time_saved = normal_duration - crashed_duration
        time_reduction_percent = (time_saved / normal_duration) * 100 if normal_duration > 0 else 0
        cost_per_time_unit = total_crash_cost / time_saved if time_saved > 0 else float('inf')
        
        return {
            'time_saved': time_saved,
            'time_reduction_percent': time_reduction_percent,
            'cost_per_time_unit': cost_per_time_unit,
            'total_crash_cost': total_crash_cost
        }


class ResourceCalculations:
    """Utility functions for resource-related calculations"""
    
    @staticmethod
    def calculate_resource_utilization(scheduled_resources: List[int], available_resources: int) -> Dict[str, float]:
        """
        Calculate resource utilization statistics
        
        Args:
            scheduled_resources: List of scheduled resources per time period
            available_resources: Total available resources
            
        Returns:
            Dict[str, float]: Utilization statistics
        """
        if not scheduled_resources or available_resources == 0:
            return {'average_utilization': 0, 'peak_utilization': 0, 'utilization_variance': 0}
        
        utilizations = [res / available_resources for res in scheduled_resources]
        
        average_utilization = np.mean(utilizations)
        peak_utilization = max(utilizations)
        utilization_variance = np.var(utilizations)
        
        return {
            'average_utilization': average_utilization,
            'peak_utilization': peak_utilization,
            'utilization_variance': utilization_variance
        }
    
    @staticmethod
    def calculate_resource_leveling_metrics(resource_usage: List[int]) -> Dict[str, float]:
        """
        Calculate resource leveling metrics
        
        Args:
            resource_usage: List of resource usage per time period
            
        Returns:
            Dict[str, float]: Leveling metrics
        """
        if not resource_usage:
            return {'resource_variance': 0, 'peak_to_average_ratio': 0, 'leveling_index': 0}
        
        mean_usage = np.mean(resource_usage)
        variance = np.var(resource_usage)
        peak_usage = max(resource_usage)
        
        peak_to_average_ratio = peak_usage / mean_usage if mean_usage > 0 else 0
        leveling_index = math.sqrt(variance) / mean_usage if mean_usage > 0 else 0
        
        return {
            'resource_variance': variance,
            'peak_to_average_ratio': peak_to_average_ratio,
            'leveling_index': leveling_index
        }


class ProbabilityCalculations:
    """Utility functions for probability calculations"""
    
    @staticmethod
    def calculate_completion_probability(target_duration: float, expected_duration: float, 
                                       std_deviation: float) -> float:
        """
        Calculate probability of completing project by target duration
        
        Args:
            target_duration: Target completion time
            expected_duration: Expected project duration
            std_deviation: Standard deviation of project duration
            
        Returns:
            float: Probability of completion (0-1)
        """
        if std_deviation == 0:
            return 1.0 if target_duration >= expected_duration else 0.0
        
        z_score = (target_duration - expected_duration) / std_deviation
        return norm.cdf(z_score)
    
    @staticmethod
    def calculate_duration_for_probability(target_probability: float, expected_duration: float,
                                         std_deviation: float) -> float:
        """
        Calculate duration for a given completion probability
        
        Args:
            target_probability: Desired probability (0-1)
            expected_duration: Expected project duration
            std_deviation: Standard deviation of project duration
            
        Returns:
            float: Duration corresponding to the probability
        """
        if not (0 <= target_probability <= 1):
            raise ValueError("Probability must be between 0 and 1")
        
        if std_deviation == 0:
            return expected_duration
        
        z_score = norm.ppf(target_probability)
        return expected_duration + (z_score * std_deviation)
    
    @staticmethod
    def calculate_risk_metrics(expected_duration: float, std_deviation: float) -> Dict[str, float]:
        """
        Calculate various risk metrics for the project
        
        Args:
            expected_duration: Expected project duration
            std_deviation: Standard deviation of project duration
            
        Returns:
            Dict[str, float]: Risk metrics
        """
        coefficient_of_variation = std_deviation / expected_duration if expected_duration > 0 else 0
        
        # Calculate probability of various completion scenarios
        prob_on_time = ProbabilityCalculations.calculate_completion_probability(
            expected_duration, expected_duration, std_deviation)
        prob_10_percent_late = ProbabilityCalculations.calculate_completion_probability(
            expected_duration * 1.1, expected_duration, std_deviation)
        prob_20_percent_late = ProbabilityCalculations.calculate_completion_probability(
            expected_duration * 1.2, expected_duration, std_deviation)
        
        return {
            'coefficient_of_variation': coefficient_of_variation,
            'probability_on_time': prob_on_time,
            'probability_10_percent_late': 1 - prob_10_percent_late,
            'probability_20_percent_late': 1 - prob_20_percent_late
        }


class NetworkMetrics:
    """Utility functions for network analysis metrics"""
    
    @staticmethod
    def calculate_network_complexity(G) -> Dict[str, float]:
        """
        Calculate complexity metrics for the project network
        
        Args:
            G: NetworkX graph
            
        Returns:
            Dict[str, float]: Network complexity metrics
        """
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        
        if num_nodes <= 2:  # Only START and END
            return {'density': 0, 'complexity_index': 0, 'avg_degree': 0}
        
        # Network density
        max_edges = num_nodes * (num_nodes - 1)
        density = num_edges / max_edges if max_edges > 0 else 0
        
        # Average degree
        avg_degree = 2 * num_edges / num_nodes if num_nodes > 0 else 0
        
        # Complexity index (simple measure)
        complexity_index = (num_edges / num_nodes) if num_nodes > 0 else 0
        
        return {
            'density': density,
            'complexity_index': complexity_index,
            'avg_degree': avg_degree,
            'num_nodes': num_nodes,
            'num_edges': num_edges
        }
    
    @staticmethod
    def calculate_criticality_metrics(G) -> Dict[str, float]:
        """
        Calculate criticality metrics for the project
        
        Args:
            G: NetworkX graph with float calculations
            
        Returns:
            Dict[str, float]: Criticality metrics
        """
        activities = [node for node in G.nodes() if node not in ['START', 'END']]
        
        if not activities:
            return {'criticality_ratio': 0, 'avg_float': 0, 'critical_activities': 0}
        
        critical_activities = [node for node in activities if G.nodes[node].get('float', 1) == 0]
        floats = [G.nodes[node].get('float', 0) for node in activities]
        
        criticality_ratio = len(critical_activities) / len(activities)
        avg_float = np.mean(floats) if floats else 0
        
        return {
            'criticality_ratio': criticality_ratio,
            'avg_float': avg_float,
            'critical_activities': len(critical_activities),
            'total_activities': len(activities)
        }
