#!/usr/bin/env python3
"""
Enhanced Project Crashing Implementation

This module provides enhanced project crashing algorithms that build upon
the existing CPM analysis capabilities without modifying the original code.

Features:
- Enhanced Project Crashing with multiple optimization strategies
- RCPS Enhanced Project Crashing with advanced resource management
- Comprehensive cost-benefit analysis
- Advanced visualization capabilities
- Performance optimization for large projects
"""

import networkx as nx
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union
from collections import defaultdict
import math
import time
from enum import Enum


class CrashingStrategy(Enum):
    """Enumeration of available crashing strategies"""
    LOWEST_COST = "lowest_cost"
    BEST_EFFICIENCY = "best_efficiency"  
    CRITICAL_PATH_PRIORITY = "critical_path_priority"
    RESOURCE_AWARE = "resource_aware"


class OptimizationObjective(Enum):
    """Enumeration of optimization objectives"""
    MINIMIZE_COST = "minimize_cost"
    MINIMIZE_DURATION = "minimize_duration"
    MAXIMIZE_EFFICIENCY = "maximize_efficiency"
    BALANCED = "balanced"


@dataclass
class CrashingResult:
    """Data class to store comprehensive crashing results"""
    crashed_graph: nx.DiGraph
    original_duration: float
    final_duration: float
    target_duration: float
    total_crash_cost: float
    total_normal_cost: float
    crash_log: List[Dict[str, Any]]
    efficiency_metrics: Dict[str, float]
    termination_reason: str
    iterations_used: int
    computation_time: float
    resource_utilization: Optional[Dict[str, Any]] = None
    critical_path_analysis: Optional[Dict[str, Any]] = None
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    
    @property
    def duration_reduction(self) -> float:
        """Calculate duration reduction achieved"""
        return self.original_duration - self.final_duration
    
    @property
    def duration_reduction_percent(self) -> float:
        """Calculate percentage duration reduction"""
        if self.original_duration == 0:
            return 0.0
        return (self.duration_reduction / self.original_duration) * 100
    
    @property
    def cost_per_unit_reduction(self) -> float:
        """Calculate cost per unit of duration reduction"""
        if self.duration_reduction == 0:
            return float('inf')
        return self.total_crash_cost / self.duration_reduction
    
    @property
    def target_achieved(self) -> bool:
        """Check if target duration was achieved"""
        return self.final_duration <= self.target_duration


@dataclass
class ActivityCrashInfo:
    """Detailed information about an activity's crashing potential"""
    activity_id: str
    current_duration: float
    min_duration: float
    normal_cost: float
    crash_cost_per_unit: float
    max_crash_units: float
    total_crash_potential: float
    crash_efficiency: float
    is_critical: bool
    resource_demand: float = 0
    current_float: float = 0
    
    @property
    def can_crash(self) -> bool:
        """Check if activity can be crashed"""
        return self.current_duration > self.min_duration and self.crash_cost_per_unit > 0
    
    @property
    def total_crash_cost(self) -> float:
        """Calculate total cost to fully crash activity"""
        return self.max_crash_units * self.crash_cost_per_unit


class EnhancedProjectCrashing:
    """
    Enhanced Project Crashing Engine
    
    Provides advanced project crashing capabilities with multiple optimization
    strategies, comprehensive analysis, and detailed reporting.
    """
    
    def __init__(self, base_analyzer):
        """
        Initialize with base CPM analyzer
        
        Args:
            base_analyzer: Existing CPMAnalyzer instance
        """
        self.base_analyzer = base_analyzer
        self.strategies = {
            CrashingStrategy.LOWEST_COST: self._lowest_cost_strategy,
            CrashingStrategy.BEST_EFFICIENCY: self._best_efficiency_strategy,
            CrashingStrategy.CRITICAL_PATH_PRIORITY: self._critical_path_strategy,
            CrashingStrategy.RESOURCE_AWARE: self._resource_aware_strategy
        }
    
    def enhanced_crash_project(
        self, 
        target_duration: float,
        strategy: CrashingStrategy = CrashingStrategy.LOWEST_COST,
        objective: OptimizationObjective = OptimizationObjective.MINIMIZE_COST,
        max_budget: Optional[float] = None,
        max_iterations: int = 1000,
        step_size: float = 1.0,
        early_termination: bool = True
    ) -> CrashingResult:
        """
        Enhanced project crashing with advanced optimization strategies
        
        Args:
            target_duration: Desired project duration
            strategy: Crashing strategy to use
            objective: Optimization objective
            max_budget: Maximum budget constraint
            max_iterations: Maximum iterations allowed
            step_size: Duration reduction per crash step
            early_termination: Enable early termination when target reached
            
        Returns:
            CrashingResult: Comprehensive results of crashing optimization
        """
        if not self.base_analyzer.G:
            raise ValueError("No network graph available. Run analysis first.")
        
        start_time = time.time()
        
        # Store original state
        original_graph = self.base_analyzer.G.copy()
        original_duration = max([original_graph.nodes[node]['EF'] for node in original_graph.nodes()])
        
        # Initialize working graph
        crashed_graph = original_graph.copy()
        
        # Initialize tracking variables
        total_crash_cost = 0.0
        crash_log = []
        iteration = 0
        
        # Get initial critical path and activity analysis
        activity_info = self._analyze_activities(crashed_graph)
        
        print(f"Enhanced Crashing - Target: {target_duration}, Strategy: {strategy.value}")
        print(f"Initial Duration: {original_duration}")
        print(f"Activities analyzed: {len(activity_info)}")
        
        # Main crashing loop
        while iteration < max_iterations:
            iteration += 1
            
            # Recalculate CPM
            crashed_graph = self._recalculate_cpm(crashed_graph)
            current_duration = max([crashed_graph.nodes[node]['EF'] for node in crashed_graph.nodes()])
            
            # Check termination conditions
            if early_termination and current_duration <= target_duration:
                termination_reason = "Target duration achieved"
                break
                
            if max_budget and total_crash_cost >= max_budget:
                termination_reason = "Budget constraint reached"
                break
            
            # Update activity analysis
            activity_info = self._analyze_activities(crashed_graph)
            crashable_activities = [act for act in activity_info if act.can_crash]
            
            if not crashable_activities:
                termination_reason = "No more activities can be crashed"
                break
            
            # Select activity to crash based on strategy
            selected_activity = self.strategies[strategy](
                crashable_activities, crashed_graph, objective, max_budget, total_crash_cost
            )
            
            if not selected_activity:
                termination_reason = "No suitable activity found for crashing"
                break
            
            # Execute crash
            crash_cost = selected_activity.crash_cost_per_unit * step_size
            
            # Budget check
            if max_budget and total_crash_cost + crash_cost > max_budget:
                termination_reason = "Next crash would exceed budget"
                break
            
            # Apply crash
            old_duration = crashed_graph.nodes[selected_activity.activity_id]['duration']
            new_duration = max(
                old_duration - step_size,
                selected_activity.min_duration
            )
            
            crashed_graph.nodes[selected_activity.activity_id]['duration'] = new_duration
            total_crash_cost += crash_cost
            
            # Log crash operation
            crash_entry = {
                'iteration': iteration,
                'activity': selected_activity.activity_id,
                'strategy': strategy.value,
                'old_duration': old_duration,
                'new_duration': new_duration,
                'crash_cost': crash_cost,
                'cumulative_cost': total_crash_cost,
                'project_duration_before': current_duration,
                'efficiency_score': selected_activity.crash_efficiency
            }
            
            crash_log.append(crash_entry)
            
            print(f"  Iteration {iteration}: Crashed {selected_activity.activity_id} "
                  f"({old_duration} -> {new_duration}, Cost: ${crash_cost:.2f})")
        
        else:
            termination_reason = "Maximum iterations reached"
        
        # Final calculations
        crashed_graph = self._recalculate_cpm(crashed_graph)
        final_duration = max([crashed_graph.nodes[node]['EF'] for node in crashed_graph.nodes()])
        computation_time = time.time() - start_time
        
        # Calculate comprehensive metrics
        efficiency_metrics = self._calculate_efficiency_metrics(
            original_duration, final_duration, total_crash_cost, crash_log
        )
        
        # Calculate cost breakdown
        total_normal_cost = self._calculate_total_normal_cost(crashed_graph)
        cost_breakdown = {
            'normal_cost': total_normal_cost,
            'crash_cost': total_crash_cost,
            'total_cost': total_normal_cost + total_crash_cost
        }
        
        # Critical path analysis
        critical_path_analysis = self._analyze_critical_path(crashed_graph, crash_log)
        
        print(f"Enhanced Crashing Complete:")
        print(f"  Final Duration: {final_duration}")
        print(f"  Total Crash Cost: ${total_crash_cost:.2f}")
        print(f"  Iterations: {iteration}")
        print(f"  Reason: {termination_reason}")
        
        return CrashingResult(
            crashed_graph=crashed_graph,
            original_duration=original_duration,
            final_duration=final_duration,
            target_duration=target_duration,
            total_crash_cost=total_crash_cost,
            total_normal_cost=total_normal_cost,
            crash_log=crash_log,
            efficiency_metrics=efficiency_metrics,
            termination_reason=termination_reason,
            iterations_used=iteration,
            computation_time=computation_time,
            critical_path_analysis=critical_path_analysis,
            cost_breakdown=cost_breakdown
        )
    
    def _analyze_activities(self, graph: nx.DiGraph) -> List[ActivityCrashInfo]:
        """Analyze all activities for crashing potential"""
        activities = []
        
        for node in graph.nodes():
            if node in ['START', 'END']:
                continue
                
            node_data = graph.nodes[node]
            current_duration = node_data.get('duration', 0)
            min_duration = node_data.get('min_duration', current_duration)
            normal_cost = node_data.get('normal_cost', 0)
            crash_cost = node_data.get('crash_cost', 0)
            resource_demand = node_data.get('resource_demand', 0)
            float_value = node_data.get('float', 0)
            
            max_crash_units = current_duration - min_duration
            crash_efficiency = 0
            if crash_cost > 0 and max_crash_units > 0:
                crash_efficiency = max_crash_units / crash_cost
            
            activities.append(ActivityCrashInfo(
                activity_id=node,
                current_duration=current_duration,
                min_duration=min_duration,
                normal_cost=normal_cost,
                crash_cost_per_unit=crash_cost,
                max_crash_units=max_crash_units,
                total_crash_potential=max_crash_units,
                crash_efficiency=crash_efficiency,
                is_critical=(float_value == 0),
                resource_demand=resource_demand,
                current_float=float_value
            ))
        
        return activities
    
    def _recalculate_cpm(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Recalculate CPM analysis on graph"""
        # Use base analyzer methods
        graph = self.base_analyzer.forward_pass(graph)
        graph = self.base_analyzer.backward_pass(graph)
        graph = self.base_analyzer.calculate_float(graph)
        return graph
    
    def _lowest_cost_strategy(
        self, 
        activities: List[ActivityCrashInfo], 
        graph: nx.DiGraph,
        objective: OptimizationObjective,
        max_budget: Optional[float],
        current_cost: float
    ) -> Optional[ActivityCrashInfo]:
        """Select activity with lowest crash cost"""
        critical_activities = [act for act in activities if act.is_critical]
        candidates = critical_activities if critical_activities else activities
        
        if not candidates:
            return None
            
        return min(candidates, key=lambda x: x.crash_cost_per_unit)
    
    def _best_efficiency_strategy(
        self, 
        activities: List[ActivityCrashInfo], 
        graph: nx.DiGraph,
        objective: OptimizationObjective,
        max_budget: Optional[float],
        current_cost: float
    ) -> Optional[ActivityCrashInfo]:
        """Select activity with best crash efficiency"""
        critical_activities = [act for act in activities if act.is_critical]
        candidates = critical_activities if critical_activities else activities
        
        if not candidates:
            return None
            
        return max(candidates, key=lambda x: x.crash_efficiency)
    
    def _critical_path_strategy(
        self, 
        activities: List[ActivityCrashInfo], 
        graph: nx.DiGraph,
        objective: OptimizationObjective,
        max_budget: Optional[float],
        current_cost: float
    ) -> Optional[ActivityCrashInfo]:
        """Prioritize critical path activities"""
        critical_activities = [act for act in activities if act.is_critical]
        
        if critical_activities:
            # Among critical activities, choose by efficiency
            return max(critical_activities, key=lambda x: x.crash_efficiency)
        
        # If no critical activities can be crashed, choose best overall
        return max(activities, key=lambda x: x.crash_efficiency) if activities else None
    
    def _resource_aware_strategy(
        self, 
        activities: List[ActivityCrashInfo], 
        graph: nx.DiGraph,
        objective: OptimizationObjective,
        max_budget: Optional[float],
        current_cost: float
    ) -> Optional[ActivityCrashInfo]:
        """Consider resource constraints in selection"""
        # For now, use efficiency-based selection
        # This can be extended to consider resource utilization
        return self._best_efficiency_strategy(activities, graph, objective, max_budget, current_cost)
    
    def _calculate_efficiency_metrics(
        self, 
        original_duration: float, 
        final_duration: float, 
        total_crash_cost: float,
        crash_log: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate comprehensive efficiency metrics"""
        duration_reduction = original_duration - final_duration
        
        metrics = {
            'duration_reduction': duration_reduction,
            'duration_reduction_percent': (duration_reduction / original_duration * 100) if original_duration > 0 else 0,
            'cost_per_time_unit': total_crash_cost / duration_reduction if duration_reduction > 0 else float('inf'),
            'total_crash_cost': total_crash_cost,
            'average_crash_cost_per_iteration': total_crash_cost / len(crash_log) if crash_log else 0,
            'efficiency_score': duration_reduction / total_crash_cost if total_crash_cost > 0 else 0
        }
        
        return metrics
    
    def _calculate_total_normal_cost(self, graph: nx.DiGraph) -> float:
        """Calculate total normal cost of project"""
        total_cost = 0.0
        for node in graph.nodes():
            if node not in ['START', 'END']:
                total_cost += graph.nodes[node].get('normal_cost', 0)
        return total_cost
    
    def _analyze_critical_path(self, graph: nx.DiGraph, crash_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze critical path and crashing impact"""
        critical_activities = [
            node for node in graph.nodes() 
            if graph.nodes[node].get('float', float('inf')) == 0 and node not in ['START', 'END']
        ]
        
        crashed_critical_activities = [
            entry['activity'] for entry in crash_log 
            if entry['activity'] in critical_activities
        ]
        
        analysis = {
            'critical_path': critical_activities,
            'critical_path_length': len(critical_activities),
            'crashed_critical_activities': list(set(crashed_critical_activities)),
            'critical_activities_crashed_count': len(set(crashed_critical_activities)),
            'critical_path_crash_percentage': (
                len(set(crashed_critical_activities)) / len(critical_activities) * 100
                if critical_activities else 0
            )
        }
        
        return analysis


class EnhancedRCPSProjectCrashing:
    """
    Enhanced RCPS Project Crashing Engine
    
    Provides advanced RCPS-integrated project crashing with sophisticated
    resource management and optimization algorithms.
    """
    
    def __init__(self, base_analyzer):
        """
        Initialize with base CPM analyzer
        
        Args:
            base_analyzer: Existing CPMAnalyzer instance with RCPS capabilities
        """
        self.base_analyzer = base_analyzer
    
    def enhanced_rcps_crash_project(
        self,
        target_duration: float,
        resource_limit: int,
        priority_rule: str = 'minimum_slack',
        strategy: CrashingStrategy = CrashingStrategy.RESOURCE_AWARE,
        max_budget: Optional[float] = None,
        max_iterations: int = 1000,
        resource_efficiency_weight: float = 0.3
    ) -> CrashingResult:
        """
        Enhanced RCPS project crashing with advanced resource-aware optimization
        
        Args:
            target_duration: Desired project duration
            resource_limit: Maximum resource availability per time period
            priority_rule: RCPS scheduling rule
            strategy: Crashing strategy to use
            max_budget: Maximum budget constraint
            max_iterations: Maximum iterations allowed
            resource_efficiency_weight: Weight for resource efficiency in selection
            
        Returns:
            CrashingResult: Comprehensive results including resource utilization
        """
        if not self.base_analyzer.G:
            raise ValueError("No network graph available. Run analysis first.")
        
        start_time = time.time()
        
        # Store original state
        original_graph = self.base_analyzer.G.copy()
        
        # Get initial RCPS schedule
        initial_schedule = self.base_analyzer.generate_rcps_schedule_for_graph(
            original_graph, resource_limit, priority_rule
        )
        original_duration = initial_schedule['project_duration']
        
        # Initialize working graph
        crashed_graph = original_graph.copy()
        
        # Initialize tracking variables
        total_crash_cost = 0.0
        crash_log = []
        iteration = 0
        current_time = 0
        
        print(f"Enhanced RCPS Crashing - Target: {target_duration}, Resource Limit: {resource_limit}")
        print(f"Initial RCPS Duration: {original_duration}")
        
        # Main crashing loop
        while iteration < max_iterations:
            iteration += 1
            
            # Generate current RCPS schedule
            current_schedule = self.base_analyzer.generate_rcps_schedule_for_graph(
                crashed_graph, resource_limit, priority_rule
            )
            current_duration = current_schedule['project_duration']
            
            # Check termination conditions
            if current_duration <= target_duration:
                termination_reason = "Target duration achieved"
                break
                
            if max_budget and total_crash_cost >= max_budget:
                termination_reason = "Budget constraint reached"
                break
            
            # Analyze crashable activities with RCPS considerations
            crash_options = self._analyze_rcps_crash_options(
                crashed_graph, current_schedule, resource_limit, priority_rule,
                current_time, resource_efficiency_weight
            )
            
            if not crash_options:
                termination_reason = "No more activities can be crashed under RCPS constraints"
                break
            
            # Select best crash option
            selected_option = self._select_best_rcps_crash_option(
                crash_options, strategy, max_budget, total_crash_cost
            )
            
            if not selected_option:
                termination_reason = "No suitable crash option found"
                break
            
            # Budget check
            if max_budget and total_crash_cost + selected_option['crash_cost'] > max_budget:
                termination_reason = "Next crash would exceed budget"
                break
            
            # Apply crash
            activity_id = selected_option['activity_id']
            old_duration = crashed_graph.nodes[activity_id]['duration']
            new_duration = old_duration - 1
            
            crashed_graph.nodes[activity_id]['duration'] = new_duration
            total_crash_cost += selected_option['crash_cost']
            
            # Log crash operation
            crash_entry = {
                'iteration': iteration,
                'activity': activity_id,
                'old_duration': old_duration,
                'new_duration': new_duration,
                'crash_cost': selected_option['crash_cost'],
                'cumulative_cost': total_crash_cost,
                'project_duration_before': current_duration,
                'project_duration_after': selected_option['resulting_duration'],
                'duration_reduction': selected_option['duration_reduction'],
                'resource_efficiency': selected_option['resource_efficiency'],
                'rcps_schedule_info': {
                    'actual_start': selected_option.get('actual_start', 0),
                    'actual_finish': selected_option.get('actual_finish', 0),
                    'resource_demand': selected_option.get('resource_demand', 0)
                }
            }
            
            crash_log.append(crash_entry)
            
            print(f"  Iteration {iteration}: RCPS Crashed {activity_id} "
                  f"({old_duration} -> {new_duration}, Cost: ${selected_option['crash_cost']:.2f}, "
                  f"Duration Reduction: {selected_option['duration_reduction']})")
            
            # Advance simulation time
            current_time += 1
        
        else:
            termination_reason = "Maximum iterations reached"
        
        # Final calculations
        final_schedule = self.base_analyzer.generate_rcps_schedule_for_graph(
            crashed_graph, resource_limit, priority_rule
        )
        final_duration = final_schedule['project_duration']
        computation_time = time.time() - start_time
        
        # Calculate resource utilization analysis
        resource_utilization = self._analyze_resource_utilization(
            final_schedule, resource_limit, crash_log
        )
        
        # Calculate comprehensive metrics
        efficiency_metrics = self._calculate_rcps_efficiency_metrics(
            original_duration, final_duration, total_crash_cost, crash_log,
            resource_utilization
        )
        
        # Calculate cost breakdown
        total_normal_cost = self._calculate_total_normal_cost(crashed_graph)
        cost_breakdown = {
            'normal_cost': total_normal_cost,
            'crash_cost': total_crash_cost,
            'total_cost': total_normal_cost + total_crash_cost
        }
        
        print(f"Enhanced RCPS Crashing Complete:")
        print(f"  Final Duration: {final_duration}")
        print(f"  Total Crash Cost: ${total_crash_cost:.2f}")
        print(f"  Iterations: {iteration}")
        print(f"  Reason: {termination_reason}")
        
        return CrashingResult(
            crashed_graph=crashed_graph,
            original_duration=original_duration,
            final_duration=final_duration,
            target_duration=target_duration,
            total_crash_cost=total_crash_cost,
            total_normal_cost=total_normal_cost,
            crash_log=crash_log,
            efficiency_metrics=efficiency_metrics,
            termination_reason=termination_reason,
            iterations_used=iteration,
            computation_time=computation_time,
            resource_utilization=resource_utilization,
            cost_breakdown=cost_breakdown
        )
    
    def _analyze_rcps_crash_options(
        self,
        graph: nx.DiGraph,
        current_schedule: Dict[str, Any],
        resource_limit: int,
        priority_rule: str,
        current_time: float,
        resource_efficiency_weight: float
    ) -> List[Dict[str, Any]]:
        """Analyze crash options considering RCPS constraints"""
        crash_options = []
        current_duration = current_schedule['project_duration']
        
        for activity_id, activity_data in current_schedule['activities'].items():
            if activity_id in ['START', 'END']:
                continue
            
            # Get activity properties
            current_dur = graph.nodes[activity_id]['duration']
            min_dur = graph.nodes[activity_id].get('min_duration', current_dur)
            crash_cost = graph.nodes[activity_id].get('crash_cost', 0)
            resource_demand = graph.nodes[activity_id].get('resource_demand', 0)
            
            # Check if activity can be crashed
            if current_dur <= min_dur or crash_cost <= 0:
                continue
            
            # Test impact of crashing this activity
            temp_graph = graph.copy()
            temp_graph.nodes[activity_id]['duration'] = current_dur - 1
            
            # Generate new RCPS schedule
            temp_schedule = self.base_analyzer.generate_rcps_schedule_for_graph(
                temp_graph, resource_limit, priority_rule
            )
            temp_duration = temp_schedule['project_duration']
            duration_reduction = current_duration - temp_duration
            
            # Calculate resource efficiency
            resource_efficiency = self._calculate_resource_efficiency(
                activity_id, temp_schedule, resource_limit, resource_demand, resource_efficiency_weight
            )
            
            # Store crash option
            crash_option = {
                'activity_id': activity_id,
                'crash_cost': crash_cost,
                'current_duration': current_dur,
                'min_duration': min_dur,
                'duration_reduction': duration_reduction,
                'resulting_duration': temp_duration,
                'resource_efficiency': resource_efficiency,
                'resource_demand': resource_demand,
                'actual_start': activity_data.get('actual_start', 0),
                'actual_finish': activity_data.get('actual_finish', 0),
                'efficiency_score': duration_reduction / crash_cost if crash_cost > 0 else 0,
                'combined_score': (
                    duration_reduction / crash_cost * (1 - resource_efficiency_weight) +
                    resource_efficiency * resource_efficiency_weight
                ) if crash_cost > 0 else 0
            }
            
            crash_options.append(crash_option)
        
        return crash_options
    
    def _calculate_resource_efficiency(
        self,
        activity_id: str,
        schedule: Dict[str, Any],
        resource_limit: int,
        resource_demand: float,
        weight: float
    ) -> float:
        """Calculate resource efficiency score for an activity"""
        if resource_limit == 0 or resource_demand == 0:
            return 0.0
        
        # Basic resource efficiency calculation
        # This can be enhanced with more sophisticated resource analysis
        utilization_ratio = resource_demand / resource_limit
        
        # Prefer activities that don't over-utilize resources
        if utilization_ratio <= 1.0:
            efficiency = 1.0 - utilization_ratio * 0.5  # Higher is better for lower utilization
        else:
            efficiency = 0.5 / utilization_ratio  # Penalize over-utilization
        
        return min(max(efficiency, 0.0), 1.0)
    
    def _select_best_rcps_crash_option(
        self,
        crash_options: List[Dict[str, Any]],
        strategy: CrashingStrategy,
        max_budget: Optional[float],
        current_cost: float
    ) -> Optional[Dict[str, Any]]:
        """Select the best crash option based on strategy"""
        if not crash_options:
            return None
        
        # Filter options that exceed budget
        if max_budget:
            crash_options = [
                opt for opt in crash_options 
                if current_cost + opt['crash_cost'] <= max_budget
            ]
        
        if not crash_options:
            return None
        
        # Select based on strategy
        if strategy == CrashingStrategy.LOWEST_COST:
            return min(crash_options, key=lambda x: x['crash_cost'])
        elif strategy == CrashingStrategy.BEST_EFFICIENCY:
            return max(crash_options, key=lambda x: x['efficiency_score'])
        elif strategy == CrashingStrategy.RESOURCE_AWARE:
            return max(crash_options, key=lambda x: x['combined_score'])
        else:
            # Default to lowest cost
            return min(crash_options, key=lambda x: x['crash_cost'])
    
    def _analyze_resource_utilization(
        self,
        final_schedule: Dict[str, Any],
        resource_limit: int,
        crash_log: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze resource utilization throughout the project"""
        if 'activities' not in final_schedule:
            return {}
        
        # Calculate resource usage over time
        time_periods = {}
        max_time = 0
        
        for activity_id, activity_data in final_schedule['activities'].items():
            if activity_id in ['START', 'END']:
                continue
            
            start_time = activity_data.get('actual_start', 0)
            finish_time = activity_data.get('actual_finish', 0)
            resource_demand = activity_data.get('resource_demand', 0)
            
            max_time = max(max_time, finish_time)
            
            for t in range(int(start_time), int(finish_time)):
                if t not in time_periods:
                    time_periods[t] = 0
                time_periods[t] += resource_demand
        
        # Calculate utilization statistics
        utilizations = list(time_periods.values())
        total_periods = len(utilizations)
        
        if total_periods == 0:
            return {}
        
        over_limit_periods = sum(1 for u in utilizations if u > resource_limit)
        avg_utilization = sum(utilizations) / total_periods
        max_utilization = max(utilizations) if utilizations else 0
        
        return {
            'max_time': max_time,
            'total_periods': total_periods,
            'average_utilization': avg_utilization,
            'max_utilization': max_utilization,
            'resource_limit': resource_limit,
            'over_limit_periods': over_limit_periods,
            'utilization_percentage': (avg_utilization / resource_limit * 100) if resource_limit > 0 else 0,
            'periods_over_limit_percentage': (over_limit_periods / total_periods * 100) if total_periods > 0 else 0,
            'time_periods': time_periods
        }
    
    def _calculate_rcps_efficiency_metrics(
        self,
        original_duration: float,
        final_duration: float,
        total_crash_cost: float,
        crash_log: List[Dict[str, Any]],
        resource_utilization: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate RCPS-specific efficiency metrics"""
        duration_reduction = original_duration - final_duration
        
        metrics = {
            'duration_reduction': duration_reduction,
            'duration_reduction_percent': (duration_reduction / original_duration * 100) if original_duration > 0 else 0,
            'cost_per_time_unit': total_crash_cost / duration_reduction if duration_reduction > 0 else float('inf'),
            'total_crash_cost': total_crash_cost,
            'average_crash_cost_per_iteration': total_crash_cost / len(crash_log) if crash_log else 0,
            'efficiency_score': duration_reduction / total_crash_cost if total_crash_cost > 0 else 0
        }
        
        # Add resource-specific metrics
        if resource_utilization:
            metrics.update({
                'average_resource_utilization': resource_utilization.get('average_utilization', 0),
                'max_resource_utilization': resource_utilization.get('max_utilization', 0),
                'resource_efficiency': (
                    resource_utilization.get('utilization_percentage', 0) / 100.0
                    if resource_utilization.get('resource_limit', 0) > 0 else 0
                ),
                'periods_over_limit_percent': resource_utilization.get('periods_over_limit_percentage', 0)
            })
        
        return metrics
    
    def _calculate_total_normal_cost(self, graph: nx.DiGraph) -> float:
        """Calculate total normal cost of project"""
        total_cost = 0.0
        for node in graph.nodes():
            if node not in ['START', 'END']:
                total_cost += graph.nodes[node].get('normal_cost', 0)
        return total_cost


# Utility functions for enhanced crashing features

def compare_crashing_results(results: List[CrashingResult]) -> Dict[str, Any]:
    """
    Compare multiple crashing results and provide analysis
    
    Args:
        results: List of CrashingResult objects to compare
        
    Returns:
        Comprehensive comparison analysis
    """
    if not results:
        return {}
    
    comparison = {
        'total_results': len(results),
        'best_cost': min(results, key=lambda x: x.total_crash_cost),
        'best_duration': min(results, key=lambda x: x.final_duration),
        'best_efficiency': max(results, key=lambda x: x.efficiency_metrics.get('efficiency_score', 0)),
        'fastest_computation': min(results, key=lambda x: x.computation_time),
        'summary_stats': {
            'avg_crash_cost': sum(r.total_crash_cost for r in results) / len(results),
            'avg_final_duration': sum(r.final_duration for r in results) / len(results),
            'avg_iterations': sum(r.iterations_used for r in results) / len(results),
            'targets_achieved': sum(1 for r in results if r.target_achieved),
            'success_rate': sum(1 for r in results if r.target_achieved) / len(results) * 100
        }
    }
    
    return comparison


def generate_crashing_report(result: CrashingResult) -> str:
    """
    Generate a comprehensive text report for crashing results
    
    Args:
        result: CrashingResult object
        
    Returns:
        Formatted text report
    """
    report_lines = [
        "=" * 70,
        "ENHANCED PROJECT CRASHING ANALYSIS REPORT",
        "=" * 70,
        "",
        "PROJECT OVERVIEW:",
        f"  Original Duration: {result.original_duration:.2f}",
        f"  Target Duration: {result.target_duration:.2f}",
        f"  Final Duration: {result.final_duration:.2f}",
        f"  Target Achieved: {'✓ YES' if result.target_achieved else '✗ NO'}",
        "",
        "COST ANALYSIS:",
        f"  Total Crash Cost: ${result.total_crash_cost:,.2f}",
        f"  Total Normal Cost: ${result.total_normal_cost:,.2f}",
        f"  Total Project Cost: ${result.total_crash_cost + result.total_normal_cost:,.2f}",
        "",
        "EFFICIENCY METRICS:",
        f"  Duration Reduction: {result.duration_reduction:.2f} units ({result.duration_reduction_percent:.1f}%)",
        f"  Cost per Unit Reduction: ${result.cost_per_unit_reduction:,.2f}",
        f"  Efficiency Score: {result.efficiency_metrics.get('efficiency_score', 0):.4f}",
        "",
        "EXECUTION DETAILS:",
        f"  Iterations Used: {result.iterations_used}",
        f"  Computation Time: {result.computation_time:.2f} seconds",
        f"  Termination Reason: {result.termination_reason}",
        "",
        "CRASH LOG SUMMARY:",
        f"  Total Crashes: {len(result.crash_log)}",
    ]
    
    if result.crash_log:
        report_lines.extend([
            "  Activities Crashed:",
            *[f"    - {entry['activity']}: {entry['old_duration']} -> {entry['new_duration']} (${entry['crash_cost']:.2f})" 
              for entry in result.crash_log]
        ])
    
    if result.resource_utilization:
        report_lines.extend([
            "",
            "RESOURCE UTILIZATION:",
            f"  Average Utilization: {result.resource_utilization.get('average_utilization', 0):.2f}",
            f"  Max Utilization: {result.resource_utilization.get('max_utilization', 0):.2f}",
            f"  Resource Limit: {result.resource_utilization.get('resource_limit', 0)}",
            f"  Utilization Percentage: {result.resource_utilization.get('utilization_percentage', 0):.1f}%"
        ])
    
    if result.critical_path_analysis:
        report_lines.extend([
            "",
            "CRITICAL PATH ANALYSIS:",
            f"  Critical Path Length: {result.critical_path_analysis.get('critical_path_length', 0)}",
            f"  Critical Activities Crashed: {result.critical_path_analysis.get('critical_activities_crashed_count', 0)}",
            f"  Critical Path Crash %: {result.critical_path_analysis.get('critical_path_crash_percentage', 0):.1f}%"
        ])
    
    report_lines.extend([
        "",
        "=" * 70
    ])
    
    return "\n".join(report_lines)


if __name__ == "__main__":
    print("Enhanced Project Crashing Module Loaded Successfully")
    print("Available Classes:")
    print("  - EnhancedProjectCrashing")
    print("  - EnhancedRCPSProjectCrashing") 
    print("  - CrashingResult")
    print("  - ActivityCrashInfo")
    print("Available Strategies:")
    for strategy in CrashingStrategy:
        print(f"  - {strategy.value}")
    print("Available Objectives:")
    for objective in OptimizationObjective:
        print(f"  - {objective.value}")
