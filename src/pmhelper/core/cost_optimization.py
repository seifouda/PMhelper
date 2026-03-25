"""
Cost Optimization Module

Implements time-cost trade-off analysis and indirect cost modeling for project optimization.
Supports CPM crashing integration and total cost minimization.

Author: PMHelper Team
Version: 1.1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CostPoint:
    """Represents a point on the time-cost curve"""
    duration: int
    direct_cost: float
    indirect_cost: float
    total_cost: float
    activities_crashed: List[str]


class IndirectCostModel:
    """Model indirect costs as function of project duration"""

    def __init__(self, cost_categories: Dict[str, float]):
        """
        Initialize indirect cost model with cost categories.
        
        Args:
            cost_categories: Dictionary mapping category name to daily rate
                           e.g., {'facilities': 200, 'equipment': 150, 'overhead': 100}
        
        Example:
            >>> model = IndirectCostModel({
            ...     'facilities': 200.0,
            ...     'equipment': 150.0,
            ...     'utilities': 50.0,
            ...     'overhead': 100.0
            ... })
            >>> model.calculate_cost(10)
            5000.0
        """
        self.categories = cost_categories
        self.daily_rate = sum(cost_categories.values())
        logger.info(f"Initialized IndirectCostModel with daily rate: ${self.daily_rate:.2f}")

    def calculate_cost(self, duration: int) -> float:
        """
        Calculate total indirect cost for given duration.
        
        Args:
            duration: Project duration in days
            
        Returns:
            Total indirect cost
        """
        if duration < 0:
            raise ValueError("Duration cannot be negative")
        return self.daily_rate * duration

    def breakdown_by_category(self, duration: int) -> Dict[str, float]:
        """
        Return cost breakdown by category.
        
        Args:
            duration: Project duration in days
            
        Returns:
            Dictionary mapping category to total cost
        """
        return {cat: rate * duration for cat, rate in self.categories.items()}

    def cost_curve(self, duration_range: range) -> pd.DataFrame:
        """
        Generate cost curve data for a range of durations.
        
        Args:
            duration_range: Range of durations to calculate
            
        Returns:
            DataFrame with columns: duration, indirect_cost
        """
        data = []
        for d in duration_range:
            data.append({
                'duration': d,
                'indirect_cost': self.calculate_cost(d)
            })
        return pd.DataFrame(data)


class TimeCostOptimizer:
    """Generate time-cost optimization curves and find optimal project duration"""

    def __init__(self, cpm_analyzer, indirect_cost_model: IndirectCostModel):
        """
        Initialize time-cost optimizer.
        
        Args:
            cpm_analyzer: CPMAnalyzer instance with analyzed project
            indirect_cost_model: IndirectCostModel for indirect costs
        """
        self.cpm = cpm_analyzer
        self.indirect_model = indirect_cost_model
        self.curve_data = []
        logger.info("Initialized TimeCostOptimizer")

    def generate_curve(self) -> pd.DataFrame:
        """
        Generate complete time-cost trade-off curve.
        
        Algorithm:
        1. Start with normal schedule (no crashing)
        2. Iteratively crash activities on critical path with lowest cost slope
        3. Calculate direct cost, indirect cost, and total cost at each point
        4. Stop when no more activities can be crashed
        
        Returns:
            DataFrame with columns: duration, direct_cost, indirect_cost, total_cost, activities_crashed
        
        Example:
            >>> optimizer = TimeCostOptimizer(cpm, indirect_model)
            >>> curve = optimizer.generate_curve()
            >>> print(curve[['duration', 'total_cost']])
        """
        curve_points = []
        
        # Get normal schedule information
        if not hasattr(self.cpm, 'G') or self.cpm.G is None:
            raise ValueError("CPM analysis must be performed before optimization")
        
        # Get initial project duration and costs
        # Calculate project duration from graph (max EF of all nodes)
        normal_duration = max([self.cpm.G.nodes[node].get('EF', 0) 
                              for node in self.cpm.G.nodes()])
        
        # Calculate normal direct cost (sum of all normal costs)
        normal_direct_cost = 0
        for activity_id in self.cpm.G.nodes():
            if activity_id not in ['Start', 'End']:
                activity_data = self.cpm.G.nodes[activity_id]
                normal_direct_cost += activity_data.get('normal_cost', 0)
        
        # Start with normal schedule
        current_duration = normal_duration
        current_direct_cost = normal_direct_cost
        crashed_activities = []
        
        # Add normal point
        indirect_cost = self.indirect_model.calculate_cost(current_duration)
        curve_points.append({
            'duration': current_duration,
            'direct_cost': current_direct_cost,
            'indirect_cost': indirect_cost,
            'total_cost': current_direct_cost + indirect_cost,
            'activities_crashed': list(crashed_activities)
        })
        
        # Simulate crashing iteratively
        # This is a simplified implementation - for full functionality,
        # integrate with existing crashing module
        max_iterations = 100
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Find activities on critical path that can be crashed
            crashable = self._find_crashable_activities(crashed_activities)
            
            if not crashable:
                logger.info("No more activities can be crashed")
                break
            
            # Select activity with minimum crash cost slope
            best_activity = min(crashable, key=lambda x: x['crash_cost_slope'])
            
            # Crash the activity
            crashed_activities.append(best_activity['id'])
            current_direct_cost += best_activity['crash_cost_slope']
            current_duration -= 1  # Simplified: assume 1 day reduction
            
            # Calculate costs at this point
            indirect_cost = self.indirect_model.calculate_cost(current_duration)
            curve_points.append({
                'duration': current_duration,
                'direct_cost': current_direct_cost,
                'indirect_cost': indirect_cost,
                'total_cost': current_direct_cost + indirect_cost,
                'activities_crashed': list(crashed_activities)
            })
            
            # Check if we've reached minimum possible duration
            if current_duration <= 1:
                break
        
        self.curve_data = curve_points
        return pd.DataFrame(curve_points)

    def _find_crashable_activities(self, already_crashed: List[str]) -> List[Dict]:
        """
        Find activities on critical path that can still be crashed.
        
        Args:
            already_crashed: List of activity IDs already crashed
            
        Returns:
            List of dictionaries with activity info and crash cost slope
        """
        crashable = []
        
        for activity_id in self.cpm.critical_activities:
            if activity_id in already_crashed:
                continue
            
            if activity_id in ['Start', 'End']:
                continue
            
            activity_data = self.cpm.G.nodes[activity_id]
            duration = activity_data.get('duration', 0)
            min_duration = activity_data.get('min_duration', duration)
            
            # Can crash if current duration > minimum duration
            if duration > min_duration:
                crash_cost = activity_data.get('crash_cost', 0)
                normal_cost = activity_data.get('normal_cost', 0)
                
                # Calculate crash cost slope (cost per day saved)
                days_crashable = duration - min_duration
                crash_cost_slope = (crash_cost - normal_cost) / days_crashable if days_crashable > 0 else float('inf')
                
                crashable.append({
                    'id': activity_id,
                    'crash_cost_slope': crash_cost_slope,
                    'days_crashable': days_crashable
                })
        
        return crashable

    def find_optimal_duration(self) -> dict:
        """
        Find duration that minimizes total cost.
        
        Returns:
            Dictionary with optimal duration, costs, and savings
        
        Example:
            >>> result = optimizer.find_optimal_duration()
            >>> print(f"Optimal duration: {result['optimal_duration']} days")
            >>> print(f"Total cost savings: ${result['savings_vs_normal']:.2f}")
        """
        if not self.curve_data:
            df = self.generate_curve()
        else:
            df = pd.DataFrame(self.curve_data)
        
        # Find point with minimum total cost
        optimal_idx = df['total_cost'].idxmin()
        optimal_point = df.iloc[optimal_idx]
        
        # Get normal schedule point (first point)
        normal_point = df.iloc[0]
        
        savings = normal_point['total_cost'] - optimal_point['total_cost']
        savings_pct = (savings / normal_point['total_cost'] * 100) if normal_point['total_cost'] > 0 else 0
        
        result = {
            'optimal_duration': int(optimal_point['duration']),
            'optimal_total_cost': float(optimal_point['total_cost']),
            'direct_cost': float(optimal_point['direct_cost']),
            'indirect_cost': float(optimal_point['indirect_cost']),
            'activities_crashed': optimal_point['activities_crashed'],
            'normal_duration': int(normal_point['duration']),
            'normal_total': float(normal_point['total_cost']),
            'normal_direct': float(normal_point['direct_cost']),
            'normal_indirect': float(normal_point['indirect_cost']),
            'savings_vs_normal': float(savings),
            'savings_pct': float(savings_pct)
        }
        
        logger.info(f"Optimal duration: {result['optimal_duration']} days (savings: ${savings:.2f})")
        return result


def integrate_cost_optimization_with_cpm(cpm_analyzer):
    """
    Add cost optimization methods to CPMAnalyzer instance.
    
    This function extends an existing CPMAnalyzer with cost optimization capabilities.
    
    Args:
        cpm_analyzer: CPMAnalyzer instance to extend
    """
    
    def attach_indirect_costs(self, cost_categories: Dict[str, float]):
        """Attach indirect cost model to CPM analysis"""
        self.indirect_model = IndirectCostModel(cost_categories)
        logger.info("Attached indirect cost model to CPM analyzer")

    def optimize_cost(self) -> dict:
        """Run time-cost optimization"""
        if not hasattr(self, 'indirect_model'):
            raise ValueError("Must attach indirect costs first using attach_indirect_costs()")

        optimizer = TimeCostOptimizer(self, self.indirect_model)
        return optimizer.find_optimal_duration()

    def get_optimization_curve(self) -> pd.DataFrame:
        """Get full time-cost curve data"""
        if not hasattr(self, 'indirect_model'):
            raise ValueError("Must attach indirect costs first using attach_indirect_costs()")
            
        optimizer = TimeCostOptimizer(self, self.indirect_model)
        return optimizer.generate_curve()
    
    # Add methods to the instance
    import types
    cpm_analyzer.attach_indirect_costs = types.MethodType(attach_indirect_costs, cpm_analyzer)
    cpm_analyzer.optimize_cost = types.MethodType(optimize_cost, cpm_analyzer)
    cpm_analyzer.get_optimization_curve = types.MethodType(get_optimization_curve, cpm_analyzer)
    
    logger.info("Successfully integrated cost optimization with CPM analyzer")
