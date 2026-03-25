"""
Tests for Multi-Objective Optimization Module

Comprehensive tests for Pareto frontier analysis, dominance checking,
and schedule generation.
"""

import pytest
import pandas as pd
import numpy as np
from src.pmhelper.core.multi_objective import (
    MultiObjectiveOptimizer, Solution, ScheduleGenerator
)


class TestSolution:
    """Tests for Solution dataclass"""
    
    def test_create_solution(self):
        """Test creating a solution"""
        schedule = {'A': 0, 'B': 3}
        objectives = {'duration': 10, 'cost': 5000, 'npv': 8000}
        
        solution = Solution(schedule=schedule, objectives=objectives)
        
        assert solution.schedule == schedule
        assert solution.objectives == objectives
        assert solution.metadata == {}
    
    def test_solution_with_metadata(self):
        """Test solution with custom metadata"""
        schedule = {'A': 0}
        objectives = {'duration': 5}
        metadata = {'iteration': 10, 'strategy': 'early'}
        
        solution = Solution(schedule, objectives, metadata)
        
        assert solution.metadata == metadata


class TestMultiObjectiveOptimizer:
    """Tests for MultiObjectiveOptimizer class"""
    
    @pytest.fixture
    def simple_objectives(self):
        """Create simple objective functions"""
        def duration(schedule):
            return max(schedule.values()) + 3  # Simplified
        
        def cost(schedule):
            return sum(schedule.values()) * 100
        
        return {'duration': duration, 'cost': cost}
    
    @pytest.fixture
    def optimizer(self, simple_objectives):
        """Create optimizer for testing"""
        return MultiObjectiveOptimizer(simple_objectives)
    
    def test_initialization(self, optimizer):
        """Test optimizer initialization"""
        assert len(optimizer.objective_functions) == 2
        assert 'duration' in optimizer.objective_functions
        assert 'cost' in optimizer.objective_functions
        assert len(optimizer.solutions) == 0
        assert len(optimizer.pareto_frontier) == 0
    
    def test_evaluate_solution(self, optimizer):
        """Test evaluating a single solution"""
        schedule = {'A': 0, 'B': 3, 'C': 5}
        solution = optimizer.evaluate_solution(schedule)
        
        assert isinstance(solution, Solution)
        assert solution.schedule == schedule
        assert 'duration' in solution.objectives
        assert 'cost' in solution.objectives
        assert solution.objectives['duration'] == 8  # max(5) + 3
        assert solution.objectives['cost'] == 800  # (0+3+5)*100
    
    def test_add_solution(self, optimizer):
        """Test adding solutions to set"""
        schedule = {'A': 0}
        solution = optimizer.evaluate_solution(schedule)
        
        optimizer.add_solution(solution)
        
        assert len(optimizer.solutions) == 1
    
    def test_dominates_minimization(self):
        """Test dominance checking with minimization objectives"""
        objectives = {
            'duration': lambda s: s.get('val', 0),
            'cost': lambda s: s.get('val', 0)
        }
        optimizer = MultiObjectiveOptimizer(objectives)
        
        # Solution 1: duration=5, cost=100 (better)
        sol1 = Solution({'val': 1}, {'duration': 5, 'cost': 100})
        
        # Solution 2: duration=10, cost=200 (worse)
        sol2 = Solution({'val': 2}, {'duration': 10, 'cost': 200})
        
        # sol1 should dominate sol2 (both objectives minimized)
        assert optimizer.dominates(sol1, sol2, ['duration', 'cost'])
        assert not optimizer.dominates(sol2, sol1, ['duration', 'cost'])
    
    def test_dominates_mixed(self):
        """Test dominance with mixed minimize/maximize objectives"""
        objectives = {
            'duration': lambda s: s.get('val', 0),
            'npv': lambda s: s.get('val', 0)
        }
        optimizer = MultiObjectiveOptimizer(objectives)
        
        # Solution 1: duration=5 (min), npv=1000 (max)
        sol1 = Solution({'val': 1}, {'duration': 5, 'npv': 1000})
        
        # Solution 2: duration=10 (worse), npv=500 (worse)
        sol2 = Solution({'val': 2}, {'duration': 10, 'npv': 500})
        
        # sol1 dominates sol2: better duration (lower) and better npv (higher)
        minimize_objectives = ['duration']  # Only duration minimized, npv maximized
        assert optimizer.dominates(sol1, sol2, minimize_objectives)
    
    def test_no_dominance_tradeoff(self):
        """Test no dominance when solutions trade off"""
        objectives = {
            'duration': lambda s: s.get('val', 0),
            'cost': lambda s: s.get('val', 0)
        }
        optimizer = MultiObjectiveOptimizer(objectives)
        
        # Solution 1: duration=5, cost=200 (fast but expensive)
        sol1 = Solution({'val': 1}, {'duration': 5, 'cost': 200})
        
        # Solution 2: duration=10, cost=100 (slow but cheap)
        sol2 = Solution({'val': 2}, {'duration': 10, 'cost': 100})
        
        # Neither dominates (trade-off)
        assert not optimizer.dominates(sol1, sol2, ['duration', 'cost'])
        assert not optimizer.dominates(sol2, sol1, ['duration', 'cost'])
    
    def test_compute_pareto_frontier_simple(self):
        """Test Pareto frontier computation"""
        objectives = {
            'duration': lambda s: s['duration'],
            'cost': lambda s: s['cost']
        }
        optimizer = MultiObjectiveOptimizer(objectives)
        
        # Add solutions
        # Dominated: (10, 200)
        optimizer.add_solution(Solution({'duration': 10, 'cost': 200}, 
                                       {'duration': 10, 'cost': 200}))
        
        # Pareto: (5, 150) - fast, medium cost
        optimizer.add_solution(Solution({'duration': 5, 'cost': 150}, 
                                       {'duration': 5, 'cost': 150}))
        
        # Pareto: (8, 100) - medium speed, cheap
        optimizer.add_solution(Solution({'duration': 8, 'cost': 100}, 
                                       {'duration': 8, 'cost': 100}))
        
        # Pareto: (12, 80) - slow, very cheap
        optimizer.add_solution(Solution({'duration': 12, 'cost': 80}, 
                                       {'duration': 12, 'cost': 80}))
        
        frontier = optimizer.compute_pareto_frontier(['duration', 'cost'])
        
        # Should have 3 Pareto solutions (all except (10, 200))
        assert len(frontier) == 3
    
    def test_compute_pareto_frontier_all_pareto(self):
        """Test when all solutions are on Pareto frontier"""
        objectives = {
            'duration': lambda s: s['duration'],
            'cost': lambda s: s['cost']
        }
        optimizer = MultiObjectiveOptimizer(objectives)
        
        # All solutions trade off perfectly
        optimizer.add_solution(Solution({'duration': 5, 'cost': 200}, 
                                       {'duration': 5, 'cost': 200}))
        optimizer.add_solution(Solution({'duration': 10, 'cost': 100}, 
                                       {'duration': 10, 'cost': 100}))
        optimizer.add_solution(Solution({'duration': 15, 'cost': 50}, 
                                       {'duration': 15, 'cost': 50}))
        
        frontier = optimizer.compute_pareto_frontier(['duration', 'cost'])
        
        assert len(frontier) == 3  # All are Pareto
    
    def test_get_solution_summary(self):
        """Test getting solution summary DataFrame"""
        objectives = {'duration': lambda s: s['val']}
        optimizer = MultiObjectiveOptimizer(objectives)
        
        optimizer.add_solution(Solution({'val': 5}, {'duration': 5}))
        optimizer.add_solution(Solution({'val': 10}, {'duration': 10}))
        
        optimizer.compute_pareto_frontier(['duration'])
        
        summary = optimizer.get_solution_summary()
        
        assert isinstance(summary, pd.DataFrame)
        assert len(summary) == 2
        assert 'solution_id' in summary.columns
        assert 'duration' in summary.columns
        assert 'is_pareto' in summary.columns
    
    def test_get_pareto_summary(self):
        """Test getting Pareto frontier summary"""
        objectives = {'duration': lambda s: s['val']}
        optimizer = MultiObjectiveOptimizer(objectives)
        
        optimizer.add_solution(Solution({'val': 5}, {'duration': 5}))
        optimizer.add_solution(Solution({'val': 10}, {'duration': 10}))
        
        optimizer.compute_pareto_frontier(['duration'])
        
        pareto_summary = optimizer.get_pareto_summary()
        
        assert isinstance(pareto_summary, pd.DataFrame)
        assert len(pareto_summary) > 0
        assert 'pareto_rank' in pareto_summary.columns
    
    def test_find_tradeoffs(self):
        """Test finding trade-offs between objectives"""
        objectives = {
            'duration': lambda s: s['duration'],
            'cost': lambda s: s['cost']
        }
        optimizer = MultiObjectiveOptimizer(objectives)
        
        optimizer.add_solution(Solution({'duration': 5, 'cost': 200}, 
                                       {'duration': 5, 'cost': 200}))
        optimizer.add_solution(Solution({'duration': 10, 'cost': 150}, 
                                       {'duration': 10, 'cost': 150}))
        optimizer.add_solution(Solution({'duration': 15, 'cost': 100}, 
                                       {'duration': 15, 'cost': 100}))
        
        optimizer.compute_pareto_frontier(['duration', 'cost'])
        
        tradeoffs = optimizer.find_tradeoffs('duration', 'cost')
        
        assert isinstance(tradeoffs, pd.DataFrame)
        assert 'marginal_rate' in tradeoffs.columns
        assert len(tradeoffs) == 2  # n-1 transitions for n solutions
    
    def test_generate_solutions_grid(self):
        """Test generating solutions from schedule grid"""
        objectives = {
            'duration': lambda s: max(s.values()) if s else 0,
            'cost': lambda s: sum(s.values()) if s else 0
        }
        optimizer = MultiObjectiveOptimizer(objectives)
        
        schedules = [
            {'A': 0, 'B': 3},
            {'A': 0, 'B': 5},
            {'A': 0, 'B': 7}
        ]
        
        frontier = optimizer.generate_solutions_grid(schedules, ['duration', 'cost'])
        
        assert len(optimizer.solutions) == 3
        assert len(frontier) > 0
    
    def test_empty_solutions(self):
        """Test behavior with no solutions"""
        objectives = {'duration': lambda s: 0}
        optimizer = MultiObjectiveOptimizer(objectives)
        
        frontier = optimizer.compute_pareto_frontier(['duration'])
        
        assert len(frontier) == 0
    
    def test_single_solution(self):
        """Test with single solution"""
        objectives = {'duration': lambda s: s['val']}
        optimizer = MultiObjectiveOptimizer(objectives)
        
        optimizer.add_solution(Solution({'val': 5}, {'duration': 5}))
        frontier = optimizer.compute_pareto_frontier(['duration'])
        
        assert len(frontier) == 1  # Only solution is on frontier


class TestScheduleGenerator:
    """Tests for ScheduleGenerator class"""
    
    @pytest.fixture
    def activities_with_float(self):
        """Create activities with float"""
        class Activity:
            def __init__(self, id, es, ls, float_val):
                self.id = id
                self.es = es
                self.ls = ls
                self.float = float_val
        
        return [
            Activity('A', 0, 0, 0),      # Critical
            Activity('B', 3, 5, 2),      # 2 days float
            Activity('C', 7, 10, 3)      # 3 days float
        ]
    
    def test_generate_all_feasible_small(self, activities_with_float):
        """Test generating all feasible schedules for small project"""
        schedules = ScheduleGenerator.generate_all_feasible(activities_with_float)
        
        # A: 1 position, B: 3 positions (3,4,5), C: 4 positions (7,8,9,10)
        # Total: 1 * 3 * 4 = 12 schedules
        assert len(schedules) == 12
        
        # All schedules should have A at 0
        for schedule in schedules:
            assert schedule['A'] == 0
    
    def test_generate_all_feasible_critical_only(self):
        """Test with only critical activities"""
        class Activity:
            def __init__(self, id, es):
                self.id = id
                self.es = es
                self.float = 0
        
        activities = [Activity('A', 0), Activity('B', 3)]
        
        schedules = ScheduleGenerator.generate_all_feasible(activities)
        
        # Only one schedule possible
        assert len(schedules) == 1
        assert schedules[0] == {'A': 0, 'B': 3}
    
    def test_generate_sampled(self, activities_with_float):
        """Test sampling schedules"""
        num_samples = 50
        schedules = ScheduleGenerator.generate_sampled(activities_with_float, num_samples)
        
        assert len(schedules) == num_samples
        
        # Should include early and late start schedules
        early_schedule = {'A': 0, 'B': 3, 'C': 7}
        late_schedule = {'A': 0, 'B': 5, 'C': 10}
        
        assert early_schedule in schedules
        assert late_schedule in schedules
    
    def test_generate_heuristic_early(self, activities_with_float):
        """Test early start heuristic"""
        schedules = ScheduleGenerator.generate_heuristic(activities_with_float, ['early'])
        
        assert len(schedules) == 1
        schedule = schedules[0]
        
        assert schedule['A'] == 0
        assert schedule['B'] == 3  # Early start
        assert schedule['C'] == 7  # Early start
    
    def test_generate_heuristic_late(self, activities_with_float):
        """Test late start heuristic"""
        schedules = ScheduleGenerator.generate_heuristic(activities_with_float, ['late'])
        
        assert len(schedules) == 1
        schedule = schedules[0]
        
        assert schedule['A'] == 0  # Critical, must be 0
        assert schedule['B'] == 5  # Late start
        assert schedule['C'] == 10  # Late start
    
    def test_generate_heuristic_middle(self, activities_with_float):
        """Test middle position heuristic"""
        schedules = ScheduleGenerator.generate_heuristic(activities_with_float, ['middle'])
        
        assert len(schedules) == 1
        schedule = schedules[0]
        
        assert schedule['B'] == 4  # (3+5)//2
        assert schedule['C'] == 8  # (7+10)//2
    
    def test_generate_heuristic_multiple(self, activities_with_float):
        """Test multiple heuristic strategies"""
        strategies = ['early', 'late', 'middle']
        schedules = ScheduleGenerator.generate_heuristic(activities_with_float, strategies)
        
        assert len(schedules) == 3
    
    def test_generate_heuristic_cash_flow(self):
        """Test cash flow-based heuristics"""
        class Activity:
            def __init__(self, id, es, ls, cash_flow):
                self.id = id
                self.es = es
                self.ls = ls
                self.float = ls - es
                self.cash_flow = cash_flow
        
        activities = [
            Activity('A', 0, 2, 10000),   # Positive cash flow
            Activity('B', 3, 5, -5000)    # Negative cash flow
        ]
        
        schedules = ScheduleGenerator.generate_heuristic(activities, ['cash_flow_early'])
        schedule = schedules[0]
        
        # Positive cash flow scheduled early
        assert schedule['A'] == 0
        # Negative cash flow scheduled late
        assert schedule['B'] == 5
    
    def test_max_combinations_sampling(self):
        """Test that large combination spaces trigger sampling"""
        class Activity:
            def __init__(self, id, es, ls):
                self.id = id
                self.es = es
                self.ls = ls
                self.float = ls - es
        
        # Create activities with large combination space
        activities = [Activity(f'A{i}', 0, 10) for i in range(5)]
        # 11^5 = 161,051 combinations would be generated
        
        max_combinations = 100
        schedules = ScheduleGenerator.generate_all_feasible(activities, max_combinations)
        
        # Should sample instead of generating all
        assert len(schedules) <= max_combinations


class TestIntegration:
    """Integration tests combining optimizer and generator"""
    
    def test_full_workflow(self):
        """Test complete multi-objective optimization workflow"""
        # Define activities
        class Activity:
            def __init__(self, id, es, ls, duration, cost, cash_flow):
                self.id = id
                self.es = es
                self.ls = ls
                self.float = ls - es
                self.duration = duration
                self.cost = cost
                self.cash_flow = cash_flow
        
        activities = [
            Activity('A', 0, 0, 3, 1000, 5000),
            Activity('B', 3, 5, 2, 800, -2000)
        ]
        
        # Define objectives
        def duration(schedule):
            max_time = 0
            for act in activities:
                finish = schedule.get(act.id, act.es) + act.duration
                max_time = max(max_time, finish)
            return max_time
        
        def cost(schedule):
            return sum(act.cost for act in activities)
        
        def npv(schedule):
            total = 0
            for act in activities:
                finish = schedule.get(act.id, act.es) + act.duration
                pv = act.cash_flow / ((1.1) ** finish)
                total += pv
            return -total  # Negative to minimize (we want to maximize NPV)
        
        objectives = {'duration': duration, 'cost': cost, 'npv': npv}
        
        # Generate schedules
        schedules = ScheduleGenerator.generate_sampled(activities, 20)
        
        # Optimize
        optimizer = MultiObjectiveOptimizer(objectives)
        frontier = optimizer.generate_solutions_grid(schedules, ['duration', 'cost', 'npv'])
        
        assert len(frontier) > 0
        assert len(optimizer.solutions) == 20
        
        # Get summaries
        summary = optimizer.get_solution_summary()
        assert not summary.empty
        
        pareto_summary = optimizer.get_pareto_summary()
        assert not pareto_summary.empty
