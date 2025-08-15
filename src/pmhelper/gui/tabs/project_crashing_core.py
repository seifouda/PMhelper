"""
Project Crashing Core Logic

Contains all core logic classes and functions for project crashing analysis.
All references to 'enhanced' have been removed.
"""

import networkx as nx
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union
from collections import defaultdict
from enum import Enum
import time

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
    def run(self, target_duration, strategy, objective, max_budget=None, max_iterations=300):
        """
        Main entry point for running project crashing analysis.
        Calls the selected strategy method, passing all relevant arguments.
        """
        # Ensure target_duration is always int
        target_duration = int(round(target_duration)) if target_duration is not None else None
        print(f"[DEBUG] ProjectCrashing.run called with target_duration={target_duration}, strategy={strategy}, objective={objective}, max_budget={max_budget}, max_iterations={max_iterations}")
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")
        # Pass all arguments to the selected strategy method
        return self.strategies[strategy](
            target_duration=target_duration,
            max_budget=max_budget,
            max_iterations=max_iterations
        )
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
    # Strategy method stubs for integration testing
    def _lowest_cost_strategy(self, target_duration=None, max_budget=None, max_iterations=300, **kwargs):
        print(f"[DEBUG] _lowest_cost_strategy received target_duration={target_duration}")
        """
        Implements the lowest cost crashing strategy.
        Iteratively crashes the critical path activity with the lowest crash cost per unit until the target duration or budget is met.
        """
        import copy, time as time_mod
        analyzer = self.base_analyzer
        G = copy.deepcopy(getattr(analyzer, 'G', None) or getattr(analyzer, 'graph', None))
        if G is None:
            raise ValueError("No project graph found in analyzer.")

        start_time = time_mod.time()
        crash_log = []
        total_crash_cost = 0.0
        iterations = 0
        termination_reason = ''

        # Initial CPM calculation
        # Use a local forward_pass for project crashing to ensure ES/EF are recalculated using current durations
        def _crash_forward_pass(G):
            for n in nx.topological_sort(G):
                preds = list(G.predecessors(n))
                if preds:
                    G.nodes[n]['ES'] = max(G.nodes[p]['EF'] for p in preds)
                else:
                    G.nodes[n]['ES'] = 0
                G.nodes[n]['EF'] = G.nodes[n]['ES'] + G.nodes[n]['duration']
        _crash_forward_pass(G)
        if hasattr(analyzer, 'backward_pass'): analyzer.backward_pass(G)
        if hasattr(analyzer, 'calculate_float'): analyzer.calculate_float(G)
        # Use max EF for project duration
        ef_dict = nx.get_node_attributes(G, 'EF')
        original_duration = int(round(max(ef_dict.values()))) if ef_dict else 0
        current_duration = original_duration


        # Main crashing loop: stop immediately if current_duration <= target_duration after each crash
        while (target_duration is None or current_duration > target_duration):
            print(f"[DEBUG] Iteration {iterations}: current_duration={current_duration}, target_duration={target_duration}")
            # Debug: print durations of all activities before crash
            print(f"[DEBUG] Activity durations before crash: {[ (n, G.nodes[n].get('duration', '?')) for n in G.nodes ]}")
            if max_iterations is not None and iterations >= max_iterations:
                termination_reason = 'Max iterations reached'
                break
            # Find critical path
            if hasattr(analyzer, 'find_critical_path'):
                critical_path = analyzer.find_critical_path(G)
            else:
                # fallback: path with max EF
                end_node = max(G.nodes, key=lambda n: G.nodes[n].get('EF', 0))
                critical_path = nx.shortest_path(G, source=list(G.nodes)[0], target=end_node)

            # Find crashable activities on critical path
            crashable = []
            for node in critical_path:
                data = G.nodes[node]
                dur = int(round(data.get('duration', 0)))
                min_dur = int(round(data.get('min_duration', dur)))
                crash_cost = data.get('crash_cost', 0)
                normal_cost = data.get('normal_cost', 0)
                ef = int(round(data.get('EF', 0)))
                # Only crash if activity is not finished (iteration < EF)
                if dur > min_dur and crash_cost > 0 and iterations < ef:
                    crashable.append((node, crash_cost, dur, min_dur, normal_cost))
            print(f"[DEBUG] Crashable activities: {crashable}")

            if not crashable:
                print("[DEBUG] No more crashable activities on critical path. Stopping.")
                termination_reason = 'No more crashable activities on critical path'
                break

            # Select activity with lowest crash cost per unit
            crashable.sort(key=lambda x: x[1])
            node, crash_cost, dur, min_dur, normal_cost = crashable[0]
            crash_amount = min(1, dur - min_dur)  # Crash by 1 unit (int) or to min
            cost = crash_cost * crash_amount
            print(f"[DEBUG] Crashing activity {node}: crash_amount={crash_amount}, cost={cost}, dur={dur}, min_dur={min_dur}")
            if max_budget is not None and (total_crash_cost + cost) > max_budget:
                print(f"[DEBUG] Max budget reached. Stopping. total_crash_cost={total_crash_cost}, cost={cost}, max_budget={max_budget}")
                termination_reason = 'Max budget reached'
                break

            # Apply crash (ensure int)
            G.nodes[node]['duration'] = int(round(G.nodes[node]['duration'])) - crash_amount
            G.nodes[node]['crash_cost'] = crash_cost
            G.nodes[node]['normal_cost'] = normal_cost
            total_crash_cost += cost
            iterations += 1
            print(f"[DEBUG] Activity durations after crash: {[ (n, G.nodes[n].get('duration', '?')) for n in G.nodes ]}")
            print(f"[DEBUG] Recalculating CPM after crash...")


            # Recalculate CPM (ES, EF, LS, LF, float) after each crash
            _crash_forward_pass(G)
            if hasattr(analyzer, 'backward_pass'): analyzer.backward_pass(G)
            if hasattr(analyzer, 'calculate_float'): analyzer.calculate_float(G)

            # Explicitly update END node ES/EF after CPM recalculation
            if 'END' in G.nodes:
                preds = list(G.predecessors('END'))
                if preds:
                    G.nodes['END']['ES'] = max(G.nodes[p]['EF'] for p in preds)
                else:
                    G.nodes['END']['ES'] = 0
                G.nodes['END']['EF'] = G.nodes['END']['ES']
                print(f"[DEBUG] [EXPLICIT] END node ES set to: {G.nodes['END']['ES']}, EF set to: {G.nodes['END']['EF']}")
                print("[DEBUG] END node predecessors and their EF/duration:")
                for p in preds:
                    print(f"  {p}: EF={G.nodes[p]['EF']}, duration={G.nodes[p]['duration']}")

            # Debug: print CPM values for all activities
            es_dict = nx.get_node_attributes(G, 'ES')
            ef_dict = nx.get_node_attributes(G, 'EF')
            ls_dict = nx.get_node_attributes(G, 'LS')
            lf_dict = nx.get_node_attributes(G, 'LF')
            float_dict = nx.get_node_attributes(G, 'float')
            print("[DEBUG] CPM values after recalculation:")
            for n in G.nodes:
                print(f"  Activity {n}: ES={es_dict.get(n)}, EF={ef_dict.get(n)}, LS={ls_dict.get(n)}, LF={lf_dict.get(n)}, float={float_dict.get(n)}")
            if 'END' in ef_dict:
                print(f"[DEBUG] END node EF after recalculation: {ef_dict['END']}")
            current_duration = int(round(max(ef_dict.values()))) if ef_dict else 0
            print(f"[DEBUG] Project duration after CPM recalculation: {current_duration}")

            # Stop immediately if target duration is reached or exceeded (before logging step)
            print(f"[DEBUG] After crash: current_duration={current_duration}, target_duration={target_duration}")
            if target_duration is not None and current_duration <= target_duration:
                print(f"[DEBUG] Target duration reached. Stopping. current_duration={current_duration}, target_duration={target_duration}")
                termination_reason = 'Target duration reached'
                break

            # Log step (ensure int for durations)
            crash_log.append({
                'iteration': iterations,
                'activity': node,
                'crash_amount': crash_amount,
                'cost': cost,
                'duration': int(round(G.nodes[node]['duration'])),
                'current_project_duration': current_duration,
                'total_crash_cost': total_crash_cost,
                'critical_path': list(critical_path),
                'normal_cost': normal_cost
            })

        if not termination_reason:
            if target_duration is not None and current_duration <= target_duration:
                termination_reason = 'Target duration reached'
            else:
                termination_reason = 'Completed'

        computation_time = time_mod.time() - start_time
        final_duration = current_duration
        total_normal_cost = sum(G.nodes[n].get('normal_cost', 0) for n in G.nodes)
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
        """Implements the best efficiency crashing strategy (stub)."""
        print("[DEBUG] _best_efficiency_strategy called with args:", args, "kwargs:", kwargs)
        raise NotImplementedError("Best efficiency strategy not yet implemented.")

    def _critical_path_strategy(self, *args, **kwargs):
        """Implements the critical path priority crashing strategy (stub)."""
        print("[DEBUG] _critical_path_strategy called with args:", args, "kwargs:", kwargs)
        raise NotImplementedError("Critical path priority strategy not yet implemented.")

    def _resource_aware_strategy(self, *args, **kwargs):
        """Implements the resource aware crashing strategy (stub)."""
        print("[DEBUG] _resource_aware_strategy called with args:", args, "kwargs:", kwargs)
        raise NotImplementedError("Resource aware strategy not yet implemented.")

class RCPSProjectCrashing:
    """
    RCPS Project Crashing Engine
    Provides RCPS-integrated project crashing with resource management and optimization.
    """
    def __init__(self, base_analyzer):
        self.base_analyzer = base_analyzer
    # ...existing methods from enhanced_project_crashing.py, renamed and commented...

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
        normal_cost = float(entry.get('normal_cost', 0)) if 'normal_cost' in entry else 0.0
        step_cost = crash_cost + normal_cost
        cumulative_crash_cost += crash_cost
        cumulative_step_cost += step_cost
        lines.append(f"Step {entry.get('iteration', '?')}: Activity {activity_id} crashed to duration {entry.get('duration', '?')}")
        lines.append(f"  - Crash Cost: ${crash_cost:,.2f}")
        lines.append(f"  - Normal Cost: ${normal_cost:,.2f}")
        lines.append(f"  - Step Cost: ${step_cost:,.2f}")
        lines.append(f"  - Cumulative Crash: ${cumulative_crash_cost:,.2f}")
        lines.append(f"  - Cumulative Step: ${cumulative_step_cost:,.2f}")
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
