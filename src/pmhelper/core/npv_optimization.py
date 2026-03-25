"""
Net Present Value (NPV) Optimization Module

Implements NPV-based project scheduling optimization with time value of money.
Supports discount rate sensitivity analysis and cash flow-based scheduling.

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
class CashFlowActivity:
    """Activity with cash flow information"""
    id: str
    duration: int
    cash_flow: float  # Net cash flow at completion
    es: int
    ef: int
    ls: int
    lf: int
    float: int
    predecessors: List[str]
    successors: List[str]


class NPVOptimizer:
    """Net Present Value optimization for project scheduling"""

    def __init__(self, activities: List[CashFlowActivity], discount_rate: float = 0.10):
        """
        Initialize NPV optimizer.
        
        Args:
            activities: List of CashFlowActivity objects with cash flows
            discount_rate: Annual discount rate (e.g., 0.10 for 10%)
        
        Example:
            >>> activities = [CashFlowActivity('A', 4, 10000, 0, 4, 0, 4, 0, [], ['B'])]
            >>> optimizer = NPVOptimizer(activities, discount_rate=0.12)
        """
        self.activities = {act.id: act for act in activities}
        self.discount_rate = discount_rate
        self.original_schedule = {act.id: act.es for act in activities}
        logger.info(f"Initialized NPVOptimizer with {len(activities)} activities, rate={discount_rate}")

    def calculate_npv(self, schedule: Dict[str, int]) -> float:
        """
        Calculate Net Present Value for a given schedule.
        
        NPV = Σ(CF_i / (1 + r)^t_i)
        where CF_i is cash flow and t_i is time of completion
        
        Args:
            schedule: Dictionary mapping activity ID to start time
            
        Returns:
            Net Present Value of the schedule
        
        Example:
            >>> schedule = {'A': 0, 'B': 4}
            >>> npv = optimizer.calculate_npv(schedule)
        """
        npv = 0.0
        
        for act_id, start_time in schedule.items():
            if act_id not in self.activities:
                continue
            
            activity = self.activities[act_id]
            # Cash flow occurs at activity completion
            completion_time = start_time + activity.duration
            
            # Discount to present value
            if activity.cash_flow != 0:
                pv = activity.cash_flow / ((1 + self.discount_rate) ** completion_time)
                npv += pv
        
        return npv

    def maximize_npv(self, max_iterations: int = 1000) -> dict:
        """
        Find schedule that maximizes NPV.
        
        Algorithm:
        1. Start with early start schedule
        2. For activities with positive cash flows, try earlier starts
        3. For activities with negative cash flows, try later starts
        4. Keep changes that improve NPV
        
        Args:
            max_iterations: Maximum optimization iterations
            
        Returns:
            Dictionary with optimization results including:
            - optimal_schedule: Dict mapping activity ID to start time
            - optimal_npv: Maximum NPV achieved
            - original_npv: NPV of early start schedule
            - improvement: NPV improvement amount
            - improvement_pct: Percentage improvement
            - iterations: Number of iterations performed
        
        Example:
            >>> result = optimizer.maximize_npv()
            >>> print(f"NPV improved by {result['improvement_pct']:.1f}%")
        """
        current_schedule = self.original_schedule.copy()
        activities_list = list(self.activities.values())
        
        # Calculate baseline NPV (early start)
        original_npv = self.calculate_npv(current_schedule)
        best_npv = original_npv
        
        logger.info(f"Starting NPV maximization - Original NPV: ${original_npv:,.2f}")
        
        # Get non-critical activities (can be shifted)
        non_critical = [act for act in activities_list if act.float > 0]
        
        if not non_critical:
            logger.info("No non-critical activities to optimize")
            return self._create_result(current_schedule, original_npv, best_npv, 0)
        
        improved = True
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for activity in non_critical:
                best_position = current_schedule[activity.id]
                
                # Strategy: 
                # - Positive cash flow: try earlier (less discounting)
                # - Negative cash flow: try later (more discounting reduces impact)
                
                positions_to_try = range(activity.es, activity.ls + 1)
                
                for start_time in positions_to_try:
                    test_schedule = current_schedule.copy()
                    test_schedule[activity.id] = start_time
                    
                    # Check precedence constraints
                    if not self._check_precedence(test_schedule, activity):
                        continue
                    
                    test_npv = self.calculate_npv(test_schedule)
                    
                    if test_npv > best_npv:
                        best_npv = test_npv
                        best_position = start_time
                        improved = True
                
                if best_position != current_schedule[activity.id]:
                    current_schedule[activity.id] = best_position
                    logger.debug(f"Iteration {iteration}: Moved {activity.id} to time {best_position}")
        
        logger.info(f"NPV maximization complete after {iteration} iterations")
        logger.info(f"Final NPV: ${best_npv:,.2f}")
        
        return self._create_result(current_schedule, original_npv, best_npv, iteration)

    def _check_precedence(self, schedule: Dict[str, int], activity: CashFlowActivity) -> bool:
        """
        Check if schedule respects precedence constraints for an activity.
        
        Args:
            schedule: Proposed schedule
            activity: Activity to check
            
        Returns:
            True if precedence constraints are satisfied
        """
        start_time = schedule[activity.id]
        
        # Check all predecessors finish before this activity starts
        for pred_id in activity.predecessors:
            if pred_id in self.activities and pred_id in schedule:
                pred = self.activities[pred_id]
                pred_finish = schedule[pred_id] + pred.duration
                if pred_finish > start_time:
                    return False
        
        # Check all successors start after this activity finishes
        finish_time = start_time + activity.duration
        for succ_id in activity.successors:
            if succ_id in self.activities and succ_id in schedule:
                succ_start = schedule[succ_id]
                if finish_time > succ_start:
                    return False
        
        return True

    def _create_result(self, schedule: Dict[str, int], 
                       original_npv: float,
                       optimal_npv: float,
                       iterations: int) -> dict:
        """Create result dictionary with all metrics"""
        improvement = optimal_npv - original_npv
        improvement_pct = (improvement / abs(original_npv) * 100) if original_npv != 0 else 0
        
        # Identify moved activities
        moved_activities = []
        for act_id in schedule.keys():
            if schedule[act_id] != self.original_schedule.get(act_id):
                moved_activities.append({
                    'id': act_id,
                    'original_start': self.original_schedule.get(act_id),
                    'optimal_start': schedule[act_id],
                    'cash_flow': self.activities[act_id].cash_flow
                })
        
        return {
            'optimal_schedule': schedule,
            'original_schedule': self.original_schedule,
            'optimal_npv': optimal_npv,
            'original_npv': original_npv,
            'improvement': improvement,
            'improvement_pct': improvement_pct,
            'iterations': iterations,
            'discount_rate': self.discount_rate,
            'moved_activities': moved_activities
        }

    def sensitivity_analysis(self, rate_range: List[float]) -> pd.DataFrame:
        """
        Analyze NPV sensitivity to discount rate changes.
        
        Args:
            rate_range: List of discount rates to analyze (e.g., [0.05, 0.10, 0.15])
            
        Returns:
            DataFrame with columns: discount_rate, npv_original, npv_optimal, improvement
        
        Example:
            >>> rates = [0.05, 0.08, 0.10, 0.12, 0.15]
            >>> sensitivity = optimizer.sensitivity_analysis(rates)
            >>> print(sensitivity)
        """
        results = []
        
        original_rate = self.discount_rate
        
        for rate in rate_range:
            # Temporarily set new rate
            self.discount_rate = rate
            
            # Calculate NPVs
            npv_original = self.calculate_npv(self.original_schedule)
            result = self.maximize_npv(max_iterations=500)
            
            results.append({
                'discount_rate': rate,
                'npv_original': npv_original,
                'npv_optimal': result['optimal_npv'],
                'improvement': result['improvement'],
                'improvement_pct': result['improvement_pct']
            })
        
        # Restore original rate
        self.discount_rate = original_rate
        
        logger.info(f"Sensitivity analysis complete for {len(rate_range)} discount rates")
        return pd.DataFrame(results)

    def get_cash_flow_schedule(self, schedule: Dict[str, int]) -> pd.DataFrame:
        """
        Get detailed cash flow schedule.
        
        Args:
            schedule: Activity start times
            
        Returns:
            DataFrame with columns: time, activity, cash_flow, discounted_value
        """
        cash_flows = []
        
        for act_id, start_time in schedule.items():
            if act_id not in self.activities:
                continue
            
            activity = self.activities[act_id]
            completion_time = start_time + activity.duration
            
            if activity.cash_flow != 0:
                discounted = activity.cash_flow / ((1 + self.discount_rate) ** completion_time)
                cash_flows.append({
                    'time': completion_time,
                    'activity': act_id,
                    'cash_flow': activity.cash_flow,
                    'discounted_value': discounted,
                    'discount_factor': 1 / ((1 + self.discount_rate) ** completion_time)
                })
        
        df = pd.DataFrame(cash_flows)
        if not df.empty:
            df = df.sort_values('time')
        
        return df


def activities_from_cpm_with_cashflows(cpm_analyzer, cash_flows: Dict[str, float]) -> List[CashFlowActivity]:
    """
    Convert CPM analyzer results to CashFlowActivity objects.
    
    Args:
        cpm_analyzer: CPMAnalyzer instance with completed analysis
        cash_flows: Dictionary mapping activity ID to cash flow amount
        
    Returns:
        List of CashFlowActivity objects
        
    Example:
        >>> cpm = CPMAnalyzer()
        >>> cpm.analyze(activity_data)
        >>> cash_flows = {'A': 10000, 'B': -5000, 'C': 15000}
        >>> activities = activities_from_cpm_with_cashflows(cpm, cash_flows)
    """
    activities = []
    
    if not hasattr(cpm_analyzer, 'G') or cpm_analyzer.G is None:
        raise ValueError("CPM analysis must be performed first")
    
    G = cpm_analyzer.G
    
    for node_id in G.nodes():
        if node_id in ['Start', 'End', 'START', 'END']:
            continue
        
        node_data = G.nodes[node_id]
        
        # Get predecessors and successors
        predecessors = list(G.predecessors(node_id))
        predecessors = [p for p in predecessors if p not in ['Start', 'START']]
        
        successors = list(G.successors(node_id))
        successors = [s for s in successors if s not in ['End', 'END']]
        
        # Get cash flow for this activity
        cash_flow = cash_flows.get(node_id, 0.0)
        
        activity = CashFlowActivity(
            id=node_id,
            duration=int(node_data.get('duration', 0)),
            cash_flow=float(cash_flow),
            es=int(node_data.get('ES', 0)),
            ef=int(node_data.get('EF', 0)),
            ls=int(node_data.get('LS', 0)),
            lf=int(node_data.get('LF', 0)),
            float=int(node_data.get('float', 0)),
            predecessors=predecessors,
            successors=successors
        )
        
        activities.append(activity)
    
    logger.info(f"Converted {len(activities)} activities with cash flows from CPM analysis")
    return activities
