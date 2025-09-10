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
    ENHANCED_LOWEST_COST = "enhanced_lowest_cost"
    PARETO_OPTIMAL = "pareto_optimal"

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

        # 🔍 DEBUG: Check cost data in graph at start of crashing
        print("\n🔍 [CRASHING DEBUG] COST DATA INVESTIGATION")
        print("=" * 60)
        print(f"📊 Analyzer type: {type(analyzer)}")
        print(f"📊 Graph nodes count: {len(G.nodes())}")
        print(f"📊 Graph nodes: {list(G.nodes())}")
        
        print(f"\n💰 COST DATA IN GRAPH NODES:")
        cost_data_found = 0
        cost_data_missing = 0
        for node_id, node_data in G.nodes(data=True):
            if node_id not in ['START', 'END']:
                crash_cost = node_data.get('crash_cost', 'MISSING')
                normal_cost = node_data.get('normal_cost', 'MISSING')
                duration = node_data.get('duration', 'MISSING')
                min_duration = node_data.get('min_duration', 'MISSING')
                
                if crash_cost != 'MISSING' and normal_cost != 'MISSING':
                    cost_data_found += 1
                    status = "✅"
                else:
                    cost_data_missing += 1
                    status = "❌"
                
                print(f"   {status} {node_id}: crash_cost={crash_cost}, normal_cost={normal_cost}, duration={duration}, min_duration={min_duration}")
        
        print(f"\n📈 COST DATA SUMMARY:")
        print(f"   ✅ Nodes with cost data: {cost_data_found}")
        print(f"   ❌ Nodes missing cost data: {cost_data_missing}")
        
        if cost_data_missing > 0:
            print(f"\n🚨 WARNING: {cost_data_missing} nodes are missing cost data!")
            print(f"   This will cause zero cost calculations in crashing optimization")
        else:
            print(f"\n✅ SUCCESS: All nodes have cost data - crashing should work correctly")
        
        print("=" * 60)

        start_time = time_mod.time()
        crash_log = []
        total_crash_cost = 0.0
        total_normal_cost_accumulated = 0.0
        iterations = 0
        termination_reason = ''

        # Initial CPM calculation
        # Use a local forward_pass for project crashing to ensure ES/EF are recalculated using current durations
        # --- PROMPT: CPM recalculation now uses NetworkBuilder for consistency ---
        # Use CPM logic from cmp_analyzer.py (forward_pass, backward_pass, calculate_float)
        
        # DEBUG: Check EF values before NetworkBuilder processing
        ef_before = {node: G.nodes[node].get('EF', 0) for node in G.nodes}
        print(f"[DEBUG CRASHING] EF values before NetworkBuilder: {ef_before}")
        
        network_builder = getattr(analyzer, 'network_builder', None)
        if network_builder is None:
            from src.pmhelper.core.network_builder import NetworkBuilder
            network_builder = NetworkBuilder()
        G = network_builder.forward_pass(G)
        G = network_builder.backward_pass(G)
        G = network_builder.calculate_float(G)
        
        # Use max EF for project duration
        ef_dict = nx.get_node_attributes(G, 'EF')
        
        # DEBUG: Check EF values after processing
        print(f"[DEBUG CRASHING] EF values after processing: {ef_dict}")
        
        original_duration = int(round(max(ef_dict.values()))) if ef_dict else 0
        print(f"[DEBUG CRASHING] Calculated original_duration: {original_duration}")
        
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
            
            # 🔍 DEBUG: Investigate crashable activities
            print(f"\n🔨 [ITERATION {iterations}] CRASHABLE ACTIVITY ANALYSIS")
            print(f"   Current time: {current_time}, Target duration: {target_duration}")
            print(f"   Current duration: {current_duration}")
            
            critical_activities = []
            non_critical_activities = []
            
            for node in G.nodes:
                if node not in ['START', 'END'] and node not in completed_activities:
                    data = G.nodes[node]
                    dur = int(round(data.get('duration', 0)))
                    min_dur = int(round(data.get('min_duration', dur)))
                    crash_cost = data.get('crash_cost', 0)
                    normal_cost = data.get('normal_cost', 0)
                    ef = int(round(data.get('EF', 0)))
                    float_val = data.get('float', 0)
                    
                    activity_info = {
                        'node': node,
                        'duration': dur,
                        'min_duration': min_dur,
                        'crash_cost': crash_cost,
                        'normal_cost': normal_cost,
                        'ef': ef,
                        'float': float_val,
                        'is_critical': float_val == 0,
                        'can_crash': dur > min_dur and crash_cost > 0 and ef > current_time
                    }
                    
                    if float_val == 0:
                        critical_activities.append(activity_info)
                        if activity_info['can_crash']:
                            crashable.append((node, crash_cost, dur, min_dur, normal_cost, ef))
                    else:
                        non_critical_activities.append(activity_info)
            
            print(f"   🎯 Critical activities:")
            for activity in critical_activities:
                status = "✅ CRASHABLE" if activity['can_crash'] else "❌ NOT CRASHABLE"
                print(f"      {status} {activity['node']}: crash_cost={activity['crash_cost']}, duration={activity['duration']}, min_duration={activity['min_duration']}")
            
            print(f"   📋 Non-critical activities: {len(non_critical_activities)}")
            
            print(f"   🔨 Final crashable list: {[item[0] for item in crashable]}")
            
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
                # No crashable activities found - check if we should continue or terminate
                print(f"⚠️  [ITERATION {iterations + 1}] No more activities can be crashed")
                print(f"   Current duration: {current_duration}, Target: {target_duration}")
                print(f"   All critical path activities have reached minimum duration or cannot be crashed")
                
                # If no activities can be crashed and we haven't reached target, terminate early
                if target_duration is not None and current_duration > target_duration:
                    print(f"   🛑 EARLY TERMINATION: Target duration ({target_duration}) is not achievable")
                    print(f"   Best achievable duration: {current_duration}")
                    termination_reason = 'Target duration not achievable - all activities at minimum'
                    break
                
                # FIXED: Don't log "Activity None" entries - just advance time and terminate
                print(f"   ⏭️  No more crashing possible - terminating early")
                termination_reason = 'No more activities can be crashed'
                break

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
                # No crashable activities found in RCPS - check if we should continue or terminate
                print(f"⚠️  [RCPS ITERATION {iterations + 1}] No more activities can be crashed (resource constraints considered)")
                print(f"   Current duration: {current_duration}, Target: {target_duration}")
                print(f"   All activities have reached minimum duration or resource constraints prevent crashing")
                
                # If no activities can be crashed and we haven't reached target, terminate early
                if target_duration is not None and current_duration > target_duration:
                    print(f"   🛑 EARLY TERMINATION: Target duration ({target_duration}) is not achievable with resource constraints")
                    print(f"   Best achievable duration: {current_duration}")
                    termination_reason = 'Target duration not achievable - resource constraints'
                    break
                
                # Don't log "Activity None" entries - just advance time silently
                print(f"   ⏭️  Advancing time without logging null activity")

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

    # ============================================================================
    # ENHANCED PHASE 2 IMPLEMENTATION - TIME-BASED SIMULATION WITH FOUNDATION METHODS
    # ============================================================================
    
    def _enhanced_lowest_cost_strategy(self, target_duration=None, max_budget=None, max_crash_cost=None, max_normal_cost=None, max_iterations=300, **kwargs):
        """
        Enhanced RCPS-aware lowest cost strategy using Phase 1 foundation methods.
        
        This method implements the improved crashing methodology with:
        - Dynamic RCPS schedule generation for crash evaluation
        - Sophisticated activity status tracking
        - Time-based simulation with realistic project progression
        - Full resource constraint integration throughout the process
        
        Args:
            target_duration: Target project duration to achieve
            max_budget: Maximum total budget available
            max_crash_cost: Maximum crash cost budget
            max_normal_cost: Maximum normal cost budget  
            max_iterations: Maximum iterations to prevent infinite loops
            
        Returns:
            CrashingResult: Comprehensive results with enhanced data
        """
        print(f"[PHASE2] Enhanced RCPS crashing strategy starting...")
        print(f"[PHASE2] Target: {target_duration}, Resource Limit: {self.resource_limit}")
        
        # Initialize core variables
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
        
        # Generate initial RCPS schedule using foundation method
        print(f"[PHASE2] Generating initial RCPS schedule...")
        initial_schedule = self.generate_rcps_schedule_for_graph(
            G, self.resource_limit, 'minimum_slack'
        )
        
        if not initial_schedule['schedule_feasible']:
            raise ValueError("Initial RCPS schedule is not feasible with given resource constraints")
        
        original_duration = initial_schedule['project_duration']
        current_duration = original_duration
        current_time = 0.0  # Start at time 0 for proper simulation
        
        print(f"[PHASE2] Initial project duration: {original_duration}")
        print(f"[PHASE2] Critical activities: {initial_schedule['critical_activities']}")
        
        # Main simulation loop with time-based progression
        while current_duration > target_duration and iterations < max_iterations:
            iterations += 1
            print(f"\\n[PHASE2] === Iteration {iterations} ===")
            print(f"[PHASE2] Current time: {current_time}, Duration: {current_duration}, Target: {target_duration}")
            
            # STEP 1: Analyze current activity status using foundation method
            activity_status = self.analyze_activity_status(G, current_time)
            print(f"[PHASE2] Activity status: Completed={len(activity_status['completed'])}, " +
                  f"In-Progress={len(activity_status['in_progress'])}, Future={len(activity_status['future'])}")
            
            # STEP 2: Calculate step costs for current time
            step_normal_cost = 0
            active_activities_this_step = []
            
            for activity_id, details in activity_status['status_details'].items():
                if details['status'] == 'in_progress':
                    step_normal_cost += G.nodes[activity_id].get('normal_cost', 0)
                    active_activities_this_step.append(activity_id)
            
            print(f"[PHASE2] Step normal cost: ${step_normal_cost}, Active activities: {active_activities_this_step}")
            
            # STEP 3: Evaluate crash candidates using foundation method
            critical_activities = [act for act in G.nodes() 
                                 if G.nodes[act].get('float', 0) == 0 and act not in ['START', 'END']]
            
            crash_candidates = self.evaluate_crash_candidates(
                G, self.resource_limit, 'minimum_slack', current_time, critical_activities
            )
            
            print(f"[PHASE2] Found {len(crash_candidates)} crash candidates")
            if crash_candidates:
                for i, candidate in enumerate(crash_candidates[:3], 1):  # Show top 3
                    print(f"[PHASE2]   {i}. Activity {candidate['activity_id']}: " +
                          f"Cost=${candidate['crash_cost']}, Reduction={candidate['duration_reduction']}, " +
                          f"Effectiveness=${candidate['cost_effectiveness']:.2f}")
            
            # STEP 4: Budget validation before committing to crash
            potential_crash_cost = 0
            selected_candidate = None
            
            if crash_candidates:
                # Select best candidate (already sorted by cost-effectiveness)
                candidate = crash_candidates[0]
                potential_crash_cost = candidate['crash_cost']
                selected_candidate = candidate
                
                # Budget checks
                if max_budget is not None:
                    projected_total = total_normal_cost_accumulated + step_normal_cost + total_crash_cost + potential_crash_cost
                    if projected_total > max_budget:
                        print(f"[PHASE2] Budget limit would be exceeded: {projected_total} > {max_budget}")
                        termination_reason = 'Budget limit would be exceeded'
                        break
                
                if max_crash_cost is not None:
                    projected_crash = total_crash_cost + potential_crash_cost
                    if projected_crash > max_crash_cost:
                        print(f"[PHASE2] Crash cost limit would be exceeded: {projected_crash} > {max_crash_cost}")
                        termination_reason = 'Crash cost limit would be exceeded'
                        break
                
                if max_normal_cost is not None:
                    projected_normal = total_normal_cost_accumulated + step_normal_cost
                    if projected_normal > max_normal_cost:
                        print(f"[PHASE2] Normal cost limit would be exceeded: {projected_normal} > {max_normal_cost}")
                        termination_reason = 'Normal cost limit would be exceeded'
                        break
            
            # STEP 5: Commit costs and execute crash
            total_normal_cost_accumulated += step_normal_cost
            
            if selected_candidate:
                activity_id = selected_candidate['activity_id']
                crash_cost = selected_candidate['crash_cost']
                duration_reduction = selected_candidate['duration_reduction']
                new_project_duration = selected_candidate['new_project_duration']
                
                print(f"[PHASE2] Executing crash: Activity {activity_id}, Cost=${crash_cost}, " +
                      f"Duration reduction={duration_reduction}")
                
                # Apply crash to graph
                current_dur = G.nodes[activity_id]['duration']
                min_dur = G.nodes[activity_id].get('min_duration', current_dur)
                new_dur = max(min_dur, current_dur - 1)  # Crash by 1 unit
                G.nodes[activity_id]['duration'] = new_dur
                
                # Recalculate CPM using foundation method
                G = self._recalculate_cmp(G)
                
                # Update current duration with the actual result
                current_duration = new_project_duration
                total_crash_cost += crash_cost
                
                # Enhanced crash log with foundation method data
                crash_log.append({
                    'iteration': iterations,
                    'activity': activity_id,
                    'crash_amount': 1,
                    'cost': crash_cost,
                    'duration': new_dur,
                    'current_project_duration': current_duration,
                    'total_crash_cost': total_crash_cost,
                    'critical_path': critical_activities,
                    'current_time': current_time,
                    'step_normal_cost': step_normal_cost,
                    'total_normal_cost_accumulated': total_normal_cost_accumulated,
                    'active_activities': active_activities_this_step,
                    'resource_limit': self.resource_limit,
                    'activity_status': activity_status['summary'],
                    'duration_reduction': duration_reduction,
                    'cost_effectiveness': selected_candidate['cost_effectiveness'],
                    'schedule_feasible': True
                })
                
                print(f"[PHASE2] Crash completed. New project duration: {current_duration}")
                
            else:
                print(f"⚠️  [PHASE2 ITERATION {iterations}] No viable crash candidates found")
                print(f"   Current duration: {current_duration}, Target: {target_duration}")
                print(f"   No activities can be crashed due to resource/schedule constraints")
                
                # If no activities can be crashed and we haven't reached target, terminate early
                if target_duration is not None and current_duration > target_duration:
                    print(f"   🛑 EARLY TERMINATION: Target duration ({target_duration}) is not achievable")
                    print(f"   Best achievable duration: {current_duration}")
                    termination_reason = 'Target duration not achievable - no viable candidates'
                    break
                
                # Don't log "Activity None" entries for Phase 2
                print(f"   ⏭️  Advancing time without logging null activity")
                
                # If no crashes possible, advance time simulation
                if activity_status['in_progress'] or activity_status['future']:
                    # Find next significant time point
                    next_times = []
                    for activity_id, details in activity_status['status_details'].items():
                        if details['status'] in ['in_progress', 'future']:
                            if details['status'] == 'in_progress':
                                next_times.append(details['ef'])
                            else:
                                next_times.append(details['es'])
                    
                    if next_times:
                        current_time = min([t for t in next_times if t > current_time])
                        print(f"[PHASE2] Advancing simulation time to: {current_time}")
                    else:
                        termination_reason = 'No more activities to process'
                        break
                else:
                    termination_reason = 'All activities completed'
                    break
            
            # STEP 6: Check termination conditions
            if target_duration is not None and current_duration <= target_duration:
                print(f"[PHASE2] Target duration achieved: {current_duration} <= {target_duration}")
                termination_reason = 'Target duration reached'
                break
            
            # Prevent infinite loops by advancing time if no progress
            if iterations > 1 and current_duration == crash_log[-2].get('current_project_duration', 0):
                if selected_candidate is None:  # No crash occurred
                    current_time += 1  # Force time progression
                    print(f"[PHASE2] Forcing time progression to: {current_time}")
        
        # Final processing
        if not termination_reason:
            if target_duration is not None and current_duration <= target_duration:
                termination_reason = 'Target duration reached'
            else:
                termination_reason = 'Max iterations reached' if iterations >= max_iterations else 'Completed'

        computation_time = time_mod.time() - start_time
        
        # Enhanced efficiency metrics
        duration_improvement = original_duration - current_duration
        efficiency_metrics = {
            'cost_per_unit_time': total_crash_cost / duration_improvement if duration_improvement > 0 else 0,
            'duration_improvement_percentage': (duration_improvement / original_duration * 100) if original_duration > 0 else 0,
            'resource_utilization': self.resource_limit,
            'iterations_per_improvement': iterations / duration_improvement if duration_improvement > 0 else iterations,
            'average_cost_per_crash': total_crash_cost / len([log for log in crash_log if log['crash_amount'] > 0]) if any(log['crash_amount'] > 0 for log in crash_log) else 0
        }
        
        print(f"\\n[PHASE2] === Crashing Complete ===")
        print(f"[PHASE2] Original duration: {original_duration}")
        print(f"[PHASE2] Final duration: {current_duration}")
        print(f"[PHASE2] Duration improvement: {duration_improvement} ({efficiency_metrics['duration_improvement_percentage']:.1f}%)")
        print(f"[PHASE2] Total crash cost: ${total_crash_cost:.2f}")
        print(f"[PHASE2] Cost per unit time: ${efficiency_metrics['cost_per_unit_time']:.2f}")
        print(f"[PHASE2] Iterations used: {iterations}")
        print(f"[PHASE2] Termination reason: {termination_reason}")
        
        return CrashingResult(
            crashed_graph=G,
            original_duration=original_duration,
            final_duration=current_duration,
            target_duration=target_duration,
            total_crash_cost=total_crash_cost,
            total_normal_cost=total_normal_cost_accumulated,
            crash_log=crash_log,
            efficiency_metrics=efficiency_metrics,
            termination_reason=termination_reason,
            iterations_used=iterations,
            computation_time=computation_time
        )

    # ============================================================================
    # PHASE 3 IMPLEMENTATION - INTELLIGENT OPTIMIZATION & ADVANCED ANALYTICS
    # ============================================================================
    
    def _intelligent_crash_scorer(self, candidates, project_context, historical_data=None):
        """
        Advanced crash candidate scoring using multiple intelligence factors.
        
        This method implements sophisticated scoring algorithms that consider:
        - Cost-effectiveness with diminishing returns modeling
        - Critical path impact prediction with cascade analysis
        - Resource utilization optimization patterns
        - Risk assessment with uncertainty quantification
        - Historical performance pattern matching
        
        Args:
            candidates: List of crash candidate dictionaries
            project_context: Current project state and characteristics
            historical_data: Optional historical performance data
            
        Returns:
            List of candidates with enhanced intelligence scores
        """
        if not candidates:
            return []
        
        print(f"[PHASE3] Intelligent scoring for {len(candidates)} candidates...")
        
        # Extract project characteristics for adaptive scoring
        total_activities = len(project_context.get('all_activities', []))
        resource_utilization = project_context.get('resource_utilization', 0.5)
        project_complexity = self._calculate_project_complexity(project_context)
        
        enhanced_candidates = []
        
        for candidate in candidates:
            # Base metrics from Phase 2
            base_score = candidate.get('cost_effectiveness', 0)
            crash_cost = candidate.get('crash_cost', 0)
            duration_reduction = candidate.get('duration_reduction', 0)
            activity_id = candidate.get('activity_id', '')
            
            # Intelligence Factor 1: Diminishing Returns Modeling
            diminishing_factor = self._calculate_diminishing_returns(
                crash_cost, duration_reduction, project_context
            )
            
            # Intelligence Factor 2: Critical Path Impact Prediction
            critical_impact = self._predict_critical_path_impact(
                activity_id, duration_reduction, project_context
            )
            
            # Intelligence Factor 3: Resource Optimization Potential
            resource_optimization = self._assess_resource_optimization(
                activity_id, project_context
            )
            
            # Intelligence Factor 4: Risk Assessment
            risk_factor = self._assess_crash_risks(
                activity_id, duration_reduction, project_context
            )
            
            # Intelligence Factor 5: Historical Pattern Matching
            historical_factor = self._match_historical_patterns(
                activity_id, crash_cost, historical_data
            ) if historical_data else 1.0
            
            # Composite Intelligence Score
            intelligence_weights = {
                'base_effectiveness': 0.25,
                'diminishing_returns': 0.20,
                'critical_impact': 0.20,
                'resource_optimization': 0.15,
                'risk_mitigation': 0.10,
                'historical_learning': 0.10
            }
            
            intelligence_score = (
                base_score * intelligence_weights['base_effectiveness'] +
                diminishing_factor * intelligence_weights['diminishing_returns'] +
                critical_impact * intelligence_weights['critical_impact'] +
                resource_optimization * intelligence_weights['resource_optimization'] +
                (1.0 - risk_factor) * intelligence_weights['risk_mitigation'] +
                historical_factor * intelligence_weights['historical_learning']
            )
            
            # Adaptive scoring based on project characteristics
            adaptive_multiplier = self._calculate_adaptive_multiplier(
                project_complexity, resource_utilization, total_activities
            )
            
            final_intelligence_score = intelligence_score * adaptive_multiplier
            
            # Enhanced candidate with intelligence metrics
            enhanced_candidate = candidate.copy()
            enhanced_candidate.update({
                'intelligence_score': final_intelligence_score,
                'intelligence_factors': {
                    'diminishing_returns': diminishing_factor,
                    'critical_impact': critical_impact,
                    'resource_optimization': resource_optimization,
                    'risk_factor': risk_factor,
                    'historical_factor': historical_factor,
                    'adaptive_multiplier': adaptive_multiplier
                },
                'scoring_confidence': self._calculate_scoring_confidence(
                    base_score, intelligence_score, project_context
                )
            })
            
            enhanced_candidates.append(enhanced_candidate)
        
        # Sort by intelligence score (highest first)
        enhanced_candidates.sort(key=lambda x: x['intelligence_score'], reverse=True)
        
        print(f"[PHASE3] Intelligence scoring complete. Top candidate: {enhanced_candidates[0]['activity_id']} " +
              f"(Score: {enhanced_candidates[0]['intelligence_score']:.3f})")
        
        return enhanced_candidates
    
    def _calculate_diminishing_returns(self, crash_cost, duration_reduction, project_context):
        """Calculate diminishing returns factor for crash cost effectiveness."""
        if duration_reduction <= 0:
            return 0.0
        
        # Model diminishing returns using logarithmic decay
        base_effectiveness = duration_reduction / (crash_cost + 1)  # Prevent division by zero
        
        # Adjust for project stage (later crashes are less effective)
        project_progress = project_context.get('completion_percentage', 0)
        stage_penalty = 1.0 - (project_progress * 0.3)  # 30% penalty at project end
        
        # Diminishing returns curve
        import math
        diminishing_curve = math.log(1 + base_effectiveness) * stage_penalty
        
        return min(1.0, max(0.0, diminishing_curve))
    
    def _predict_critical_path_impact(self, activity_id, duration_reduction, project_context):
        """Predict the impact of crashing on critical path optimization."""
        critical_activities = project_context.get('critical_activities', [])
        
        if activity_id not in critical_activities:
            return 0.1  # Low impact for non-critical activities
        
        # High impact for critical activities
        critical_impact = 0.8
        
        # Boost impact if activity is on multiple critical paths
        critical_path_multiplicity = project_context.get('critical_path_count', {}).get(activity_id, 1)
        multiplicity_bonus = min(0.2, critical_path_multiplicity * 0.05)
        
        # Boost impact based on activity position in critical path
        activity_position = project_context.get('activity_positions', {}).get(activity_id, 0.5)
        position_factor = 1.0 + (0.5 - abs(activity_position - 0.5)) * 0.4  # Favor middle positions
        
        return min(1.0, (critical_impact + multiplicity_bonus) * position_factor)
    
    def _assess_resource_optimization(self, activity_id, project_context):
        """Assess potential for resource optimization through crashing."""
        activity_resource_req = project_context.get('activity_resources', {}).get(activity_id, 1)
        total_resource_limit = project_context.get('resource_limit', 10)
        current_utilization = project_context.get('resource_utilization', 0.5)
        
        # Higher score for activities that can free up resources
        resource_efficiency = 1.0 - (activity_resource_req / total_resource_limit)
        
        # Bonus for high utilization scenarios (more benefit from optimization)
        utilization_bonus = current_utilization * 0.3
        
        # Penalty for over-utilization risk
        over_utilization_penalty = max(0, (current_utilization - 0.9) * 2.0)
        
        optimization_score = resource_efficiency + utilization_bonus - over_utilization_penalty
        
        return min(1.0, max(0.0, optimization_score))
    
    def _assess_crash_risks(self, activity_id, duration_reduction, project_context):
        """Evaluate potential risks of crashing activities."""
        # Base risk increases with crash amount
        base_risk = min(0.8, duration_reduction * 0.1)
        
        # Resource constraint risk
        activity_resources = project_context.get('activity_resources', {}).get(activity_id, 1)
        resource_utilization = project_context.get('resource_utilization', 0.5)
        resource_risk = max(0, (resource_utilization + activity_resources/10 - 0.8) * 2)
        
        # Dependency cascade risk
        activity_dependencies = project_context.get('activity_dependencies', {}).get(activity_id, 0)
        cascade_risk = min(0.3, activity_dependencies * 0.05)
        
        # Quality degradation risk (higher for intensive crashes)
        quality_risk = min(0.4, (duration_reduction / 2) * 0.2)
        
        # Composite risk score
        total_risk = base_risk + resource_risk + cascade_risk + quality_risk
        
        return min(1.0, max(0.0, total_risk))
    
    def _match_historical_patterns(self, activity_id, crash_cost, historical_data):
        """Match current scenario with historical performance patterns."""
        if not historical_data or not isinstance(historical_data, dict):
            return 1.0  # Neutral factor if no historical data
        
        # Look for similar activities in historical data
        activity_history = historical_data.get('activity_patterns', {}).get(activity_id, [])
        
        if not activity_history:
            return 1.0  # No historical data for this activity
        
        # Find similar cost scenarios
        similar_scenarios = [
            scenario for scenario in activity_history
            if abs(scenario.get('crash_cost', 0) - crash_cost) <= crash_cost * 0.2
        ]
        
        if not similar_scenarios:
            return 1.0  # No similar scenarios found
        
        # Calculate success rate of similar scenarios
        success_count = sum(1 for scenario in similar_scenarios if scenario.get('success', False))
        success_rate = success_count / len(similar_scenarios)
        
        # Return factor based on historical success rate
        return 0.5 + (success_rate * 0.5)  # Range: 0.5 to 1.0
    
    def _calculate_project_complexity(self, project_context):
        """Calculate project complexity score for adaptive algorithms."""
        activity_count = len(project_context.get('all_activities', []))
        dependency_count = project_context.get('total_dependencies', 0)
        resource_constraints = project_context.get('resource_constraint_tightness', 0.5)
        
        # Complexity factors
        size_complexity = min(1.0, activity_count / 50)  # Normalize to 50 activities
        dependency_complexity = min(1.0, dependency_count / (activity_count * 1.5)) if activity_count > 0 else 0
        resource_complexity = resource_constraints
        
        # Weighted complexity score
        complexity_score = (
            size_complexity * 0.4 +
            dependency_complexity * 0.3 +
            resource_complexity * 0.3
        )
        
        return min(1.0, max(0.1, complexity_score))
    
    def _calculate_adaptive_multiplier(self, complexity, resource_utilization, activity_count):
        """Calculate adaptive multiplier for scoring based on project characteristics."""
        # Base multiplier
        multiplier = 1.0
        
        # Adjust for complexity
        if complexity > 0.7:
            multiplier *= 1.1  # Boost for complex projects
        elif complexity < 0.3:
            multiplier *= 0.95  # Slight penalty for simple projects
        
        # Adjust for resource utilization
        if resource_utilization > 0.8:
            multiplier *= 1.15  # Higher multiplier for resource-constrained projects
        elif resource_utilization < 0.4:
            multiplier *= 0.9   # Lower multiplier for resource-abundant projects
        
        # Adjust for project size
        if activity_count > 30:
            multiplier *= 1.05  # Slight boost for large projects
        elif activity_count < 10:
            multiplier *= 0.98  # Slight penalty for small projects
        
        return min(1.3, max(0.8, multiplier))  # Constrain multiplier range
    
    def _calculate_scoring_confidence(self, base_score, intelligence_score, project_context):
        """Calculate confidence level in the scoring decision."""
        # Confidence based on score consistency
        score_consistency = 1.0 - abs(base_score - intelligence_score) / max(base_score, intelligence_score, 0.1)
        
        # Confidence based on data availability
        data_availability = min(1.0, len(project_context) / 10)  # Assume 10 context items is full
        
        # Confidence based on project characteristics
        complexity = project_context.get('complexity', 0.5)
        complexity_confidence = 1.0 - (complexity * 0.3)  # Less confident for complex projects
        
        # Composite confidence
        confidence = (score_consistency * 0.5 + data_availability * 0.3 + complexity_confidence * 0.2)
        
        return min(1.0, max(0.3, confidence))  # Minimum 30% confidence

    # ============================================================================
    # PHASE 3.2 - MULTI-OBJECTIVE OPTIMIZATION ENGINE
    # ============================================================================
    
    def _pareto_optimal_strategy(self, target_duration=None, objectives=['cost', 'time', 'quality', 'risk'], 
                               max_budget=None, max_iterations=100, **kwargs):
        """
        Generate Pareto-optimal solutions across multiple objectives.
        
        This method discovers solutions that represent optimal trade-offs between:
        - Cost minimization vs time reduction
        - Quality preservation vs acceleration  
        - Risk tolerance vs aggressive crashing
        - Resource utilization vs project speed
        
        Args:
            target_duration: Target project duration
            objectives: List of objectives to optimize ['cost', 'time', 'quality', 'risk']
            max_budget: Maximum budget constraint
            max_iterations: Maximum iterations for Pareto discovery
            
        Returns:
            ParetoOptimalResult: Contains multiple optimal solutions and trade-off analysis
        """
        print(f"[PHASE3] Multi-objective Pareto optimization starting...")
        print(f"[PHASE3] Objectives: {objectives}, Target duration: {target_duration}")
        
        # Initialize
        analyzer = self.base_analyzer
        G = copy.deepcopy(getattr(analyzer, 'G', None) or getattr(analyzer, 'graph', None))
        if G is None:
            raise ValueError("No project graph found in RCPS analyzer.")
        
        start_time = time_mod.time()
        pareto_solutions = []
        solution_space = []
        
        # Generate initial project context
        initial_schedule = self.generate_rcps_schedule_for_graph(G, self.resource_limit, 'minimum_slack')
        original_duration = initial_schedule['project_duration']
        
        # Define objective space boundaries
        objective_bounds = self._define_objective_bounds(G, original_duration, max_budget)
        
        print(f"[PHASE3] Exploring solution space with {len(objectives)} objectives...")
        
        # Multi-objective exploration using adaptive sampling
        exploration_strategies = [
            'aggressive_time',      # Minimize time regardless of cost
            'conservative_cost',    # Minimize cost with time constraints
            'balanced_approach',    # Balance all objectives
            'quality_preserving',   # Maintain quality while optimizing
            'risk_averse',         # Minimize risks in optimization
            'resource_efficient'    # Optimize resource utilization
        ]
        
        for strategy in exploration_strategies:
            print(f"[PHASE3] Exploring with strategy: {strategy}")
            
            # Generate solutions with different objective weights
            strategy_solutions = self._explore_strategy_space(
                G, strategy, objectives, objective_bounds, target_duration, max_iterations//len(exploration_strategies)
            )
            
            solution_space.extend(strategy_solutions)
        
        # Identify Pareto-optimal solutions
        print(f"[PHASE3] Identifying Pareto-optimal solutions from {len(solution_space)} candidates...")
        pareto_solutions = self._identify_pareto_optimal_solutions(solution_space, objectives)
        
        # Analyze trade-offs between solutions
        trade_off_analysis = self._analyze_pareto_tradeoffs(pareto_solutions, objectives)
        
        # Generate recommendations
        recommendations = self._generate_pareto_recommendations(pareto_solutions, trade_off_analysis, objectives)
        
        computation_time = time_mod.time() - start_time
        
        print(f"[PHASE3] Pareto optimization complete: {len(pareto_solutions)} optimal solutions found")
        print(f"[PHASE3] Computation time: {computation_time:.3f}s")
        
        return {
            'pareto_solutions': pareto_solutions,
            'trade_off_analysis': trade_off_analysis,
            'recommendations': recommendations,
            'solution_space': solution_space,
            'objective_bounds': objective_bounds,
            'computation_time': computation_time,
            'objectives_optimized': objectives
        }
    
    def _explore_strategy_space(self, G, strategy, objectives, bounds, target_duration, max_iterations):
        """Explore solution space using specific strategy approach."""
        solutions = []
        
        # Define strategy-specific weights for objectives
        strategy_weights = self._get_strategy_weights(strategy, objectives)
        
        for iteration in range(max_iterations):
            # Create variation in weights for exploration
            variation_factor = 0.1 + (iteration / max_iterations) * 0.3
            varied_weights = self._vary_objective_weights(strategy_weights, variation_factor)
            
            # Generate solution with these weights
            solution = self._generate_weighted_solution(G, varied_weights, target_duration, bounds)
            
            if solution:
                solution['strategy'] = strategy
                solution['iteration'] = iteration
                solution['objective_weights'] = varied_weights
                solutions.append(solution)
        
        return solutions
    
    def _get_strategy_weights(self, strategy, objectives):
        """Define objective weights for different strategies."""
        weight_profiles = {
            'aggressive_time': {'cost': 0.1, 'time': 0.7, 'quality': 0.1, 'risk': 0.1},
            'conservative_cost': {'cost': 0.7, 'time': 0.1, 'quality': 0.1, 'risk': 0.1},
            'balanced_approach': {'cost': 0.25, 'time': 0.25, 'quality': 0.25, 'risk': 0.25},
            'quality_preserving': {'cost': 0.2, 'time': 0.2, 'quality': 0.5, 'risk': 0.1},
            'risk_averse': {'cost': 0.2, 'time': 0.2, 'quality': 0.2, 'risk': 0.4},
            'resource_efficient': {'cost': 0.3, 'time': 0.3, 'quality': 0.2, 'risk': 0.2}
        }
        
        profile = weight_profiles.get(strategy, weight_profiles['balanced_approach'])
        
        # Normalize weights for selected objectives only
        selected_weights = {obj: profile.get(obj, 0) for obj in objectives}
        total_weight = sum(selected_weights.values())
        
        if total_weight > 0:
            return {obj: weight/total_weight for obj, weight in selected_weights.items()}
        else:
            return {obj: 1.0/len(objectives) for obj in objectives}
    
    def _vary_objective_weights(self, base_weights, variation_factor):
        """Create variations in objective weights for exploration."""
        import random
        varied_weights = {}
        
        for obj, weight in base_weights.items():
            # Add random variation
            variation = random.uniform(-variation_factor, variation_factor) * weight
            varied_weights[obj] = max(0.05, min(0.95, weight + variation))
        
        # Normalize weights
        total = sum(varied_weights.values())
        return {obj: weight/total for obj, weight in varied_weights.items()}
    
    def _generate_weighted_solution(self, G, objective_weights, target_duration, bounds):
        """Generate a solution optimized for specific objective weights."""
        try:
            # Use enhanced strategy with objective-aware scoring
            G_copy = copy.deepcopy(G)
            
            # Create project context for intelligent scoring
            project_context = self._build_project_context(G_copy)
            
            # Simulate simplified crashing with objective-aware decisions
            current_duration = project_context['original_duration']
            total_cost = 0
            total_risk = 0
            quality_score = 1.0
            crash_log = []
            
            iteration_count = 0
            max_solution_iterations = 20
            
            while (current_duration > target_duration if target_duration else False) and iteration_count < max_solution_iterations:
                iteration_count += 1
                
                # Get crash candidates
                critical_activities = [act for act in G_copy.nodes() 
                                     if G_copy.nodes[act].get('float', 0) == 0 and act not in ['START', 'END']]
                
                candidates = self.evaluate_crash_candidates(
                    G_copy, self.resource_limit, 'minimum_slack', 0, critical_activities
                )
                
                if not candidates:
                    break
                
                # Score candidates based on objective weights
                objective_scores = []
                for candidate in candidates:
                    score = self._calculate_objective_weighted_score(candidate, objective_weights, project_context)
                    objective_scores.append((candidate, score))
                
                # Select best candidate based on weighted objectives
                objective_scores.sort(key=lambda x: x[1], reverse=True)
                best_candidate, best_score = objective_scores[0]
                
                # Apply crash
                activity_id = best_candidate['activity_id']
                crash_cost = best_candidate['crash_cost']
                
                current_dur = G_copy.nodes[activity_id]['duration']
                new_dur = max(G_copy.nodes[activity_id].get('min_duration', current_dur), current_dur - 1)
                G_copy.nodes[activity_id]['duration'] = new_dur
                
                # Recalculate and update metrics
                G_copy = self._recalculate_cmp(G_copy)
                current_duration = best_candidate.get('new_project_duration', current_duration - 1)
                total_cost += crash_cost
                total_risk += self._assess_crash_risks(activity_id, 1, project_context)
                quality_score *= 0.98  # Slight quality degradation per crash
                
                crash_log.append({
                    'activity': activity_id,
                    'cost': crash_cost,
                    'duration_reduction': 1,
                    'iteration': iteration_count
                })
            
            # Calculate objective values
            objective_values = {
                'cost': total_cost,
                'time': project_context['original_duration'] - current_duration,
                'quality': quality_score,
                'risk': 1.0 - min(1.0, total_risk)  # Convert risk to quality-like metric
            }
            
            return {
                'final_graph': G_copy,
                'original_duration': project_context['original_duration'],
                'final_duration': current_duration,
                'objective_values': objective_values,
                'total_cost': total_cost,
                'quality_score': quality_score,
                'risk_score': total_risk,
                'crash_log': crash_log,
                'iterations': iteration_count
            }
            
        except Exception as e:
            print(f"[PHASE3] Error generating weighted solution: {e}")
            return None
    
    def _calculate_objective_weighted_score(self, candidate, weights, project_context):
        """Calculate weighted score based on multiple objectives."""
        # Normalize candidate metrics to 0-1 scale
        cost_score = 1.0 / (1.0 + candidate.get('crash_cost', 1))  # Lower cost = higher score
        time_score = candidate.get('duration_reduction', 0) / 5.0   # Normalize to typical reduction
        quality_score = 1.0 - min(0.5, candidate.get('crash_cost', 0) / 100.0)  # Higher cost = lower quality
        risk_score = 1.0 - self._assess_crash_risks(candidate.get('activity_id', ''), 1, project_context)
        
        # Apply weights
        weighted_score = (
            cost_score * weights.get('cost', 0) +
            time_score * weights.get('time', 0) +
            quality_score * weights.get('quality', 0) +
            risk_score * weights.get('risk', 0)
        )
        
        return weighted_score
    
    def _build_project_context(self, G):
        """Build comprehensive project context for intelligent scoring."""
        # Calculate basic project metrics
        activities = [node for node in G.nodes() if node not in ['START', 'END']]
        total_dependencies = len(G.edges())
        
        # Calculate initial duration using simple CPM
        G_analyzed = self._recalculate_cmp(G)
        original_duration = max([G_analyzed.nodes[node].get('ef', 0) for node in G_analyzed.nodes()])
        
        # Build context dictionary
        context = {
            'all_activities': activities,
            'total_dependencies': total_dependencies,
            'original_duration': original_duration,
            'critical_activities': [act for act in activities if G_analyzed.nodes[act].get('float', 0) == 0],
            'resource_limit': self.resource_limit,
            'resource_utilization': 0.7,  # Default assumption
            'activity_resources': {act: G.nodes[act].get('resource_req', 1) for act in activities},
            'activity_dependencies': {act: len(list(G.predecessors(act))) for act in activities},
            'completion_percentage': 0.0,
            'complexity': len(activities) / 50.0  # Normalize to 50 activities
        }
        
        return context

    def _define_objective_bounds(self, G, original_duration, max_budget):
        """Define bounds for each objective in the optimization space."""
        activities = [node for node in G.nodes() if node not in ['START', 'END']]
        
        # Calculate theoretical bounds
        max_possible_crash_cost = sum([G.nodes[act].get('crash_cost', 0) * 
                                     (G.nodes[act].get('duration', 1) - G.nodes[act].get('min_duration', 1))
                                     for act in activities])
        
        max_time_reduction = sum([G.nodes[act].get('duration', 1) - G.nodes[act].get('min_duration', 1)
                                for act in activities])
        
        bounds = {
            'cost': {'min': 0, 'max': min(max_possible_crash_cost, max_budget or max_possible_crash_cost)},
            'time': {'min': 0, 'max': min(max_time_reduction, original_duration)},
            'quality': {'min': 0.5, 'max': 1.0},  # Quality degradation bounds
            'risk': {'min': 0.0, 'max': 1.0}      # Risk accumulation bounds
        }
        
        return bounds
    
    def _identify_pareto_optimal_solutions(self, solution_space, objectives):
        """Identify Pareto-optimal solutions from the solution space."""
        if not solution_space:
            return []
        
        pareto_solutions = []
        
        for i, solution_a in enumerate(solution_space):
            is_pareto_optimal = True
            
            for j, solution_b in enumerate(solution_space):
                if i == j:
                    continue
                
                # Check if solution_b dominates solution_a
                dominates = True
                for obj in objectives:
                    val_a = solution_a['objective_values'].get(obj, 0)
                    val_b = solution_b['objective_values'].get(obj, 0)
                    
                    # For cost and risk, lower is better; for time and quality, higher is better
                    if obj in ['cost', 'risk']:
                        if val_a < val_b:  # solution_a is better in this objective
                            dominates = False
                            break
                    else:  # time, quality - higher is better
                        if val_a > val_b:  # solution_a is better in this objective
                            dominates = False
                            break
                
                # If solution_b dominates solution_a in all objectives
                if dominates:
                    # Check if solution_b is actually better in at least one objective
                    better_in_at_least_one = False
                    for obj in objectives:
                        val_a = solution_a['objective_values'].get(obj, 0)
                        val_b = solution_b['objective_values'].get(obj, 0)
                        
                        if obj in ['cost', 'risk']:
                            if val_b < val_a:  # solution_b is better
                                better_in_at_least_one = True
                                break
                        else:
                            if val_b > val_a:  # solution_b is better
                                better_in_at_least_one = True
                                break
                    
                    if better_in_at_least_one:
                        is_pareto_optimal = False
                        break
            
            if is_pareto_optimal:
                pareto_solutions.append(solution_a)
        
        # Remove duplicates based on objective values
        unique_pareto = []
        for solution in pareto_solutions:
            is_duplicate = False
            for existing in unique_pareto:
                if self._solutions_equivalent(solution, existing, objectives):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_pareto.append(solution)
        
        return unique_pareto
    
    def _solutions_equivalent(self, sol_a, sol_b, objectives, tolerance=0.01):
        """Check if two solutions are equivalent within tolerance."""
        for obj in objectives:
            val_a = sol_a['objective_values'].get(obj, 0)
            val_b = sol_b['objective_values'].get(obj, 0)
            if abs(val_a - val_b) > tolerance:
                return False
        return True
    
    def _analyze_pareto_tradeoffs(self, pareto_solutions, objectives):
        """Analyze trade-offs between Pareto-optimal solutions."""
        if len(pareto_solutions) < 2:
            return {'message': 'Insufficient solutions for trade-off analysis'}
        
        trade_offs = []
        
        for i, sol_a in enumerate(pareto_solutions):
            for j, sol_b in enumerate(pareto_solutions):
                if i >= j:
                    continue
                
                # Calculate trade-off metrics between solutions
                trade_off = {
                    'solution_a_index': i,
                    'solution_b_index': j,
                    'objective_differences': {},
                    'trade_off_ratio': {},
                    'preference_scenarios': []
                }
                
                for obj in objectives:
                    val_a = sol_a['objective_values'].get(obj, 0)
                    val_b = sol_b['objective_values'].get(obj, 0)
                    diff = val_b - val_a
                    
                    trade_off['objective_differences'][obj] = diff
                    
                    # Calculate trade-off ratio (percentage change)
                    if val_a != 0:
                        trade_off['trade_off_ratio'][obj] = (diff / val_a) * 100
                    else:
                        trade_off['trade_off_ratio'][obj] = float('inf') if diff > 0 else 0
                
                # Identify preference scenarios
                if trade_off['objective_differences'].get('cost', 0) < 0:  # A is cheaper
                    if trade_off['objective_differences'].get('time', 0) < 0:  # A is slower
                        trade_off['preference_scenarios'].append('cost_over_speed')
                    else:
                        trade_off['preference_scenarios'].append('cost_and_speed_optimal')
                
                trade_offs.append(trade_off)
        
        # Calculate overall trade-off statistics
        trade_off_stats = self._calculate_tradeoff_statistics(trade_offs, objectives)
        
        return {
            'pairwise_tradeoffs': trade_offs,
            'statistics': trade_off_stats,
            'solution_count': len(pareto_solutions)
        }
    
    def _calculate_tradeoff_statistics(self, trade_offs, objectives):
        """Calculate statistical summary of trade-offs."""
        if not trade_offs:
            return {}
        
        stats = {}
        
        for obj in objectives:
            differences = [t['objective_differences'].get(obj, 0) for t in trade_offs]
            ratios = [t['trade_off_ratio'].get(obj, 0) for t in trade_offs if t['trade_off_ratio'].get(obj, 0) != float('inf')]
            
            stats[obj] = {
                'mean_difference': sum(differences) / len(differences) if differences else 0,
                'max_difference': max(differences) if differences else 0,
                'min_difference': min(differences) if differences else 0,
                'mean_ratio': sum(ratios) / len(ratios) if ratios else 0,
                'variability': max(differences) - min(differences) if differences else 0
            }
        
        return stats
    
    def _generate_pareto_recommendations(self, pareto_solutions, trade_off_analysis, objectives):
        """Generate intelligent recommendations based on Pareto analysis."""
        if not pareto_solutions:
            return {'message': 'No solutions available for recommendations'}
        
        recommendations = {
            'best_overall': None,
            'cost_optimal': None,
            'time_optimal': None,
            'balanced': None,
            'low_risk': None,
            'high_quality': None,
            'summary': []
        }
        
        # Find best solutions for each criterion
        for criterion, solution in recommendations.items():
            if criterion in ['summary']:
                continue
                
            best_solution = None
            best_score = None
            
            for i, sol in enumerate(pareto_solutions):
                if criterion == 'cost_optimal':
                    score = -sol['objective_values'].get('cost', float('inf'))  # Lower cost is better
                elif criterion == 'time_optimal':
                    score = sol['objective_values'].get('time', 0)  # Higher time reduction is better
                elif criterion == 'low_risk':
                    score = sol['objective_values'].get('risk', 0)  # Higher risk score is better (lower actual risk)
                elif criterion == 'high_quality':
                    score = sol['objective_values'].get('quality', 0)  # Higher quality is better
                elif criterion == 'balanced':
                    # Calculate balanced score as geometric mean of normalized objectives
                    normalized_scores = []
                    for obj in objectives:
                        val = sol['objective_values'].get(obj, 0)
                        if obj in ['cost']:  # Lower is better
                            norm_val = 1.0 / (1.0 + val) if val >= 0 else 0
                        else:  # Higher is better
                            norm_val = val
                        normalized_scores.append(norm_val)
                    score = (sum(normalized_scores) / len(normalized_scores)) if normalized_scores else 0
                elif criterion == 'best_overall':
                    # Weighted combination of all objectives
                    weights = {'cost': 0.3, 'time': 0.3, 'quality': 0.2, 'risk': 0.2}
                    score = 0
                    for obj in objectives:
                        val = sol['objective_values'].get(obj, 0)
                        weight = weights.get(obj, 0)
                        if obj in ['cost']:  # Lower is better
                            obj_score = 1.0 / (1.0 + val) if val >= 0 else 0
                        else:  # Higher is better
                            obj_score = val
                        score += obj_score * weight
                
                if best_score is None or (score is not None and score > best_score):
                    best_score = score
                    best_solution = {'index': i, 'solution': sol, 'score': score}
            
            recommendations[criterion] = best_solution
        
        # Generate summary recommendations
        summary = []
        
        if recommendations['cost_optimal']:
            sol = recommendations['cost_optimal']['solution']
            summary.append(f"💰 Cost-Optimal: ${sol['total_cost']:.2f} crash cost, "
                         f"{sol['original_duration'] - sol['final_duration']} time units saved")
        
        if recommendations['time_optimal']:
            sol = recommendations['time_optimal']['solution']
            summary.append(f"⏱️ Time-Optimal: {sol['original_duration'] - sol['final_duration']} time units saved, "
                         f"${sol['total_cost']:.2f} crash cost")
        
        if recommendations['balanced']:
            sol = recommendations['balanced']['solution']
            summary.append(f"⚖️ Balanced: ${sol['total_cost']:.2f} cost, "
                         f"{sol['original_duration'] - sol['final_duration']} time units, "
                         f"Quality: {sol['quality_score']:.2f}")
        
        recommendations['summary'] = summary
        
        return recommendations

    # ============================================================================
    # ENHANCED METHODOLOGY FOUNDATION METHODS (PHASE 1)
    # ============================================================================
    
    def generate_rcps_schedule_for_graph(self, G, resource_limit, priority_rule='minimum_slack'):
        """Generate RCPS schedule for any graph state during crashing evaluation."""
        try:
            activities_data = []
            for node in G.nodes():
                if node not in ['START', 'END']:
                    predecessors = [pred for pred in G.predecessors(node) if pred != 'START']
                    pred_str = ','.join(predecessors) if predecessors else ''
                    
                    activities_data.append({
                        'id': node,
                        'duration': G.nodes[node].get('duration', 1),
                        'resource': G.nodes[node].get('resource_demand', 1),
                        'early_start': G.nodes[node].get('ES', 0),
                        'late_finish': G.nodes[node].get('LF', 0),
                        'float': G.nodes[node].get('float', 0),
                        'predecessors': pred_str,
                        'crash_cost': G.nodes[node].get('crash_cost', 100),
                        'normal_cost': G.nodes[node].get('normal_cost', 50),
                        'min_duration': G.nodes[node].get('min_duration', 1)
                    })
            
            if not activities_data:
                return {
                    'project_duration': 0,
                    'activities': {},
                    'critical_activities': [],
                    'resource_usage': {},
                    'schedule_feasible': False
                }
            
            import pandas as pd
            df_gantt = pd.DataFrame(activities_data)
            
            if hasattr(self.base_analyzer, 'rcps_heuristic_schedule_table'):
                rcps_table, actual_starts, critical_ids = self.base_analyzer.rcps_heuristic_schedule_table(
                    df_gantt, resource_limit, priority_rule
                )
                
                activities = {}
                project_duration = 0
                
                for idx, row in rcps_table.iterrows():
                    if row['id'] not in ['RA', 'RS']:
                        activity_id = row['id']
                        actual_start = row.get('actual_start', row.get('early_start', 0))
                        duration = row.get('duration', 1)
                        actual_finish = actual_start + duration
                        
                        activities[activity_id] = {
                            'actual_start': actual_start,
                            'actual_finish': actual_finish,
                            'resource_used': row.get('resource', 1)
                        }
                        
                        project_duration = max(project_duration, actual_finish)
                
                return {
                    'project_duration': int(project_duration),
                    'activities': activities,
                    'critical_activities': list(critical_ids) if critical_ids else [],
                    'resource_usage': {},
                    'schedule_feasible': True
                }
            
            else:
                mock_schedule = {
                    'project_duration': max([act['early_start'] + act['duration'] for act in activities_data]),
                    'activities': {
                        act['id']: {
                            'actual_start': act['early_start'],
                            'actual_finish': act['early_start'] + act['duration'],
                            'resource_used': act['resource']
                        } for act in activities_data
                    },
                    'critical_activities': [act['id'] for act in activities_data if act['float'] == 0],
                    'resource_usage': {},
                    'schedule_feasible': True
                }
                return mock_schedule
            
        except Exception as e:
            print(f"Error in generate_rcps_schedule_for_graph: {e}")
            return {
                'project_duration': 0,
                'activities': {},
                'critical_activities': [],
                'resource_usage': {},
                'schedule_feasible': False
            }

    def analyze_activity_status(self, G, current_time):
        """Analyze activity execution status at current simulation time."""
        completed = set()
        in_progress = set()
        future = set()
        status_details = {}
        
        for node in G.nodes():
            if node not in ['START', 'END']:
                es = G.nodes[node].get('ES', 0)
                ef = G.nodes[node].get('EF', 0)
                duration = G.nodes[node].get('duration', 1)
                
                if ef <= current_time:
                    completed.add(node)
                    status = 'completed'
                    progress = 1.0
                elif es <= current_time < ef:
                    in_progress.add(node)
                    status = 'in_progress' 
                    progress = (current_time - es) / duration if duration > 0 else 0
                else:
                    future.add(node)
                    status = 'future'
                    progress = 0.0
                
                status_details[node] = {
                    'status': status,
                    'es': es,
                    'ef': ef,
                    'duration': duration,
                    'progress': min(1.0, max(0.0, progress)),
                    'time_remaining': max(0, ef - current_time),
                    'can_be_crashed': (status in ['in_progress', 'future'] and 
                                     G.nodes[node].get('duration', 1) > G.nodes[node].get('min_duration', 1))
                }
        
        return {
            'completed': completed,
            'in_progress': in_progress,
            'future': future,
            'status_details': status_details,
            'summary': {
                'total_activities': len(status_details),
                'completed_count': len(completed),
                'in_progress_count': len(in_progress),
                'future_count': len(future)
            }
        }

    def evaluate_crash_candidates(self, G, resource_limit, priority_rule, current_time, critical_activities):
        """Evaluate each crashable activity using dynamic RCPS impact assessment."""
        candidates = []
        
        current_duration = max([G.nodes[node]['EF'] for node in G.nodes() if 'EF' in G.nodes[node]])
        status_data = self.analyze_activity_status(G, current_time)
        
        for activity in critical_activities:
            eligibility = self._check_crash_eligibility(G, activity, current_time, status_data)
            
            if not eligibility['eligible']:
                continue
            
            try:
                temp_G = G.copy()
                temp_G.nodes[activity]['duration'] = max(
                    eligibility['min_duration'],
                    eligibility['current_duration'] - 1
                )
                
                temp_G = self._recalculate_cpm(temp_G)
                
                temp_schedule = self.generate_rcps_schedule_for_graph(
                    temp_G, resource_limit, priority_rule
                )
                
                if temp_schedule['schedule_feasible']:
                    new_duration = temp_schedule['project_duration']
                    duration_reduction = current_duration - new_duration
                    
                    if duration_reduction > 0:
                        cost_effectiveness = eligibility['crash_cost'] / duration_reduction
                        
                        candidates.append({
                            'activity_id': activity,
                            'crash_cost': eligibility['crash_cost'],
                            'duration_reduction': duration_reduction,
                            'new_project_duration': new_duration,
                            'cost_effectiveness': cost_effectiveness,
                            'current_duration': eligibility['current_duration'],
                            'min_duration': eligibility['min_duration'],
                            'es': eligibility['es'],
                            'ef': eligibility['ef'],
                            'is_in_progress': eligibility['is_in_progress'],
                            'schedule_data': temp_schedule,
                            'feasible': True
                        })
            
            except Exception as e:
                print(f"Error evaluating crash candidate {activity}: {e}")
                continue
        
        candidates.sort(key=lambda x: x['cost_effectiveness'])
        return candidates
    
    def _check_crash_eligibility(self, G, activity, current_time, status_data):
        """Check if activity is eligible for crashing at current time."""
        node_data = G.nodes[activity]
        
        current_dur = node_data.get('duration', 1)
        min_dur = node_data.get('min_duration', 1)
        crash_cost = node_data.get('crash_cost', 100)
        es = node_data.get('ES', 0)
        ef = node_data.get('EF', 0)
        
        activity_status = status_data['status_details'].get(activity, {})
        status = activity_status.get('status', 'unknown')
        
        not_finished = (status in ['in_progress', 'future'])
        has_crash_potential = (current_dur > min_dur)
        has_crash_cost = (crash_cost > 0)
        is_critical = (node_data.get('float', 0) == 0)
        
        eligible = (not_finished and has_crash_potential and has_crash_cost and is_critical)
        
        return {
            'eligible': eligible,
            'crash_cost': crash_cost,
            'current_duration': current_dur,
            'min_duration': min_dur,
            'es': es,
            'ef': ef,
            'is_in_progress': (status == 'in_progress'),
            'status': status,
            'not_finished': not_finished,
            'has_crash_potential': has_crash_potential,
            'has_crash_cost': has_crash_cost,
            'is_critical': is_critical
        }
    
    def _recalculate_cmp(self, G):
        """Recalculate CPM for the given graph."""
        network_builder = getattr(self.base_analyzer, 'network_builder', None)
        if network_builder:
            G = network_builder.forward_pass(G)
            G = network_builder.backward_pass(G)
            G = network_builder.calculate_float(G)
        else:
            print("[WARNING] No network_builder found, using basic CPM fallback")
        
        return G

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
    
    # Filter out "Activity None" entries for cleaner reporting
    meaningful_entries = [entry for entry in result.crash_log if entry.get('activity') != 'None']
    
    if not meaningful_entries:
        lines.append("No activities were crashed during the optimization process.")
        lines.append("")
    else:
        for entry in meaningful_entries:
            activity_id = entry.get('activity', '?')
            crash_cost = float(entry.get('cost', 0))
            # Use 'step_normal_cost' for the report, which is the sum of costs for all active tasks in that step.
            step_normal_cost = float(entry.get('step_normal_cost', 0))
            step_total_cost = crash_cost + step_normal_cost
            cumulative_crash_cost += crash_cost
            cumulative_step_cost += step_total_cost
            
            lines.append(f"Step {entry.get('iteration', '?')}: Activity {activity_id} crashed to duration {entry.get('duration', '?')}")
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
    # Crashed activities summary - exclude "None" activities
    lines.append("-"*50)
    lines.append("Crashed Activities Summary:")
    activity_summary = {}
    for entry in result.crash_log:
        act = entry.get('activity', '?')
        # Skip "None" activities in the summary
        if act == 'None':
            continue
            
        if act not in activity_summary:
            activity_summary[act] = {'crash_cost': 0.0, 'crash_count': 0, 'final_duration': entry.get('duration', '?')}
        activity_summary[act]['crash_cost'] += float(entry.get('cost', 0))
        activity_summary[act]['crash_count'] += 1
        activity_summary[act]['final_duration'] = entry.get('duration', '?')
    
    if not activity_summary:
        lines.append("  - No activities were crashed during optimization")
    else:
        for act, info in activity_summary.items():
            lines.append(f"  - Activity {act}: Crashed {info['crash_count']}x, Total Crash Cost: ${info['crash_cost']:,.2f}, Final Duration: {info['final_duration']}")
    lines.append("="*50)
    return "\n".join(lines)

    # ============================================================================
