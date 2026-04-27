"""
Multi-Objective Optimization Module

Implements Pareto frontier analysis for simultaneous optimization of
multiple conflicting objectives (duration, cost, NPV).

Author: PMHelper Team
Version: 1.1.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Callable
from dataclasses import dataclass
import logging
import itertools

logger = logging.getLogger(__name__)


@dataclass
class Solution:
    """A single solution in the multi-objective space"""
    schedule: Dict[str, int]  # Activity start times
    # Objective values (duration, cost, npv, etc.)
    objectives: Dict[str, float]
    metadata: Dict = None  # Additional info

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MultiObjectiveOptimizer:
    """Multi-objective optimization with Pareto frontier analysis"""

    def __init__(self, objective_functions: Dict[str, Callable]):
        """
        Initialize multi-objective optimizer.

        Args:
            objective_functions: Dictionary mapping objective name to evaluation function
                               Each function should take a schedule and return a scalar value

        Example:
            >>> objectives = {
            ...     'duration': lambda s: calculate_duration(s),
            ...     'cost': lambda s: calculate_cost(s),
            ...     'npv': lambda s: -calculate_npv(s)  # Negative to minimize
            ... }
            >>> optimizer = MultiObjectiveOptimizer(objectives)
        """
        self.objective_functions = objective_functions
        self.solutions: List[Solution] = []
        self.pareto_frontier: List[Solution] = []
        logger.info(
            f"Initialized MultiObjectiveOptimizer with objectives: {
                list(
                    objective_functions.keys())}")

    def evaluate_solution(
            self, schedule: Dict[str, int], metadata: Dict = None) -> Solution:
        """
        Evaluate a schedule against all objectives.

        Args:
            schedule: Activity start times
            metadata: Optional additional information

        Returns:
            Solution object with all objective values
        """
        objectives = {}

        for obj_name, obj_func in self.objective_functions.items():
            try:
                objectives[obj_name] = obj_func(schedule)
            except Exception as e:
                logger.warning(
                    f"Failed to evaluate objective '{obj_name}': {e}")
                objectives[obj_name] = float('inf')

        return Solution(
            schedule=schedule,
            objectives=objectives,
            metadata=metadata or {})

    def add_solution(self, solution: Solution):
        """Add a solution to the solution set"""
        self.solutions.append(solution)

    def dominates(self, sol1: Solution, sol2: Solution,
                  minimize_objectives: List[str] = None) -> bool:
        """
        Check if sol1 Pareto dominates sol2.

        A solution dominates another if it is at least as good in all objectives
        and strictly better in at least one.

        Args:
            sol1: First solution
            sol2: Second solution
            minimize_objectives: List of objectives to minimize (others are maximized)
                                If None, all objectives are minimized

        Returns:
            True if sol1 dominates sol2
        """
        if minimize_objectives is None:
            minimize_objectives = list(self.objective_functions.keys())

        at_least_as_good = True
        strictly_better_in_one = False

        for obj_name in self.objective_functions.keys():
            val1 = sol1.objectives.get(obj_name, float('inf'))
            val2 = sol2.objectives.get(obj_name, float('inf'))

            if obj_name in minimize_objectives:
                # Minimize: lower is better
                if val1 > val2:
                    at_least_as_good = False
                    break
                elif val1 < val2:
                    strictly_better_in_one = True
            else:
                # Maximize: higher is better
                if val1 < val2:
                    at_least_as_good = False
                    break
                elif val1 > val2:
                    strictly_better_in_one = True

        return at_least_as_good and strictly_better_in_one

    def compute_pareto_frontier(
            self,
            minimize_objectives: List[str] = None) -> List[Solution]:
        """
        Compute Pareto frontier from solution set.

        Args:
            minimize_objectives: List of objectives to minimize (others are maximized)

        Returns:
            List of non-dominated solutions (Pareto frontier)

        Example:
            >>> optimizer.add_solution(solution1)
            >>> optimizer.add_solution(solution2)
            >>> frontier = optimizer.compute_pareto_frontier(['duration', 'cost'])
        """
        if not self.solutions:
            logger.warning("No solutions to compute Pareto frontier")
            return []

        pareto_frontier = []

        for i, solution in enumerate(self.solutions):
            is_dominated = False

            for j, other in enumerate(self.solutions):
                if i != j and self.dominates(
                        other, solution, minimize_objectives):
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_frontier.append(solution)

        self.pareto_frontier = pareto_frontier
        logger.info(
            f"Pareto frontier contains {
                len(pareto_frontier)} of {
                len(
                    self.solutions)} solutions")

        return pareto_frontier

    def generate_solutions_grid(self,
                                schedules: List[Dict[str, int]],
                                minimize_objectives: List[str] = None) -> List[Solution]:
        """
        Generate solutions from a grid of schedules and compute Pareto frontier.

        Args:
            schedules: List of candidate schedules to evaluate
            minimize_objectives: List of objectives to minimize

        Returns:
            Pareto frontier solutions
        """
        self.solutions = []

        logger.info(f"Evaluating {len(schedules)} candidate solutions...")

        for i, schedule in enumerate(schedules):
            solution = self.evaluate_solution(
                schedule,
                metadata={'solution_id': i}
            )
            self.add_solution(solution)

        return self.compute_pareto_frontier(minimize_objectives)

    def get_solution_summary(self) -> pd.DataFrame:
        """
        Get summary DataFrame of all solutions.

        Returns:
            DataFrame with objectives and metadata for each solution
        """
        if not self.solutions:
            return pd.DataFrame()

        data = []
        for i, sol in enumerate(self.solutions):
            row = {'solution_id': i}
            row.update(sol.objectives)
            row['is_pareto'] = sol in self.pareto_frontier
            row.update(sol.metadata)
            data.append(row)

        return pd.DataFrame(data)

    def get_pareto_summary(self) -> pd.DataFrame:
        """Get summary of Pareto frontier solutions only"""
        if not self.pareto_frontier:
            return pd.DataFrame()

        data = []
        for i, sol in enumerate(self.pareto_frontier):
            row = {'pareto_rank': i + 1}
            row.update(sol.objectives)
            row.update(sol.metadata)
            data.append(row)

        return pd.DataFrame(data)

    def find_tradeoffs(self, obj1: str, obj2: str) -> pd.DataFrame:
        """
        Analyze trade-offs between two objectives on Pareto frontier.

        Args:
            obj1: First objective name
            obj2: Second objective name

        Returns:
            DataFrame showing marginal rates of substitution
        """
        if not self.pareto_frontier:
            return pd.DataFrame()

        # Sort by first objective
        sorted_frontier = sorted(
            self.pareto_frontier,
            key=lambda s: s.objectives.get(obj1, float('inf'))
        )

        tradeoffs = []
        for i in range(len(sorted_frontier) - 1):
            sol_current = sorted_frontier[i]
            sol_next = sorted_frontier[i + 1]

            delta_obj1 = sol_next.objectives[obj1] - \
                sol_current.objectives[obj1]
            delta_obj2 = sol_next.objectives[obj2] - \
                sol_current.objectives[obj2]

            # Marginal rate of substitution
            mrs = delta_obj2 / delta_obj1 if delta_obj1 != 0 else float('inf')

            tradeoffs.append({
                'from_solution': i,
                'to_solution': i + 1,
                f'{obj1}_current': sol_current.objectives[obj1],
                f'{obj1}_next': sol_next.objectives[obj1],
                f'delta_{obj1}': delta_obj1,
                f'{obj2}_current': sol_current.objectives[obj2],
                f'{obj2}_next': sol_next.objectives[obj2],
                f'delta_{obj2}': delta_obj2,
                'marginal_rate': mrs
            })

        return pd.DataFrame(tradeoffs)


class ScheduleGenerator:
    """Generate candidate schedules for multi-objective optimization"""

    @staticmethod
    def generate_all_feasible(
            activities: List, max_combinations: int = 10000) -> List[Dict[str, int]]:
        """
        Generate all feasible schedules within activity float ranges.

        Args:
            activities: List of activities with es, ls, float attributes
            max_combinations: Maximum number of schedules to generate

        Returns:
            List of feasible schedules

        Note:
            For large projects, this can generate huge numbers of schedules.
            Use sampling or heuristic methods for large problems.
        """
        schedules = []

        # Get non-critical activities (can be shifted)
        non_critical = [
            act for act in activities if hasattr(
                act, 'float') and act.float > 0]
        critical = [
            act for act in activities if not hasattr(
                act, 'float') or act.float == 0]

        if not non_critical:
            # Only one schedule possible
            schedule = {act.id: act.es for act in activities}
            return [schedule]

        # Generate position options for each non-critical activity
        position_options = []
        for act in non_critical:
            positions = list(range(act.es, act.ls + 1))
            position_options.append((act.id, positions))

        # Calculate total combinations
        total_combinations = 1
        for _, positions in position_options:
            total_combinations *= len(positions)

        if total_combinations > max_combinations:
            logger.warning(
                f"Would generate {total_combinations} schedules, sampling {max_combinations}")
            return ScheduleGenerator.generate_sampled(
                activities, max_combinations)

        # Generate all combinations
        logger.info(f"Generating {total_combinations} feasible schedules...")

        # Base schedule with critical activities
        base_schedule = {act.id: act.es for act in critical}

        # Generate all combinations of non-critical positions
        activity_ids = [act_id for act_id, _ in position_options]
        position_lists = [positions for _, positions in position_options]

        for combination in itertools.product(*position_lists):
            schedule = base_schedule.copy()
            for act_id, position in zip(activity_ids, combination):
                schedule[act_id] = position
            schedules.append(schedule)

        logger.info(f"Generated {len(schedules)} feasible schedules")
        return schedules

    @staticmethod
    def generate_sampled(
            activities: List, num_samples: int = 1000) -> List[Dict[str, int]]:
        """
        Generate random sample of feasible schedules.

        Args:
            activities: List of activities
            num_samples: Number of schedules to generate

        Returns:
            List of randomly sampled schedules
        """
        schedules = []

        # Always include boundary cases
        # 1. All early start
        schedules.append({act.id: act.es for act in activities})

        # 2. All late start
        schedules.append({act.id: act.ls for act in activities})

        # Generate random samples
        for _ in range(num_samples - 2):
            schedule = {}
            for act in activities:
                if hasattr(act, 'float') and act.float > 0:
                    # Random position within float range
                    start = np.random.randint(act.es, act.ls + 1)
                else:
                    # Critical activity - must use early start
                    start = act.es
                schedule[act.id] = start
            schedules.append(schedule)

        logger.info(f"Generated {len(schedules)} sampled schedules")
        return schedules

    @staticmethod
    def generate_heuristic(
            activities: List, strategies: List[str] = None) -> List[Dict[str, int]]:
        """
        Generate schedules using heuristic strategies.

        Args:
            activities: List of activities
            strategies: List of strategy names to apply
                       Options: 'early', 'late', 'middle', 'random', 'cash_flow_early', 'cash_flow_late'

        Returns:
            List of heuristically generated schedules
        """
        if strategies is None:
            strategies = ['early', 'late', 'middle']

        schedules = []

        for strategy in strategies:
            schedule = {}

            for act in activities:
                if strategy == 'early':
                    start = act.es
                elif strategy == 'late':
                    start = act.ls
                elif strategy == 'middle':
                    start = (act.es + act.ls) // 2
                elif strategy == 'random':
                    start = np.random.randint(act.es, act.ls + 1)
                elif strategy == 'cash_flow_early':
                    # Positive cash flow early, negative late
                    if hasattr(act, 'cash_flow') and act.cash_flow > 0:
                        start = act.es
                    else:
                        start = act.ls
                elif strategy == 'cash_flow_late':
                    # Negative cash flow early, positive late
                    if hasattr(act, 'cash_flow') and act.cash_flow < 0:
                        start = act.es
                    else:
                        start = act.ls
                else:
                    start = act.es

                schedule[act.id] = start

            schedules.append(schedule)

        logger.info(f"Generated {len(schedules)} heuristic schedules")
        return schedules
