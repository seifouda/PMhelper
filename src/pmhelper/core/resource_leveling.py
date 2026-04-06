"""
Resource Leveling Module

Implements resource leveling and smoothing algorithms to optimize resource
utilization across project schedules. Supports minimum moment method and
Burgess method for resource optimization.

Author: PMHelper Team
Version: 1.1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import logging
import copy

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step recording data class
# ---------------------------------------------------------------------------

@dataclass
class LevelingStep:
    """One recorded step from the resource-leveling algorithm.

    Emitted each time an activity is actually moved during iterative leveling.
    """
    step_number: int
    activity_id: str
    from_start: int       # start time before this move
    to_start: int         # start time after this move
    metric_before: float  # moment / Burgess cost before the move
    metric_after: float   # metric after the move
    reason: str           # human-readable explanation
    profile: "Dict[int, float]"  # resource profile snapshot after the move


@dataclass
class Activity:
    """Represents an activity with scheduling and resource information"""
    id: str
    duration: int
    resource_demand: float
    es: int  # Early Start
    ef: int  # Early Finish
    ls: int  # Late Start
    lf: int  # Late Finish
    float: int  # Total Float
    predecessors: List[str]
    successors: List[str]


class ResourceProfile:
    """Calculate and manage resource usage over time"""

    def __init__(self, schedule: Dict[str, int], activities: List[Activity]):
        """
        Initialize resource profile calculator.
        
        Args:
            schedule: Dictionary mapping activity ID to start time
            activities: List of Activity objects with resource demands
        
        Example:
            >>> schedule = {'A': 0, 'B': 4, 'C': 4}
            >>> activities = [Activity('A', 4, 5.0, 0, 4, 0, 4, 0, [], ['B'])]
            >>> profile = ResourceProfile(schedule, activities)
        """
        self.schedule = schedule
        self.activities = {act.id: act for act in activities}
        self.profile = self._calculate_profile()
        logger.info(f"Initialized ResourceProfile with {len(activities)} activities")

    def _calculate_profile(self) -> Dict[int, float]:
        """
        Calculate resource usage at each time period.
        
        Returns:
            Dictionary mapping time period to resource usage
        """
        profile = {}
        
        # Find time range
        max_time = 0
        for act_id, start_time in self.schedule.items():
            if act_id in self.activities:
                activity = self.activities[act_id]
                end_time = start_time + activity.duration
                max_time = max(max_time, end_time)
        
        # Calculate usage at each time period
        for t in range(max_time + 1):
            usage = 0.0
            for act_id, start_time in self.schedule.items():
                if act_id in self.activities:
                    activity = self.activities[act_id]
                    end_time = start_time + activity.duration
                    # Activity is active during [start_time, end_time)
                    if start_time <= t < end_time:
                        usage += activity.resource_demand
            profile[t] = usage
        
        return profile

    def calculate_moment(self) -> float:
        """
        Calculate resource moment (sum of squared deviations from mean).
        
        The moment is a measure of resource usage variability.
        Lower moments indicate smoother resource utilization.
        
        Returns:
            Resource moment value
        """
        usage_values = list(self.profile.values())
        if not usage_values:
            return 0.0
        
        mean_usage = sum(usage_values) / len(usage_values)
        moment = sum((u - mean_usage) ** 2 for u in usage_values)
        
        return moment

    def get_mean_usage(self) -> float:
        """Return mean (average) resource usage across all periods."""
        if not self.profile:
            return 0.0
        return sum(self.profile.values()) / len(self.profile)

    def get_peak_usage(self) -> float:
        """
        Get maximum resource usage across all time periods.
        
        Returns:
            Peak resource usage value
        """
        if not self.profile:
            return 0.0
        return max(self.profile.values())

    def get_utilization(self, resource_limit: float) -> float:
        """
        Calculate resource utilization percentage.
        
        Args:
            resource_limit: Available resource capacity per time period
            
        Returns:
            Average utilization as percentage (0-100)
        """
        if resource_limit <= 0:
            return 0.0
        
        usage_values = list(self.profile.values())
        if not usage_values:
            return 0.0
        
        total_usage = sum(usage_values)
        total_capacity = resource_limit * len(usage_values)
        
        utilization = (total_usage / total_capacity) * 100
        return utilization

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert profile to DataFrame for plotting and analysis.
        
        Returns:
            DataFrame with columns: time, resource_usage
        """
        data = [{'time': t, 'resource_usage': usage} 
                for t, usage in sorted(self.profile.items())]
        return pd.DataFrame(data)

    def is_feasible(self, resource_limit: float) -> bool:
        """
        Check if schedule is feasible given resource limit.
        
        Args:
            resource_limit: Maximum available resources per period
            
        Returns:
            True if all periods are within resource limit
        """
        return self.get_peak_usage() <= resource_limit

    def get_overutilized_periods(self, resource_limit: float) -> List[int]:
        """
        Get time periods where resource usage exceeds limit.
        
        Args:
            resource_limit: Maximum available resources per period
            
        Returns:
            List of time periods with overutilization
        """
        return [t for t, usage in self.profile.items() 
                if usage > resource_limit]


class MinimumMomentLeveling:
    """Resource leveling using minimum moment method"""

    def __init__(self, activities: List[Activity], 
                 resource_limit: Optional[float] = None):
        """
        Initialize minimum moment leveling algorithm.
        
        Args:
            activities: List of Activity objects
            resource_limit: Optional resource constraint (if None, no limit)
        
        Example:
            >>> leveling = MinimumMomentLeveling(activities, resource_limit=10)
            >>> result = leveling.level()
        """
        self.activities = {act.id: act for act in activities}
        self.resource_limit = resource_limit
        self.original_schedule = {act.id: act.es for act in activities}
        logger.info(f"Initialized MinimumMomentLeveling with {len(activities)} activities")

    def level(self, max_iterations: int = 1000,
              record_steps: bool = False) -> dict:
        """
        Perform resource leveling using minimum moment method.
        
        Algorithm:
        1. Start with early start schedule
        2. Iteratively shift non-critical activities to reduce moment
        3. Test all feasible positions within float
        4. Stop when no improvement or max iterations reached
        
        Args:
            max_iterations: Maximum number of iterations
            record_steps: If True, record each move as a LevelingStep
            
        Returns:
            Dictionary with leveling results including:
            - leveled_schedule: Dict mapping activity ID to start time
            - original_moment: Moment before leveling
            - leveled_moment: Moment after leveling
            - improvement: Percentage improvement
            - iterations: Number of iterations performed
            - peak_usage_original: Peak resource usage before
            - peak_usage_leveled: Peak resource usage after
            - steps: List[LevelingStep] if record_steps=True else []
        """
        # Start with early start schedule
        current_schedule = self.original_schedule.copy()
        activities_list = list(self.activities.values())
        
        # Calculate original profile
        original_profile = ResourceProfile(current_schedule, activities_list)
        original_moment = original_profile.calculate_moment()
        best_moment = original_moment
        
        logger.info(f"Starting leveling - Original moment: {original_moment:.2f}")
        
        # Get non-critical activities (those with float > 0)
        non_critical = [act for act in activities_list if act.float > 0]
        
        if not non_critical:
            logger.info("No non-critical activities to level")
            return self._create_result(current_schedule, activities_list, 
                                      original_moment, original_moment, 0, [])
        
        improved = True
        iteration = 0
        steps: List[LevelingStep] = []
        step_num = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            # Try to improve by shifting each non-critical activity
            for activity in non_critical:
                best_position = current_schedule[activity.id]
                
                # Try all positions within the activity's float
                min_start = activity.es
                max_start = activity.ls
                
                for start_time in range(min_start, max_start + 1):
                    # Create test schedule
                    test_schedule = current_schedule.copy()
                    test_schedule[activity.id] = start_time
                    
                    # Check resource constraint if specified
                    if self.resource_limit is not None:
                        test_profile = ResourceProfile(test_schedule, activities_list)
                        if not test_profile.is_feasible(self.resource_limit):
                            continue
                    
                    # Calculate moment
                    test_profile = ResourceProfile(test_schedule, activities_list)
                    test_moment = test_profile.calculate_moment()
                    
                    # Update if better
                    if test_moment < best_moment:
                        best_moment = test_moment
                        best_position = start_time
                        improved = True
                
                # Apply best position if found
                if best_position != current_schedule[activity.id]:
                    old_pos = current_schedule[activity.id]
                    current_schedule[activity.id] = best_position
                    logger.debug(f"Iteration {iteration}: Moved {activity.id} to time {best_position}")
                    if record_steps:
                        step_num += 1
                        prof = ResourceProfile(current_schedule, activities_list)
                        new_moment = prof.calculate_moment()
                        steps.append(LevelingStep(
                            step_number=step_num,
                            activity_id=activity.id,
                            from_start=old_pos,
                            to_start=best_position,
                            metric_before=best_moment
                            if len(steps) == 0 else steps[-1].metric_after
                            if steps else original_moment,
                            metric_after=new_moment,
                            reason=(
                                f"Activity {activity.id} shifted from day {old_pos} "
                                f"to day {best_position} "
                                f"(float={activity.float}, resource={activity.resource_demand}) "
                                f"— moment reduced from {original_moment:.1f}"
                            ),
                            profile=dict(prof.profile),
                        ))
        
        logger.info(f"Leveling complete after {iteration} iterations")
        logger.info(f"Final moment: {best_moment:.2f}")
        
        return self._create_result(current_schedule, activities_list,
                                   original_moment, best_moment, iteration, steps)

    def _create_result(self, schedule: Dict[str, int], 
                       activities: List[Activity],
                       original_moment: float, 
                       leveled_moment: float,
                       iterations: int,
                       steps: "List[LevelingStep]" = None) -> dict:
        """Create result dictionary with all metrics"""
        original_profile = ResourceProfile(self.original_schedule, activities)
        leveled_profile = ResourceProfile(schedule, activities)
        
        improvement = 0.0
        if original_moment > 0:
            improvement = ((original_moment - leveled_moment) / original_moment) * 100
        
        return {
            'leveled_schedule': schedule,
            'original_schedule': self.original_schedule,
            'original_moment': original_moment,
            'leveled_moment': leveled_moment,
            'improvement_pct': improvement,
            'iterations': iterations,
            'peak_usage_original': original_profile.get_peak_usage(),
            'peak_usage_leveled': leveled_profile.get_peak_usage(),
            'original_profile': original_profile,
            'leveled_profile': leveled_profile,
            'feasible': (leveled_profile.is_feasible(self.resource_limit) 
                        if self.resource_limit else True),
            'steps': steps or [],
        }


class BurgessLeveling:
    """Burgess method for resource smoothing"""

    def __init__(self, activities: List[Activity],
                 resource_limit: Optional[float] = None):
        """
        Initialize Burgess leveling algorithm.
        
        The Burgess method minimizes the sum of squares of resource usage.
        
        Args:
            activities: List of Activity objects
            resource_limit: Optional resource constraint
        """
        self.activities = {act.id: act for act in activities}
        self.resource_limit = resource_limit
        self.original_schedule = {act.id: act.es for act in activities}
        logger.info(f"Initialized BurgessLeveling with {len(activities)} activities")

    def level(self, max_iterations: int = 1000,
              record_steps: bool = False) -> dict:
        """
        Perform resource leveling using Burgess method.
        
        Burgess method minimizes sum of squares of resource usage
        at each time period.
        
        Args:
            max_iterations: Maximum number of iterations
            record_steps: If True, record each move as a LevelingStep
            
        Returns:
            Dictionary with leveling results
        """
        current_schedule = self.original_schedule.copy()
        activities_list = list(self.activities.values())
        
        # Calculate original cost (sum of squares)
        original_profile = ResourceProfile(current_schedule, activities_list)
        original_cost = self._calculate_burgess_cost(original_profile)
        best_cost = original_cost
        
        logger.info(f"Starting Burgess leveling - Original cost: {original_cost:.2f}")
        
        non_critical = [act for act in activities_list if act.float > 0]
        
        if not non_critical:
            logger.info("No non-critical activities to level")
            return self._create_result(current_schedule, activities_list,
                                      original_cost, original_cost, 0, [])
        
        improved = True
        iteration = 0
        steps: List[LevelingStep] = []
        step_num = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for activity in non_critical:
                best_position = current_schedule[activity.id]
                
                for start_time in range(activity.es, activity.ls + 1):
                    test_schedule = current_schedule.copy()
                    test_schedule[activity.id] = start_time
                    
                    # Check resource constraint
                    test_profile = ResourceProfile(test_schedule, activities_list)
                    if self.resource_limit and not test_profile.is_feasible(self.resource_limit):
                        continue
                    
                    # Calculate Burgess cost
                    test_cost = self._calculate_burgess_cost(test_profile)
                    
                    if test_cost < best_cost:
                        best_cost = test_cost
                        best_position = start_time
                        improved = True
                
                if best_position != current_schedule[activity.id]:
                    old_pos = current_schedule[activity.id]
                    current_schedule[activity.id] = best_position
                    if record_steps:
                        step_num += 1
                        prof = ResourceProfile(current_schedule, activities_list)
                        new_cost = self._calculate_burgess_cost(prof)
                        prev_metric = (steps[-1].metric_after if steps else original_cost)
                        steps.append(LevelingStep(
                            step_number=step_num,
                            activity_id=activity.id,
                            from_start=old_pos,
                            to_start=best_position,
                            metric_before=prev_metric,
                            metric_after=new_cost,
                            reason=(
                                f"Activity {activity.id} shifted from day {old_pos} "
                                f"to day {best_position} "
                                f"(float={activity.float}, resource={activity.resource_demand}) "
                                f"— Burgess cost reduced from {original_cost:.1f}"
                            ),
                            profile=dict(prof.profile),
                        ))
        
        logger.info(f"Burgess leveling complete after {iteration} iterations")
        logger.info(f"Final cost: {best_cost:.2f}")
        
        return self._create_result(current_schedule, activities_list,
                                   original_cost, best_cost, iteration, steps)

    def _calculate_burgess_cost(self, profile: ResourceProfile) -> float:
        """
        Calculate Burgess cost (sum of squares of resource usage).
        
        Args:
            profile: ResourceProfile object
            
        Returns:
            Sum of squares of resource usage
        """
        return sum(usage ** 2 for usage in profile.profile.values())

    def _create_result(self, schedule: Dict[str, int],
                       activities: List[Activity],
                       original_cost: float,
                       leveled_cost: float,
                       iterations: int,
                       steps: "List[LevelingStep]" = None) -> dict:
        """Create result dictionary with all metrics"""
        original_profile = ResourceProfile(self.original_schedule, activities)
        leveled_profile = ResourceProfile(schedule, activities)
        
        improvement = 0.0
        if original_cost > 0:
            improvement = ((original_cost - leveled_cost) / original_cost) * 100
        
        return {
            'leveled_schedule': schedule,
            'original_schedule': self.original_schedule,
            'original_cost': original_cost,
            'leveled_cost': leveled_cost,
            'improvement_pct': improvement,
            'iterations': iterations,
            'peak_usage_original': original_profile.get_peak_usage(),
            'peak_usage_leveled': leveled_profile.get_peak_usage(),
            'original_profile': original_profile,
            'leveled_profile': leveled_profile,
            'original_moment': original_profile.calculate_moment(),
            'leveled_moment': leveled_profile.calculate_moment(),
            'feasible': (leveled_profile.is_feasible(self.resource_limit)
                        if self.resource_limit else True),
            'steps': steps or [],
        }


class ResourceLevelingFactory:
    """Factory to create resource leveling algorithms"""

    @staticmethod
    def create(method: str, activities: List[Activity], 
               resource_limit: Optional[float] = None):
        """
        Create a resource leveling algorithm instance.
        
        Args:
            method: Algorithm name ('minimum_moment' or 'burgess')
            activities: List of Activity objects
            resource_limit: Optional resource constraint
            
        Returns:
            Instance of leveling algorithm
            
        Raises:
            ValueError: If method is not recognized
            
        Example:
            >>> leveler = ResourceLevelingFactory.create('minimum_moment', activities, 10)
            >>> result = leveler.level()
        """
        methods = {
            'minimum_moment': MinimumMomentLeveling,
            'burgess': BurgessLeveling,
        }
        
        if method not in methods:
            raise ValueError(f"Unknown method: {method}. Available: {list(methods.keys())}")
        
        return methods[method](activities, resource_limit)


def activities_from_cpm(cpm_analyzer) -> List[Activity]:
    """
    Convert CPM analyzer results to Activity objects for resource leveling.
    
    Args:
        cpm_analyzer: CPMAnalyzer instance with completed analysis
        
    Returns:
        List of Activity objects
        
    Example:
        >>> cpm = CPMAnalyzer()
        >>> cpm.analyze(activity_data)
        >>> activities = activities_from_cpm(cpm)
        >>> leveler = MinimumMomentLeveling(activities)
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
        
        activity = Activity(
            id=node_id,
            duration=int(node_data.get('duration', 0)),
            resource_demand=float(node_data.get('resource_demand', 0)),
            es=int(node_data.get('ES', 0)),
            ef=int(node_data.get('EF', 0)),
            ls=int(node_data.get('LS', 0)),
            lf=int(node_data.get('LF', 0)),
            float=int(node_data.get('float', 0)),
            predecessors=predecessors,
            successors=successors
        )
        
        activities.append(activity)
    
    logger.info(f"Converted {len(activities)} activities from CPM analysis")
    return activities
