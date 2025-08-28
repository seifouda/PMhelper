"""
Project Crashing Core Logic

Contains all core logic classes and functions for project crashing analysis.
All references to 'enhanced' have been removed.
"""

import copy
import time as time_mod
import networkx as nx
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union
from collections import defaultdict
from enum import Enum

# Strategy and objective enums
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
    """Stores comprehensive crashing results"""
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

class ProjectCrashing:
    """
    Project Crashing Engine
    Provides advanced project crashing capabilities with multiple optimization strategies.
    """
    def __init__(self, base_analyzer):
        self.base_analyzer = base_analyzer
        self.strategies = {
            CrashingStrategy.LOWEST_COST: self._lowest_cost_strategy,
            CrashingStrategy.BEST_EFFICIENCY: self._best_efficiency_strategy,
            CrashingStrategy.CRITICAL_PATH_PRIORITY: self._critical_path_strategy,
            CrashingStrategy.RESOURCE_AWARE: self._resource_aware_strategy
        }

    def run(self, target_duration, strategy, objective, max_budget=None, max_crash_cost=None, max_normal_cost=None, max_iterations=300):
        """
        Main entry point for running project crashing analysis.
        Calls the selected strategy method, passing all relevant arguments.
        """
        # Ensure target_duration is always int
        target_duration = int(round(target_duration)) if target_duration is not None else None
        # print(f"[DEBUG] ProjectCrashing.run called with target_duration={target_duration}, strategy={strategy}, objective={objective}, max_budget={max_budget}, max_iterations={max_iterations}")
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")
        # Pass all arguments to the selected strategy method
        return self.strategies[strategy](
            target_duration=target_duration,
            max_budget=max_budget,
            max_crash_cost=max_crash_cost,
            max_normal_cost=max_normal_cost,
            max_iterations=max_iterations
        )
    # Strategy method stubs for integration testing
    def _lowest_cost_strategy(self, target_duration=None, max_budget=None, max_crash_cost=None, max_normal_cost=None, max_iterations=300, **kwargs):
        # print(f"[DEBUG] _lowest_cost_strategy received target_duration={target_duration}")
        """
        Implements the lowest cost crashing strategy.
        Iteratively crashes the critical path activity with the lowest crash cost per unit until the target duration or budget is met.
        """
        analyzer = self.base_analyzer
        G = copy.deepcopy(getattr(analyzer, 'G', None) or getattr(analyzer, 'graph', None))
        if G is None:
            raise ValueError("No project graph found in analyzer.")

        start_time = time_mod.time()
        crash_log = []
        total_crash_cost = 0.0
        total_normal_cost_accumulated = 0.0
        iterations = 0
        termination_reason = ''

        # Initial CPM calculation
        # Use a local forward_pass for project crashing to ensure ES/EF are recalculated using current durations
        # --- PROMPT: CPM recalculation now uses NetworkBuilder for consistency ---
        # Use CPM logic from cpm_analyzer.py (forward_pass, backward_pass, calculate_float)
        network_builder = getattr(analyzer, 'network_builder', None)
        if network_builder is None:
            from src.pmhelper.core.network_builder import NetworkBuilder
            network_builder = NetworkBuilder()
        G = network_builder.forward_pass(G)
        G = network_builder.backward_pass(G)
        G = network_builder.calculate_float(G)
        # Use max EF for project duration
        ef_dict = nx.get_node_attributes(G, 'EF')
        original_duration = int(round(max(ef_dict.values()))) if ef_dict else 0
        current_duration = original_duration
        current_time = 1
        completed_activities = set()
        
        while current_duration > target_duration and iterations < max_iterations:
            # print(f"[DEBUG] Iteration {iterations}: current_duration={current_duration}, target_duration={target_duration}, current_time={current_time}")
            
            # --- PREDICTIVE COST CALCULATION (START) ---
            # STEP 1: Calculate potential step normal cost for all activities that would be active in this time step
            step_normal_cost = 0
            active_activities_this_step = []
            for node_id in G.nodes:
                if node_id not in ['START', 'END']:
                    es = G.nodes[node_id].get('ES', 0)
                    ef = G.nodes[node_id].get('EF', 0)
                    # An activity is active if the current time falls within its execution window (ES < current_time <= EF)
                    if es < current_time <= ef:
                        step_normal_cost += G.nodes[node_id].get('normal_cost', 0)  # This is treated as a rate
                        active_activities_this_step.append(node_id)
            
            # STEP 2: Identify the best candidate activity to crash and calculate potential crash cost
            # print(f"[DEBUG] Activity durations before crash: {[ (n, G.nodes[n].get('duration', '?')) for n in G.nodes ]}")
            # Mark completed activities (EF <= current_time)
            completed_activities = {n for n in G.nodes if G.nodes[n].get('EF', 0) <= current_time}
            # print(f"[DEBUG] Completed activities at time {current_time}: {completed_activities}")
            # Build crashable list: critical path, not completed, not at min duration, crash_cost > 0, EF > current_time
            crashable = []
            for node in G.nodes:
                if (
                    G.nodes[node].get('float', 0) == 0
                    and node not in ['START', 'END']
                    and node not in completed_activities
                ):
                    data = G.nodes[node]
                    dur = int(round(data.get('duration', 0)))
                    min_dur = int(round(data.get('min_duration', dur)))
                    crash_cost = data.get('crash_cost', 0)
                    normal_cost = data.get('normal_cost', 0)
                    ef = int(round(data.get('EF', 0)))
                    # Only crash if duration > min_duration and crash_cost > 0 and EF strictly greater than current_time
                    if dur > min_dur and crash_cost > 0 and ef > current_time:
                        crashable.append((node, crash_cost, dur, min_dur, normal_cost, ef))
            # print(f"[DEBUG] Crashable activities (filtered for critical path, in-progress): {crashable}")
            
            # Calculate potential crash cost
            potential_crash_cost = 0
            selected_for_crash = None
            if crashable:
                # Prioritize only truly crashable activities by lowest crash cost
                crashable.sort(key=lambda x: x[1])
                # Find the first crashable activity that is eligible (EF strictly greater than current_time)
                for candidate in crashable:
                    node, crash_cost, dur, min_dur, normal_cost, ef = candidate
                    if dur > min_dur and crash_cost > 0 and ef > current_time:
                        selected_for_crash = candidate
                        # Calculate potential crash cost (1 unit of crash)
                        crash_amount = min(1, dur - min_dur)
                        potential_crash_cost = crash_cost * crash_amount
                        break
            
            # STEP 3: Implement predictive budget checks
            # Check if applying this step's costs would exceed max_budget
            if max_budget is not None:
                projected_total_cost = total_normal_cost_accumulated + step_normal_cost + total_crash_cost + potential_crash_cost
                if projected_total_cost > max_budget:
                    # print(f"[DEBUG] Budget limit would be exceeded in the next step. Projected: {projected_total_cost}, Max: {max_budget}")
                    termination_reason = 'Budget limit would be exceeded in the next step'
                    break
            
            # Check if applying crash cost would exceed max_crash_cost
            if max_crash_cost is not None:
                projected_crash_cost = total_crash_cost + potential_crash_cost
                if projected_crash_cost > max_crash_cost:
                    # print(f"[DEBUG] Crash cost budget limit would be exceeded in the next step. Projected: {projected_crash_cost}, Max: {max_crash_cost}")
                    termination_reason = 'Crash cost budget limit would be exceeded in the next step'
                    break
            
            # Check normal cost budget
            if max_normal_cost is not None:
                projected_normal_cost = total_normal_cost_accumulated + step_normal_cost
                if projected_normal_cost > max_normal_cost:
                    # print(f"[DEBUG] Normal cost budget limit would be exceeded in the next step. Projected: {projected_normal_cost}, Max: {max_normal_cost}")
                    termination_reason = 'Normal cost budget limit would be exceeded in the next step'
                    break
            
            # STEP 4: If all budget checks pass, commit the costs
            total_normal_cost_accumulated += step_normal_cost
            # print(f"[DEBUG] Time {current_time}: Active activities: {active_activities_this_step}, Step Normal Cost: {step_normal_cost}, Accumulated Normal Cost: {total_normal_cost_accumulated}")
            # --- PREDICTIVE COST CALCULATION (END) ---

            # If there are activities to crash, proceed with crashing logic
            if selected_for_crash:
                node, crash_cost, dur, min_dur, normal_cost, ef = selected_for_crash
                
                # Calculate the crash amount (we already verified this is valid in the predictive check)
                crash_amount = min(1, dur - min_dur)
                cost = crash_cost * crash_amount

                # print(f"[DEBUG] Crashing activity {node}: crash_amount={crash_amount:.2f}, cost={cost:.2f}, dur={dur}, min_dur={min_dur}, EF={ef}")

                # Update duration, ensuring it does not go below min_dur
                new_duration = max(min_dur, dur - crash_amount)
                # print(f"[DEBUG] Setting duration of {node} to {new_duration} (was {dur})")
                G.nodes[node]['duration'] = new_duration
                G.nodes[node]['crash_cost'] = crash_cost
                G.nodes[node]['normal_cost'] = normal_cost
                total_crash_cost += cost
                
                # Recalculate CPM immediately after crashing to get updated critical path
                # print(f"[DEBUG] Recalculating CPM after crash...")
                G = network_builder.forward_pass(G)
                G = network_builder.backward_pass(G)
                G = network_builder.calculate_float(G)
                ef_dict = nx.get_node_attributes(G, 'EF')
                current_duration = int(round(max(ef_dict.values()))) if ef_dict else 0
                # print(f"[DEBUG] Project duration after CPM recalculation: {current_duration}")
                
                # Record crash log AFTER CPM recalculation to get correct critical path
                crash_log.append({
                    'iteration': iterations + 1, # Use iterations+1 for 1-based log
                    'activity': node,
                    'crash_amount': crash_amount,
                    'cost': cost,
                    'duration': int(round(G.nodes[node]['duration'])),
                    'current_project_duration': current_duration, # Duration after this step's CPM recalc
                    'total_crash_cost': total_crash_cost,
                    'critical_path': [n for n in G.nodes if G.nodes[n].get('float', 0) == 0 and n not in ['START', 'END']],
                    'normal_cost': normal_cost,
                    'EF': ef,
                    'current_time': current_time,  # This shows the time when the decision was made
                    'step_normal_cost': step_normal_cost,
                    'total_normal_cost_accumulated': total_normal_cost_accumulated,
                    'active_activities': active_activities_this_step
                })

            else:
                # print("[DEBUG] No crashable activities on critical path for this time step. Advancing time.")
                # Even if nothing is crashed, we still log the costs for this time step
                crash_log.append({
                    'iteration': iterations + 1,
                    'activity': 'None',
                    'crash_amount': 0,
                    'cost': 0,
                    'duration': None,
                    'current_project_duration': current_duration,
                    'total_crash_cost': total_crash_cost,
                    'critical_path': [n for n in G.nodes if G.nodes[n].get('float', 0) == 0 and n not in ['START', 'END']],
                    'normal_cost': 0,
                    'EF': None,
                    'current_time': current_time,
                    'step_normal_cost': step_normal_cost,
                    'total_normal_cost_accumulated': total_normal_cost_accumulated,
                    'active_activities': active_activities_this_step
                })

            iterations += 1
            # print(f"[DEBUG] Activity durations after crash decision: {[ (n, G.nodes[n].get('duration', '?')) for n in G.nodes ]}")
            # CPM recalculation moved to right after crash for accurate critical path logging
            # print(f"[DEBUG] After step: current_duration={current_duration}, target_duration={target_duration}")

            # Advance simulation time
            current_time += 1
            if target_duration is not None and current_duration <= target_duration:
                # print(f"[DEBUG] Target duration reached. Stopping. current_duration={current_duration}, target_duration={target_duration}")
                termination_reason = 'Target duration reached'
                break
            
            # If time exceeds the new duration, it means we are done.
            if current_time > current_duration:
                # print(f"[DEBUG] Simulation time ({current_time}) has exceeded project duration ({current_duration}). Stopping.")
                if not termination_reason:
                    termination_reason = 'Completed'
                break

        if not termination_reason:
            if target_duration is not None and current_duration <= target_duration:
                termination_reason = 'Target duration reached'
            else:
                termination_reason = 'Max iterations reached' if iterations >= max_iterations else 'Completed'

        computation_time = time_mod.time() - start_time
        final_duration = current_duration
        # The final total normal cost is the accumulated value
        total_normal_cost = total_normal_cost_accumulated
        efficiency_metrics = {'cost_per_unit_time': total_crash_cost / (original_duration - final_duration) if final_duration < original_duration else 0}
        return CrashingResult(
            crashed_graph=G,
            original_duration=original_duration,
            final_duration=final_duration,
            target_duration=target_duration,
            total_crash_cost=total_crash_cost,
            total_normal_cost=total_normal_cost,
            crash_log=crash_log,
            efficiency_metrics=efficiency_metrics,
            termination_reason=termination_reason,
            iterations_used=iterations,
            computation_time=computation_time
        )

    def _best_efficiency_strategy(self, *args, **kwargs):
        """
        Implements the best efficiency crashing strategy (stub).
        NOTE: Must be updated to use the time-based simulation loop for cost calculation.
        """
        # print("[DEBUG] _best_efficiency_strategy called with args:", args, "kwargs:", kwargs)
        raise NotImplementedError("Best efficiency strategy not yet implemented.")

    def _critical_path_strategy(self, *args, **kwargs):
        """
        Implements the critical path priority crashing strategy (stub).
        NOTE: Must be updated to use the time-based simulation loop for cost calculation.
        """
        # print("[DEBUG] _critical_path_strategy called with args:", args, "kwargs:", kwargs)
        raise NotImplementedError("Critical path priority strategy not yet implemented.")

    def _resource_aware_strategy(self, *args, **kwargs):
        """
        Implements the resource aware crashing strategy (stub).
        NOTE: Must be updated to use the time-based simulation loop for cost calculation.
        """
        # print("[DEBUG] _resource_aware_strategy called with args:", args, "kwargs:", kwargs)
        raise NotImplementedError("Resource aware strategy not yet implemented.")

class RCPSProjectCrashing(ProjectCrashing):
    """
    RCPS Project Crashing Engine
    Provides RCPS-integrated project crashing with resource management and optimization.
    """
    def __init__(self, rcps_analyzer, resource_limit):
        """
        Initialize RCPS Project Crashing
        
        Args:
            rcps_analyzer: RCPSAnalyzer instance with RCPS network data
            resource_limit: Maximum available resources
        """
        super().__init__(rcps_analyzer)
        self.resource_limit = resource_limit
        self.rcps_analyzer = rcps_analyzer
        
        # print(f"[DEBUG] RCPSProjectCrashing initialized with resource_limit={resource_limit}")
    
    def _lowest_cost_strategy(self, target_duration=None, max_budget=None, max_crash_cost=None, max_normal_cost=None, max_iterations=300, **kwargs):
        """
        RCPS-aware lowest cost strategy with resource constraint validation
        """
        # print(f"[DEBUG] RCPS _lowest_cost_strategy received target_duration={target_duration}")
        
        # Use the same logic as parent class but with resource validation
        analyzer = self.base_analyzer
        G = copy.deepcopy(getattr(analyzer, 'G', None) or getattr(analyzer, 'graph', None))
        if G is None:
            raise ValueError("No project graph found in RCPS analyzer.")

        start_time = time_mod.time()
        crash_log = []
        total_crash_cost = 0.0
        total_normal_cost_accumulated = 0.0
        iterations = 0
        termination_reason = ''

        # CRITICAL FIX: Don't recalculate network passes - preserve RCPS times!
        # The graph already contains resource-constrained ES/EF values from RCPS analysis
        # Recalculating would overwrite actual_start times with theoretical CPM times
        
        # Use existing EF values from RCPS (resource-constrained schedule)
        ef_dict = nx.get_node_attributes(G, 'EF')
        original_duration = int(round(max(ef_dict.values()))) if ef_dict else 0
        
        print(f"[DEBUG] RCPS Crashing: Using RCPS duration={original_duration} (not recalculating CPM)")
        
        # Initialize network builder for later use when activities are crashed
        network_builder = getattr(analyzer, 'network_builder', None)
        if network_builder is None:
            from src.pmhelper.core.network_builder import NetworkBuilder
            network_builder = NetworkBuilder()
        current_duration = original_duration
        current_time = 1
        completed_activities = set()
        
        # print(f"[DEBUG] RCPS crashing starting: original_duration={original_duration}, target={target_duration}, resource_limit={self.resource_limit}")
        
        while current_duration > target_duration and iterations < max_iterations:
            # print(f"[DEBUG] RCPS Iteration {iterations}: current_duration={current_duration}, target_duration={target_duration}, current_time={current_time}")
            
            # Calculate step normal cost (same as parent)
            step_normal_cost = 0
            active_activities_this_step = []
            for node_id in G.nodes:
                if node_id not in ['START', 'END']:
                    es = G.nodes[node_id].get('ES', 0)
                    ef = G.nodes[node_id].get('EF', 0)
                    if es < current_time <= ef:
                        step_normal_cost += G.nodes[node_id].get('normal_cost', 0)
                        active_activities_this_step.append(node_id)
            
            # Find crashable activities with resource constraint validation
            completed_activities = {n for n in G.nodes if G.nodes[n].get('EF', 0) <= current_time}
            crashable = []
            for node in G.nodes:
                if (
                    G.nodes[node].get('float', 0) == 0
                    and node not in ['START', 'END']
                    and node not in completed_activities
                ):
                    data = G.nodes[node]
                    dur = int(round(data.get('duration', 0)))
                    min_dur = int(round(data.get('min_duration', dur)))
                    crash_cost = data.get('crash_cost', 0)
                    normal_cost = data.get('normal_cost', 0)
                    ef = int(round(data.get('EF', 0)))
                    
                    if dur > min_dur and crash_cost > 0 and ef > current_time:
                        # Additional RCPS validation: check resource constraints
                        if self._validate_crash_feasibility(node, 1, current_time, G):
                            crashable.append((node, crash_cost, dur, min_dur, normal_cost, ef))
                        else:
                            # print(f"[DEBUG] Activity {node} crash would violate resource constraints")
                            pass
            
            # print(f"[DEBUG] RCPS crashable activities (resource-validated): {crashable}")
            
            # Calculate potential crash cost
            potential_crash_cost = 0
            selected_for_crash = None
            if crashable:
                crashable.sort(key=lambda x: x[1])  # Sort by crash cost
                for candidate in crashable:
                    node, crash_cost, dur, min_dur, normal_cost, ef = candidate
                    if dur > min_dur and crash_cost > 0 and ef > current_time:
                        selected_for_crash = candidate
                        crash_amount = min(1, dur - min_dur)
                        potential_crash_cost = crash_cost * crash_amount
                        break
            
            # Budget checks (same as parent)
            if max_budget is not None:
                projected_total_cost = total_normal_cost_accumulated + step_normal_cost + total_crash_cost + potential_crash_cost
                if projected_total_cost > max_budget:
                    # print(f"[DEBUG] RCPS Budget limit would be exceeded. Projected: {projected_total_cost}, Max: {max_budget}")
                    termination_reason = 'Budget limit would be exceeded in the next step'
                    break
            
            if max_crash_cost is not None:
                projected_crash_cost = total_crash_cost + potential_crash_cost
                if projected_crash_cost > max_crash_cost:
                    # print(f"[DEBUG] RCPS Crash cost limit would be exceeded. Projected: {projected_crash_cost}, Max: {max_crash_cost}")
                    termination_reason = 'Crash cost budget limit would be exceeded in the next step'
                    break
            
            if max_normal_cost is not None:
                projected_normal_cost = total_normal_cost_accumulated + step_normal_cost
                if projected_normal_cost > max_normal_cost:
                    # print(f"[DEBUG] RCPS Normal cost limit would be exceeded. Projected: {projected_normal_cost}, Max: {max_normal_cost}")
                    termination_reason = 'Normal cost budget limit would be exceeded in the next step'
                    break
            
            # Commit costs
            total_normal_cost_accumulated += step_normal_cost
            
            # Execute crash if possible
            if selected_for_crash:
                node, crash_cost, dur, min_dur, normal_cost, ef = selected_for_crash
                crash_amount = min(1, dur - min_dur)
                cost = crash_cost * crash_amount

                # print(f"[DEBUG] RCPS Crashing activity {node}: crash_amount={crash_amount:.2f}, cost={cost:.2f}")

                # Update duration
                new_duration = max(min_dur, dur - crash_amount)
                G.nodes[node]['duration'] = new_duration
                total_crash_cost += cost
                
                # Recalculate CPM
                G = network_builder.forward_pass(G)
                G = network_builder.backward_pass(G)
                G = network_builder.calculate_float(G)
                ef_dict = nx.get_node_attributes(G, 'EF')
                current_duration = int(round(max(ef_dict.values()))) if ef_dict else 0
                
                # Log the crash
                crash_log.append({
                    'iteration': iterations + 1,
                    'activity': node,
                    'crash_amount': crash_amount,
                    'cost': cost,
                    'duration': int(round(G.nodes[node]['duration'])),
                    'current_project_duration': current_duration,
                    'total_crash_cost': total_crash_cost,
                    'critical_path': [n for n in G.nodes if G.nodes[n].get('float', 0) == 0 and n not in ['START', 'END']],
                    'normal_cost': normal_cost,
                    'EF': ef,
                    'current_time': current_time,
                    'step_normal_cost': step_normal_cost,
                    'total_normal_cost_accumulated': total_normal_cost_accumulated,
                    'active_activities': active_activities_this_step,
                    'resource_limit': self.resource_limit  # Add RCPS-specific info
                })
            else:
                # print("[DEBUG] RCPS No crashable activities (resource constraints considered)")
                crash_log.append({
                    'iteration': iterations + 1,
                    'activity': 'None',
                    'crash_amount': 0,
                    'cost': 0,
                    'duration': None,
                    'current_project_duration': current_duration,
                    'total_crash_cost': total_crash_cost,
                    'critical_path': [n for n in G.nodes if G.nodes[n].get('float', 0) == 0 and n not in ['START', 'END']],
                    'normal_cost': 0,
                    'EF': None,
                    'current_time': current_time,
                    'step_normal_cost': step_normal_cost,
                    'total_normal_cost_accumulated': total_normal_cost_accumulated,
                    'active_activities': active_activities_this_step,
                    'resource_limit': self.resource_limit
                })

            iterations += 1
            current_time += 1
            
            if target_duration is not None and current_duration <= target_duration:
                # print(f"[DEBUG] RCPS Target duration reached: {current_duration} <= {target_duration}")
                termination_reason = 'Target duration reached'
                break
            
            if current_time > current_duration:
                # print(f"[DEBUG] RCPS Simulation complete: time {current_time} > duration {current_duration}")
                if not termination_reason:
                    termination_reason = 'Completed'
                break

        if not termination_reason:
            if target_duration is not None and current_duration <= target_duration:
                termination_reason = 'Target duration reached'
            else:
                termination_reason = 'Max iterations reached' if iterations >= max_iterations else 'Completed'

        computation_time = time_mod.time() - start_time
        final_duration = current_duration
        total_normal_cost = total_normal_cost_accumulated
        efficiency_metrics = {'cost_per_unit_time': total_crash_cost / (original_duration - final_duration) if final_duration < original_duration else 0}
        
        # print(f"[DEBUG] RCPS crashing completed: original={original_duration}, final={final_duration}, crash_cost={total_crash_cost:.2f}")
        
        return CrashingResult(
            crashed_graph=G,
            original_duration=original_duration,
            final_duration=final_duration,
            target_duration=target_duration,
            total_crash_cost=total_crash_cost,
            total_normal_cost=total_normal_cost,
            crash_log=crash_log,
            efficiency_metrics=efficiency_metrics,
            termination_reason=termination_reason,
            iterations_used=iterations,
            computation_time=computation_time
        )
    
    def _validate_crash_feasibility(self, activity, crash_amount, current_time, G):
        """
        Validate that crashing an activity doesn't violate resource constraints
        
        Args:
            activity: Activity ID to crash
            crash_amount: Amount to crash the activity
            current_time: Current simulation time
            G: Current project graph
            
        Returns:
            bool: True if crash is feasible under resource constraints
        """
        try:
            # Create a temporary copy of the graph with the crash applied
            temp_G = G.copy()
            current_duration = temp_G.nodes[activity]['duration']
            min_duration = temp_G.nodes[activity].get('min_duration', current_duration)
            new_duration = max(min_duration, current_duration - crash_amount)
            temp_G.nodes[activity]['duration'] = new_duration
            
            # Recalculate schedule
            network_builder = getattr(self.base_analyzer, 'network_builder', None)
            if network_builder:
                temp_G = network_builder.forward_pass(temp_G)
            
            # Check resource usage at each time period
            timeline = {}
            for node in temp_G.nodes():
                if node not in ['START', 'END']:
                    node_data = temp_G.nodes[node]
                    start_time = int(node_data.get('ES', 0))
                    duration = int(node_data.get('duration', 0))
                    resource_demand = node_data.get('resource', 1)
                    
                    for t in range(start_time, start_time + duration):
                        if t not in timeline:
                            timeline[t] = 0
                        timeline[t] += resource_demand
            
            # Check if any time period exceeds resource limit
            for time_period, resource_usage in timeline.items():
                if resource_usage > self.resource_limit:
                    return False
            
            return True
            
        except Exception as e:
            # print(f"[DEBUG] Error validating crash feasibility: {e}")
            return False
    
    def _best_efficiency_strategy(self, *args, **kwargs):
        """RCPS-aware best efficiency strategy (stub)"""
        # print("[DEBUG] RCPS _best_efficiency_strategy called")
        raise NotImplementedError("RCPS Best efficiency strategy not yet implemented.")

    def _critical_path_strategy(self, *args, **kwargs):
        """RCPS-aware critical path priority strategy (stub)"""
        # print("[DEBUG] RCPS _critical_path_strategy called")
        raise NotImplementedError("RCPS Critical path priority strategy not yet implemented.")

    def _resource_aware_strategy(self, *args, **kwargs):
        """RCPS-aware resource strategy (stub)"""
        # print("[DEBUG] RCPS _resource_aware_strategy called")
        raise NotImplementedError("RCPS Resource aware strategy not yet implemented.")

def compare_crashing_results(results: List[CrashingResult]) -> Dict[str, Any]:
    """Compare multiple crashing results and provide analysis"""
    # ...existing logic from enhanced_project_crashing.py...
    pass

def generate_crashing_report(result: CrashingResult) -> str:
    """Generate a comprehensive text report for crashing results"""
    lines = []
    lines.append("PROJECT CRASHING OPTIMIZATION LOG\n" + "="*50)
    lines.append(f"Initial Project Duration: {result.original_duration}")
    lines.append(f"Target Duration: {result.target_duration}")
    lines.append(f"Final Project Duration: {result.final_duration}")
    lines.append(f"Total Crash Cost: ${result.total_crash_cost:,.2f}")
    lines.append(f"Total Normal Cost: ${result.total_normal_cost:,.2f}")
    lines.append(f"Iterations Used: {result.iterations_used}")
    lines.append(f"Termination Reason: {result.termination_reason}")
    lines.append(f"Computation Time: {result.computation_time:.3f} seconds")
    lines.append("-"*50)
    lines.append("Step-by-Step Crashing Log:")
    lines.append("-"*50)
    cumulative_crash_cost = 0.0
    cumulative_step_cost = 0.0
    for entry in result.crash_log:
        activity_id = entry.get('activity', '?')
        crash_cost = float(entry.get('cost', 0))
        # Use 'step_normal_cost' for the report, which is the sum of costs for all active tasks in that step.
        step_normal_cost = float(entry.get('step_normal_cost', 0))
        step_total_cost = crash_cost + step_normal_cost
        cumulative_crash_cost += crash_cost
        cumulative_step_cost += step_total_cost
        
        lines.append(f"Step {entry.get('iteration', '?')}: Activity {activity_id} crashed to duration {entry.get('duration', '?') if activity_id != 'None' else 'N/A'}")
        lines.append(f"  - Crash Cost: ${crash_cost:,.2f}")
        lines.append(f"  - Step Normal Cost (Active Tasks): ${step_normal_cost:,.2f}")
        lines.append(f"  - Step Total Cost: ${step_total_cost:,.2f}")
        lines.append(f"  - Cumulative Crash Cost: ${cumulative_crash_cost:,.2f}")
        lines.append(f"  - Cumulative Project Cost: ${cumulative_step_cost:,.2f}")
        lines.append(f"  - Project Duration: {entry.get('current_project_duration', '?')}")
        lines.append(f"  - Critical Path: {entry.get('critical_path', [])}")
        lines.append("")
    lines.append("="*50)
    lines.append("SUMMARY BREAKDOWN")
    lines.append("-"*50)
    lines.append(f"Original Duration: {result.original_duration}")
    lines.append(f"Final Duration: {result.final_duration}")
    lines.append(f"Duration Reduction: {result.original_duration - result.final_duration}")
    lines.append(f"Target Duration: {result.target_duration}")
    lines.append(f"Total Crash Cost: ${result.total_crash_cost:,.2f}")
    lines.append(f"Total Normal Cost: ${result.total_normal_cost:,.2f}")
    total_step_cost = result.total_crash_cost + result.total_normal_cost
    lines.append(f"Total Step Cost: ${total_step_cost:,.2f}")
    if total_step_cost > 0:
        lines.append(f"Crash Cost %: {100*result.total_crash_cost/total_step_cost:.2f}%")
        lines.append(f"Normal Cost %: {100*result.total_normal_cost/total_step_cost:.2f}%")
    lines.append(f"Cost per Unit Duration Reduction: ${result.efficiency_metrics.get('cost_per_unit_time', 0):,.2f}")
    lines.append(f"Iterations Used: {result.iterations_used}")
    lines.append(f"Termination Reason: {result.termination_reason}")
    lines.append(f"Computation Time: {result.computation_time:.3f} seconds")
    # Final critical path (if available)
    if result.crash_log:
        lines.append(f"Final Critical Path: {result.crash_log[-1].get('critical_path', [])}")
    # Crashed activities summary
    lines.append("-"*50)
    lines.append("Crashed Activities Summary:")
    activity_summary = {}
    for entry in result.crash_log:
        act = entry.get('activity', '?')
        if act not in activity_summary:
            activity_summary[act] = {'crash_cost': 0.0, 'crash_count': 0, 'final_duration': entry.get('duration', '?')}
        activity_summary[act]['crash_cost'] += float(entry.get('cost', 0))
        activity_summary[act]['crash_count'] += 1
        activity_summary[act]['final_duration'] = entry.get('duration', '?')
    for act, info in activity_summary.items():
        lines.append(f"  - Activity {act}: Crashed {info['crash_count']}x, Total Crash Cost: ${info['crash_cost']:,.2f}, Final Duration: {info['final_duration']}")
    lines.append("="*50)
    return "\n".join(lines)
